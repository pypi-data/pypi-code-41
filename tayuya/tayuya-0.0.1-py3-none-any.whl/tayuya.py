from typing import List, Dict, Iterator, Tuple

import mido
from mido import MidiFile
from music21 import note as musicnote
from music21 import stream, analysis, scale, pitch

from tayuya import constants
from tayuya.draw import Tabs
from tayuya.exceptions import TrackError


class MIDIParser:
    """
    MIDI file parser
    """

    def __init__(self, file_path: str, channel=0, *args, **kwargs):
        self.midi_file = MidiFile(file_path)

        self.channel = channel
        self.midi_data = self.midi_file.tracks[channel]

        # Get time signature
        ts_meta = list(filter(lambda x: x.type == constants.TIME_SIGNATURE,
                              self.midi_data))
        if ts_meta:
            numerator = ts_meta[0].numerator
            denominator = ts_meta[0].denominator
        else:
            numerator = denominator = 4
        self.time_signature = (numerator, denominator)

        self.stream = stream.Stream()

        if not self.midi_data:
            raise TrackError

    def _on_note(self) -> Iterator:
        """
        Filter all notes which are `on`

        :returns: List of notes which were on
        """
        return filter(
            lambda x: x.type == constants.NOTE_ON, self.midi_data)

    def _midi_to_note(self, midi_note: int) -> str:
        """
        Convert MIDI note to music note

        :param midi_note: MIDI code for this note
        :returns: String notation of MIDI note
        """
        return constants.MIDI_TO_NOTES[midi_note][0]

    def notes_played(self) -> List[Dict]:
        """
        Get all notes played in this MIDI track

        :returns: List of all notes player with note time
        """
        return [
            dict(note=self._midi_to_note(note.note), time=note.time)
            for note in self._on_note()
        ]

    def get_key(self) -> pitch.Pitch:
        """
        Get key of this MIDI track

        refer: http://web.mit.edu/music21/doc/moduleReference/moduleAnalysisDiscrete.html

        We have used Krumhansl-Schmuckler algorithm for key determitination with
        following weightings implementation:

        * Aarden-Essen
        * Bellman-Budge
        * Krumhansl-Schmuckler
        * Krumhansl-Kessler
        * Temperley-Kostka-Payne

        Key which is determined the most by these methods is chosen
        
        :returns:
        """
        note_length: float = 0.0

        for note in self.midi_data:
            if note.type not in [constants.NOTE_ON, constants.NOTE_OFF] or note.is_meta:
                continue
            note_length += note.time
            if note.type == constants.NOTE_ON:
                self.stream.append(musicnote.Note(note.note,
                                   type=self._get_note_type(note_length)))
                note_length = 0.0

        key_weight = analysis.discrete.KeyWeightKeyAnalysis().process(self.stream)
        krumhansl_shmuckler = analysis.discrete.KrumhanslSchmuckler().process(self.stream)
        bellman_budge = analysis.discrete.BellmanBudge().process(self.stream)
        aarden_essen = analysis.discrete.AardenEssen().process(self.stream)
        krumhansl_kessler = analysis.discrete.KrumhanslKessler().process(self.stream)
        temperley_kostka_payne = analysis.discrete.TemperleyKostkaPayne().process(self.stream)

        prediction = list(map(lambda x: (x[0][0], x[0][1]),
                              [key_weight, krumhansl_shmuckler, bellman_budge,
                               aarden_essen, krumhansl_kessler,
                               temperley_kostka_payne]))

        return max(prediction, key=prediction.count)

    def _get_note_type(self, note_length: int) -> str:
        """
        Get note type: `quarter`, `half`, `whole`, `eighth` or `sixteenth`

        :params note_length: length of this note played
        :returns: Type of note played
        """
        num_beats = note_length / self.midi_file.ticks_per_beat

        # Get which note type gets the beat
        beat_note = constants.NUM_TO_NOTES[self.time_signature[1]]

        if num_beats <= 1.5:
            return beat_note
        elif 1.5 < num_beats <= 2.5:
            return constants.NUM_TO_NOTES[self.time_signature[1] // 2]
        else:
            return constants.WHOLE_NOTE

    def render_tabs(self, **kwargs) -> None:
        """
        Visualize notes in tabulature format
        """
        tabs = Tabs(notes=self.notes_played())
        to_play = tabs.generate_notes(self.find_start())

        tabs.draw(to_play, **kwargs)

    def find_start(self) -> Tuple:
        """
        Generate an in memory scale chart

        :param start_fret: Starting fret of this scale
        """
        max_count: int = 0
        start_fret = start_string = start_scale_notes = None

        # (pitch, scale, color)
        scale_, scale_type = self.get_key()
        scale_ = self._fix_note_name(scale_)
        this_scale_step = constants.SCALE[scale_type]

        sc1 = scale.MajorScale(scale_)
        this_scale_notes = [note.nameWithOctave for note in sc1.pitches]
        first_note = this_scale_notes[0]

        note_info = constants.NOTE_TO_STRING[self._fix_note_name(first_note)]

        for note_string, note_fret in note_info.items():
            string: int = note_string
            fret: int = note_fret
            num_notes: int = 0
            step: int = 0
            span: int = 8
            note_list: List = [(fret, string)]

            while string > 0 and span > 0 and note_fret:
                fret += this_scale_step[step]
                step += 1
                num_notes += 1
                note_list.append((fret, string))

                if step >= len(constants.SCALE[scale_type]):
                    step = 0
                if fret > note_fret + 3:
                    fret -= 4 if string == 2 else 5
                    string -= 1
                if num_notes > max_count:
                    max_count = num_notes
                    start_fret = note_fret
                    start_string = note_string
                    start_scale_notes = note_list

                span -= 1
        return start_fret, start_string, start_scale_notes

    def _fix_note_name(self, scale_):
        if isinstance(scale_, str):
            name = scale_
        else:
            name = scale_.nameWithOctave
        name = name.replace('-', 'b')
        try:
            int(name[-1])
        except ValueError:
            name += str(scale_.implicitOctave)
        return name
