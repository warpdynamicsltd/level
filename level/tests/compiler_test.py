from level.core.compiler import Compiler
from level.core.parser.linker import Lead
from level.core.compiler.x86_64 import *
from level.core.ast import *
from level.tests import test_run
from types import SimpleNamespace

x = Var('x')
y = Var('y')
z = Var('z')

subroutine_def = SubroutineDef(SimpleNamespace(key='f', name='f'),
                               VarList(InitWithType(x, Type('u32'), ConstVoid())),
                               StatementList(
                                   Init(y),
                                   Assign(y, x),
                                   Echo(y),
                                   Return(y)
                               ), Type('u32'))

statement_list = StatementList(
    Init(x),
    Init(z),
    Assign(x, Const(0x3)),
    Assign(z, Const(0x4)),
    Init(y),
    Assign(y, Call(Var('f'), x).add_lead(Lead('f', 'f'))),
    Echo(Call(Var('f'), z).add_lead(Lead('f', 'f'))),
    Echo(x),
    Return(Const(1)))

p = Program(AssignTypeList(), DefBlock(subroutine_def), statement_list)
comp = Compiler(p, StandardObjManager, CompileDriver_x86_64)
comp.compile()

test_run(b'00000003\n00000004\n00000004\n00000003\n')