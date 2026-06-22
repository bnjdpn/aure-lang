from dataclasses import dataclass

from .errors import AureSyntaxError


@dataclass(frozen=True)
class Program:
    statements: list


@dataclass(frozen=True)
class LetStmt:
    name: str
    initializer: object


@dataclass(frozen=True)
class FunctionStmt:
    name: str
    params: list
    body: object


@dataclass(frozen=True)
class ForStmt:
    name: str
    iterable: object
    body: object


@dataclass(frozen=True)
class ReturnStmt:
    value: object


@dataclass(frozen=True)
class WhileStmt:
    condition: object
    body: object


@dataclass(frozen=True)
class BreakStmt:
    pass


@dataclass(frozen=True)
class ContinueStmt:
    pass


@dataclass(frozen=True)
class ExprStmt:
    expression: object


@dataclass(frozen=True)
class Block:
    statements: list


@dataclass(frozen=True)
class Literal:
    value: object


@dataclass(frozen=True)
class Variable:
    name: str


@dataclass(frozen=True)
class Assign:
    name: str
    value: object


@dataclass(frozen=True)
class ArrayLiteral:
    elements: list


@dataclass(frozen=True)
class MapLiteral:
    entries: list


@dataclass(frozen=True)
class FunctionExpr:
    params: list
    body: object


@dataclass(frozen=True)
class Call:
    callee: object
    args: list


@dataclass(frozen=True)
class Index:
    collection: object
    index: object


@dataclass(frozen=True)
class IndexAssign:
    collection: object
    index: object
    value: object


@dataclass(frozen=True)
class Unary:
    op: str
    right: object


@dataclass(frozen=True)
class Binary:
    left: object
    op: str
    right: object


@dataclass(frozen=True)
class Logical:
    left: object
    op: str
    right: object


@dataclass(frozen=True)
class Pipe:
    left: object
    right: object


@dataclass(frozen=True)
class IfExpr:
    condition: object
    then_block: object
    else_block: object


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        statements = []
        while not self._check("EOF"):
            statements.append(self._statement())
        return Program(statements)

    def _statement(self):
        if self._match("LET"):
            return self._let_statement()
        if self._check("FN") and self._check_next("IDENTIFIER"):
            return self._function_statement()
        if self._match("FOR"):
            return self._for_statement()
        if self._match("RETURN"):
            return ReturnStmt(self._expression())
        if self._match("BREAK"):
            return BreakStmt()
        if self._match("CONTINUE"):
            return ContinueStmt()
        if self._match("WHILE"):
            condition = self._expression()
            return WhileStmt(condition, self._block())
        return ExprStmt(self._expression())

    def _let_statement(self):
        name = self._consume("IDENTIFIER", "Expected a variable name after 'let'.")
        self._consume("EQUAL", "Expected '=' after variable name.")
        return LetStmt(name.lexeme, self._expression())

    def _function_statement(self):
        self._consume("FN", "Expected 'fn'.")
        name = self._consume("IDENTIFIER", "Expected function name.")
        params = self._parameters()
        return FunctionStmt(name.lexeme, params, self._block())

    def _for_statement(self):
        name = self._consume("IDENTIFIER", "Expected loop variable name after 'for'.")
        self._consume("IN", "Expected 'in' after loop variable.")
        iterable = self._expression()
        return ForStmt(name.lexeme, iterable, self._block())

    def _parameters(self):
        self._consume("LPAREN", "Expected '(' before parameters.")
        params = []
        if not self._check("RPAREN"):
            while True:
                params.append(self._consume("IDENTIFIER", "Expected parameter name.").lexeme)
                if not self._match("COMMA"):
                    break
        self._consume("RPAREN", "Expected ')' after parameters.")
        return params

    def _block(self):
        self._consume("LBRACE", "Expected '{' before block.")
        statements = []
        while not self._check("RBRACE") and not self._check("EOF"):
            statements.append(self._statement())
        self._consume("RBRACE", "Expected '}' after block.")
        return Block(statements)

    def _expression(self):
        return self._assignment()

    def _assignment(self):
        expr = self._pipe()
        if self._match("EQUAL"):
            value = self._assignment()
            if isinstance(expr, Variable):
                return Assign(expr.name, value)
            if isinstance(expr, Index):
                return IndexAssign(expr.collection, expr.index, value)
            token = self._previous()
            raise AureSyntaxError("Invalid assignment target at line %s, column %s." % (token.line, token.column))
        return expr

    def _pipe(self):
        expr = self._or()
        while self._match("PIPE"):
            expr = Pipe(expr, self._or())
        return expr

    def _or(self):
        expr = self._and()
        while self._match("OR"):
            expr = Logical(expr, self._previous().lexeme, self._and())
        return expr

    def _and(self):
        expr = self._equality()
        while self._match("AND"):
            expr = Logical(expr, self._previous().lexeme, self._equality())
        return expr

    def _equality(self):
        expr = self._comparison()
        while self._match("BANG_EQUAL", "EQUAL_EQUAL"):
            operator = self._previous().lexeme
            right = self._comparison()
            expr = Binary(expr, operator, right)
        return expr

    def _comparison(self):
        expr = self._term()
        while self._match("GREATER", "GREATER_EQUAL", "LESS", "LESS_EQUAL"):
            operator = self._previous().lexeme
            right = self._term()
            expr = Binary(expr, operator, right)
        return expr

    def _term(self):
        expr = self._factor()
        while self._match("PLUS", "MINUS"):
            operator = self._previous().lexeme
            right = self._factor()
            expr = Binary(expr, operator, right)
        return expr

    def _factor(self):
        expr = self._unary()
        while self._match("STAR", "SLASH", "PERCENT"):
            operator = self._previous().lexeme
            right = self._unary()
            expr = Binary(expr, operator, right)
        return expr

    def _unary(self):
        if self._match("BANG", "MINUS"):
            return Unary(self._previous().lexeme, self._unary())
        return self._call()

    def _call(self):
        expr = self._primary()
        while True:
            if self._match("LPAREN"):
                args = []
                if not self._check("RPAREN"):
                    while True:
                        args.append(self._expression())
                        if not self._match("COMMA"):
                            break
                self._consume("RPAREN", "Expected ')' after arguments.")
                expr = Call(expr, args)
            elif self._match("LBRACKET"):
                index = self._expression()
                self._consume("RBRACKET", "Expected ']' after index.")
                expr = Index(expr, index)
            else:
                break
        return expr

    def _primary(self):
        if self._match("FALSE"):
            return Literal(False)
        if self._match("TRUE"):
            return Literal(True)
        if self._match("NIL"):
            return Literal(None)
        if self._match("NUMBER", "STRING"):
            return Literal(self._previous().literal)
        if self._match("IDENTIFIER"):
            return Variable(self._previous().lexeme)
        if self._match("LBRACKET"):
            elements = []
            if not self._check("RBRACKET"):
                while True:
                    elements.append(self._expression())
                    if not self._match("COMMA"):
                        break
            self._consume("RBRACKET", "Expected ']' after array literal.")
            return ArrayLiteral(elements)
        if self._match("LBRACE"):
            entries = []
            if not self._check("RBRACE"):
                while True:
                    key = self._expression()
                    self._consume("COLON", "Expected ':' between map key and value.")
                    entries.append((key, self._expression()))
                    if not self._match("COMMA"):
                        break
            self._consume("RBRACE", "Expected '}' after map literal.")
            return MapLiteral(entries)
        if self._match("IF"):
            condition = self._expression()
            then_block = self._block()
            else_block = None
            if self._match("ELSE"):
                else_block = self._block()
            return IfExpr(condition, then_block, else_block)
        if self._match("FN"):
            return FunctionExpr(self._parameters(), self._block())
        if self._match("LPAREN"):
            expr = self._expression()
            self._consume("RPAREN", "Expected ')' after expression.")
            return expr

        token = self._peek()
        raise AureSyntaxError("Expected expression at line %s, column %s." % (token.line, token.column))

    def _match(self, *kinds):
        for kind in kinds:
            if self._check(kind):
                self._advance()
                return True
        return False

    def _consume(self, kind, message):
        if self._check(kind):
            return self._advance()
        token = self._peek()
        raise AureSyntaxError("%s at line %s, column %s." % (message, token.line, token.column))

    def _check(self, kind):
        return self._peek().kind == kind

    def _check_next(self, kind):
        if self.current + 1 >= len(self.tokens):
            return False
        return self.tokens[self.current + 1].kind == kind

    def _advance(self):
        if not self._check("EOF"):
            self.current += 1
        return self._previous()

    def _peek(self):
        return self.tokens[self.current]

    def _previous(self):
        return self.tokens[self.current - 1]


def parse(tokens):
    return Parser(tokens).parse()
