from . import cli


def main():
    parser = cli.CmdLineParser()
    parser.parse()
