import sys
import subprocess
import os

def system(s):
    output_stream = os.popen(s)
    return output_stream.read().strip()

def main():
    issue = sys.argv[1]
    res = system("git branch --show-current")
    branch = f"LVL-{issue}"
    if res == branch:
        cmd = "python3 scripts/incv.py"
        print(cmd)
        os.system(cmd)
        cmd = f'git commit -am"close #{issue}"'
        print(cmd)
        os.system(cmd)
        cmd = f'git push --set-upstream origin {branch}'
        print(cmd)
        os.system(cmd)
    else:
        sys.stderr.write("You are in wrong branch!\n")


if __name__ == "__main__":
    main()