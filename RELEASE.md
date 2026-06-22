# Aure 0.1.0

Aure 0.1.0 is the first public release of a small practical programming language and its Python reference interpreter.

## Highlights

- Expression-oriented syntax with functions, closures, arrays, maps, `if`, and `while`.
- Pipeline operator for readable data transformations.
- Built-ins for printing, conversion, ranges, mapping, filtering, and reducing.
- CLI modes for files, inline `-e` programs, REPL, and version output.
- Standard-library-only test suite with runnable examples.

## Try It

```bash
git clone https://github.com/bnjdpn/aure-lang.git
cd aure-lang
PYTHONPATH=src python3 -m aure examples/hello.aure
PYTHONPATH=src python3 -m unittest
```
