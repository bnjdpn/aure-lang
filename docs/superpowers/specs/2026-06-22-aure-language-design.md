# Aure Language Design

## Purpose

Aure is a small, practical programming language for clear scripts, teaching, and language experimentation. The "perfect" scope for v0.1 is not maximal feature count; it is a coherent language with a small surface area, deterministic behavior, readable errors, tests, examples, and documentation.

## Design Principles

- Expression-oriented: programs are made of expressions and statements that produce values where useful.
- Low ceremony: top-level `let`, `fn`, `if`, loops, arrays, maps, and function calls are enough for useful scripts.
- Clear failure modes: lexer, parser, and runtime errors include human-readable context.
- Portable implementation: the reference interpreter uses Python 3.9+ and only the standard library.
- Open source ready: the repository includes license, contributing notes, examples, tests, CLI usage, and release notes.

## Language Summary

Aure files use the `.aure` extension.

```aure
let numbers = [1, 2, 3, 4, 5]

fn square(x) {
  x * x
}

let squares = map(numbers, square)
print("squares:", squares)
```

Core values:

- `nil`
- booleans: `true`, `false`
- numbers: integer and decimal values represented as Python numbers
- strings with common escapes
- arrays: `[1, 2, 3]`
- maps: `{"name": "Aure", "version": 0.1}`
- first-class functions and closures

Core syntax:

- `let name = expression` creates or updates a binding in the current scope.
- `fn name(args) { body }` creates a named function.
- anonymous functions use `fn(args) { body }`.
- `if condition { then } else { otherwise }` evaluates to the last value in the chosen block.
- `while condition { body }` repeats while truthy.
- `return expression` exits the current function.
- `expression |> call(...)` pipes the left value into the next call as the first argument.
- comments start with `#` and run to the end of the line.

Built-ins:

- `print(...)` writes values to stdout and returns `nil`.
- `len(value)` returns length for strings, arrays, and maps.
- `type(value)` returns an Aure type name.
- `str(value)`, `int(value)`, and `float(value)` convert values.
- `range(stop)` and `range(start, stop)` return arrays of integers.
- `map(array, fn)` and `filter(array, fn)` return transformed arrays.
- `reduce(array, initial, fn)` folds an array.

## Architecture

The implementation is a tree-walking interpreter:

- `src/aure/lexer.py` converts source text into tokens.
- `src/aure/parser.py` parses tokens into AST dataclasses.
- `src/aure/runtime.py` evaluates the AST in nested environments.
- `src/aure/cli.py` exposes `aure file.aure`, `aure -e "code"`, and `aure repl`.

This keeps the v0.1 implementation small and inspectable while leaving a clean path to bytecode or static analysis later.

## Error Handling

All public execution paths raise or print `AureError` subclasses:

- `AureSyntaxError` for lexing and parsing failures.
- `AureRuntimeError` for undefined names, invalid operations, arity mismatches, and invalid indexing.

CLI errors go to stderr and exit with status `1`. Successful runs exit with status `0`.

## Testing

The test suite uses Python `unittest` so contributors can run it without installing dependencies:

```bash
python3 -m unittest
```

Coverage targets the lexer/parser boundary, runtime semantics, built-ins, pipelines, closures, CLI execution, and error output.

## Release Criteria

Version `0.1.0` is releasable when:

- the interpreter runs real `.aure` examples;
- unit tests pass with Python 3.9+;
- CLI commands work for file, `-e`, and REPL smoke paths;
- README, language guide, examples, license, changelog, and release notes exist;
- the repository is public under `bnjdpn`;
- GitHub release `v0.1.0` exists with concise notes.
