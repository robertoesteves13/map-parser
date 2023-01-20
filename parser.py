from lexer import BeatmapLexer, BeatmapToken

class HitObject:
    def __init__(self, x, y, time, type, hitsound, params, sample) -> None:
        self.x = x
        self.y = y
        self.time = time
        self.type = type
        self.hitsound = hitsound
        self.params = params
        self.sample = sample

class TimingPoint:
    def __init__(self, time, length, meter, sample_set, sample_index, volume, uninherited, effects) -> None:
        self.time = time
        self.length = length,
        self.meter = meter,
        self.sample_set = sample_set,
        self.sample_index = sample_index
        self.volume = volume
        self.uninherited = uninherited
        self.effects = effects

class Event:
    def __init__(self, type, start_time, params=[]):
        self.type = type
        self.start_time = start_time
        self.params = params

class BeatmapParser:
    def __init__(self, filename) -> None:
        self.lexer = BeatmapLexer(filename)

        self.general_dict = dict()
        self.editor_dict = dict()
        self.metadata_dict = dict()
        self.difficulty_dict = dict()

        self.events = []
        self.combo_colors = []
        self.timing_points = []
        self.hit_objects = []

    def process(self):
        self.lexer.process()
        header = self.lexer.next()
        if header.type != 'header':
            self.__error("First line must be a header", header)

        while not self.lexer.eof():
            self.__add_section()

    def __add_section(self):
        section = self.lexer.next()
        match section.value:
            case '[General]':
                self.__parse_key_value(': ')
            case '[Editor]':
                self.__parse_key_value(': ')
            case '[Metadata]':
                self.__parse_key_value(':')
            case '[Difficulty]':
                self.__parse_key_value(':')
            case '[Events]':
                self.__parse_events()
            case '[TimingPoints]':
                self.__parse_timing_points()
            case '[Colours]':
                self.__parse_colours()
            case '[HitObjects]':
                self.__parse_hit_objects()
            case _:
                self.__error('Invalid section', section)

    def __parse_key_value(self, separator: str):
        while not self.__eof_or_new_section():
            identifier = self.lexer.next()
            if identifier.type != 'identifier':
                self.__error(f'Expected identifier, found {identifier.type}', self.lexer.peek())

            tk_separator = self.lexer.next()
            if tk_separator.type != 'separator':
                self.__error(f'Expected separator, found {tk_separator.type}', tk_separator)
            elif tk_separator.value != separator:
                self.__error(f'Expected separator `{separator}`', tk_separator)

            value = self.lexer.next().value
            self.general_dict[identifier.value] = value

    def __parse_events(self):
        while not self.__eof_or_new_section():
            type = self.lexer.next().value

            if self.lexer.peek().value != ',':
                self.__error('Expected comma separator', self.lexer.peek())
            self.__skip_separator()
            
            start_time = self.lexer.next()
            if start_time.type != 'number':
                self.__error(f'Expected number, got {start_time.type}', start_time)

            list = []
            while self.lexer.peek().value == ',':
                self.__skip_separator()
                list.append(self.lexer.next().value)

            event = Event(type, start_time.value, list)
            self.events.append(event)

    def __parse_timing_points(self):
        while not self.__eof_or_new_section():
            list = []
            while True:
                list.append(self.lexer.next().value)

                if self.lexer.peek().value != ',':
                    break
                self.__skip_separator()

            self.timing_points.append(list)
            

    def __parse_colours(self):
        while not self.__eof_or_new_section():
            # We don't care about naming as long as 
            # the colors list is in the corret order :)
            self.__skip_identifier()
            self.__skip_separator()

            red = self.lexer.next().value
            self.__skip_separator()

            green = self.lexer.next().value
            self.__skip_separator()

            blue = self.lexer.next().value

            self.combo_colors.append([red, green, blue])

    def __parse_hit_objects(self):
        while not self.__eof_or_new_section():
            list = []
            for _ in range(0, 5):
                list.append(self.lexer.next().value)
                self.__skip_separator()

            if int(list[-2]) & 0b00000001:
                # Circle
                pass
            elif int(list[-2]) & 0b00000010:
                # Slider
                list.append(self.__parse_slider_params())
            elif int(list[-2]) & 0b00001000:
                # Spinner
                list.append(self.__parse_spinner_params())
            elif int(list[-2]) & 0b10000000:
                # Mania hold
                list.append(self.__parse_hold_params())

            if self.lexer.peek().type == 'number':
                self.hit_objects.append(list)
                continue

            hit_sample = []
            for i in range(0, 5):
                hit_sample.append(self.lexer.next().value)

                if i != 4:
                  self.__skip_separator()

            list.append(hit_sample)
            self.hit_objects.append(list)

    def __parse_slider_params(self):
        letter = self.lexer.next().value

        control_points = []
        while self.lexer.next().value == '|':
            x = self.lexer.next().value
            self.__skip_separator()
            y = self.lexer.next().value

            control_points.append([x, y])

        slides = self.lexer.next().value
        self.__skip_separator()
        length = self.lexer.next().value

        if self.lexer.peek().type != 'separator':
          return [letter, control_points, slides, length]
        self.__skip_separator()

        edge_sounds = [self.lexer.next().value]
        while self.lexer.next().value == '|':
            edge_sounds.append(self.lexer.next().value)


        normal_set = self.lexer.next().value
        self.__skip_separator()
        addition_set = self.lexer.next().value
        edge_sets = [[normal_set, addition_set]]

        while self.lexer.next().value == '|':
            normal_set = self.lexer.next().value
            self.__skip_separator()
            addition_set = self.lexer.next().value
            edge_sets.append([normal_set, addition_set])

        return [letter, control_points, slides, length, edge_sounds, edge_sets]

    def __parse_spinner_params(self):
        end_time = self.lexer.next().value
        self.lexer.next()

        return end_time

    def __parse_hold_params(self):
        end_time = self.lexer.next().value
        self.lexer.next()

        return end_time

    def __eof_or_new_section(self):
        return self.lexer.peek().type == 'section' or self.lexer.eof()

    def __skip_separator(self):
        token = self.lexer.next()
        if token.type != 'separator':
            self.__error(f'Expected separator, found {token.type}', token)

    def __skip_identifier(self):
        token = self.lexer.next()
        if token.type != 'identifier':
            self.__error(f'Expected separator, found {token.type}', token)

    def __error(self, msg: str, token: BeatmapToken):
        raise TypeError(f'{msg}: `{token.value}` ({token.col}:{token.line})')
