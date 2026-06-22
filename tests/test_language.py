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


if __name__ == "__main__":
    unittest.main()
