from enum import Enum
from typing import Dict, Tuple, List

from tayuya import constants


class Instrument(Enum):
    GUITAR = 1
    UKULELE = 2

    def strings(self):
        if self == Instrument.GUITAR:
            return constants.GUITAR_STRING
        elif self == Instrument.UKULELE:
            return constants.UKULELE_STRING


class Tabs(object):
    def __init__(self, notes: Dict, *args, **kwargs):
        self.notes = notes
        self.notes_cache: Dict = {}
        # self.scale = scale_

    def note_nearest_to_fret(self, fret: int, note: str, scale_notes: List) -> Tuple:
        try:
            note_info = constants.NOTE_TO_STRING[note]
        except:
            try:
                if int(note[-1]) <= 2:
                    n = note[:-1] + '3'
                    note_info = constants.NOTE_TO_STRING[n]
            except ValueError:
                print('error')

        min_diff: int = 999
        min_fret = min_string = None

        for note_string, note_fret in note_info.items():
            if not note_fret:
                continue

            if (note_fret, note_string) in scale_notes:
                return (note_fret, note_string)

            if self.notes_cache.get(note):
                return (self.notes_cache[note])

            diff = abs(note_fret - fret)
            if diff <= min_diff:
                min_diff = diff
                min_fret = note_fret
                min_string = note_string

        self.notes_cache[note] = (min_fret, min_string)
        return (min_fret, min_string)

    def generate_notes(self, key: Tuple) -> List[Dict]:
        fret, string, scale_notes = key
        to_play: List = []

        for note in self.notes:
            note_fret, note_string = self.note_nearest_to_fret(fret, note['note'], scale_notes)
            to_play.append((note['note'], note_string, note_fret))
            fret = note_fret

        return to_play

    def draw(self, notes_list, **kwargs):
        staff_length = kwargs.get('staff_length', constants.MAX_RENDER_COLUMNS)
        render = ['' for _ in range(constants.GUITAR_STRING)]
        for note, x, y in notes_list:
            idx_x = int(x) - 1
            for idx, r in enumerate(render):
                if len(r) > len(render[idx_x]):
                    diff = len(r) - len(render[idx_x])
                    render[idx_x] += f'{constants.TAB_LINE_CHAR}'*diff
            fret = str(y)
            render[idx_x] += f'{constants.TAB_LINE_CHAR}{fret}{constants.TAB_LINE_CHAR}'

        max_staff_length = len(max(render, key=len))

        for idx, string in enumerate(render):
            diff = max_staff_length - len(string)
            render[idx] = render[idx] + constants.TAB_LINE_CHAR * diff

        break_point = staff_length

        for string in render:
            if string[break_point] != constants.TAB_LINE_CHAR:
                break_point += 1
                continue

        string_idx = 0
        start = 0
        end = break_point
        while True:
            if not render[string_idx][start:] and start > staff_length:
                break
            for idx, string in enumerate(render):
                print(constants.GUITAR_STAFF[idx] + string[start:end])

            string_idx += 1
            string_idx = string_idx % constants.GUITAR_STRING
            start = end
            end = start + break_point

            self._print_blank_line()

    def _print_blank_line(self):
        print()

