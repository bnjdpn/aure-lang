import argparse
import sys

from . import __version__
from .errors import AureError
from .runtime import Interpreter


def build_parser():
    parser = argparse.ArgumentParser(
        prog="aure",
        description="Run Aure programs.",
    )
    parser.add_argument("file", nargs="?", help="Path to an .aure source file.")
    parser.add_argument("-e", "--eval", dest="eval_source", help="Run Aure source passed on the command line.")
    parser.add_argument("--version", action="store_true", help="Print the Aure version.")
    parser.add_argument("args", nargs=argparse.REMAINDER, help=argparse.SUPPRESS)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    if args.version:
        sys.stdout.write("Aure %s\n" % __version__)
        return 0

    if args.eval_source is not None:
        return run_source(args.eval_source)

    if args.file == "repl" or args.file is None:
        return repl()

    try:
        with open(args.file, "r", encoding="utf-8") as handle:
            return run_source(handle.read())
    except OSError as exc:
        sys.stderr.write("aure: %s\n" % exc)
        return 1


def run_source(source):
    try:
        result = Interpreter().run(source)
    except AureError as exc:
        sys.stderr.write("aure: %s\n" % exc)
        return 1

    sys.stdout.write(result.output)
    return 0


def repl():
    interpreter = Interpreter()
    while True:
        try:
            line = input("aure> ")
        except EOFError:
            sys.stdout.write("\n")
            return 0

        if line.strip() in ("exit", "quit"):
            return 0
        if not line.strip():
            continue

        try:
            result = interpreter.run(line)
        except AureError as exc:
            sys.stderr.write("aure: %s\n" % exc)
            continue

        sys.stdout.write(result.output)
        if result.value is not None and not result.output:
            sys.stdout.write(interpreter.format_value(result.value) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
