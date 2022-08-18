import os
import sys
import tempfile
import subprocess
import time

from level.core.x86_64 import *
from level.utils.binparse import *
from level.utils.elf64 import ELF64


def run(*args):
    tmp_f = tempfile.NamedTemporaryFile('wb', delete=False)
    cmp(tmp_f.name)
    tmp_f.close()
    process = subprocess.Popen([tmp_f.name, *args],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    os.remove(tmp_f.name)
    return stdout, stderr

def run_listen(*args):
    tmp_f = tempfile.NamedTemporaryFile('wb', delete=False)
    machine_code_size = cmp(tmp_f.name)
    build_time = time.time()
    tmp_f.close()
    process = subprocess.run([tmp_f.name, *args],
                               stdout=sys.stdout,
                               stderr=sys.stderr)
    os.remove(tmp_f.name)
    return build_time, machine_code_size


def cmp(filename):
    resolve_symbols()
    machine_code = begin.buffer.get_bytes()
    buffer = bytearray(0x1000 + len(machine_code))
    elf = ELF64(buffer,
                mode=BinParse.ACTIVE,
                text_payload=machine_code,
                text_offset=begin.offset,
                entry=begin.entry,
                n_segments=begin.n_segments,
                segment_size = 0x1000 + len(machine_code))

    with open(filename, 'wb', buffering=0x100000) as fout:
        fout.write(buffer[:elf.size])

    os.chmod(filename, 0o700)

    return len(machine_code)


def terminal():
    sys.stdout.write(str(run(), encoding='utf-8'))

