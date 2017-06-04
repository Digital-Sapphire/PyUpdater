from __future__ import print_function

VERSION = '4.2'


def main():
    print(VERSION)
    with open('version1.txt', 'w') as f:
        f.write(VERSION)
    return VERSION


if __name__ == '__main__':
    main()
