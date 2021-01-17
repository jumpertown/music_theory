import os
import argparse

from random import randint
from time import sleep
from collections import namedtuple


ChordShape = namedtuple('ChordShape', (
    'root_string',
    'first_root',
    'chord',
))


DEFAULT_NUMBER_OF_TURNS = 20
DEFAULT_TIME_BETWEEN_TURNS = 10
DEFAULT_TIME_BEFORE_REVEAL = 2
DEFAULT_EXERCISE='fret'
MAX_FRET = 17

NOTES = (
    ('C', ),
    ('C#', 'Db'),
    ('D', ),
    ('D#', 'Eb'),
    ('E', ),
    ('F', ),
    ('F#', 'Gb'),
    ('G', ),
    ('G#', 'Ab'),
    ('A', ),
    ('A#', 'Bb'),
    ('B', ),
)

GUITAR_STRINGS = {
    6: 'E',
    5: 'A',
    4: 'D',
    3: 'G',
    2: 'B',
    1: 'E',
}

CHORD_SHAPES = {
    ('C', 'Maj'): ChordShape(
        root_string=5,
        first_root=3,
        chord=(None, 3, 2, 0, 1, 0)
    ),
    ('C', 'min'): ChordShape(
        root_string=5,
        first_root=3,
        chord=(None, 3, 1, 0, 1, None)
    ),
    ('A', 'Maj'): ChordShape(
        root_string=5,
        first_root=0,
        chord=(None, 0, 2, 2, 2, 0)
    ),
    ('A', 'min'): ChordShape(
        root_string=5,
        first_root=0,
        chord=(None, 0, 2, 2, 1, 0)
    ),
    ('G', 'Maj'): ChordShape(
        root_string=6,
        first_root=3,
        chord=(3, 2, 0, 0, 0, 3)
    ),
    ('G', 'min'): ChordShape(
        root_string=6,
        first_root=3,
        chord=(3, 1, 0, 0, None, None)
    ),
    ('E', 'Maj'): ChordShape(
        root_string=6,
        first_root=0,
        chord=(0, 2, 2, 1, 0, 0)
    ),
    ('E', 'min'): ChordShape(
        root_string=6,
        first_root=0,
        chord=(0, 2, 2, 0, 0, 0)
    ),
    ('D', 'Maj'): ChordShape(
        root_string=4,
        first_root=0,
        chord=(None, None, 0, 2, 3, 2)
    ),
    ('D', 'min'): ChordShape(
        root_string=4,
        first_root=0,
        chord=(None, None, 0, 2, 3, 1)
    ),
}


def main():
    parser = argparse.ArgumentParser(
        description='Fretboard exercises.'
    )
    parser.add_argument(
        '--exercise',
        type=str,
        required=False,
        default=DEFAULT_EXERCISE,
    )
    parser.add_argument(
        '--number-of-turns',
        type=int,
        required=False,
        default=DEFAULT_NUMBER_OF_TURNS,
    )
    parser.add_argument(
        '--time-between-turns',
        type=float,
        required=False,
        default=DEFAULT_TIME_BETWEEN_TURNS,
    )
    parser.add_argument(
        '--time-before-reveal',
        type=float,
        required=False,
        default=DEFAULT_TIME_BEFORE_REVEAL,
    )

    parser.add_argument(
        '--frets',
        type=list_of_ints,
        required=False,
        default=None,
    )

    parser.add_argument(
        '--chord-shapes',
        type=list_of_strings,
        required=False,
        default=['C', 'A', 'G', 'E', 'D'],
    )

    parser.add_argument(
        '--chords',
        type=list_of_strings,
        required=False,
        default=['Maj', 'min'],
    )

    args = parser.parse_args()
    run_exercise(args)


def list_of_strings(string):
    return string.split(',')


def list_of_ints(string):
    return [
        int(part)
        for part
        in list_of_strings(string)
    ]


def pick_random(collection):
    random_index = randint(0, len(collection) - 1)
    return collection[random_index]


def clear():
    os.system('cls' if os.name=='nt' else 'clear')


def half_step_c_interval(note):
    interval = 0
    for test_note in NOTES:
        for enharmonic in test_note:
            if note == enharmonic:
                return interval
        interval += 1

    raise ValueError(f'Unknown note: {note}')


def fret_to_note(string_number, fret):
    open_string_note = GUITAR_STRINGS[string_number]
    interval_from_c = half_step_c_interval(open_string_note) + fret
    interval_from_c %= 12
    return ' or '.join(NOTES[interval_from_c])


def format_fret(string_number, fret):
    if fret == 0:
        return f'Open {string_number} string'

    string_name = format_string(string_number)
    return f'{string_name} fret {fret}'


def format_string(string_number):
    string_note = GUITAR_STRINGS[string_number]
    return f'{string_number}{string_note}'


def note_interval(note, interval):
    new_offset = (half_step_c_interval(note) + interval) % 12
    return NOTES[new_offset][0]


def chord_form(note, chord_shape):
    root_note = note_interval(
        GUITAR_STRINGS[chord_shape.root_string],
        chord_shape.first_root
    )

    root = half_step_c_interval(root_note)
    fretted = half_step_c_interval(note)
    offset = (fretted - root) % 12

    return tuple(
        n + offset if n is not None else None
        for n in chord_shape.chord
    )


def print_single_note_tab(string_number, fret):
    frets = [None] * 6
    frets[6 - string_number] = fret
    print_fret_tab(frets)

def print_fret_tab(frets):
    for (num, name), fret in zip(sorted(list(GUITAR_STRINGS.items())), reversed(frets)):
        if fret is None:
            padded = '--'
        elif fret < 10:
            padded = f'-{fret}'
        else:
            padded = fret

        print(f'{name} -{padded}--')

def run_exercise(args):
    exercise_class = exercises[args.exercise]
    for turn in range(args.number_of_turns):
        exercise = exercise_class(args)
        clear()
        exercise.print_question()
        sleep(args.time_before_reveal)
        print()
        exercise.print_solution()
        print()
        sleep(args.time_between_turns)


class Exercise:
    def print_question(self):
        raise NotImplementedError()

    def print_solution(self):
        raise NotImplementedError()


class FretExercise(Exercise):
    def __init__(self, args):
        self.string_number = pick_random(list(GUITAR_STRINGS.keys()))

        if args.frets:
            self.fret = pick_random(args.frets)
        else:
            self.fret = randint(0, MAX_FRET)

    def print_question(self):
        print(format_fret(self.string_number, self.fret))
        print_single_note_tab(self.string_number, self.fret)

    def print_solution(self):
        note = fret_to_note(self.string_number, self.fret)
        print(f'The note is {note}')


class NoteExercise(Exercise):
    def __init__(self, args):
        self.string_number = pick_random(list(GUITAR_STRINGS.keys()))
        self.string_note = GUITAR_STRINGS[self.string_number]
        self.string_name = format_string(self.string_number)
        note = pick_random(NOTES)
        self.note = pick_random(note)

    def print_question(self):
        print(f'Play {self.note} on the {self.string_name} string')

    def print_solution(self):
        open_string = half_step_c_interval(self.string_note)
        fretted = half_step_c_interval(self.note)
        fret = (fretted - open_string) % 12
        print(format_fret(self.string_number, fret))
        print_single_note_tab(self.string_number, fret)


class ChordExercise(Exercise):
    def __init__(self, args):
        self.chord_shape_root_note = pick_random(args.chord_shapes)
        self.chord = pick_random(args.chords)
        self.chord_shape = CHORD_SHAPES[(self.chord_shape_root_note, self.chord)]
        note = pick_random(NOTES)
        self.note = pick_random(note)

    def print_question(self):
        print(f'Play {self.note} {self.chord} using the {self.chord_shape_root_note} shape')

    def print_solution(self):
        chord = chord_form(self.note, self.chord_shape)
        print_fret_tab(chord)


exercises = {
    'fret': FretExercise,
    'note': NoteExercise,
    'chord': ChordExercise,
}
main()
