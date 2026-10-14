# Polarized TM25RAY source files in OpticStudio: notes, test results and planned workflow

This document collects what is known about writing **polarized** TM25RAY source files with skZemax and tracing them
in Ansys Zemax OpticStudio (non-sequential mode, `SourceFile` object). It covers:

1. [How TM-25 defines the polarization of a ray](#1-how-tm-25-defines-the-polarization-of-a-ray)
2. [How OpticStudio reads TM25RAY polarization](#2-how-opticstudio-reads-tm25ray-polarization)
3. [How skZemax encodes polarization](#3-how-skzemax-encodes-polarization)
4. [Test results](#4-test-results)
5. [Known OpticStudio limitation: power of polarized source rays](#5-known-opticstudio-limitation-power-of-polarized-source-rays)
6. [Planned workflow for weighted scenes with complex polarization (TODO)](#6-planned-workflow-for-weighted-scenes-with-complex-polarization-todo)
7. [Open questions and things to re-check](#7-open-questions-and-things-to-re-check)

Unless stated otherwise, all tests were run with **OpticStudio 2026 R1** through skZemax (ZOS-API), with
`NCE_RunRayTrace(SplitNSCRays=True, UsePolarization=True)`, a single wavelength of 820 nm, and rays travelling along +Z.
Section references such as §3.21 refer to ANSI/IES TM-25-20(R25); page references such as p. 599 refer to the
OpticStudio 2026 R1 User Manual (`OpticStudio_UserManual_EN.pdf`). The TM-25 standard is paraphrased here, not quoted.

---

## 1. How TM-25 defines the polarization of a ray

A polarized TM25RAY file sets the **Stokes flag** (§4.7.2.6), which adds six float columns to every ray line, after
the radiant flux / S0 and wavelength columns:

| Column (skZemax name) | Meaning |
|---|---|
| `StokesS1`, `StokesS2`, `StokesS3` | Stokes components **normalized by S0** (§3.21, §4.8.1.10-12) |
| `PolarizationEllipseMajorAxis_XDirectionCosine` (and `_Y`, `_Z`) | Unit vector **M**, orthogonal to the ray direction, giving the Stokes reference frame (§4.8.1.13-15) |

Key rules:

* **Normalization.** S1, S2 and S3 are each in [-1, 1] and S1² + S2² + S3² ≤ 1; the sum equals the polarization
  fraction. S0 itself is the ray's radiant flux (the `RadiantFluxStokesS0` column). S1 = S2 = S3 = 0 is unpolarized.
  Non-normalized Stokes vectors and non-normalized M vectors make the file invalid.
* **Reference frame.** The frame is right-handed: x = M, y = k × M, where **k is the direction of ray propagation**
  (the ray's own direction cosines), not the direction towards the source.
* **What M is.** §3.21 only *recommends* that M lie along the major axis of the polarization ellipse ("because it has
  physical significance"), but the column definitions in §4.8.1.13-15 say M *is* the major axis. Read strictly, a
  Stokes vector expressed in this frame must therefore have **S2 = 0 and S1 ≥ 0**, and the orientation of linear
  polarization is carried entirely by M.
* **Handedness of S3.** TM-25 does not define the sign convention of S3; it defers to "standard textbooks".

## 2. How OpticStudio reads TM25RAY polarization

From the User Manual (Source File object, "Read TM-25 rayfiles (polarization)", pp. 599-600), confirmed by the tests
in section 4:

1. **Polarized or random, per ray.** OpticStudio computes the polarized fraction Sp/S0 with
   Sp = sqrt(S1² + S2² + S3²) and draws a uniform random number per ray. If the random number is larger than the
   polarized fraction, the ray gets a **random** polarization state; otherwise it is fully polarized as described by
   the Stokes vector. Partial polarization is therefore represented *statistically* across many rays, and an
   unpolarized ray (Sp = 0) is always randomized.
2. **Ellipse shape from the Stokes vector.** The shape and handedness of the ellipse come from a standard
   Stokes-to-Jones conversion in a local frame: Ax = sqrt((S0+S1)/2), Ay = sqrt((S0-S1)/2), relative phase
   -atan2(S3, S2). The manual writes these equations with S0, but the stored S1-S3 are used as **normalized** values
   (tested, section 4.2): the S0 value does not affect the polarization state.
3. **Orientation only from M.** The ellipse is rotated about k so that its **major axis lies along M**. S2 can not
   rotate the state away from M (tested, section 4.1). (The manual describes the rotation as "by angle Ap"; the
   observed behaviour is that the major axis ends up on M.)
4. **E-field columns take priority.** If the file contains the extra columns `phase`, `phase_dbl_err`, `exr`, `exi`,
   `eyr`, `eyi`, `ezr`, `ezi`, OpticStudio uses those E-field components for the polarization **state** instead of
   the Stokes columns. The manual only mentions this for files written by OpticStudio, but it also works for files
   written by skZemax (tested, section 4.5). The E-field **magnitude** of each ray is *not* used (section 5).
5. **Files written by OpticStudio** (`Save Rays` on a detector, `NCE_RunRayTrace(SaveRays=True, ...)`):
   * contain the 8 E-field/phase columns above, with |E|² (summed over x, y, z) equal to the ray power in the file's
     raw units,
   * write normalized Stokes values with **M on the major axis (S2 = 0)**, and S3 = +1 written back for a ray that
     was read in with S3 = +1 (the sign is self-consistent),
   * use Spectral Data Identifier 2 (wavelength per ray), description strings such as "Zemax OpticStudio", and a
     creation date like `2026-10-14T16:38:34-0600` (no colon in the time-zone offset).

## 3. How skZemax encodes polarization

### 3.1 Stokes in a user basis → TM25RAY columns

`_stokes_to_TM25RAY_polarization_` (in `wirting_workers.py`) converts Stokes vectors measured in a user-chosen basis
into the TM25RAY columns. The user basis is (x_ref, y_ref, k) with y_ref = k × x_ref (right-handed), so that +S1 is
linear along x_ref, +S2 is linear at +45° from x_ref towards y_ref, and S3 is circular. The defaults are k = +Z,
x_ref = +X (so y_ref = +Y), the usual lab frame. The conversion rotates the basis about k by the ellipse azimuth:

```
psi = 0.5 * atan2(S2, S1)                      # azimuth of the major axis from x_ref towards y_ref
M   = cos(psi) * x_ref + sin(psi) * y_ref      # where the major axis points (3D, orthogonal to k)
(S1, S2, S3)_TM25 = (sqrt(S1² + S2²), 0, S3) / S0
```

* The factor ½ is there because an ellipse repeats every 180° while the Stokes angle repeats every 360°.
* After the rotation all of the linear part is in S1 (S2 = 0, S1 ≥ 0); S3 is unchanged by a rotation about k.
* The result is valid under both readings of TM-25 (section 1) and gives the intended state in OpticStudio.
* Edge cases: `reference_x` does not need to be exactly orthogonal to k (its component along k is removed), but it
  must not be parallel to k. For circular or unpolarized light psi is undefined and M = x_ref is used.
  M and -M describe the same ellipse.
* **Backward rays:** because y_ref = k × x_ref, reversing k with the same x_ref flips y_ref (k = -Z, x_ref = +X gives
  y_ref = -Y), so +S2 then appears at -45° in lab coordinates. Use x_ref = -X for backward rays to keep the lab sense
  of +45°.

Worked examples (k = +Z, x_ref = +X):

| Input (S0, S1, S2, S3) | Written Stokes | M |
|---|---|---|
| unpolarized (1, 0, 0, 0) | (0, 0, 0) | (1, 0, 0) |
| X-linear (1, 1, 0, 0) | (1, 0, 0) | (1, 0, 0) |
| Y-linear (1, -1, 0, 0) | (1, 0, 0) | (0, 1, 0) |
| +45° (1, 0, 1, 0) | (1, 0, 0) | (0.707, 0.707, 0) |
| -45° (1, 0, -1, 0) | (1, 0, 0) | (0.707, -0.707, 0) |
| circular (1, 0, 0, 1) | (0, 0, 1) | (1, 0, 0) |
| 50% polarized at +45° (2, 0, 1, 0) | (0.5, 0, 0) | (0.707, 0.707, 0) |

### 3.2 Validation done by the reader and writer

`_ray_data_error_checking_` (in `reading_and_writeing_workers.py`) rejects ray data with NaNs, non-normalized Stokes
vectors, non-unit M, or M not orthogonal to the ray direction (tolerance 1e-3). The writer also **warns** when a
polarized file has non-uniform S0, because of the limitation in section 5.

## 4. Test results

All tests ran from a scratch folder; source files were written to OpticStudio's `Objects\Sources\Source Files`
folder. Ray data was read back with `TM25RAY_ReadFile` from files saved by OpticStudio at the named detector object.
Detector totals were read with `GetAllDetectorDataSafe` (incoherent power), with no rescaling by skZemax.

### 4.1 Orientation comes only from M

Four rays along +Z, S0 = 1, all with M = +Y, saved at a transparent detector 0.01 mm after the source:

| Ray | Stokes (S1, S2, S3) in file | State in OpticStudio |
|---|---|---|
| 0 | (0, 0, 0) | random (different each trace) |
| 1 | (1, 0, 0) | Y-linear |
| 2 | (0, 1, 0) | **Y-linear** (same as ray 1: S2 did not rotate it) |
| 3 | (0, 0, 1) | circular, E_y = -i·E_x, written back as S3 = +1 |

With the same four states converted by `_stokes_to_TM25RAY_polarization_` (lab basis), OpticStudio gave X-linear,
+45° linear (E_x = E_y) and circular for rays 1-3, as intended. After an ideal linear polarizer at 45° (Mueller matrix
object) the transmitted fractions followed Malus's law (1.0 for the +45° ray, 0.5 for X-linear and circular, and
cos² of the random angle for ray 0).

### 4.2 Stokes S1-S3 are read as normalized by S0

500 identical rays per run, only S0 changed between runs:

| Stored Stokes | S0 per ray | Fraction arriving X-linear | Expected if read as absolute values |
|---|---|---|---|
| S1 = 1 (fully polarized) | 1, 2, 4, 0.5 | 1.000 for all | 1.00, 0.50, 0.25, NaN/error |
| S1 = 0.5 (50 % polarized) | 1, 2, 0.5 | 0.486, 0.490, 0.512 | 0.50, 0.25, 1.00 |

So the S0 value does not affect the polarization state, and partial polarization is randomized per ray in proportion
to the degree of polarization, as described in section 2. Each ray arrived with 10 W / 500 = 0.02 W: OpticStudio
rescales the total to the source's `Power_Watts`; S0 in the file only sets relative weights.

### 4.3 Power drops after the first interaction (polarized files)

Four polarized rays, S0 = 1 each, `Power_Watts` = 10, a transparent detector ("dummy", blank material) 0.01 mm after
the source and an absorbing detector at 20 mm:

| Object between the detectors | Dummy detector | Final detector |
|---|---|---|
| Ideal linear polarizer at 45° (Mueller matrix) | 10 W (2.5 W per ray) | 2.07 W (0.07, 0.5, 1, 0.5 per ray) |
| Identity Mueller matrix | 10 W | **4 W (1.0 per ray)** |
| Null object (nothing) | 10 W | **4 W (1.0 per ray)** |
| No dummy detector at all | - | **10 W** |

The drop does not depend on the number of analysis rays (4, 10 and 20 gave the same totals).

With S0 = 0.5, 1, 2, 3 (sum 6.5) and X-linear rays:

| `Power_Watts` | Dummy detector (first hit) | Final detector |
|---|---|---|
| 10 | 10 W; 0.77, 1.54, 3.08, 4.62 W per ray (correct) | **6.5 W; 1.625 W per ray** |
| 20 | 20 W; 1.54, 3.08, 6.15, 9.23 W per ray (correct) | **6.5 W; 1.625 W per ray** |

### 4.4 The drop only affects polarized TM25RAY files

Same S0 = 0.5, 1, 2, 3 rays, `Power_Watts` = 10 (expected 0.77, 1.54, 3.08, 4.62 W per ray everywhere):

| Variant | Final detector |
|---|---|
| Polarized TM25RAY (Stokes columns) | 6.5 W, 1.625 W per ray (wrong) |
| Header `TotalRadiantFlux` patched to 100 W | 6.5 W, 1.625 W per ray (header value is not used) |
| Dummy replaced by a plain transparent Rectangle (not a detector) | 6.5 W, 1.625 W per ray (any interaction triggers it) |
| **Text `.DAT` source file** | **10 W, 0.77, 1.54, 3.08, 4.62 W (correct)** |
| **TM25RAY without Stokes columns** | **10 W, 0.77, 1.54, 3.08, 4.62 W (correct)** |

### 4.5 E-field columns set the state but not the power

Same rays, Stokes columns saying X-linear, plus hand-written E-field columns:

| E-field columns | State arriving | \|E\|² per ray at dummy | Final detector |
|---|---|---|---|
| Y-linear, \|E\|² = S0 | **Y** (E-field wins over Stokes) | 1.625 each (file average) | 6.5 W, 1.625 each |
| X-linear, \|E\|² = S0 | X | 1.625 each | 6.5 W, 1.625 each |
| X-linear, \|E\|² = 10·S0/6.5 | X | 2.5 each (file average) | 10 W, 2.5 each |

## 5. Known OpticStudio limitation: power of polarized source rays

**Summary (OpticStudio 2026 R1):** for a TM25RAY source file with polarization data (Stokes columns and/or E-field
columns), every ray's electric field gets the **file-average magnitude**. The *first* ray segment still carries the
correct power (`Power_Watts` × the ray's relative S0, as the manual describes for source files), but after the ray's
first interaction with **any** object (transparent detector, plain surface, Mueller matrix, ...) the power is
recomputed from |E|². From then on every polarized ray carries the file-average power:

* **per-ray weighting is lost** (rays with S0 = 0.5 and 3 both continue with the average), and
* the absolute power is only right if the file-average ray power equals `Power_Watts` / N; otherwise the downstream
  total is the sum of the file's raw S0 (or |E|²) values, regardless of `Power_Watts`.

Not affected: unpolarized TM25RAY files and DAT/SDF source files keep each ray's scaled power throughout.
Measurements at the *first* object the rays hit are also correct.

**Consequences for skZemax users (current state):**

* Write polarized source files with **uniform S0** (equal power per ray). The writer issues a warning otherwise, but
  still writes the file as given (so the file stays a faithful TM-25 file for other software).
* For correct absolute power, make S0 the real per-ray power in watts and set the source's `Power_Watts` to ΣS0
  (= N × S0).
* Results computed only as ratios between rays with equal S0 (e.g. polarizer transmission) are unaffected.
* This looks like an OpticStudio bug and should be reported to Ansys; the tables in section 4.3-4.5 are a minimal
  reproducible example.

**Why simple workarounds do not scale.** A weighted ray can be represented by several identical equal-power copies
(e.g. weights 0.5 : 1 : 2 : 3 as 1 + 2 + 4 + 6 copies of 0.5 W). This is exact only for weights that are integer
multiples of a common unit, the ray count grows quickly for large dynamic ranges, and `Analysis_Rays` must cover all
copies. For coherent work it is also physically wrong: a coherent detector sums complex amplitudes, so representing a
bright region with *more* equal-amplitude rays instead of *stronger* rays makes the summed amplitude scale like the
intensity rather than its square root, distorting fringe contrast. Sampling ray density in proportion to intensity has
the same problem for interferograms (it is fine for incoherent images). Neither approach is suitable for scenes with
several hundred thousand rays.

## 6. Planned workflow for weighted scenes with complex polarization (TODO)

The goal is to trace scenes of up to several hundred thousand rays with arbitrary, spatially varying polarization
states and weights, to simulate images and interferograms at the ray level, on typical desktop machines. The idea is
to only ever trace **uniform-power rays with uniform polarization** in OpticStudio (which works correctly, section 5)
and to apply the scene's weights and polarization states in skZemax afterwards, using the linearity of Mueller (for
intensities) and Jones (for fields) calculus.

### 6.1 Imaging: per-pixel (scene-dependent) Mueller matrix of the instrument

1. **Calibration traces.** Trace the scene's own ray geometry (same positions and directions as the scene, so field
   angles and pupil filling match) with uniform power and a uniform polarization state, once for each of at least
   **4 linearly independent states**, e.g. H, V, +45° and right circular. Six states (H, V, ±45°, R, L) over-determine
   the solution and average out noise. Depolarizing optics (e.g. Mueller matrix objects with depolarization,
   scattering) and ray splitting are allowed: they act incoherently and are captured statistically.
2. **Output Stokes per pixel.** Save the rays at the detector (`SaveRays`) and bin their E-fields into per-pixel
   Stokes images (incoherent sum of the Stokes vectors of the rays landing in each pixel). Enough rays per pixel are
   needed for the statistics of randomized/depolarized rays.
3. **Mueller matrix per pixel.** Each calibration state gives S_out(p) = M(p)·S_in for every pixel p. Solve for the
   16 elements of M(p) per pixel (exactly with 4 states, by least squares with more).
4. **Scene trace.** Trace the scene once **unpolarized** with its true per-ray weights (unaffected by the limitation,
   section 4.4). This gives the intensity reaching each pixel and which scene rays contribute to it.
5. **Effective input Stokes per pixel.** Average the scene's per-ray Stokes vectors over the rays reaching pixel p,
   weighted by their power: S_in,eff(p) = Σ w_i S_in,i / Σ w_i. This is valid because Mueller calculus is linear.
   It needs the identity of each detected ray (source ray → pixel), e.g. from the ZRD ray database.
6. **Polarized image.** S_out(p) = M(p) · S_in,eff(p), scaled by the scene trace's intensity.

**Assumption to document with results:** each pixel sees a *localized* scene region, so one M(p) applies to all light
reaching it. Blur, ghosts and stray light (e.g. from ray splitting) mix light from distant scene points into a pixel;
to first order this is absorbed into the "scene-dependent" M(p), but it is not exact. Calibration is per wavelength.

### 6.2 Interferograms: per-ray Jones matrices

1. Trace the same uniform-power rays twice, with X-linear and Y-linear input (e.g. written with E-field columns).
2. Each detected ray's output E-field for the two inputs gives a 2×2 (complex) **Jones matrix per ray**, including the
   phase (the `phase`/`phase_dbl_err` columns of saved files).
3. In skZemax: E_out,i = J_i · (sqrt(w_i) · E_in,i) for any scene weight w_i and polarization state E_in,i, then sum
   the complex fields per pixel (coherent sum) to form the interferogram. Partially polarized input is an incoherent
   sum of two orthogonal pure states.
4. Changing scene weights or polarization does not need a new trace.

**Limitations:** this is a first-order approach. It requires a deterministic, one-to-one mapping between source rays
and detected rays, so it does **not** support depolarizing optics or ray splitting (turn splitting off or keep only
the main path), and it needs ray identity to be preserved between the X and Y traces.

Memory estimate: a saved TM25RAY ray line from OpticStudio has about 22 floats (88 bytes), so 300 000 rays are about
26 MB per trace, which is fine for typical desktop memory.

## 7. Open questions and things to re-check

* **Ray identity between traces.** Is the order of rays in files saved by OpticStudio stable between traces, also
  with multi-core tracing? If not, the ZRD ray database (which stores ray numbers) is needed for sections 6.1 step 5
  and 6.2. Not yet tested.
* **Linearity check for 6.2.** Verify per ray that E_45 = (E_X + E_Y)/sqrt(2), including phase, through
  representative optics.
* **Physical handedness of S3.** OpticStudio is self-consistent (S3 = +1 in, S3 = +1 out, E_y = -i·E_x), but the
  physical handedness depends on its phase/time convention. Check against a known circular source before relying on
  the sign.
* **Re-test the limitation in new OpticStudio versions** (section 4.3-4.5 tables are the reproduction recipe), and
  report it to Ansys.
* **Weighted, polarized SDF/DAT?** DAT/SDF files keep per-ray power but have no per-ray polarization; their
  polarization comes from the source object's settings (uniform per source object).
