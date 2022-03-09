import argparse, pathlib, sys

platform = sys.platform

if platform == 'linux':
    logPath = pathlib.Path('~/.local/share/ACP/log.txt').expanduser()
    configPath = pathlib.Path('~/.local/share/ACP/config.json').expanduser()

def getArgs(null):
    rootParser = argparse.ArgumentParser(prog='ACP', description='A package manager that aims to eliminate the headaches other package managers incur.')
    subParsers = rootParser.add_subparsers()
    
    infoParser = subParsers.add_parser('info')
    infoParser.set_defaults(function=info)
    infoParser.add_argument(
        name='package',
        help='package to operate on',
        type=str
    )

    return rootParser.parse_args()

def info(args):
    print(args)

def main(argv):
    args = getArgs(argv)
    args.function(args)


if __name__ == '__main__':
    main(sys.argv)