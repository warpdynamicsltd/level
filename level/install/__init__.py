import os
from pathlib import Path
home = str(Path.home())

home_level = os.path.join(home, '.level')

def is_setup_done():
    return os.path.isdir(home_level)

def level_setup(path):
    if not is_setup_done():
        os.mkdir(home_level)

        test_path_ = os.path.abspath(os.path.join(path, 'examples'))
        stdlib_path = os.path.abspath(os.path.join(path, 'include'))
        test_include_path_ = os.path.abspath(os.path.join(path, 'test_include'))

        with open(os.path.join(home_level, 'test'), 'w') as f:
            f.write(test_path_)

        with open(os.path.join(home_level, 'test_include'), 'w') as f:
            f.write(test_include_path_)

        with open(os.path.join(home_level, 'modules'), 'w') as f:
            f.write(f"{stdlib_path}\n")



def test_path(filename):
    if is_setup_done():
        with open(os.path.join(home_level, 'test'), 'r') as f:
            return os.path.join(f.read().rstrip(), filename)
    else:
        return None

def test_include_path():
    if is_setup_done():
        with open(os.path.join(home_level, 'test_include'), 'r') as f:
            return f.read().rstrip()
    else:
        return None

def modules():
    res = []
    if is_setup_done():
        with open(os.path.join(home_level, 'modules'), 'r') as f:
            for line in f:
                res.append(line.rstrip())

        return res
    else:
        return []

