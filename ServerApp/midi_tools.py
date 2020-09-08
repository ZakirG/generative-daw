from midiutil import MIDIFile
from audiolazy import str2midi

def note_name_to_numeral(note_name):
    letter = note_name.strip()[0]
    octave = note_name.strip()[-1]
    if len(note_name) == 3:
        letter = note_name.strip()[0:2].replace('s','#').upper()
    return str2midi(letter+octave)

# Creates a MIDI File following the example from MIDIUtil: https://pypi.org/project/MIDIUtil/
def create_midi_file(daw_state):
    num_tracks = len(daw_state['tracks'])

    channel  = 0
    time     = 0    # In beats
    duration = 1    # In beats
    tempo    = daw_state['tempo']   # In BPM
    volume   = 50  # 0-127, as per the MIDI standard

    midi_object = MIDIFile(numTracks=num_tracks)  # One track, defaults to format 1 (tempo track is created automatically)
    
    # The daw_state representation gives note a time state array. To write a MIDI file,
    # we'll need to transpose the mapping so that each time step maps to a set of active note numerals.
    
    max_time_steps = len(daw_state['tracks'][0][0]['timeStates'])
    for current_time_step in range(0, max_time_steps):
        notes_active_at_this_timestep = []

        for track_index in range(0, num_tracks):
            note_states = daw_state['tracks'][track_index]
            for note in note_states:
                if note['timeStates'][current_time_step]:
                    this_note_numeral = note_name_to_numeral(note['id'])
                    notes_active_at_this_timestep.append(this_note_numeral)

        # This timestep has been scanned and active notes gathered. We can write all notes to the file.
        midi_object.addTempo(track_index, time, tempo)
        for note in notes_active_at_this_timestep:
            midi_object.addNote(track_index, channel, note, current_time_step, duration, volume)

    with open("midi-export.mid", "wb") as output_file:
        midi_object.writeFile(output_file)

    return ("midi-export.mid", output_file)