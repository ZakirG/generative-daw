constants = {
    'chromatic_scale' : [{'note': 'c'}, {'note': 'cs'}, {'note': 'd'}, {'note': 'ds'}, {'note': 'e'}, {'note': 'f'}, {'note': 'fs'}, {'note': 'g'}, {'note': 'gs'}, {'note': 'a'}, {'note': 'as'}, {'note': 'b'}],
    'chromatic_scale_letters' : ['c', 'cs', 'd', 'ds', 'e', 'f', 'fs', 'g', 'gs', 'a', 'as', 'b'],
    'enharmonic_equivalents': {
        'as' : 'bb',
        'cs' : 'db',
        'ds': 'eb',
        'fs' : 'gb', 
        'gs': 'ab'
    },
    'scales' : {
        'maj' : {'name' : 'major', 'intervals' : [2,2,1,2,2,2,1 ], 'code' : 'maj' },
        'min' : {'name' : 'minor', 'intervals' : [2,1,2,2,1,2,2 ], 'code' : 'min' },
        'dhmaj' : {'name' : 'double harmonic maj', 'intervals' : [1,3,1,2,1,3,1 ], 'code' : 'dhmaj' },
        'majpent' : {'name' : 'major pentatonic', 'intervals' : [2,2,3,2,3], 'code' : 'majpent', 'parent_scale': 'maj' },
        'minpent' : {'name' : 'minor pentatonic', 'intervals' : [3,2,2,3,2], 'code' : 'minpent', 'parent_scale': 'min' },
    },
    'roman_numerals_upper': ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
}

chord_charts = {
    'maj': ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii\xB0'],
    'min': ['i', 'ii', 'III', 'iv', 'v', 'VI', 'VII' ]
}

# When the chord leading constraint is applied, if a chord has no member
# in this dictionary, it may lead to any chord.
# Traditionally, V -> I is the only option for V in a major chord leading chart.
# But in pop music, vi is a popular follow-up as well, so I included it.
chord_leading_chart = { 
    'major': {
        'ii': ['IV', 'V', 'vii\xB0'],
        'iii': ['ii', 'IV', 'vi'],
        'IV': ['I', 'iii', 'V', 'vii\xB0'],
        'V': ['I', 'vi'],
        'vi': ['ii', 'IV', 'V', 'I'],
        'vii\xB0': ['I', 'iii'],
    },
    'minor': {
        'ii\xB0': ['V', 'vii\xB0'],
        'III': ['VI'],
        'iv': ['v', 'vii\xB0'],
        'v': ['i'],
        'VI': ['ii\xB0', 'iv'],
        'vii\xB0': ['i'],
        'VII': ['III']
    }
}


"""
Fill this dictionary with voicings that you find to be tasteful.
The goal is to increase the probability that a tasteful voicing will be used over a boring or dissonant one. 

By my personal standards, a 1-3-5 major triad is boring and I will never use it in a composition with my name on it.
So I wouldn't include that triad in this dictionary. The program will then generate a 1-3-5
triad less often than the voicings that I do like. So it'll generate compositions with nice voicings more often.

starting_scale_degree: 
    This is the lowest note in the chord, referenced by that note's position in the mode of the root. 
    So for a C major chord, a 7 would mean B, even if we're playing in the global key of E.
roman_numerals: 
    An array of numerals this voicing is good for. A major second inversion voicing, for example, will be useful if you
    need a I voicing in a major scale, or a IV voicing in a minor scale, so those numerals will be present in the array.
    A minor power chord voicing, for example, applies to the iii situation for a major tonic, but also the i situation for a minor tonic.
"""
good_voicings = {
    'major': [
        {'roman_numerals': ['I', 'IV', 'V'], 'name': 'major first inversion', 'starting_scale_degree': 3, 'intervals': [3, 5]},
        {'roman_numerals': ['I', 'IV', 'V'], 'name': 'major second inversion', 'starting_scale_degree': 5, 'intervals': [5,4]},
        {'roman_numerals': ['I'], 'name': 'maj 7 (three note voicing)', 'starting_scale_degree': 1, 'intervals': [4, 7]},
        # So pretty. Neo-soul major 7/9 
        {'roman_numerals': ['I'], 'name': 'neosoul maj7/9', 'starting_scale_degree': 1, 'intervals': [7, 7, 2, 3, 4]},
        {'roman_numerals': ['I'], 'name': 'gospel maj9', 'starting_scale_degree': 1, 'intervals': [7, 5, 2, 2, 3]},
        # Sounds good with the top rolled on:
        {'roman_numerals': ['I'], 'name': 'neosoul maj7/9/#11', 'starting_scale_degree': 7, 'intervals': [1,4,3,4,3,4]},
        {'roman_numerals': ['I'], 'name': 'major 7/9/#11 (lydian chord)', 'starting_scale_degree': 7, 'intervals': [1,4,3,4,3,4]}
    ],
    'minor': [
         {'roman_numerals': ['ii', 'i'], 'name': 'min 7 (three note voicing)', 'starting_scale_degree': 1, 'intervals': [3, 7]},
         {'roman_numerals': ['i', 'ii', 'iii', 'iv'], 'name': 'minor (power chord voicing)', 'starting_scale_degree': 1, 'intervals': [7, 5, 3, 4]},
        {'roman_numerals': ['i', 'ii', 'iii', 'iv'], 'name': 'neosoul minor 7/9', 'starting_scale_degree': 1, 'intervals': [7, 3, 4, 1, 4]}
    ],
    'dominant 7': [
        {'roman_numerals': ['V'], 'name': 'dominant 7 (three note voicing)', 'starting_scale_degree': 1, 'intervals': [10, 6]},
        #  Sounds good if u play it right after its root in the bass:
        {'roman_numerals': ['VII'], 'name': 'neosoul alt dominant seventh chord', 'starting_scale_degree': 7, 'intervals': [6, 4, 4, 3]}
    ],
    'diminished': [],
    'augmented': []
}

# Some sources:
# >> https://mixedinkey.com/captain-plugins/wiki/best-chord-progressions/
# >> https://www.libertyparkmusic.com/common-chord-progressions/
nice_progressions = {
    'major': [
        ['I', 'IV', 'V'],
        ['I', 'V6', 'vi', 'V'],
        ['I', 'V', 'vi', 'iii', 'IV'],
        ['I', 'vi', 'IV', 'V'], # the 50s progression
        ['I', 'IV', 'V', 'vi'],
        ['I', 'IV', 'vi', 'V'],
        ['IV', 'I6', 'ii'],
        ['vi', 'V', 'IV', 'V'],
        ['vi', 'IV', 'I', 'V'],
        ['vi', 'V', 'I', 'IV'],
        ['vi', 'I', 'V', 'IV'],

        # Songs that use this chord progression include: No Woman No Cry by Bob Marley, Love Story by Taylor Swift, 
        # the verse of Don’t Stop Believing by Journey, the chorus of Someone Like You by Adele...
        ['I', 'V', 'vi', 'IV'] # The 'Axis of Awesome' progression.
    ],
    'minor': [
        ['ii', 'V', 'I'],
    ]
}