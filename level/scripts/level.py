import sys
import shutil

import argparse

from level.core.parser.code import *
from level.core.compiler.x86_64 import *
from level.core.parser.linker import LinkerException
from level.core.ast import GrammarTreeError
from level.execute import cmp, run_listen
from level.install import *

welcome_message = \
f"""Level Compiler {level.__version__}
Copyright (c) 2022 Michal Stanislaw Wojcik. All rights reserved."""

home = str(Path.home())

class LevelArgumentParser(argparse.ArgumentParser):
   def error(self, message):
       print(welcome_message)
       argparse.ArgumentParser.error(self, message)

def get_args():
    parser = LevelArgumentParser(description=welcome_message)
    subparsers = parser.add_subparsers()
    comp = subparsers.add_parser("c", help="Level compiler")

    comp.add_argument("source", metavar="arg", type=str, nargs="+", help="Level source code file path and args to pass")
    comp.add_argument("-o", "--out", type=str, default=None, help="executable output path")
    comp.add_argument("-r", "--run", action='store_true', help="compile and run redirecting stdout and stderr")
    comp.add_argument("-d", "--dev", action='store_true', help="Level developer mode")
    comp.set_defaults(func=do_cmp)

    install = subparsers.add_parser("install", help="install Level module")
    install.add_argument("path", nargs="?", type=str, help="Level module path")
    install.add_argument("-l", "--list", action='store_true', help="list all modules")
    install.set_defaults(func=do_install)

    uninstall = subparsers.add_parser("uninstall", help="uninstall Level module")
    uninstall.add_argument("path", type=str, nargs="?", help="Level module path")
    uninstall.set_defaults(func=do_uninstall)

    clear = subparsers.add_parser("clear", help="delete ~/.level directory. warning: this will uninstall all modules")
    clear.add_argument("-y", "--yes", action='store_true', help="answer all yes")
    clear.set_defaults(func=do_clear)

    setup = subparsers.add_parser("setup", help="complete Level installation")
    setup.add_argument("path", type=str, help="Level root directory" )
    setup.set_defaults(func=do_setup)

    test = subparsers.add_parser("test", help="test Level installation")
    test.set_defaults(func=do_test)

    args = parser.parse_args()

    return args

def stop_if_no_setup():
    if not is_setup_done():
        print("'level setup' not done")
        print("nothing to do")
        sys.exit(0)

def do_install(args):
    stop_if_no_setup()

    if not os.path.isdir(home_level):
        os.mkdir(home_level)

    if args.path:
        modules_file = os.path.join(home_level, 'modules')
        paths_set = set()
        with open(modules_file, "r") as f:
            for line in f:
                paths_set.add(line.rstrip())

        new_line = os.path.abspath(args.path)
        if new_line not in paths_set:
            with open(modules_file, "a") as f:
                f.write(f"{new_line}\n")

        return

    if args.list:
        modules_file = os.path.join(home_level, 'modules')
        with open(modules_file, "r") as f:
            for line in f:
                print(line.rstrip())

def do_uninstall(args):
    stop_if_no_setup()

    if args.path:
        modules_file = os.path.join(home_level, 'modules')
        paths_set = set()
        with open(modules_file, "r") as f:
            for line in f:
                paths_set.add(line.rstrip())

        line = os.path.abspath(args.path)

        if line in paths_set:
            paths_set.remove(line)

            with open(modules_file, "w") as f:
                for line in paths_set:
                    f.write(f"{line}\n")

        return

def do_setup(args):
    level_setup(args.path)

def do_clear(args):
    print('deleting ~/.level directory and uninstall all modules')
    if args.yes or input('Do you wish to continue [y/n]: ') in {'y', 'yes'}:
        if is_setup_done():
            shutil.rmtree(home_level)
        print("all deleted")
    else:
        print("nothing has been done")

def do_test(args):
    stop_if_no_setup()
    print(welcome_message)
    import level.install.test

def do_cmp(args):
    sys.exit(do_cmp_(args))

def do_cmp_(args):
    stop_if_no_setup()

    if not os.path.isfile(args.source[0]):
        sys.stderr.write(f"path '{args.source[0]}' doesn't exist\n")
        return 1

    with open(args.source[0], "rb", buffering=100000) as f:
        code = str(f.read(), encoding='utf-8')
        if not args.dev:
            try:
                program = Parser(code).parse()
            except LinkerException as e:
                sys.stderr.write(str(e))
                sys.stderr.write('\n')
                return 1
            except ParseException as e:
                sys.stderr.write(str(e))
                sys.stderr.write('\n')
                return 1
            except Exception as e:
                sys.stderr.write("unrecognised parser error")
                sys.stderr.write('\n')
                return 1
        else:
            program = Parser(code).parse()

        if not args.dev:
            try:
                comp = Compiler(program, StandardObjManager, CompileDriver_x86_64)
                comp.compile()
            except CompilerException as e:
                sys.stderr.write(str(e))
                sys.stderr.write('\n')
                return 1
            except CompilerNotLocatedException as e:
                sys.stderr.write(str(e))
                sys.stderr.write(f": compiler error in {comp.meta}")
                sys.stderr.write('\n')
                return 1
            except GrammarTreeError as e:
                sys.stderr.write(str(e))
                sys.stderr.write(f": compiler error in {comp.meta}")
                sys.stderr.write('\n')
                return 1
            except Exception as e:
                sys.stderr.write(str(e))
                sys.stderr.write(f": unrecognised compiler error in {comp.meta}")
                sys.stderr.write('\n')
                return 1
        else:
            try:
                comp = Compiler(program, StandardObjManager, CompileDriver_x86_64)
                comp.compile()
            except Exception as e:
                sys.stderr.write(f"compiler error in {comp.meta}\n")
                sys.stderr.write('\n')
                raise e

        if args.out is None:
            filename = Path(args.source[0]).stem
        else:
            filename = args.out

        if not args.run:
            if not args.dev:
                try:
                    cmp(filename)
                except Exception as e:
                    sys.stderr.write("unrecognised error")
                    sys.stderr.write('\n')
                    return 1
            else:
                cmp(filename)

        else:
            if not args.dev:
                try:
                    run_listen(*args.source[1:])
                except Exception as e:
                    sys.stderr.write("unrecognised compile time error")
                    sys.stderr.write('\n')
                    return 1
            else:
                run_listen(*args.source[1:])

    return 0

def main():
    args = get_args()
    if 'func' in args:
        args.func(args)
    else:
        print(welcome_message)

