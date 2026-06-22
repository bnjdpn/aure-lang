from dataclasses import dataclass

from .errors import AureSyntaxError


@dataclass(frozen=True)
class Token:
    kind: str
    lexeme: str
    literal: object
    line: int
    column: int


KEYWORDS = {
    "and": "AND",
    "else": "ELSE",
    "false": "FALSE",
    "fn": "FN",
    "if": "IF",
    "let": "LET",
    "nil": "NIL",
    "or": "OR",
    "return": "RETURN",
    "true": "TRUE",
    "while": "WHILE",
}

SINGLE_CHAR_TOKENS = {
    "(": "LPAREN",
    ")": "RPAREN",
    "{": "LBRACE",
    "}": "RBRACE",
    "[": "LBRACKET",
    "]": "RBRACKET",
    ",": "COMMA",
    ":": "COLON",
    "+": "PLUS",
    "-": "MINUS",
    "*": "STAR",
    "/": "SLASH",
    "%": "PERCENT",
}


class Lexer:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.token_line = 1
        self.token_column = 1

    def tokenize(self):
        while not self._is_at_end():
            self.start = self.current
            self.token_line = self.line
            self.token_column = self.column
            self._scan_token()

        self.tokens.append(Token("EOF", "", None, self.line, self.column))
        return self.tokens

    def _scan_token(self):
        char = self._advance()

        if char in SINGLE_CHAR_TOKENS:
            self._add_token(SINGLE_CHAR_TOKENS[char])
        elif char == "=":
            self._add_token("EQUAL_EQUAL" if self._match("=") else "EQUAL")
        elif char == "!":
            self._add_token("BANG_EQUAL" if self._match("=") else "BANG")
        elif char == "<":
            self._add_token("LESS_EQUAL" if self._match("=") else "LESS")
        elif char == ">":
            self._add_token("GREATER_EQUAL" if self._match("=") else "GREATER")
        elif char == "|":
            if self._match(">"):
                self._add_token("PIPE")
            else:
                self._error("Unexpected character '|'. Did you mean '|>'?")
        elif char == "#":
            while self._peek() != "\n" and not self._is_at_end():
                self._advance()
        elif char in (" ", "\r", "\t"):
            return
        elif char == "\n":
            self.line += 1
            self.column = 1
        elif char == '"':
            self._string()
        elif char.isdigit():
            self._number()
        elif char.isalpha() or char == "_":
            self._identifier()
        else:
            self._error("Unexpected character '%s'." % char)

    def _string(self):
        value = []

        while not self._is_at_end():
            char = self._advance()
            if char == '"':
                self._add_token("STRING", "".join(value))
                return
            if char == "\\":
                value.append(self._escape())
            else:
                if char == "\n":
                    self.line += 1
                    self.column = 1
                value.append(char)

        self._error("Unterminated string literal.")

    def _escape(self):
        if self._is_at_end():
            self._error("Unterminated escape sequence.")
        char = self._advance()
        escapes = {
            "n": "\n",
            "r": "\r",
            "t": "\t",
            '"': '"',
            "\\": "\\",
        }
        if char not in escapes:
            self._error("Unknown escape sequence '\\%s'." % char)
        return escapes[char]

    def _number(self):
        while self._peek().isdigit():
            self._advance()

        is_float = False
        if self._peek() == "." and self._peek_next().isdigit():
            is_float = True
            self._advance()
            while self._peek().isdigit():
                self._advance()

        text = self.source[self.start : self.current]
        self._add_token("NUMBER", float(text) if is_float else int(text))

    def _identifier(self):
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()

        text = self.source[self.start : self.current]
        self._add_token(KEYWORDS.get(text, "IDENTIFIER"))

    def _add_token(self, kind, literal=None):
        self.tokens.append(
            Token(
                kind=kind,
                lexeme=self.source[self.start : self.current],
                literal=literal,
                line=self.token_line,
                column=self.token_column,
            )
        )

    def _advance(self):
        char = self.source[self.current]
        self.current += 1
        self.column += 1
        return char

    def _match(self, expected):
        if self._is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        self.column += 1
        return True

    def _peek(self):
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self):
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def _is_at_end(self):
        return self.current >= len(self.source)

    def _error(self, message):
        raise AureSyntaxError("%s at line %s, column %s" % (message, self.token_line, self.token_column))


def tokenize(source):
    return Lexer(source).tokenize()
