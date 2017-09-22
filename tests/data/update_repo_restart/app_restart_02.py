from __future__ import print_function

VERSION = '4.2'


def main():
    print(VERSION)
    with open('version2.txt', 'w') as f:
        print("Writing version file")
        f.write(VERSION)

    print("Leaving main()")


if __name__ == '__main__':
    main()
