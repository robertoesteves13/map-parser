import sys
from parser import BeatmapParser

def main():
    lexer = BeatmapParser(sys.argv[1])
    lexer.process()

    print('[General]')
    for key, value in lexer.general_dict.items():
        print(f'\t{key}: {value}')

    print('[Editor]')
    for key, value in lexer.editor_dict.items():
        print(f'\t{key}: {value}')

    print('[Metadata]')
    for key, value in lexer.metadata_dict.items():
        print(f'\t{key}: {value}')

    print('[Difficulty]')
    for key, value in lexer.difficulty_dict.items():
        print(f'\t{key}: {value}')

    print('[Event]')
    for event in lexer.events:
        print(f'\t{event.type},{event.start_time},{event.params}')

    print('[TimingPoints]')
    for timing_point in lexer.timing_points:
        print(f'\t{timing_point}')

    print('[Colours]')
    for color in lexer.combo_colors:
        print(f'\t{color}')

    print('[HitObjects]')
    for hit_object in lexer.hit_objects:
        print(f'\t{hit_object}')

if __name__ == '__main__':
    main()
