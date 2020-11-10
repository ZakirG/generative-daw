from midiutil import MIDIFile
from audiolazy import str2midi
import io
import datetime
import mido

def note_to_numeral(note):
    """
    This function takes my internal note data structure.
    {'note': 'c', 'octave': 4}
    """
    letter = note['note'].strip()[0].upper()
    octave = note['octave']
    if len(note['note']) == 2:
        letter = note['note'].strip().replace('s','#')
        letter = letter[0].upper() + letter[1:]
    return str2midi(letter+str(octave))

def note_name_to_numeral(note_name):
    """
    This function takes a string letter
    """
    letter = note_name.strip()[0].upper()
    octave = note_name.strip()[-1]
    if len(note_name) == 3:
        letter = note_name.strip()[0:2].replace('s','#').upper()
    return str2midi(letter+octave)

def numeral_to_note(midi_numeral):
    midi_numeral = int(midi_numeral)
    MIDI_A4 = 69
    num = midi_numeral - (MIDI_A4 - 4 * 12 - 9)
    note = (num + .5) // 12 - .5
    rnote = round(note);
    octave = str(round((num - note) / 12.0))
    namesArr = ["c", "cs", "d", "ds", "e", "f", "fs", "g", "gs", "a", "as", "b"]
    names = namesArr[rnote] + octave
    
    return names

# Creates a MIDI File following the example from MIDIUtil: https://pypi.org/project/MIDIUtil/
def create_midi_file(daw_state):
    print('inside create midi file with ', daw_state['sequence'])
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

def midi_file_to_sequence(midi_file):
    """
    Using MIDO to translate a midi file into a sequence.
    A sequence is a list of dicts of this form:
        {
            n: 37,      # The MIDI note numeral.
            g: 4,       # The sustain time, in ticks.
            t: 0,       # The start time of the note in ticks.
        }
    """

    # Save the user file locally so MIDO can read it
    timestamp =  datetime.datetime.now().timestamp()
    midi_filename = 'artifacts/midi-import-' + str(timestamp) + '.mid'
    midi_file.save(midi_filename)

    notes_as_sequence = []

    input_midi = mido.MidiFile(midi_filename)
    output_sequence = []

    ticks_per_beat = input_midi.ticks_per_beat
    notes_from_file = {} # convert relative time -> absolute time
    current_absolute_time = 0
    tempo = 0
    for track in input_midi.tracks:
        print('track: ', track)
        for message in track:
            print('\t message: ', message)
            current_absolute_time += message.time
            print('\t current time:', current_absolute_time)
            if message.type in ['note_on','note_off']:
                note = str(message.note)

                if note in notes_from_file:
                    notes_from_file[note].append({ 'type' : message.type, 'time' : current_absolute_time })
                else:
                    notes_from_file[note] = [{ 'type' : message.type, 'time' : current_absolute_time }]
            elif message.type == 'set_tempo':
                tempo = message.tempo / 6000

    
    notes_as_sequence = []
    current_time = 0
    
    
    for note_numeral in notes_from_file.keys():
        messages = notes_from_file[note_numeral].copy()

        print('messages for note ', numeral_to_note(note_numeral), ': ', messages)
        
        message_index = 0
        while message_index < len(messages):
            message = messages[message_index]

            if message['type'] != 'note_on':
                # print('huh?', message['type'])
                message_index += 1
                continue
            
            note_sustain = 0
            note_start_time = message['time']

            for off_candidate_index in range(message_index  + 1, len(messages)):
                if messages[off_candidate_index]['type'] == 'note_off':
                    note_sustain = messages[off_candidate_index]['time'] - message['time']
                else:
                    print('\n\n\nError: these messages are not alternating on off')
            
            sequence_note = {
                'n': int(note_numeral) + 24,
                't': (note_start_time / 60),
                'g': (note_sustain / 60)
            }
            notes_as_sequence.append(sequence_note)
            message_index += 1
    


    return notes_as_sequence, tempo