from dataclasses import dataclass
from io import StringIO

from .errors import AureRuntimeError
from .lexer import tokenize
from .parser import (
    Assign,
    ArrayLiteral,
    Binary,
    Block,
    BreakStmt,
    Call,
    ContinueStmt,
    ExprStmt,
    ForStmt,
    FunctionExpr,
    FunctionStmt,
    IfExpr,
    Index,
    IndexAssign,
    LetStmt,
    Literal,
    Logical,
    MapLiteral,
    Pipe,
    Program,
    ReturnStmt,
    Unary,
    Variable,
    WhileStmt,
    parse,
)


@dataclass(frozen=True)
class RunResult:
    value: object
    output: str


class ReturnSignal(Exception):
    def __init__(self, value):
        super().__init__()
        self.value = value


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.values = {}

    def define(self, name, value):
        self.values[name] = value

    def assign_or_define(self, name, value):
        if name in self.values:
            self.values[name] = value
            return
        if self.parent is not None and self.parent.contains(name):
            self.parent.assign_or_define(name, value)
            return
        self.values[name] = value

    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value
            return
        if self.parent is not None:
            self.parent.assign(name, value)
            return
        raise AureRuntimeError("Undefined name '%s'." % name)

    def contains(self, name):
        return name in self.values or (self.parent is not None and self.parent.contains(name))

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise AureRuntimeError("Undefined name '%s'." % name)


class AureFunction:
    def __init__(self, params, body, closure, name=None):
        self.params = params
        self.body = body
        self.closure = closure
        self.name = name

    def call(self, interpreter, args):
        if len(args) != len(self.params):
            expected = len(self.params)
            got = len(args)
            raise AureRuntimeError("Function expected %s arguments but got %s." % (expected, got))

        env = Environment(self.closure)
        for name, value in zip(self.params, args):
            env.define(name, value)

        try:
            return interpreter.execute_block(self.body, env)
        except ReturnSignal as signal:
            return signal.value
        except BreakSignal:
            raise AureRuntimeError("break used outside a loop.")
        except ContinueSignal:
            raise AureRuntimeError("continue used outside a loop.")

    def __repr__(self):
        return "<fn %s>" % (self.name or "anonymous")


class BuiltinFunction:
    def __init__(self, name, func, arity=None):
        self.name = name
        self.func = func
        self.arity = arity

    def call(self, interpreter, args):
        if self.arity is not None and len(args) != self.arity:
            raise AureRuntimeError("%s expected %s arguments but got %s." % (self.name, self.arity, len(args)))
        return self.func(interpreter, *args)

    def __repr__(self):
        return "<builtin %s>" % self.name


class Interpreter:
    def __init__(self):
        self.output = StringIO()
        self.globals = Environment()
        self.environment = self.globals
        self._install_builtins()

    def run(self, source):
        program = parse(tokenize(source))
        try:
            value = self.execute(program)
        except BreakSignal:
            raise AureRuntimeError("break used outside a loop.")
        except ContinueSignal:
            raise AureRuntimeError("continue used outside a loop.")
        return RunResult(value=value, output=self.output.getvalue())

    def execute(self, node):
        if isinstance(node, Program):
            value = None
            for statement in node.statements:
                value = self.execute(statement)
            return value
        if isinstance(node, LetStmt):
            value = self.evaluate(node.initializer)
            self.environment.assign_or_define(node.name, value)
            return value
        if isinstance(node, FunctionStmt):
            function = AureFunction(node.params, node.body, self.environment, node.name)
            self.environment.define(node.name, function)
            return function
        if isinstance(node, ForStmt):
            return self._execute_for(node)
        if isinstance(node, ReturnStmt):
            raise ReturnSignal(self.evaluate(node.value))
        if isinstance(node, BreakStmt):
            raise BreakSignal()
        if isinstance(node, ContinueStmt):
            raise ContinueSignal()
        if isinstance(node, WhileStmt):
            value = None
            while self._truthy(self.evaluate(node.condition)):
                try:
                    value = self.execute_block(node.body, Environment(self.environment))
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break
            return value
        if isinstance(node, ExprStmt):
            return self.evaluate(node.expression)
        raise AureRuntimeError("Unsupported statement %s." % type(node).__name__)

    def execute_block(self, block, environment):
        previous = self.environment
        self.environment = environment
        try:
            value = None
            for statement in block.statements:
                value = self.execute(statement)
            return value
        finally:
            self.environment = previous

    def _execute_for(self, node):
        iterable = self.evaluate(node.iterable)
        values = self._iterate(iterable)
        loop_env = Environment(self.environment)
        value = None

        for item in values:
            loop_env.assign_or_define(node.name, item)
            try:
                value = self.execute_block(node.body, Environment(loop_env))
            except ContinueSignal:
                continue
            except BreakSignal:
                break

        return value

    def evaluate(self, node):
        if isinstance(node, Literal):
            return node.value
        if isinstance(node, Variable):
            return self.environment.get(node.name)
        if isinstance(node, Assign):
            value = self.evaluate(node.value)
            self.environment.assign(node.name, value)
            return value
        if isinstance(node, ArrayLiteral):
            return [self.evaluate(element) for element in node.elements]
        if isinstance(node, MapLiteral):
            result = {}
            for key_expr, value_expr in node.entries:
                key = self.evaluate(key_expr)
                try:
                    hash(key)
                except TypeError:
                    raise AureRuntimeError("Map keys must be hashable values.")
                result[key] = self.evaluate(value_expr)
            return result
        if isinstance(node, FunctionExpr):
            return AureFunction(node.params, node.body, self.environment)
        if isinstance(node, IfExpr):
            if self._truthy(self.evaluate(node.condition)):
                return self.execute_block(node.then_block, Environment(self.environment))
            if node.else_block is not None:
                return self.execute_block(node.else_block, Environment(self.environment))
            return None
        if isinstance(node, Call):
            callee = self.evaluate(node.callee)
            args = [self.evaluate(arg) for arg in node.args]
            return self._call(callee, args)
        if isinstance(node, Pipe):
            value = self.evaluate(node.left)
            if isinstance(node.right, Call):
                callee = self.evaluate(node.right.callee)
                args = [value] + [self.evaluate(arg) for arg in node.right.args]
                return self._call(callee, args)
            callee = self.evaluate(node.right)
            return self._call(callee, [value])
        if isinstance(node, Index):
            collection = self.evaluate(node.collection)
            index = self.evaluate(node.index)
            return self._index(collection, index)
        if isinstance(node, IndexAssign):
            collection = self.evaluate(node.collection)
            index = self.evaluate(node.index)
            value = self.evaluate(node.value)
            self._assign_index(collection, index, value)
            return value
        if isinstance(node, Unary):
            right = self.evaluate(node.right)
            if node.op == "-":
                self._require_number(right, "Unary '-'")
                return -right
            if node.op == "!":
                return not self._truthy(right)
        if isinstance(node, Logical):
            left = self.evaluate(node.left)
            if node.op == "or":
                if self._truthy(left):
                    return left
                return self.evaluate(node.right)
            if node.op == "and":
                if not self._truthy(left):
                    return left
                return self.evaluate(node.right)
        if isinstance(node, Binary):
            return self._binary(node)
        raise AureRuntimeError("Unsupported expression %s." % type(node).__name__)

    def _binary(self, node):
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        op = node.op

        if op == "+":
            if isinstance(left, str) or isinstance(right, str):
                return self.format_value(left) + self.format_value(right)
            self._require_number(left, "'+'")
            self._require_number(right, "'+'")
            return left + right
        if op == "-":
            self._require_number(left, "'-'")
            self._require_number(right, "'-'")
            return left - right
        if op == "*":
            self._require_number(left, "'*'")
            self._require_number(right, "'*'")
            return left * right
        if op == "/":
            self._require_number(left, "'/'")
            self._require_number(right, "'/'")
            if right == 0:
                raise AureRuntimeError("Division by zero.")
            return left / right
        if op == "%":
            self._require_number(left, "'%'")
            self._require_number(right, "'%'")
            return left % right
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == ">":
            return left > right
        if op == ">=":
            return left >= right
        if op == "<":
            return left < right
        if op == "<=":
            return left <= right
        raise AureRuntimeError("Unknown operator '%s'." % op)

    def _call(self, callee, args):
        if hasattr(callee, "call"):
            return callee.call(self, args)
        raise AureRuntimeError("Value is not callable: %s." % self.format_value(callee))

    def _index(self, collection, index):
        if isinstance(collection, list):
            if not isinstance(index, int) or isinstance(index, bool):
                raise AureRuntimeError("Array index must be an integer.")
            try:
                return collection[index]
            except IndexError:
                raise AureRuntimeError("Array index out of range.")
        if isinstance(collection, str):
            if not isinstance(index, int) or isinstance(index, bool):
                raise AureRuntimeError("String index must be an integer.")
            try:
                return collection[index]
            except IndexError:
                raise AureRuntimeError("String index out of range.")
        if isinstance(collection, dict):
            try:
                return collection[index]
            except KeyError:
                raise AureRuntimeError("Map key not found: %s." % self.format_value(index))
        raise AureRuntimeError("Value is not indexable: %s." % self.format_value(collection))

    def _assign_index(self, collection, index, value):
        if isinstance(collection, list):
            if not isinstance(index, int) or isinstance(index, bool):
                raise AureRuntimeError("Array index must be an integer.")
            try:
                collection[index] = value
            except IndexError:
                raise AureRuntimeError("Array index out of range.")
            return
        if isinstance(collection, dict):
            try:
                hash(index)
            except TypeError:
                raise AureRuntimeError("Map keys must be hashable values.")
            collection[index] = value
            return
        raise AureRuntimeError("Value does not support indexed assignment: %s." % self.format_value(collection))

    def _iterate(self, value):
        if isinstance(value, list):
            return list(value)
        if isinstance(value, str):
            return list(value)
        if isinstance(value, dict):
            return list(value.keys())
        raise AureRuntimeError("for expects an array, string, or map.")

    def _install_builtins(self):
        self.globals.define("print", BuiltinFunction("print", _builtin_print))
        self.globals.define("assert", BuiltinFunction("assert", _builtin_assert))
        self.globals.define("len", BuiltinFunction("len", _builtin_len, arity=1))
        self.globals.define("map", BuiltinFunction("map", _builtin_map, arity=2))
        self.globals.define("filter", BuiltinFunction("filter", _builtin_filter, arity=2))
        self.globals.define("reduce", BuiltinFunction("reduce", _builtin_reduce, arity=3))
        self.globals.define("range", BuiltinFunction("range", _builtin_range))
        self.globals.define("push", BuiltinFunction("push", _builtin_push, arity=2))
        self.globals.define("pop", BuiltinFunction("pop", _builtin_pop, arity=1))
        self.globals.define("keys", BuiltinFunction("keys", _builtin_keys, arity=1))
        self.globals.define("values", BuiltinFunction("values", _builtin_values, arity=1))
        self.globals.define("contains", BuiltinFunction("contains", _builtin_contains, arity=2))
        self.globals.define("type", BuiltinFunction("type", _builtin_type, arity=1))
        self.globals.define("str", BuiltinFunction("str", _builtin_str, arity=1))
        self.globals.define("int", BuiltinFunction("int", _builtin_int, arity=1))
        self.globals.define("float", BuiltinFunction("float", _builtin_float, arity=1))

    def _truthy(self, value):
        return value not in (False, None)

    def _require_number(self, value, context):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise AureRuntimeError("%s expects numbers." % context)

    def format_value(self, value):
        if value is None:
            return "nil"
        if value is True:
            return "true"
        if value is False:
            return "false"
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        if isinstance(value, list):
            return "[" + ", ".join(self.format_value(item) for item in value) + "]"
        if isinstance(value, dict):
            items = []
            for key, item in value.items():
                items.append("%s: %s" % (self.format_value(key), self.format_value(item)))
            return "{" + ", ".join(items) + "}"
        return str(value)


def _builtin_print(interpreter, *values):
    interpreter.output.write(" ".join(interpreter.format_value(value) for value in values) + "\n")
    return None


def _builtin_assert(interpreter, *args):
    if len(args) not in (1, 2):
        raise AureRuntimeError("assert expected 1 or 2 arguments but got %s." % len(args))
    if interpreter._truthy(args[0]):
        return None
    if len(args) == 2:
        raise AureRuntimeError("Assertion failed: %s" % interpreter.format_value(args[1]))
    raise AureRuntimeError("Assertion failed.")


def _builtin_len(interpreter, value):
    if isinstance(value, (str, list, dict)):
        return len(value)
    raise AureRuntimeError("len expects a string, array, or map.")


def _builtin_map(interpreter, values, function):
    if not isinstance(values, list):
        raise AureRuntimeError("map expects an array as first argument.")
    return [interpreter._call(function, [value]) for value in values]


def _builtin_filter(interpreter, values, function):
    if not isinstance(values, list):
        raise AureRuntimeError("filter expects an array as first argument.")
    return [value for value in values if interpreter._truthy(interpreter._call(function, [value]))]


def _builtin_reduce(interpreter, values, initial, function):
    if not isinstance(values, list):
        raise AureRuntimeError("reduce expects an array as first argument.")
    acc = initial
    for value in values:
        acc = interpreter._call(function, [acc, value])
    return acc


def _builtin_range(interpreter, *args):
    if len(args) == 1:
        start = 0
        stop = args[0]
    elif len(args) == 2:
        start, stop = args
    else:
        raise AureRuntimeError("range expected 1 or 2 arguments but got %s." % len(args))
    if not isinstance(start, int) or isinstance(start, bool) or not isinstance(stop, int) or isinstance(stop, bool):
        raise AureRuntimeError("range expects integer arguments.")
    return list(range(start, stop))


def _builtin_push(interpreter, values, value):
    if not isinstance(values, list):
        raise AureRuntimeError("push expects an array as first argument.")
    values.append(value)
    return values


def _builtin_pop(interpreter, values):
    if not isinstance(values, list):
        raise AureRuntimeError("pop expects an array.")
    if not values:
        raise AureRuntimeError("pop expects a non-empty array.")
    return values.pop()


def _builtin_keys(interpreter, value):
    if not isinstance(value, dict):
        raise AureRuntimeError("keys expects a map.")
    return list(value.keys())


def _builtin_values(interpreter, value):
    if not isinstance(value, dict):
        raise AureRuntimeError("values expects a map.")
    return list(value.values())


def _builtin_contains(interpreter, collection, value):
    if isinstance(collection, (str, list)):
        return value in collection
    if isinstance(collection, dict):
        return value in collection
    raise AureRuntimeError("contains expects a string, array, or map.")


def _builtin_type(interpreter, value):
    if value is None:
        return "nil"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "map"
    if isinstance(value, AureFunction):
        return "function"
    if isinstance(value, BuiltinFunction):
        return "builtin"
    return "unknown"


def _builtin_str(interpreter, value):
    return interpreter.format_value(value)


def _builtin_int(interpreter, value):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise AureRuntimeError("int could not convert %s." % interpreter.format_value(value))


def _builtin_float(interpreter, value):
    try:
        return float(value)
    except (TypeError, ValueError):
        raise AureRuntimeError("float could not convert %s." % interpreter.format_value(value))


def run(source):
    return Interpreter().run(source)
