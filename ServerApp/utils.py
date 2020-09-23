import random

def roman_to_int(s):
    """
    :type s: str
    :rtype: int
    """
    roman = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000,'IV':4,'IX':9,'XL':40,'XC':90,'CD':400,'CM':900}
    i = 0
    num = 0
    while i < len(s):
        if i+1<len(s) and s[i:i+2] in roman:
            num+=roman[s[i:i+2]]
            i+=2
        else:
            num+=roman[s[i]]
            i+=1
    return num

def decide_will_event_occur(probability_of_event_happening):
    # Weighted coin toss
    # Returns True or False 
    outcomes = [True, False]
    weights = [probability_of_event_happening, 1 - probability_of_event_happening]
    result = random.choices(outcomes, weights, k=1000)
    return result[0]

def flatten_note_set(note_set):
    # Transform from [{'note': 'b', 'octave': 3}, {'note': 'd', 'octave': 3}, {'note': 'e', 'octave': 3}]
    # to ['b3', 'd3', 'e3']
    return [x['note'] + str(x['octave']) for x in note_set]

def pick_n_random_notes(allowed_notes_in, n):
    allowed_notes = allowed_notes_in.copy()
    note_set = []
    for j in range(n):
        random_index = random.choice(range(len(allowed_notes)))
        note_set.append(allowed_notes[random_index])
        allowed_notes.pop(random_index)
    return note_set

def pretty_print_progression(progression):
    rv = ''
    for numeral in progression:
        rv += numeral
        rv += ', '
    
    return rv[:-2]

