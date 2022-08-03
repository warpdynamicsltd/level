# LEVEL Language

**Level** is a novel compiled programming language written for Linux based OS 
with x86-64 architecture. Note that Level is under constant development 
and is not ready for use.
This is an early access repository.

**Important information about Level**

- At the current stage of development, **Level** a is statically-typed language with minimalistic support for 
object-oriented programing and with functions, methods and operators overloading.
- Level compiler source code is written entirely in Python 3.x using only standard library modules.
- There are no 3rd party dependencies.
- <i>Python 3.x</i> with installed <i>pip</i> is the only requirement to install and run Level compiler 
on your Linux OS with x86-64 architecture.
- There is no **Level** documentation yet, so the best reference so far is the source code, 
especially files with Level code in [level\examples](examples)
 
### Short Usage Guide

#### System requirements to install and use Level
* x86-64 Linux based OS
* installed Python 3.x with pip

##### Installation guide

To install **Level compiler** execute the following commands from your command line:
```
git clone git@gitlab.com:warpdynamics/level.git

cd level

./install.sh
```

Test if your installation is successful by executing command:

```
level test
```

If installation is successful, you should be able to see something 
similar to the text below. 
```
Level Compiler v0.1.4a
Copyright (c) 2022 Warp Dynamics Limited. All rights reserved.
............................................................................
All tests OK

```

#### Compile Level code

To compile a file `hello.lvl` with **Level** code, execute 
in your command line:
```
level c hello.lvl
```
The above should create a default executable `hello` which
can be executed e.g.
by typing `./hello` in your command line and pressing enter.