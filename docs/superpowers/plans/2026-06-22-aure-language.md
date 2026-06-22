# Aure Language Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish Aure v1.0.0, a small interpreted programming language with CLI, REPL, examples, tests, documentation, commit, push, and GitHub release.

**Architecture:** Aure is implemented as a Python 3.9+ tree-walking interpreter. Source text flows through lexer, parser, AST, runtime evaluator, built-ins, and CLI wrappers.

**Tech Stack:** Python standard library, `unittest`, Git, GitHub CLI.

---

## File Structure

- `src/aure/lexer.py`: tokenization, comments, literals, operators, keywords.
- `src/aure/parser.py`: AST dataclasses and recursive/Pratt parser.
- `src/aure/runtime.py`: evaluator, environments, functions, built-ins, Aure value formatting.
- `src/aure/errors.py`: shared exception hierarchy.
- `src/aure/cli.py`: file execution, `-e`, REPL, version output.
- `src/aure/__main__.py`: `python3 -m aure` entrypoint.
- `tests/test_language.py`: language semantics and errors.
- `tests/test_cli.py`: CLI subprocess behavior.
- `examples/*.aure`: runnable language examples.
- `README.md`, `docs/language-guide.md`, `CHANGELOG.md`, `RELEASE.md`, `CONTRIBUTING.md`, `LICENSE`: open-source documentation and release material.

### Task 1: Failing Runtime Tests

**Files:**
- Create: `tests/test_language.py`

- [ ] **Step 1: Write failing tests**

```python
import unittest

from aure import run


class AureLanguageTests(unittest.TestCase):
    def test_arithmetic_functions_arrays_and_builtins(self):
        source = """
        fn square(x) { x * x }
        let values = [1, 2, 3, 4]
        let doubled = map(values, fn(x) { x * 2 })
        print(square(5), len(doubled), doubled[2])
        """
        result = run(source)
        self.assertEqual(result.output, "25 4 6\n")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python3 -m unittest tests.test_language.AureLanguageTests.test_arithmetic_functions_arrays_and_builtins`
Expected: fail because module `aure` does not exist.

### Task 2: Minimal Interpreter

**Files:**
- Create: `src/aure/__init__.py`
- Create: `src/aure/errors.py`
- Create: `src/aure/lexer.py`
- Create: `src/aure/parser.py`
- Create: `src/aure/runtime.py`

- [ ] **Step 1: Implement just enough lexer/parser/runtime for Task 1**

The first implementation must support numbers, strings, arrays, indexing, calls, `fn`, `let`, blocks, arithmetic, and `print`, `len`, `map`.

- [ ] **Step 2: Run Task 1 test**

Run: `PYTHONPATH=src python3 -m unittest tests.test_language.AureLanguageTests.test_arithmetic_functions_arrays_and_builtins`
Expected: pass.

### Task 3: Control Flow, Maps, Pipelines, Closures, and Errors

**Files:**
- Modify: `tests/test_language.py`
- Modify: `src/aure/parser.py`
- Modify: `src/aure/runtime.py`

- [ ] **Step 1: Add failing tests**

```python
def test_control_flow_maps_pipelines_and_closures(self):
    source = """
    fn makeAdder(base) {
      fn(x) { base + x }
    }
    let add10 = makeAdder(10)
    let evens = range(1, 7) |> filter(fn(x) { x % 2 == 0 })
    let total = reduce(evens, 0, fn(acc, x) { acc + x })
    let user = {"name": "Aure", "score": add10(total)}
    if user["score"] == 22 {
      print(user["name"], user["score"])
    } else {
      print("wrong")
    }
    """
    result = run(source)
    self.assertEqual(result.output, "Aure 22\n")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python3 -m unittest tests.test_language.AureLanguageTests.test_control_flow_maps_pipelines_and_closures`
Expected: fail before the feature is implemented.

- [ ] **Step 3: Implement the missing semantics**

Add maps, modulo, equality, comparison, `if`, closures, pipeline operator, `range`, `filter`, and `reduce`.

- [ ] **Step 4: Run full language tests**

Run: `PYTHONPATH=src python3 -m unittest tests.test_language`
Expected: all tests pass.

### Task 4: CLI and REPL

**Files:**
- Create: `src/aure/cli.py`
- Create: `src/aure/__main__.py`
- Create: `tests/test_cli.py`
- Create: `pyproject.toml`

- [ ] **Step 1: Add failing CLI tests**

```python
def test_cli_eval_prints_output(self):
    proc = subprocess.run(
        [sys.executable, "-m", "aure", "-e", "print(1 + 2)"],
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        text=True,
        capture_output=True,
        check=False,
    )
    self.assertEqual(proc.returncode, 0)
    self.assertEqual(proc.stdout, "3\n")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python3 -m unittest tests.test_cli`
Expected: fail before CLI entrypoint exists.

- [ ] **Step 3: Implement CLI**

Support `aure FILE`, `aure -e CODE`, `aure repl`, `aure --version`, and useful stderr for failures.

- [ ] **Step 4: Run CLI tests**

Run: `PYTHONPATH=src python3 -m unittest tests.test_cli`
Expected: pass.

### Task 5: Documentation and Examples

**Files:**
- Create: `README.md`
- Create: `docs/language-guide.md`
- Create: `examples/hello.aure`
- Create: `examples/pipeline.aure`
- Create: `examples/fibonacci.aure`
- Create: `CHANGELOG.md`
- Create: `RELEASE.md`
- Create: `CONTRIBUTING.md`
- Create: `LICENSE`

- [ ] **Step 1: Add runnable examples**

Examples must exercise functions, arrays, maps, loops or recursion, and pipelines.

- [ ] **Step 2: Document installation and usage**

README must include quick start, CLI, examples, design goals, and test command.

- [ ] **Step 3: Document language syntax**

Language guide must describe values, expressions, functions, control flow, built-ins, and errors.

### Task 6: Verification, Commit, Push, Release

**Files:**
- Modify as needed from verification feedback.

- [ ] **Step 1: Run full test suite**

Run: `PYTHONPATH=src python3 -m unittest`
Expected: all tests pass.

- [ ] **Step 2: Run CLI smoke checks**

Run: `PYTHONPATH=src python3 -m aure --version`
Expected: prints `Aure 1.0.0`.

Run: `PYTHONPATH=src python3 -m aure examples/hello.aure`
Expected: prints a friendly Aure greeting.

- [ ] **Step 3: Inspect git state**

Run: `git status --short`
Expected: only intended project files.

- [ ] **Step 4: Commit all project files**

Run: `git add . && git commit -m "Release Aure 1.0.0"`
Expected: initial commit succeeds.

- [ ] **Step 5: Create public GitHub repo and push**

Run: `gh auth switch -u bnjdpn`, `gh repo create bnjdpn/aure-lang --public --source=. --remote=origin --push`
Expected: repository exists at `https://github.com/bnjdpn/aure-lang`.

- [ ] **Step 6: Create release**

Run: `gh release create v1.0.0 --title "Aure 1.0.0" --notes-file RELEASE.md`
Expected: public release exists for tag `v1.0.0`.

### Task 7: Aure 1.0 Language Enrichment

**Files:**
- Modify: `src/aure/lexer.py`
- Modify: `src/aure/parser.py`
- Modify: `src/aure/runtime.py`
- Modify: `tests/test_language.py`
- Modify: `tests/test_cli.py`
- Modify: `README.md`
- Modify: `docs/language-guide.md`
- Modify: `CHANGELOG.md`
- Modify: `RELEASE.md`
- Create: `examples/collections.aure`

- [ ] **Step 1: Add failing language tests**

Add tests for assignment to existing names, array/map indexed assignment, `for`, `break`, `continue`, short-circuiting `and`/`or`, and collection built-ins.

- [ ] **Step 2: Run targeted tests to verify they fail before implementation**

Run: `PYTHONPATH=src python3 -m unittest tests.test_language.AureLanguageTests.test_for_loop_assignment_mutation_and_collection_builtins tests.test_language.AureLanguageTests.test_logical_operators_short_circuit_and_assert_builtin tests.test_language.AureLanguageTests.test_assignment_requires_existing_binding`
Expected: fail on missing parser/runtime support.

- [ ] **Step 3: Implement 1.0 language support**

Add lexer keywords, AST nodes, parser rules, runtime signals, assignment helpers, iteration helpers, logical evaluation, and collection built-ins.

- [ ] **Step 4: Update docs, examples, and metadata**

Set package version to `1.0.0`, document the 1.0 language surface, add `examples/collections.aure`, and update release notes.

- [ ] **Step 5: Run full verification**

Run: `PYTHONPATH=src python3 -m unittest`
Expected: all tests pass.

## Self-Review

- Spec coverage: runtime, CLI, docs, examples, GitHub repo, and release are mapped to tasks.
- Placeholder scan: no task contains unresolved `TBD` or incomplete requirements.
- Type consistency: public API is `aure.run(source)` returning an object with `output` and `value`.
