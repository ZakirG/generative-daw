constants = {
    'chromatic_scale' : [{'note': 'c'}, {'note': 'cs'}, {'note': 'd'}, {'note': 'ds'}, {'note': 'e'}, {'note': 'f'}, {'note': 'fs'}, {'note': 'g'}, {'note': 'gs'}, {'note': 'a'}, {'note': 'as'}, {'note': 'b'}],
    'enharmonic_equivalents': {
        'as' : 'bb',
        'cs' : 'db',
        'ds': 'eb',
        'fs' : 'gb', 
        'gs': 'ab'
    },
    'scales' : {
        'maj' : {'name' : 'major', 'intervals' : [2,2,1,2,2,2,1 ], 'code' : 'maj' },
        'min' : {'name' : 'minor', 'intervals' : [2,1,1,2,2,1,2 ], 'code' : 'min' },
        'dhmaj' : {'name' : 'double harmonic maj', 'intervals' : [1,3,1,2,1,3,1 ], 'code' : 'dhmaj' },
        'majpent' : {'name' : 'major pentatonic', 'intervals' : [2,2,3,2,3], 'code' : 'majpent', 'parent_scale': 'maj' },
        'minpent' : {'name' : 'minor pentatonic', 'intervals' : [3,2,2,3,2], 'code' : 'minpent', 'parent_scale': 'min' },
    },
    'roman_numerals_upper': ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
}

# When the chord leading constraint is applied, if a chord has no member
# in this dictionary, it may lead to any chord.
chord_leading_chart = { 
    'major': {
        'ii': ['IV', 'V', 'vii\xB0'],
        'iii': ['ii', 'IV', 'vi'],
        'IV': ['I', 'iii', 'V', 'vii\xB0'],
        'V': ['I'],
        'vi': ['ii', 'IV', 'V', 'I'],
        'vii\xB0': ['I', 'iii'],
    },
    'minor': {
        'ii\xB0': ['V', 'vii\xB0'],
        'III': ['VI'],
        'iv': ['V', 'vii\xB0'],
        'V': ['i'],
        'VI': ['ii\xB0', 'iv'],
        'vii\xB0': ['i'],
        'VII': ['III']
    }
}


"""
Fill this dictionary with voicings that you find to be tasteful.
The goal is to increase the probability that a tasteful voicing will be used over a boring or bad one. 

By my personal standards, a 1-3-5 triad is boring and I will never use it.
So I wouldn't include that triad in this dictionary. As a result, the program will generate a 1-3-5
triad less often than the voicings that I do like, more often resulting in compositions
with voicings I enjoy.
"""
good_voicings = {
    # Quality of chord in question
    'major': {
        # Number of notes in chord
        '3': [
            {
                # Starting scale degree relative to the root of the chord's scale.
                'starting_scale_degree': 1,
                
                # Note that len(intervals) will be one less than num_notes_in_chord
                'intervals': [],

                # Details: Metadata strings that may be useful to the program in the future.
                # Example values: neosoul, gospel, herbie_hancock, miles_davis_fourth_chord
                'details': []
            }
        ],
        '4': [
            {'starting_scale_degree': 1, 'intervals': []},
            {'starting_scale_degree': 1, 'intervals': []},
        ],
        '5': [
            {'starting_scale_degree': 1, 'intervals': []},
            {'starting_scale_degree': 1, 'intervals': []},
        ],
        '6': [
            {'starting_scale_degree': 1, 'intervals': []},
            {'starting_scale_degree': 1, 'intervals': []},
        ],
    },
    'minor': {
        '3': [
            {'starting_scale_degree': 1, 'intervals': []},
            {'starting_scale_degree': 1, 'intervals': []},
        ],
        '4': [
            {'starting_scale_degree': 1, 'intervals': []},
            {'starting_scale_degree': 1, 'intervals': []},
        ],
        '5': [
            {'starting_scale_degree': 1, 'intervals': []},
            {'starting_scale_degree': 1, 'intervals': []},
        ],
        '6': [
            {'starting_scale_degree': 1, 'intervals': []},
            {'starting_scale_degree': 1, 'intervals': []},
        ],
    }
}