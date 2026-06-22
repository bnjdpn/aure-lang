# Aure 1.0.0

Aure 1.0.0 is the first stable release of a small practical programming language and its Python reference interpreter.

Aure v1.0.0 was written with assistance from GPT-5 through Codex.

## Highlights

- Expression-oriented syntax with functions, closures, arrays, maps, `if`, and `while`.
- `for` loops over arrays, strings, and map keys, with `break` and `continue`.
- Mutable bindings through assignment, plus indexed assignment for arrays and maps.
- Short-circuiting `and` and `or`.
- Pipeline operator for readable data transformations.
- Built-ins for printing, assertions, conversion, ranges, mapping, filtering, reducing, mutation, and collection inspection.
- CLI modes for files, inline `-e` programs, REPL, and version output.
- Standard-library-only test suite with runnable examples.

## Try It

```bash
git clone https://github.com/bnjdpn/aure-lang.git
cd aure-lang
PYTHONPATH=src python3 -m aure examples/hello.aure
PYTHONPATH=src python3 -m aure examples/collections.aure
PYTHONPATH=src python3 -m unittest
```
