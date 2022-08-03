from level.execute import *


def test(expected_result):
    assert begin.buffer.get_bytes() == expected_result
    print('.', end='', flush=True)


def test_run(expected_result):
    res = run()
    try:
        assert res == expected_result
    except Exception as e:
        print(f"is: {res}")
        print(f"should be: {expected_result}")
        raise e
    print('.', end='', flush=True)


def test_source(cmd, expected_stdout, expected_stderr=b''):
    process = subprocess.Popen(['level', 'c', '-dr', *cmd],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    try:
        assert bytes(stdout) == expected_stdout
    except Exception as e:
        print(cmd)
        print(f"stdout is: {stdout}")
        print(f"stdout should be: {expected_stdout}")
        print(str(stderr, encoding='utf-8'))
        raise e

    try:
        assert stderr == expected_stderr
    except Exception as e:
        print(cmd)
        print(f"stdout is: {stderr}")
        print(f"stdout should be: {expected_stderr}")
        raise e
    print('.', end='', flush=True)