# LEVEL Language

**Level** is a novel compiled programming language written for Linux based OS 
with x86-64 architecture. Note that Level is under constant development 
and is not ready for use.
This is an early access repository.

**Important information about Level**

- At the current stage of development, **Level** is a statically-typed language with minimalistic support for 
object-oriented programing and with functions, methods and operators overloading.
- **Level compiler** source code is written in Python 3 using ONLY Python's standard library. 
- There are no other 3rd party dependencies.
- <i>Python 3.6.0</i> or higher with installed <i>pip</i> is the only requirement to install and run **Level compiler** 
on your Linux OS with x86-64 architecture.
- There is no **Level** documentation yet, so the best reference so far is the source code, 
especially files with Level code in [level\examples](examples).
- **Level compiler** source code in early access phase is published under Attribution-NonCommercial-NoDerivatives 4.0 International
licence. After the project will become more mature the final licence will be worked out.
 
### Short Usage Guide

#### System requirements to install and use Level
* x86-64 Linux based OS
* installed Python 3.x with pip

#### Installation guide

You may obtain **Level compiler** source code from the official repository using `git`: 
```
git clone git@github.com:warpdynamicsltd/level.git
```
To install **Level compiler** execute the following commands in your terminal:
```
cd level
```
```
./install.sh
```

If you want any change in the **Level compiler** source code (e.g. after next `git clone`) to be immediately available 
and want to have [level\test_include](test_include) imported 
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
Level Compiler v0.1.4a
Copyright (c) 2022 Warp Dynamics Limited. All rights reserved.
............................................................................
All tests OK
```
#### Compile Level code

To compile a text file `hello.lvl` with **Level** code, execute the following command 
in your terminal:
```
level c hello.lvl
```
The above should create an ELF64 executable `hello` which
can be executed e.g.
by typing `./hello` in your terminal and pressing enter.