#!/usr/bin/env python
import os
import subprocess
import sys


def main():
    darwin = sys.platform == 'darwin'
    directory = os.path.dirname(__file__)
    for builder in os.listdir(directory):
        if not builder.endswith('_build.py'):
            continue
        if builder.startswith('macosx_') and not darwin:
            continue
        fn = os.path.join(directory, builder)
        subprocess.check_call((sys.executable, fn))


if __name__ == '__main__':
    main()
