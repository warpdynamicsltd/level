import level.core.x86_64
from level.core.machine_x86_64 import *

class Optimiser():
    def __init__(self):
        level.core.x86_64.code = []

    def compile_machine_code(self):
        self.simple_optimise()
        for i, line in enumerate(level.core.x86_64.code):
            #print(line)
            eval(line[0])(*line[1:])


    def simple_optimise(self):
        _code = []
        prev_line = None
        for i, line in enumerate(level.core.x86_64.code):
            if i > 0 and line[0] == 'mov_' and prev_line[0] == 'mov_':
                if line[1] == prev_line[2] and line[2] == prev_line[1]:
                    continue
            _code.append(line)
            prev_line = line
        level.core.x86_64.code = _code

