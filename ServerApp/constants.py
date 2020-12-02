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
        'maj' : {'name' : 'major', 'intervals' : [2,2,1,2,2,2,1], 'code' : 'maj' },
        'min' : {'name' : 'minor', 'intervals' : [2,1,2,2,1,2,2], 'code' : 'min' },
        'dhmaj' : {'name' : 'double harmonic maj', 'intervals' : [1,3,1,2,1,3,1], 'code' : 'dhmaj' },
        'majpent' : {'name' : 'major pentatonic', 'intervals' : [2,2,3,2,3], 'code' : 'majpent', 'parent_scale': 'maj' },
        'minpent' : {'name' : 'minor pentatonic', 'intervals' : [3,2,2,3,2], 'code' : 'minpent', 'parent_scale': 'min' },
        'bebopmaj' : {'name' : 'bebop major scale', 'intervals' : [2,2,1,2,1,1,2,1], 'code' : 'bebopmaj', 'contains_scale': 'maj'},
        'bebopmin' : {'name' : 'bebop minor scale', 'intervals' : [2,1,2,2,1,2,1,1], 'code' : 'bebopmin', 'contains_scale': 'min'},
        'bebopdom' : {'name' : 'bebop dominant scale', 'intervals' : [2,2,1,2,2,1,1,1], 'code' : 'bebopdom', 'contains_scale': 'maj' },
    },
    'roman_numerals_upper': ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
}