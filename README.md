# SkZemax - Still In Development 

[![Anaconda-Server Badge](https://anaconda.org/usask-arg/usask_arg_example/badges/version.svg)](https://anaconda.org/usask-arg/usask_arg_example)
[![Documentation Status](https://app.readthedocs.org/projects/skzemax/badge/?version=latest)](https://skzemax.readthedocs.io/en/latest/index.html)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/usask-arg/usask_arg_example/main.svg)](https://results.pre-commit.ci/latest/github/usask-arg/usask_arg_example/main)

This package provides a class `skZemaxClass()` to interface with the `PythonStandaloneApplication()` class of Zemax.
All of the things one does in Zemax (and in some cases more) is exposed by the base API of Zemax (ZOS-API). 
The `PythonStandaloneApplication()` class is a boiler plate class that runs Zemax in a standalone way entirely through python code using this API.

However, much of ZOS-API is spread out, inconvenient, and in many cases just doesn't work as intended.
The purpose of this work, and that of `skZemaxClass()`, is to provide convenient encapsulated (and actually working) functions in python which 
execute Zemax operations while making life easier on a user.


To use this package (or the API in general), the user will need some familiarity with the ZOS-API. 
The best place for documentation is to open Zemax and click on `Help->ZOS-API Syntax Help`' and `Help->Help PDF`. 

See the examples in `docs\Examples` which show how to use `skZemaxClass()` to execute some of the examples included with Zemax in `Documents\Zemax\ZOS-API Sample Code\Python`.

## Installation
The package can be installed through `conda` with

`conda install -c usask-arg skZemax`

and the latest nightly available version is available through

`conda install -c usask-arg-nightly skZemax`

## Usage
Documentation can be found at  https://skZemax.readthedocs.io/

## License
This project is licensed under the MIT license
