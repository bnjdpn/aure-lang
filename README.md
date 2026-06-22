<p align="center">
  <img src="docs/assets/aure-logo.svg" alt="Aure logo" width="420">
</p>

# Aure

Aure is a small practical programming language with a readable Python reference interpreter.

Version `1.0.0` focuses on a coherent core: functions, closures, arrays, maps, loops, mutation, pipelines, collection built-ins, a CLI, a REPL, examples, and tests.

## Quick Start

Run from a checkout:

```bash
PYTHONPATH=src python3 -m aure --version
PYTHONPATH=src python3 -m aure examples/hello.aure
PYTHONPATH=src python3 -m aure examples/collections.aure
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
- assignment with `name = expression`
- named and anonymous functions
- closures
- `if` expressions
- `while` loops and `for name in collection` loops
- `break` and `continue`
- short-circuiting `and` and `or`
- array, string, and map indexing
- array and map indexed assignment
- pipeline operator: `value |> call(extra)`
- built-ins: `print`, `assert`, `len`, `type`, `str`, `int`, `float`, `range`, `map`, `filter`, `reduce`, `push`, `pop`, `keys`, `values`, `contains`

See [docs/language-guide.md](docs/language-guide.md) for syntax details.

## Testing

```bash
PYTHONPATH=src python3 -m unittest
```

## Project Status

Aure 1.0 is intentionally small and optimized for clarity over raw speed. The current interpreter is a tree-walking reference implementation, which makes the language easy to inspect and evolve.

## AI Assistance

Aure v1.0.0 was written with assistance from GPT-5 through Codex.

## License

MIT. See [LICENSE](LICENSE).
