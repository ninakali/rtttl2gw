import argparse

# Note: flat notes or "H" sometimes are used, but not implemented (yet?)
pitches = ["p", "c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]


class Note:
    duration = None
    dot = False
    pitch = pitches.index("p")
    octave = None

    def __repr__(self):
        s = ""
        if self.duration:
            s += str(self.duration)
        s += pitches[self.pitch]
        if self.octave:
            s += str(self.octave)
        if self.dot:
            s += "."
        return s


class Melody:
    name = ""
    duration = 4
    octave = 5
    bpm = 120
    notes = []

    def __repr__(self):
        return "RTTTL[%s: <d:%s o:%s b:%s> <%s>]" % (
            self.name,
            self.duration,
            self.octave,
            self.bpm,
            self.notes,
        )


def parse_notes(notes):
    notes = notes.strip().lower().split(",")
    notes = [n.strip() for n in notes]
    parsed_notes = []
    for note in notes:
        new_note = Note()
        if note[0].isdigit():
            # duration is present
            if note[1].isdigit():
                # 16 or 32
                new_note.duration = int(note[0:2])
                note = note[2:]
            else:
                new_note.duration = int(note[0])
                note = note[1:]
        if len(note) > 1 and note[1] == "#":
            # sharp note
            new_note.pitch = pitches.index(note[0:2])
            note = note[2:]
        else:
            new_note.pitch = pitches.index(note[0])
            note = note[1:]
        if len(note) >= 1 and note[0].isdigit():
            # octave
            new_note.octave = int(note[0])
            note = note[1:]
        # final check for dotted notes
        if len(note) >= 1:
            new_note.dot = True
        parsed_notes.append(new_note)
    return parsed_notes


def parse_rtttl(rtttl):
    print(rtttl)
    rtttl = rtttl.strip()
    melody = Melody()
    name, defaults, notes = rtttl.split(":")
    defaults = defaults.split(",")
    melody.name = name
    for df in defaults:
        df = df.strip()
        if "d=" in df:
            melody.duration = int(df[2:])
        if "o=" in df:
            melody.octave = int(df[2:])
        if "b=" in df:
            melody.bpm = int(df[2:])
    melody.notes = parse_notes(notes)
    print(melody)
    return melody


def generate_play(melody):
    program = []
    config = "L%d O%d T%d " % (melody.duration, melody.octave - 1, melody.bpm)
    cmd = ""
    prev_duration = melody.duration
    prev_octave = melody.octave
    unprocessed_left = False
    for note in melody.notes:
        unprocessed_left = True
        if not note.duration:
            note.duration = melody.duration
        if not note.octave:
            note.octave = melody.octave
        if note.pitch == 0:
            # pause
            cmd += "p%d " % note.duration
        else:
            # not pause
            if note.duration != prev_duration:
                cmd += "L%d " % note.duration
                prev_duration = note.duration
            if note.octave != prev_octave:
                cmd += "O%d " % (note.octave - 1)
                prev_octave = note.octave
            if note.dot:
                cmd += "%s. " % pitches[note.pitch]
            else:
                cmd += "%s " % pitches[note.pitch]
        # check max len
        if len(cmd) + len(config) + len("play ''") > 60:
            program.append('PLAY "' + config + cmd + '"')
            config = "L%d O%d T%d " % (prev_duration, prev_octave - 1, melody.bpm)
            cmd = ""
            unprocessed_left = False
    if unprocessed_left:
        program.append('PLAY "' + config + cmd + '"')
    return program


def main(infile, outfile):
    melody = parse_rtttl(open(infile).read())
    program = generate_play(melody)
    with open(outfile, "w") as dest:
        for ln, line in enumerate(program):
            dest.write(str(ln + 1) + " " + line + "\r\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="RTTTL2GW",
        description="Convert simple RTTTL melodies into GW BASIC programs",
    )
    parser.add_argument("infile", help="Name of a text file with RTTTL info")
    parser.add_argument("outfile", help="Name of a plain text BAS program to generate")
    args = parser.parse_args()
    main(args.infile, args.outfile)
