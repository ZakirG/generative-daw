import random

chromatic_scale = [{'note': 'c'}, {'note': 'cs'}, {'note': 'd'}, {'note': 'ds'}, {'note': 'e'}, {'note': 'f'}, {'note': 'fs'}, {'note': 'g'}, {'note': 'gs'}, {'note': 'a'}, {'note': 'as'}, {'note': 'b'}]

allowed_chord_sizes = range(3, 7)

scales = {
            'maj' : {'name' : 'major', 'intervals' : [2,2,1,2,2,2,1 ] },
            'min' : {'name' : 'minor', 'intervals' : [2,1,1,2,2,1,2 ] },
            'dhmaj' : {'name' : 'maj (b2 b6)', 'intervals' : [1,3,1,2,1,3,1 ] },
        }

def get_allowed_notes(key, scale, octave): 
    possible_octaves = []
    if octave == 'any':
        possible_octaves = range(1,3)
        octave = 1
    else:
        possible_octaves = [octave]
        
    allowed_chromatic_notes = []
    for octave in possible_octaves:
        for note in chromatic_scale:
            allowed_chromatic_notes.append({'note' : note['note'], 'octave' : octave})
    
    return get_key_scale_notes(key, scale, octave, allowed_chromatic_notes)
    
def get_key_scale_notes(key, scale_code, octave, allowed_chromatic_notes):
    index_of_key = allowed_chromatic_notes.index({'note' : key.lower(), 'octave' : octave})
    notes_sorted_starting_at_root = allowed_chromatic_notes[index_of_key:] + allowed_chromatic_notes[:index_of_key]
    notes_sorted_starting_at_root = notes_sorted_starting_at_root * 2 # double list to make note selection circular
    print(notes_sorted_starting_at_root)
    intervals = scales[scale_code]['intervals']
    print(intervals)
    key_scale_notes = []
    i = 0
    for interval in intervals:
        print(notes_sorted_starting_at_root[i + interval])
        key_scale_notes.append( notes_sorted_starting_at_root[i + interval] )
        i = i + interval
    return key_scale_notes

def generate_random_melody(length, key, scale, octave):
    allowed_notes = get_allowed_notes(key, scale, octave)
    
    result = []
    for i in range(length):
        result.append([random.choice(allowed_notes)])
    
    print('melody:' + str(result))
    return result
    
def generate_random_chords(length, key, scale, octave):
    allowed_notes = get_allowed_notes(key, scale, octave)
    
    result = []
    for i in range(length):
        num_notes_in_chord = random.choice(allowed_chord_sizes)
        chord = []
        unused_chord_tones = allowed_notes.copy()
        for j in range(num_notes_in_chord):
            generated_note_index = random.choice(range(len(unused_chord_tones)))
            chord.append(unused_chord_tones[generated_note_index])
            unused_chord_tones.pop(generated_note_index)
        result.append(chord)
            
    print('chords:' + str(result))
    return result
    