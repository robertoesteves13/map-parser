class InputStream:
    def __init__(self, filename) -> None:
        with open(filename, 'r') as f:
            self.file = ''.join(f.readlines())
            self.file_size = len(self.file)
            self.pos = 0
            self.line = 1
            self.col = 0

    def peek(self) -> str:
        if self.eof():
            return ''

        return self.file[self.pos]

    def next(self) -> str:
        if self.eof():
            return ''

        char = self.file[self.pos]
        self.pos += 1

        if char == '\n':
            self.line += 1
            self.col = 0
        else:
            self.col += 1

        return char
    
    def eof(self) -> bool:
        return self.file_size == self.pos

    def croak(self, msg: str):
        raise TypeError(f'{msg} ({self.line}:{self.col})')
