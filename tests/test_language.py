import unittest

from aure import AureRuntimeError, run


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

    def test_while_loop_updates_existing_bindings(self):
        source = """
        let i = 0
        let total = 0

        while i < 5 {
          let i = i + 1
          let total = total + i
        }

        print(total)
        """

        result = run(source)

        self.assertEqual(result.output, "15\n")

    def test_for_loop_assignment_mutation_and_collection_builtins(self):
        source = """
        let values = [1, 2, 3]
        values[1] = values[1] * 10
        push(values, 4)

        let total = 0
        for value in values {
          if value == 3 {
            continue
          }

          total = total + value

          if total > 20 {
            break
          }
        }

        let user = {"name": "Aure"}
        user["version"] = "1.0"
        let last = pop(values)

        print(values, total, user["version"], contains(keys(user), "name"), last)
        """

        result = run(source)

        self.assertEqual(result.output, "[1, 20, 3] 21 1.0 true 4\n")

    def test_logical_operators_short_circuit_and_assert_builtin(self):
        source = """
        let called = false

        fn mark() {
          called = true
          true
        }

        assert(true, "assert accepts truthy values")

        if false and mark() {
          print("bad")
        } else {
          print(called)
        }

        if true or mark() {
          print(called)
        }
        """

        result = run(source)

        self.assertEqual(result.output, "false\nfalse\n")

    def test_assignment_requires_existing_binding(self):
        with self.assertRaisesRegex(AureRuntimeError, "Undefined name 'missing'."):
            run("missing = 1")


if __name__ == "__main__":
    unittest.main()
