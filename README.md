# LEVEL Language

**Level** is a novel compiled programming language being developed by Michał Stanisław Wójcik.
The ambition is to create fast (compiled to machine code) language convenient for 
scientific programming.
Note that **Level** is under very dynamic development and is not ready for use yet.
This is an early access repository and you are strongly disencouraged to begin any serious project 
in **Level** yet.

### Quick overview of current Level features
- compiles to ELF executable under Linux based OS on x86-64 architecture 
- statically typed
- basic types: <i>int</i>, <i>byte</i>, <i>bool</i>, <i>i64</i>, <i>i32</i>, <i>u64</i>, <i>u32</i>, <i>float</i> 
- user defined types as combination of <i>ref</i> (pointer/reference type), <i>rec</i> (struct type) and <i>array</i> (array type)
- templates for subroutines and types with second order type variables
- functions and operators overloading
- support for object-oriented programming:
  - dot notation
  - special method definition syntax
  - multiple inheritance
- reference count garbage collection for manged objects (must derive from <i>object</i>)
- standard library with basic data structures: stack, vector, ascii and utf-8 strings

### Important information about Level

- **Level compiler** source code is written in Python 3 using purposely ONLY Python's standard library. Compiler doesn't use any external libraries like 
<i>binutils</i> or <i>glibc</i>. All assembly is coded purely in Python's standard library.
- <i>Python 3.6.0</i> or higher with installed <i>pip</i> is the only requirement to install and run **Level compiler** 
on Linux OS with x86-64 architecture.
- There are no other 3rd party dependencies needed for **Level compiler**.
- At the current phase of development, **Level** supports only x86-64 architecture with Linux based OS.
- There is no **Level** documentation yet, so the best reference so far is the source code, 
especially files with Level code in [examples](examples) (for expected results study 
[level/install/test.py](level/install/test.py)) .
- **Level compiler** source code in this early access phase is published under very restrictive [Level Licence](LICENCE.md), 
which allows only non-commercial use of Level for private persons. At this phase the project also 
does not seek community contributions, hence very restrictive contributions section D of the Level Licence.
Please read very carefully section D of the Level Licence before you attempt to contribute to the project.
After the project will become more mature a proper licence will be worked out.
 
### Short Usage Guide

#### System requirements to install and use Level
* x86-64 architecture with Linux based OS
* installed <i>Python 3.6.0</i> or higher with pip

#### Installation guide

You may obtain **Level compiler** source code from the official repository using `git`: 
```
git clone git@github.com:warpdynamicsltd/level.git
```
To install **Level compiler**, go to the root directory of this project.
Assuming you are still where you ran `git clone` you can go there by

```
cd level
```
and run the following command in your terminal:
```
./install.sh
```

If you want any change in the **Level compiler** source code (e.g. after next `git clone`) to be immediately available 
and/or want to have [level\test_include](test_include) imported 
(some files in [level\examples](examples) will not compile without it),
you should choose `./dev_install.sh`
instead.

Test if your installation is successful by executing the following command:

```
level test
```

If installation is successful, you should be able to see something 
similar to the text below in your terminal. 
```
Level Compiler v0.3.2a
Copyright (c) 2022 Michal Stanislaw Wojcik. All rights reserved.
..........................................................................................................................
Done in 5.13 s
All tests OK
```
#### Compile Level code

To compile a text file `hello.lvl` with **Level** code, run the following command 
in your terminal:
```
level c hello.lvl
```
The above should create an ELF64 executable `hello` which
can be executed e.g.
by typing `./hello` in your terminal and pressing enter.

A short manual for `level` command line tool is available after running:
```
level --help
```
Also each subcommand of `level` can be explained by:
```
level <subcommand> --help
```