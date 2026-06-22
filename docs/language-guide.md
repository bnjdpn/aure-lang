<p align="center">
  <img src="assets/aure-logo.svg" alt="Aure logo" width="360">
</p>

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

Use assignment without `let` when the binding must already exist:

```aure
let score = 1
score = score + 9
print(score)
```

Assigning to a missing name is a runtime error.

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

`for` iterates arrays, strings, and map keys:

```aure
for value in [1, 2, 3] {
  print(value)
}
```

Use `break` to exit a loop and `continue` to skip to the next iteration.

Only `false` and `nil` are falsey.

`and` and `or` short-circuit and return one of their operand values:

```aure
let label = "aure" or "fallback"
print(label)
```

## Collections

Arrays and strings use integer indexes:

```aure
let xs = [10, 20, 30]
print(xs[1])
xs[1] = 99
print(xs)
```

Maps use any hashable key:

```aure
let user = {"name": "Ada", "score": 42}
print(user["name"], user["score"])
user["score"] = user["score"] + 1
print(user["score"])
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
- `assert(condition)`: raises a runtime error when the condition is falsey.
- `assert(condition, message)`: raises a runtime error with a custom message when the condition is falsey.
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
- `push(array, value)`: appends a value and returns the array.
- `pop(array)`: removes and returns the last item.
- `keys(map)`: returns map keys.
- `values(map)`: returns map values.
- `contains(collection, value)`: checks string, array, or map membership. For maps, it checks keys.

## Errors

The CLI prints syntax and runtime errors to stderr:

```bash
aure: Undefined name 'missing'.
```

Library users can catch `AureSyntaxError`, `AureRuntimeError`, or their shared base class `AureError`.
