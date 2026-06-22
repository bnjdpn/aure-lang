# Aure Language Guide

## Files and Comments

Aure source files usually use `.aure`.

Comments start with `#` and continue to the end of the line.

```aure
# This is a comment
print("hello")
```

## Values

Aure supports:

- `nil`
- booleans: `true`, `false`
- numbers: `1`, `3.14`
- strings: `"hello\nworld"`
- arrays: `[1, 2, 3]`
- maps: `{"name": "Aure", "version": 0.1}`
- functions

## Bindings

Use `let` to create or update a binding in the nearest scope where it already exists.

```aure
let count = 0
let count = count + 1
print(count)
```

## Functions

Named functions:

```aure
fn square(x) {
  x * x
}
```

Anonymous functions:

```aure
let double = fn(x) { x * 2 }
```

Functions return the last value in their block. `return` can exit early:

```aure
fn identity(x) {
  return x
}
```

Closures capture surrounding bindings:

```aure
fn makeAdder(base) {
  fn(x) { base + x }
}

let add5 = makeAdder(5)
print(add5(7))
```

## Control Flow

`if` is an expression:

```aure
let label = if len("aure") > 3 { "long" } else { "short" }
print(label)
```

`while` repeats while the condition is truthy:

```aure
let i = 0
while i < 3 {
  print(i)
  let i = i + 1
}
```

Only `false` and `nil` are falsey.

## Collections

Arrays and strings use integer indexes:

```aure
let xs = [10, 20, 30]
print(xs[1])
```

Maps use any hashable key:

```aure
let user = {"name": "Ada", "score": 42}
print(user["name"], user["score"])
```

## Pipelines

The pipeline operator sends the value on the left into the next call as the first argument:

```aure
let total = range(1, 6)
  |> filter(fn(x) { x % 2 == 1 })
  |> map(fn(x) { x * x })
  |> reduce(0, fn(acc, x) { acc + x })

print(total)
```

## Built-ins

- `print(...)`: writes values separated by spaces.
- `len(value)`: length of a string, array, or map.
- `type(value)`: returns a type name.
- `str(value)`: converts a value to its Aure display string.
- `int(value)`: converts to integer.
- `float(value)`: converts to float.
- `range(stop)`: array from `0` to `stop - 1`.
- `range(start, stop)`: array from `start` to `stop - 1`.
- `map(array, fn)`: transforms an array.
- `filter(array, fn)`: keeps values where the function returns truthy.
- `reduce(array, initial, fn)`: folds an array.

## Errors

The CLI prints syntax and runtime errors to stderr:

```bash
aure: Undefined name 'missing'.
```

Library users can catch `AureSyntaxError`, `AureRuntimeError`, or their shared base class `AureError`.
