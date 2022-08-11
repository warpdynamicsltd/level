from level.core.compiler import Compiler
from level.core.parser.linker import Lead
from level.core.compiler.x86_64 import *
from level.core.ast import *
from level.tests import test_run
from types import SimpleNamespace

x = Var('x')
y = Var('y')
z = Var('z')

subroutine_def = SubroutineDef('f',
                               VarList(InitWithType(x, Type('u32'), ConstVoid())),
                               StatementList(
                                   InitWithType(y, Type('u32'), ConstVoid()),
                                   Assign(y, x),
                                   Echo(y),
                                   Return(y)
                               ), Type('u32'))

statement_list = StatementList(
    InitWithType(x, Type('u32'), ConstVoid()),
    InitWithType(z, Type('u32'), ConstVoid()),
    Assign(x, Const(0x3)),
    Assign(z, Const(0x4)),
    InitWithType(y, Type('u32'), ConstVoid()),
    Assign(y, Call(Var('f'), x).add_calling_name('f')),
    Echo(Call(Var('f'), z).add_calling_name('f')),
    Echo(x),
    Return(Const(1)))

p = Program(AssignTypeList(), GlobalBlock(), DefBlock(subroutine_def), statement_list)
comp = Compiler(p, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'00000003\n00000004\n00000004\n00000003\n')