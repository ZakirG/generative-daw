# Populated during the lifecycle of the app
chord_name_caches = {}

chord_charts = {
    'maj': ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii\xB0'],
    'min': ['i', 'ii\xB0', 'III', 'iv', 'v', 'VI', 'VII' ],
    'majpent': ['I', 'ii', 'iii', 'V', 'vi' ],
    'minpent': ['i', 'III', 'iv', 'v', 'VII' ],
    'dhmaj': ['I', 'II', 'iii', 'iv', 'V-flat-5'] # TODO: fill this in
}

roman_lower = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii']
roman_upper = list(map(lambda x: x.upper(), roman_lower))
roman_dim = list(map(lambda x: x + '\xB0', roman_lower))
roman_aug = list(map(lambda x: x + '+', roman_upper))
roman_flat_5 = list(map(lambda x: x + '-flat-5', roman_upper))
all_roman = roman_lower + roman_upper + roman_dim + roman_aug + roman_flat_5

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
Fill this dictionary with chord voicings that you find to be tasteful.

starting_scale_degree: 
    This is the lowest note in the chord, referenced by that note's position in the mode of the root.
    So for a C major chord, a starting scale degree = 7 would mean the lowest note is B, 
    even if we're playing in the global key of E.
roman_numerals: 
    An array of numerals this voicing is good for. A major second inversion voicing, for example, will be useful if you
    need a I voicing in a major scale, or a IV voicing in a minor scale, so those numerals will be present in the array.
    A minor power chord voicing, for example, applies to the iii situation for a major tonic, but also the i situation for a minor tonic.
"""
good_voicings = {
    'major': [
        {'name': 'major first inversion', 'starting_scale_degree': 3, 'intervals': [3, 5]},
        {'name': 'major second inversion', 'starting_scale_degree': 5, 'intervals': [5, 4]},
        {'name': 'maj 7 (three note voicing)', 'starting_scale_degree': 1, 'intervals': [4, 7]},
        {'name': 'maj 7 (four note voicing)', 'starting_scale_degree': 1, 'intervals': [11, 5, 3]},
        {'name': 'maj 7 (Bill Evans voicing)', 'starting_scale_degree': 7, 'intervals': [1, 4, 8]},
        {'name': 'maj 9 (four note voicing)', 'starting_scale_degree': 1, 'intervals': [11, 3, 2]},
        {'name': 'add 9', 'starting_scale_degree': 1, 'intervals': [4, 3, 7]},
        {'name': 'add 9 (Robert Glasper dirty chord)', 'starting_scale_degree': 1, 'intervals': [2, 2, 3, 5]},
        {'name': 'maj 7/9 (no5)', 'starting_scale_degree': 1, 'intervals': [4, 7, 3]},
        {'name': 'maj 7 (drop 2 voicing)', 'starting_scale_degree': 5, 'intervals': [5, 4, 7]},
        {'name': 'maj 7 (2 drop 2 voicing)', 'starting_scale_degree': 3, 'intervals': [7, 1, 7]},
        {'name': '6 (open voicing)', 'starting_scale_degree': 1, 'intervals': [7, 9, 5]},
        {'name': '6 (doubled root)', 'starting_scale_degree': 1, 'intervals': [4, 3, 2, 3]},
        # A very lovely voicing.
        {'name': 'maj 9 (Bill Evans voicing)', 'starting_scale_degree': 5, 'intervals': [4, 1, 4, 10]},
        {'name': 'major 6/9 (four note voicing)', 'starting_scale_degree': 1, 'intervals': [4, 5, 5]},
        # This chord lacks the root entirely. But it sounds great. From the Jazz Piano Book
        {'name': 'major 6/9 (left hand voicing)', 'starting_scale_degree': 7, 'intervals': [3, 2, 5]},
        {'name': 'major 6/9 (fifth on top)', 'starting_scale_degree': 1, 'intervals': [4, 5, 5, 5]},
        {'name': 'major 6/9 (doubled fifth)', 'starting_scale_degree': 1, 'intervals': [4, 3, 2, 5, 5]},
        # Taken from Jazz Piano Book's rendition of Infant Eyes
        {'name': 'major 6/9 (five note voicing)', 'starting_scale_degree': 1, 'intervals': [7, 9, 5, 5]},
        # This below chord is enharmonic with minor 7/11 So What built on the root that is 4 semitones above this starting scale degree 
        {'name': 'major 6/9 (So What voicing)', 'starting_scale_degree': 3, 'intervals': [5, 5, 5, 4]},
        {'name': 'major 6/9 (Bud Powell Fourth Chord)', 'starting_scale_degree': 3, 'intervals': [5, 5, 5, 5]},
        # Source: https://www.youtube.com/watch?v=FdlyUU5M2dI&ab_channel=PrettySimpleMusic at 9:03
        {'name': 'major 6/9 (Robert Glasper dirty chord)', 'starting_scale_degree': 5, 'intervals': [2, 3, 2, 2, 5]},
        # Source: https://www.youtube.com/watch?v=FdlyUU5M2dI&ab_channel=PrettySimpleMusic at 9:05
        {'name': "major add 11 (Robert Glasper dirty chord)", 'starting_scale_degree': 1, 'intervals': [4, 1, 2, 5]},
        # Source: https://www.youtube.com/watch?v=FdlyUU5M2dI&ab_channel=PrettySimpleMusic at 9:08
        {'name': "major 6/11 (Robert Glasper dirty chord)", 'starting_scale_degree': 7, 'intervals': [1, 2, 2, 3, 4]},
        {'name': "major 6/11 (Robert Glasper dirty chord)", 'starting_scale_degree': 7, 'intervals': [1, 2, 2, 3, 5]},
        # Source: https://www.youtube.com/watch?v=owi7EmvoGsk&ab_channel=PianoLessonwithWarren
        {'name': 'gospel major 6/9/11', 'starting_scale_degree': 1, 'intervals': [7, 5, 2, 2, 1, 4]},
        # So pretty. Neo-soul major 7/9 
        {'name': 'maj7/9 (neosoul voicing #1)', 'starting_scale_degree': 1, 'intervals': [7, 7, 2, 3, 4]},
        {'name': 'maj7/9 (neosoul voicing #2)', 'starting_scale_degree': 1, 'intervals': [7, 3, 4, 1, 4]},
        {'name': 'maj 7/9', 'starting_scale_degree': 1, 'intervals': [4, 3, 4, 3, 4]},
        {'name': 'maj 7/9 (open voicing)', 'starting_scale_degree': 1, 'intervals': [7, 7, 2, 7, 5]},
        # Source: https://www.youtube.com/watch?v=FdlyUU5M2dI&ab_channel=PrettySimpleMusic at 9:08
        {'name': "maj 7/9 (Robert Glasper dirty chord)", 'starting_scale_degree': 1, 'intervals': [2, 2, 3, 4]},
        {'name': 'gospel maj9', 'starting_scale_degree': 1, 'intervals': [7, 5, 2, 2, 3]},
        # Sounds good with the top rolled on:
        # {'name': 'neosoul maj7/9/#11', 'starting_scale_degree': 7, 'intervals': [1,4,3,4,3,4]},
        {'name': 'gospel maj13', 'starting_scale_degree': 1, 'intervals': [10, 6, 3, 2, 3]},
        # Source: https://www.youtube.com/watch?v=KhpPqV6j59Y&ab_channel=8-bitMusicTheory
        {'name': 'maj7/13 (Halo 3 ODST Voicing)', 'starting_scale_degree': 1, 'intervals': [7, 2, 7, 7]},
        {'name': 'maj7/13', 'starting_scale_degree': 1, 'intervals': [4, 3, 2, 2]},

        {'name': 'maj 7/b5', 'starting_scale_degree': '5b', 'intervals': [5,1,4]},
    ],
    'minor': [
        {'name': 'minor (Lil Tecca - Ransom voicing)', 'starting_scale_degree': 5, 'intervals': [5, 3, 4]},
        {'name': 'minor (add root on top)', 'starting_scale_degree': 1, 'intervals': [3, 4, 5]},
        {'name': 'min 7 (three note voicing)', 'starting_scale_degree': 1, 'intervals': [3, 7]},
        {'name': 'min 7 (four note voicing)', 'starting_scale_degree': 1, 'intervals': [10, 5, 4]},
        {'name': 'min 7 (open voicing)', 'starting_scale_degree': 1, 'intervals': [7, 8, 7]},
        {'name': 'min 7 (open voicing #2)', 'starting_scale_degree': 1, 'intervals': [10, 5, 7]},
        # The root isn't even in the below chord! But it sounds good. Taken from Jazz Piano Book.
        {'name': 'min 7 (left hand voicing)', 'starting_scale_degree': 3, 'intervals': [4, 3, 4]},

        {'name': 'minor add 9', 'starting_scale_degree': 1, 'intervals': [3, 4, 7]},
        {'name': "minor add 11 (Dua Lipa - Don't Start Now voicing)", 'starting_scale_degree': 1, 'intervals': [3, 4, 10]},
        {'name': 'minor add 11 (Robert Glasper dirty chord)', 'starting_scale_degree': 1, 'intervals': [3, 2, 2, 5]},
        {'name': 'minor (power chord voicing)', 'starting_scale_degree': 1, 'intervals': [7, 5, 3, 4]},
        {'name': 'gospel minor 7/9', 'starting_scale_degree': 1, 'intervals': [3, 4, 3, 4, 1, 4]},
        # Source: https://www.youtube.com/watch?v=zuHtyBNNngU&ab_channel=JeffSchneider
        {'name': 'neosoul minor 7/9', 'starting_scale_degree': 1, 'intervals': [10, 4, 1, 4]},
        {'name': 'minor 7/9/11', 'starting_scale_degree': 1, 'intervals': [5, 9, 1, 7]},
        # Source: https://www.youtube.com/watch?v=FdlyUU5M2dI&ab_channel=PrettySimpleMusic at 9:09
        {'name': 'minor 7/9/11 (Robert Glasper dirty chord)', 'starting_scale_degree': 1, 'intervals': [2, 1, 2, 2, 3, 4]},
        {'name': 'minor 7/9/11 (Robert Glasper dirty chord)', 'starting_scale_degree': 1, 'intervals': [2, 1, 2, 2, 3]},

        {'name': 'minor 7/11', 'starting_scale_degree': 1, 'intervals': [3, 4, 3, 7]},
        {'name': 'minor 7/11 (close voicing)', 'starting_scale_degree': 1, 'intervals': [3, 2, 2, 3]},
        {'name': 'minor 9/11 (close voicing)', 'starting_scale_degree': 1, 'intervals': [3, 2, 2, 3, 4, 5]},
        {'name': 'minor 7/11 (four note voicing)', 'starting_scale_degree': 1, 'intervals': [10, 5, 2]},
        # This below chord is enharmonic with major 6/9 So What built on the root that is 4 semitones below this starting scale degree 
        {'name': 'minor 7/11 (So What voicing)', 'starting_scale_degree': 1, 'intervals': [5, 5, 5, 4]},
        {'name': 'neosoul minor 7/9/11', 'starting_scale_degree': 1, 'intervals': [7, 7, 1, 2, 5]},
        {'name': 'minor 7/b5', 'starting_scale_degree': 1, 'intervals': [3, 7, 8]},

        # From the Jazz Piano Book. The sixth is sometimes played in place of the seventh in minor ii chords.
        # Minor sixth chords are preferably used as minor tonic i's rather than ii's.
        {'name': 'minor 6 (four note voicing)', 'starting_scale_degree': 1, 'intervals': [10, 5, 5]},
        {'name': 'minor 6', 'starting_scale_degree': 1, 'intervals': [3, 4, 2]},
        {'name': 'gospel minor 7/9/11', 'starting_scale_degree': 1, 'intervals': [3, 4, 3, 9, 3, 4, 3]},
        # Source: https://www.youtube.com/watch?v=FdlyUU5M2dI&ab_channel=PrettySimpleMusic 9:06
        {'name': 'min 7/b13 (Robert Glasper dirty chord)', 'starting_scale_degree': 1, 'intervals': [3, 4, 1, 2, 5]},

        # Source: https://www.youtube.com/watch?v=fk9r8sVGb74&ab_channel=AlainMerville at 1:31
        {'name': 'minor 7/9/11 (Jesús Molina 10-note voicing)', 'starting_scale_degree': 1, 'intervals': [7, 3, 4, 1, 2, 2, 3, 4, 3]},
        # Source: https://www.youtube.com/watch?v=FdlyUU5M2dI&ab_channel=PrettySimpleMusic at 6:13
        {'name': 'minor 7/9/11 (10 note voicing)', 'starting_scale_degree': 1, 'intervals': [7, 7, 1, 2, 2, 3, 2, 2, 3]},
    ],
    'dominant-7': [
        {'name': '7sus4', 'starting_scale_degree': 1, 'intervals': [5, 5]},
        {'name': 'dominant 7', 'starting_scale_degree': 1, 'intervals': [4, 3, 3]},
        {'name': 'dominant 7 (three note voicing)', 'starting_scale_degree': 1, 'intervals': [10, 6]},
        {'name': 'dominant 7/9 (four note voicing)', 'starting_scale_degree': 1, 'intervals': [14, 2, 6]},
        {'name': 'dominant 7 (open voicing)', 'starting_scale_degree': 1, 'intervals': [7, 3, 6]},
    # A little too spicy
        {'name': 'dominant 7/#9 (four note voicing)', 'starting_scale_degree': 1, 'intervals': [4, 6, 5]},
        {'name': 'dominant 7 alt (left hand voicing)', 'starting_scale_degree': 1, 'intervals': [4, 2, 5]},
        {'name': 'dom7/9sus4 (no3 7/9)', 'starting_scale_degree': 1, 'intervals': [7, 3, 4, 3]},
        # Source: https://www.youtube.com/watch?v=FdlyUU5M2dI&ab_channel=PrettySimpleMusic at 9:05
        {'name': "dom7/9sus4 (Robert Glasper dirty chord)", 'starting_scale_degree': 1, 'intervals': [2, 3, 2, 3, 4]},
        # Source: https://www.youtube.com/watch?v=TUT3M3q5F_k&ab_channel=RWP at 0:07
        {'name': "dom7/9 (Kali Uchis - After the Storm voicing)", 'starting_scale_degree': 1, 'intervals': [2, 2, 3, 3, 4, 2, 3]},
        {'name': '7sus4 (no3 7/9/11)', 'starting_scale_degree': 1, 'intervals': [10, 4, 3]},
        {'name': '7sus4 (no3 7/9/11/13)', 'starting_scale_degree': 1, 'intervals': [10, 4, 3, 4]},
        # Source: https://www.youtube.com/watch?v=C90JiwuIPS8&ab_channel=MangoldProject
        {'name': 'dominant 7/9sus4 (the Big Sus voicing)', 'starting_scale_degree': 1, 'intervals': [7, 7, 3, 5, 4, 3]},
        {'name': 'dominant 7 (Lil Tecca - Ransom voicing)', 'starting_scale_degree': 1, 'intervals': [4, 3, 3, 2, 4]},
    # A little too spicy
        {'name': 'alt (aug dominant 7/#9)', 'starting_scale_degree': 1, 'intervals': [10, 5, 5, 1, 4]},
        #  Sounds good if u play it right after its root in the bass:
        {'name': 'neosoul alt dominant seventh chord', 'starting_scale_degree': 7, 'intervals': [6, 4, 4, 3]},
        {'name': 'dominant 7 (Bud Powell Fourth Chord over root)', 'starting_scale_degree': 7, 'intervals': [6, 5, 5, 5]},
        # Wow, so beautiful
        {'name': 'gospel dom 7/9/11', 'starting_scale_degree': 1, 'intervals': [7, 3, 4, 3, 5]},
        # This chord is very spicy. Beware.
        {'name': 'dominant 7/b9 (upper structure II)', 'starting_scale_degree': 3, 'intervals': [6, 5, 4, 3]},
        # Lovely. Source: https://www.youtube.com/watch?v=m0p-n0wgzV4&ab_channel=PrettySimpleMusic
        {'name': 'dominant 7/b9/13', 'starting_scale_degree': 1, 'intervals': [10, 11, 4, 3]},
        # Augmented chord
        {'name': 'aug dominant 7', 'starting_scale_degree': 1, 'intervals': [10, 6, 4] }
    ],
    'sus': [
        {'name': 'sus4', 'starting_scale_degree': 1, 'intervals': [5, 2]},
        {'name': 'sus2', 'starting_scale_degree': 1, 'intervals': [2, 5]},
        {'name': '6sus2 (no3 6/9)', 'starting_scale_degree': 1, 'intervals': [9, 5, 5]},
        {'name': '6sus2 (no3 6/9) (doubled fifth)', 'starting_scale_degree': 1, 'intervals': [7, 2, 5, 5]},
        
    ],
    'diminished': [
        {'name': 'half-diminished 7th chord', 'starting_scale_degree': 1, 'intervals': [6, 4, 5]},
    ],
    'lydian': [
        {'name': 'major 7/9/#11 (lydian chord)', 'starting_scale_degree': 7, 'intervals': [1, 4, 3, 4, 3, 4]},
    ],
    'jazz-minor': [
        # The jazz minor is built on the melodic minor, except only the ascendant form is used.
        # TODO: Add code to support jazz minor.
        {'name': 'major-minor chord', 'starting_scale_degree': 1, 'intervals': [3, 4, 4] },
        # A nice 1950s detective TV show type voicing
        {'name': 'major-minor chord', 'starting_scale_degree': 1, 'intervals': [14, 1, 4, 4] }
    ],
}

# Some sources:
# >> https://mixedinkey.com/captain-plugins/wiki/best-chord-progressions/
# >> https://www.libertyparkmusic.com/common-chord-progressions/
good_chord_progressions = {
    'maj': [
        { 'roman_numerals': ['I', 'IV', 'V'], 'name': ''},
        # { 'roman_numerals': ['I', 'V6', 'vi', 'V'], 'name': ''},
        { 'roman_numerals': ['I', 'V', 'vi', 'iii', 'IV'], 'name': ''},
        { 'roman_numerals': ['I', 'vi', 'IV', 'V'], 'name': 'The 50s progression'},
        { 'roman_numerals': ['I', 'IV', 'V', 'vi'], 'name': ''},
        { 'roman_numerals': ['I', 'IV', 'vi', 'V'], 'name': ''},
        # { 'roman_numerals': ['IV', 'I6', 'ii'], 'name': ''},
        { 'roman_numerals': ['vi', 'V', 'IV', 'V'], 'name': ''},
        { 'roman_numerals': ['vi', 'IV', 'I', 'V'], 'name': ''},
        { 'roman_numerals': ['vi', 'V', 'I', 'IV'], 'name': ''},
        { 'roman_numerals': ['vi', 'I', 'V', 'IV'], 'name': ''},
        { 'roman_numerals': ['I', 'V', 'vi', 'IV'], 'name': 'The Axis of Awesome overused pop progression.'},
        { 'roman_numerals': ['ii', 'V', 'I'], 'name': ''},
        { 'roman_numerals': ['iii', 'IV', 'iii', 'vi'], 'name': ''},
        { 'roman_numerals': ['iii', 'IV'], 'name': 'PND - Come and See Me progression'}
    ],
    'min': [
        { 'roman_numerals': ['i', 'iv', 'v'], 'name': 'The Weeknd - Often progression'}, # Example:
        # { 'roman_numerals': ['i', 'ii\xB0', 'V', 'i'], 'name': ''}, # Contains borrowed chord
        { 'roman_numerals': ['i', 'VI', 'III', 'VII'], 'name': ''},
        { 'roman_numerals': ['i', 'iv', 'V'], 'name': ''}, # Contains borrowed chord
        { 'roman_numerals': ['iv', 'v', 'i'], 'name': ''},
        { 'roman_numerals': ['i', 'iv', 'iv', 'i'], 'name': 'Bandkidjay - Bleu Chanel progression'},
        { 'roman_numerals': ['VI', 'i', 'i', 'i'], 'name': 'Nav - Myself progression'},
        # { 'roman_numerals': ['i', 'VI', 'i', 'V7'], 'name': 'Lil Tecca - Ransom progression'},
        { 'roman_numerals': [ 'i' , 'III', 'v'], 'name': '88Glam - On Sight progression'},
        { 'roman_numerals': [ 'iv', 'i', 'iv', 'VII'], 'name': 'J Balvin - Solitario progression'},
    ],
    'dhmaj': []
}