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
        {'name': 'major first inversion', 'starting_scale_degree': 3, 'intervals': [3, 5]},
        {'name': 'major second inversion', 'starting_scale_degree': 5, 'intervals': [5,4]},
        {'name': 'maj 7 (three note voicing)', 'starting_scale_degree': 1, 'intervals': [4, 7]},
        {'name': 'maj 7 (four note voicing)', 'starting_scale_degree': 1, 'intervals': [11, 5, 3]},
        {'name': 'maj 9 (four note voicing)', 'starting_scale_degree': 1, 'intervals': [11, 3, 2]},
        {'name': 'major 6/9 (four note voicing)', 'starting_scale_degree': 1, 'intervals': [4, 5, 5]},
        # This chord lacks the root entirely. But it sounds great. From the Jazz Piano Book
        {'name': 'major 6/9 (left hand voicing)', 'starting_scale_degree': 7, 'intervals': [3, 2, 5]},
        # Taken from Jazz Piano Book's rendition of Infant Eyes
        {'name': 'major 6/9 (five note voicing)', 'starting_scale_degree': 1, 'intervals': [7, 9, 5, 5]},
        # So pretty. Neo-soul major 7/9 
        {'name': 'neosoul maj7/9', 'starting_scale_degree': 1, 'intervals': [7, 7, 2, 3, 4]},
        {'name': 'gospel maj9', 'starting_scale_degree': 1, 'intervals': [7, 5, 2, 2, 3]},
        # Sounds good with the top rolled on:
        {'name': 'neosoul maj7/9/#11', 'starting_scale_degree': 7, 'intervals': [1,4,3,4,3,4]},
        {'name': 'major 7/9/#11 (lydian chord)', 'starting_scale_degree': 7, 'intervals': [1, 4, 3, 4, 3, 4]},
    ],
    'minor': [
        {'name': 'min 7 (three note voicing)', 'starting_scale_degree': 1, 'intervals': [3, 7]},
        {'name': 'min 7 (four note voicing)', 'starting_scale_degree': 1, 'intervals': [10, 5, 4]},
        # The root isn't even in the below chord! But it sounds good. Taken from Jazz Piano Book.
        {'name': 'min 7 (left hand voicing)', 'starting_scale_degree': 3, 'intervals': [4, 3, 4]},
        {'name': 'minor (power chord voicing)', 'starting_scale_degree': 1, 'intervals': [7, 5, 3, 4]},
        {'name': 'neosoul minor 7/9', 'starting_scale_degree': 1, 'intervals': [7, 3, 4, 1, 4]},
        {'name': 'minor 7/9/11', 'starting_scale_degree': 1, 'intervals': [5, 9, 1, 7]},
        {'name': 'minor 7/11 (four note voicing)', 'starting_scale_degree': 1, 'intervals': [10, 5, 2]},
        # From the Jazz Piano Book. The sixth is sometimes played in place of the seventh in minor ii chords.
        # Minor sixth chords are preferably used as minor tonic i's rather than ii's.
        {'name': 'minor 6 (four note voicing)', 'starting_scale_degree': 1, 'intervals': [10, 5, 5]},

    ],
    'dominant 7': [
        {'name': 'dominant 7 (three note voicing)', 'starting_scale_degree': 1, 'intervals': [10, 6]},
        {'name': 'dominant 7/9 (four note voicing)', 'starting_scale_degree': 1, 'intervals': [14, 2, 6]},
        {'name': 'dominant 7/#9 (four note voicing)', 'starting_scale_degree': 1, 'intervals': [4, 6, 5]},
        {'name': 'dominant 7 alt (left hand voicing)', 'starting_scale_degree': 1, 'intervals': [4, 2, 5]},
        {'name': 'alt (aug dominant 7/#9)', 'starting_scale_degree': 1, 'intervals': [10, 5, 5, 1, 4]},
        #  Sounds good if u play it right after its root in the bass:
        {'name': 'neosoul alt dominant seventh chord', 'starting_scale_degree': 7, 'intervals': [6, 4, 4, 3]},
    ],
    'jazz-minor': [
        # The jazz minor is built on the melodic minor, except only the ascendant form is used.
        # TODO: Add code to support jazz minor.
        {'name': 'major-minor chord', 'starting_scale_degree': 1, 'intervals': [3, 4, 4] },
        # A nice 1950s detective TV show type voicing
        {'name': 'major-minor chord', 'starting_scale_degree': 1, 'intervals': [14, 1, 4, 4] }
    ],
    'diminished': [
        {'name': 'half-diminished 7th chord', 'starting_scale_degree': 1, 'intervals': [6, 4, 5]},
    ],
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
        ['I', 'V', 'vi', 'IV'], # The 'Axis of Awesome' progression.
        ['ii', 'V', 'I'], # Jazz =)
    ],
    'minor': [
        
    ]
}