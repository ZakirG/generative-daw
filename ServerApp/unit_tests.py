import music_theory
import pytest

# Run with pytest unit_tests.py

def test_chord_to_topline_int():
    tt = music_theory.chord_to_topline_int
    
    chord = [{'note': 'g', 'octave': 3},{'note': 'c', 'octave': 4}, {'note': 'g', 'octave': 4}]
    result = tt(chord)
    assert result == 67    

def test_topline_note_passes_topline_distance_constraint():
    tt =  music_theory.topline_note_passes_topline_distance_constraint
    result = tt(75, 70, 3)
    assert result is False
    
    result = tt({'note': 'ds', 'octave': 5}, 70, 3)
    assert result is False
    
    result = tt(75, 70, 7)
    assert result is True

    result = tt({'note': 'ds', 'octave': 5}, 70, 7)
    assert result is True

def test_non_topline_note_passes_topline_distance_constraint():
    tt =  music_theory.non_topline_note_passes_topline_distance_constraint
    result = tt(75, 70, 3)
    assert result is False
    
    result = tt({'note': 'ds', 'octave': 5}, 70, 3)
    assert result is False
    
    result = tt(60, 70, 2)
    assert result is True
    
def test_topline_note_passes_topline_constraints():
    # topline_note_passes_topline_constraints(self.get_current_topline_direction(), voicing['roman_numerals_to_topline_positions'][chosen_target_degree], previous_chord_topline_position, self.max_topline_distance)
    tt = music_theory.topline_note_passes_topline_constraints

    result = tt("up", 73, 71, 3)
    assert result is True
    
    result = tt("up", {'note': 'cs', 'octave': 5}, 71, 3)
    assert result is True

    result = tt("up", {'note': 'cs', 'octave': 5}, 71, 1)
    assert result is False

    result = tt("down", 73, 71, 3)
    assert result is False

    result = tt("down", 60, 80, 3)
    assert result is False

    result = tt("equal", 73, 71, 3)
    assert result is False

    result = tt("unequal", {'note': 'cs', 'octave': 5}, 71, 3)
    assert result is True

    result = tt("unequal", 71, 71, 3)
    assert result is False

    result = tt("equal", 73, 73, 3)
    assert result is True

    
def test_non_topline_note_meets_topline_constraints():
    tt = music_theory.non_topline_note_meets_topline_constraints

    result = tt("up", 73, 71, 3)
    assert result is True

    result = tt("up", 60, 71, 3)
    assert result is True
    
    result = tt("down", 73, 71, 3)
    assert result is False

    result = tt("unequal", 71, 71, 3)
    assert result is True
    
def test_chord_passes_topline_contour_constraint():
    # return chord_passes_topline_contour_constraint(self.get_current_topline_direction(), music_theory.chord_to_topline_int(candidate_chord), music_theory.chord_to_topline_int(previous_chord))
    tt = music_theory.chord_passes_topline_contour_constraint
    
    result = tt("up", 80, 75)
    assert result is True

    result = tt("up", 70, 75)
    assert result is False

    result = tt("equal", 76, 75)
    assert result is False

    result = tt("equal", 75, 75)
    assert result is True

    result = tt("unequal", 75, 75)
    assert result is False

    result = tt("unequal", 76, 75)
    assert result is True

    previous_chord = [{'note': 'f', 'octave': 3}, {'note': 'a', 'octave': 3}, {'note': 'c', 'octave': 4}, {'note': 'e', 'octave': 4}, {'note': 'g', 'octave': 4}, {'note': 'b', 'octave': 4}]
    candidate_chord = [{'note': 'b', 'octave': 3}, {'note': 'd', 'octave': 3}, {'note': 'e', 'octave': 4}, {'note': 'b', 'octave': 4}]
    result = tt("equal", music_theory.chord_to_topline_int(candidate_chord), music_theory.chord_to_topline_int(previous_chord))