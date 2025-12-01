skZemax documentation
=====================

The skZemax class is essentially just a wrapper around the native ZOS-API stand-alone application provided by Zemax distributions, :ref:`ZOSAPI`.

This wrapper was made because much of the default/example code and methods of the ZOS-API are cumbersome to use or simply do not work as intended.
skZemax attempts to make an easy to use - and robust - python interface to the ZOS-API.

skZemax is not the first package to do this. For instance, there are good alternative packages like `ZOSPy <https://github.com/MREYE-LUMC/ZOSPy/tree/main>`_.
skZemax however is developed and supported by the Atmospheric Research Group (ARG), at the University of Saskatchewan - Institute of Space and Atmospheric Studies, for its optical work.
The software presented here consists only of the underlying Zemax python interface that ARG incorporates into its other optical work. We have made this interface publicly available in hopes that others will also
find it useful.

   Primary author and point of contact: daniel.letros@usask.ca

Methods of skZemax are organized into categories (see :ref:`api`). This is cosmetic only since all of these functions are members of the same skZemaxClass.
skZemax intentionally has this flattened class architecture for three main reasons:
   
   - The ZOS-API stand-alone application is inherently meant to work within one instantiated class.
   - Ease of use for a user to find functionality with the auto-complete features available in common python IDEs (i.e. VScode, PyCharm).
   - A flattened code hierarchy with minimal abstraction tends to yield code easier to trace and understand (especially for people with minimal experience). 

It is helpful to be familiar with Zemax and the ZOS-API, but skZemax attempts to lighten the load on the user as much as possible. Two main sources
of Zemax documentation can be found through Zemax within the normal user interface of the application:

   - `Help->ZOS-API Syntax Help`
   - `Help->Help PDF`. 

To familiarize yourself with the skZemax package, it is recommend to look through the guided examples given in :ref:`examples` - particularly `Example 01`.
These are some of the native ZOS-API examples (which generally don't work without debugging) reimplemented using the skZemax package.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   Examples/index
   api/index

