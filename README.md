# Aure

Aure is a small practical programming language with a readable Python reference interpreter.

Version `0.1.0` focuses on a coherent core: functions, closures, arrays, maps, loops, pipelines, built-ins, a CLI, a REPL, examples, and tests.

## Quick Start

Run from a checkout:

```bash
PYTHONPATH=src python3 -m aure --version
PYTHONPATH=src python3 -m aure examples/hello.aure
PYTHONPATH=src python3 -m aure -e 'print("Aure", 1 + 2 * 3)'
```

Install locally:

```bash
python3 -m pip install .
aure examples/hello.aure
```

Run the REPL:

```bash
PYTHONPATH=src python3 -m aure repl
```

## Example

```aure
fn makeAdder(base) {
  fn(x) { base + x }
}

let add10 = makeAdder(10)
let evens = range(1, 7) |> filter(fn(x) { x % 2 == 0 })
let total = reduce(evens, 0, fn(acc, x) { acc + x })

print("score:", add10(total))
```

## Language Features

- numbers, strings, booleans, `nil`, arrays, and maps
- `let` bindings that create or update names
- named and anonymous functions
- closures
- `if` expressions
- `while` loops
- array, string, and map indexing
- pipeline operator: `value |> call(extra)`
- built-ins: `print`, `len`, `type`, `str`, `int`, `float`, `range`, `map`, `filter`, `reduce`

See [docs/language-guide.md](docs/language-guide.md) for syntax details.

## Testing

```bash
PYTHONPATH=src python3 -m unittest
```

## Project Status

Aure is an experimental v0.1 language. It is intentionally small and optimized for clarity over raw speed. The current interpreter is a tree-walking reference implementation, which makes the language easy to inspect and evolve.

## AI Assistance

Aure v0.1.0 was written with assistance from GPT-5 through Codex.

## License

MIT. See [LICENSE](LICENSE).
