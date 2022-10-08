import level.core.x86_64
from level.core.machine_x86_64 import *

class Optimiser():
    def __init__(self, compiler, optimise=False):
        self.compiler = compiler
        self.optimise = optimise
        level.core.x86_64.code = []

    def make_ref_count(self):
        for line in level.core.x86_64.code:
            if line[0] in {'mov_', 'lea_'} and type(line[2]) is list and type(line[2][0]) is Register:
                a = line[2][0]
                a.ref_count += 1

    def compile_machine_code(self):
        if self.optimise:
            self.make_ref_count()
            self.simple_optimise()
        for i, line in enumerate(level.core.x86_64.code):
            eval(line[0])(*line[1:])


    def simple_optimise(self):
        c = 0
        d = 0
        _code = []
        prev_line = None
        for line in level.core.x86_64.code:
            reduction = False
            deep_reduction = False
            if prev_line is not None and line[0] == 'mov_' and prev_line[0] == 'mov_':
                if line[1] == prev_line[2] and line[2] == prev_line[1]:
                    reduction = True
                    a = line[2]
                    b = line[1]
                    if type(a) is list and type(a[0]) is Register and a[0].ref_count == 1:
                        deep_reduction = True

            if not reduction:
                _code.append(line)
            else:
                if deep_reduction:
                    d += 1
                    _code.pop()
                c += 1
            prev_line = line
        # print(c, d)
        level.core.x86_64.code = _code

