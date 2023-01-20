import re
import sys
from typing import Any
from reader import InputStream


class BeatmapToken:
    def __init__(self, type: str, value: Any, line: int, col: int) -> None:
        self.type = type
        self.value = value

        self.line = line
        self.col = col


class BeatmapLexer:
    separator = [":", ": ", " : ", ',', '|']

    def __init__(self, filename) -> None:
        self.stream = InputStream(filename)
        self.tokens = []

        self.processed = False
        self.pos = 0

    def next(self) -> BeatmapToken:
        if not self.processed:
            raise RuntimeError('Lexer have not processed already')

        if self.eof():
            return self.tokens[-1]

        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def peek(self) -> BeatmapToken:
        if not self.processed:
            raise RuntimeError('Lexer have not processed already')

        if self.eof():
            return self.tokens[-1]

        return self.tokens[self.pos]

    def eof(self):
        return len(self.tokens) <= self.pos

    def process(self):
        self.__get_first_line()

        while not self.stream.eof():
            token = self.__read_token()
            line = self.stream.line
            col = self.stream.col - len(token)

            if len(token) == 0:
                if self.tokens[-1].value in [':', ': ', ' : ']:
                    self.tokens.append(BeatmapToken('text', '', line, col))
                self.stream.next()
                continue

            type = self.__categorize_token(token)
            if type != 'comment':
                self.tokens.append(BeatmapToken(type, token, line, col))

        self.processed = True

    def __get_first_line(self):
        first_line = ''
        while self.stream.peek() != '\n':
            first_line += self.stream.next()

        line = self.stream.line
        col = self.stream.col - len(first_line)

        self.stream.next()
        self.tokens.append(BeatmapToken("header", first_line, line, col))

    def __read_token(self) -> str:
        token = ''

        if self.stream.peek() == ':':
            token += self.stream.next()

            if self.stream.peek() == ' ':
                token += self.stream.next()

            if self.tokens[-1].value == ' ':
                self.tokens[-1].value.removesuffix(' ')
                token = ' : '

            return token

        while not self.__is_new_line() and self.stream.peek() not in self.separator:
            token += self.stream.next()

        if len(token) == 0 and not self.__is_new_line():
            token = self.stream.next()

        return token

    def __categorize_token(self, token) -> str:
        if token in self.separator:
            return 'separator'
        elif self.stream.peek() in [':', ' :']:
            return 'identifier'
        elif self.tokens[-1].value in self.separator or self.stream.peek() in [',', '|']:
            return self.__categorize_value(token)
        elif token[0] == '[' and token[-1] == ']':
            return 'section'
        elif token[0] == '/' and token[1] == '/':
            return 'comment'
        else:
            self.stream.croak(f'Unknown token type `{token}`')

    def __categorize_value(self, token) -> str:
        if token.isnumeric() or re.match(r'^\d*\.\d$', token):
            return 'number'
        else:
            return 'text'

    def __is_new_line(self) -> bool:
        return self.stream.peek() == '\n'


if __name__ == '__main__':
    tokenizer = BeatmapLexer(sys.argv[1])
    tokenizer.process()
    for token in tokenizer.tokens:
        print(f'type: `{token.type}`, value: `{token.value}` ({token.col}:{token.line})')
