import re

def inc_version(filename):
    def replacer(m):
        return m.group(1) + str(int(m.group(2)) + 1)

    with open(filename) as f:
        content = f.read()
        content = re.sub(r"(\d+\.\d+\.)(\d+)", replacer, content)

    with open(filename, "w") as f:
        f.write(content)

    print(content)

if __name__ == "__main__":
    inc_version("level/__init__.py")
