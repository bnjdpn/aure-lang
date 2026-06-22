# Contributing to Aure

Thanks for improving Aure.

## Local Checks

Run the full test suite before proposing changes:

```bash
PYTHONPATH=src python3 -m unittest
```

Run examples after changing language semantics:

```bash
PYTHONPATH=src python3 -m aure examples/hello.aure
PYTHONPATH=src python3 -m aure examples/pipeline.aure
PYTHONPATH=src python3 -m aure examples/fibonacci.aure
```

## Design Rules

- Keep the language small and coherent.
- Add tests before changing behavior.
- Prefer clear errors over clever recovery.
- Keep the interpreter readable before optimizing it.
- Update the language guide when syntax or built-ins change.
