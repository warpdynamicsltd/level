import io
from types import SimpleNamespace

from level.execute import *
from level.scripts.level import compile


def test(expected_result):
    assert begin.buffer.get_bytes() == expected_result
    print('.', end='', flush=True)


def test_run(expected_result):
    res, err = run()
    try:
        assert res == expected_result
    except Exception as e:
        print(f"is: {res}")
        print(f"should be: {expected_result}")
        raise e
    print('.', end='', flush=True)


def test_source(cmd, expected_stdout, expected_stderr=b'', script=False):
    if script:
        if expected_stderr == b'':
            switch = '-dr'
        else:
            switch = '-r'

        process = subprocess.Popen(['level', 'c', switch, *cmd],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
    else:
        args = SimpleNamespace(source=cmd, run=True, dev=(expected_stderr== b''), out=False, stats=False, optimise=True)
        if expected_stderr == b'':
            res = compile(args)
            if res != 0:
                sys.exit(res)
            stdout, stderr = run(*cmd[1:])
        else:
            stdout = io.BytesIO()
            stderr = io.StringIO()
            compile(args, stderr=stderr)
            stderr.seek(0)
            stderr = bytes(stderr.read(), encoding='utf-8')

    try:
        assert bytes(stdout) == expected_stdout
    except Exception as e:
        print(cmd)
        print(f"stdout is: {stdout}")
        print(f"stdout should be: {expected_stdout}")
        print(str(stderr, encoding='utf-8'))
        raise e

    try:
        assert expected_stderr in bytes(stderr)
    except Exception as e:
        print(cmd)
        print(f"stderr is: {stderr}")
        print(f"stderr should include: {expected_stderr}")
        raise e
    print('.', end='', flush=True)