import sys
import subprocess
import os

def system(s):
    output_stream = os.popen(s)
    return output_stream.read().strip()

def main():
    issue = sys.argv[1]
    res = system("git branch --show-current")
    if res == f"LVL-{issue}":
        cmd = "python scripts/incv.py"
        print(cmd)
        os.system(cmd)
        cmd = f'git commit -am"close #{issue}"'
        print(cmd)
        os.system(cmd)
        cmd = f'git push'
        print(cmd)
        os.system(cmd)
    else:
        sys.stderr.write("You are in wrong branch!\n")


if __name__ == "__main__":
    main()