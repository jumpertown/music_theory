import os
import argparse

from random import randint
from time import sleep


DEFAULT_NUMBER_OF_TURNS = 20
DEFAULT_TIME_BETWEEN_TURNS = 3
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
        default=['A', 'E'],
    )

    parser.add_argument(
        '--chords',
        type=list_of_strings,
        required=False,
        default=['M', 'm'],
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


def print_fret_tab(string_number, fret):
    for num, name in sorted(list(GUITAR_STRINGS.items())):
        if num == string_number:
            print(f'{name} -{fret}--')
        else:
            padding = '-' if fret < 10 else '--'
            print(f'{name} -{padding}--')


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
    def __init__(self, args):
        self.args = args
    
    def print_question(self):
        raise NotImplementedError()

    def print_solution(self):
        raise NotImplementedError()


class FretExercise(Exercise):
    def __init__(self, args):
        super().__init__(args)
        self.string_number = pick_random(list(GUITAR_STRINGS.keys()))

        if self.args.frets:
            self.fret = pick_random(self.args.frets)
        else:
            self.fret = randint(0, MAX_FRET)

    def print_question(self):
        print(format_fret(self.string_number, self.fret))
        print_fret_tab(self.string_number, self.fret)
    
    def print_solution(self):
        note = fret_to_note(self.string_number, self.fret)
        print(f'The note is {note}')


class NoteExercise(Exercise):
    def __init__(self, args):
        super().__init__(args)
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
        print_fret_tab(self.string_number, fret)
     

exercises = {
    'fret': FretExercise,
    'note': NoteExercise,
}
main()
