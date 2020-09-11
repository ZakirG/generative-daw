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
The goal is to increase the probability that a tasteful voicing will be used over a boring or dissonant one. 

By my personal standards, a 1-3-5 major triad is boring and I will never use it in a composition with my name on it.
So I wouldn't include that triad in this dictionary. The program will then generate a 1-3-5
triad less often than the voicings that I do like. So it'll generate compositions with nice voicings more often.

first_scale_degree: This is the lowest note in the chord, referenced by that note's position in the scale. So in C major, a 7 would mean B.
"""
good_voicings = {
    # Quality of chord in question
    'major': [
        {'roman_numeral': 'I', 'starting_scale_degree': 5, 'intervals': [5,4], 'name': 'major second inversion', 'details': []},
        #  Sounds good if u play it right after its root in the bass:
        {'roman_numeral': 'VII', 'name': 'neosoul dominant seventh chord', 'first_scale_degree': 6, 'intervals': [6, 4, 4, 3]},
        # So pretty. Neo-soul major 7/9 
        {'roman_numeral': 'I', 'name': 'neosoul maj7/9', 'first_scale_degree': 1, 'intervals': [7, 7, 2, 3, 4]},
        {'roman_numeral': 'I', 'name': 'gospel maj9', 'first_scale_degree': 1, 'intervals': [7, 5, 2, 2, 3]},
        # Sounds good with the top rolled on:
        {'roman_numeral': 'I', 'name': 'neosoul maj7/9/#11', 'first_scale_degree': 7, 'intervals': [1,4,3,4,3,4]}
    ],
    'minor': [
        {'roman_numeral': 'i', 'name': 'neosoul minor 7/9', 'first_scale_degree': 1, 'intervals': [7, 3, 4, 1, 4]}
    ]
}


# Some sources:
# >> https://mixedinkey.com/captain-plugins/wiki/best-chord-progressions/
# >> https://www.libertyparkmusic.com/common-chord-progressions/
nice_progressions = {
    'major-classical': [
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
    'major-jazz': [
        ['ii', 'V', 'I'],


    ]
    
}