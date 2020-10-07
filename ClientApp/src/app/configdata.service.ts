import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class ConfigDataService {
    inPlayState : boolean;
    numBeatsInProject : number;
    numSubdivisionsPerBeat : number;
    numDivisions : number;
    viewStateLength: number;
    constants: any;
    tempo : number;
    key : string;
    scales: any;
    scale : any;
    dawState : any;
    stateWidth: string;
    serverURL: string;
    constantsURL: string;
    notes: any;
    playOffsetPerNoteDueToRoll : number;
    toplineContour : any;
    toplineContours : any;
    logSeparator = '----------';
    appLogs = ['Welcome to GenerativeDAW =)', this.logSeparator];
    
    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

    constructor(private http: HttpClient) {
        this.serverURL = 'http://localhost:5000/'
        this.constantsURL = this.serverURL + 'constants';
        
        this.key = this.keys[0];
        this.scale = [];
        this.toplineContours = [
          {'name': 'no preference', 'code': 'any'},
          {'name': 'static', 'code': 'static'},
          {'name': 'anything but static', 'code': 'nonstatic'},
          {'name': 'upward', 'code': 'up'},
          {'name': 'downward', 'code': 'down'},
          {'name': 'up and then down', 'code': 'updown'},
          {'name': 'down and then up', 'code': 'downup'}
        ];
        this.toplineContour = this.toplineContours[0];
        this.tempo = 60;
        this.inPlayState = false;
        this.numBeatsInProject = 8;
        this.numSubdivisionsPerBeat = 8;
        this.numDivisions = this.numBeatsInProject * this.numSubdivisionsPerBeat;
        this.dawState = {};
        this.stateWidth = (100 / this.numDivisions)  + '%';
        this.dawState.chord_names = [[]];
        this.dawState.chord_degrees = [[]];
        this.playOffsetPerNoteDueToRoll = 0.01;

        var noteColors = [
          {'color' : 'white', 'note' : 'b' },
          {'color' : 'black', 'note' : 'as' },
          {'color' : 'white', 'note' : 'a' },
          {'color' : 'black', 'note' : 'gs' },
          {'color' : 'white', 'note' : 'g' },
          {'color' : 'black', 'note' : 'fs' },
          {'color' : 'white', 'note' : 'f' },
          {'color' : 'white', 'note' : 'e' },
          {'color' : 'black', 'note' : 'ds'},
          {'color' : 'white', 'note' : 'd' },
          {'color' : 'black', 'note' : 'cs' },
          {'color' : 'white', 'note' : 'c' },
      ]

      this.notes = [];
      for(let octaveIndex = 5; octaveIndex > 1; octaveIndex -= 1) {
          let octaveArray = noteColors.map(x => Object.assign({}, x));
          octaveArray = octaveArray.map(x => ({ ...x, 'octave': octaveIndex}));
          this.notes = this.notes.concat(octaveArray);
      }
    }

    initializeEmptyGridState() {
      var emptyTimeState = this.makeEmptyTimeState();

      let gridState = [];
      for (let note of this.notes) {
          var noteRow = {
              'color' : note.color,
              'octave' : note.octave,
              'note' : note.note,
              'timeStates' : emptyTimeState.slice(),
              'stateWidth' : this.stateWidth,
              'id' : note.note + note.octave
          };
          gridState.push(noteRow);
      }
      return gridState;
  }

  makeEmptyTimeState() {
    return Array.apply(null, Array(this.numDivisions)).map(Number.prototype.valueOf,0);
  }

  convertNoteListToSequence(noteList) {
    var sequence = [];
    for(let timeStateIndex = 0; timeStateIndex < noteList.length; timeStateIndex+=1) {
      for(let noteIndex = 0; noteIndex < noteList[timeStateIndex].length; noteIndex+=1) {
          let sustainTime = 4; // for now, all notes are equal time
          let noteNumeral = noteList[timeStateIndex][noteIndex]['numeral'] + 24;
          sequence.push({
              t: timeStateIndex * sustainTime,
              n: noteNumeral,
              g: sustainTime,
              v : 0,
              f: 0,
              note: noteList[timeStateIndex][noteIndex]['note'],
              octave: noteList[timeStateIndex][noteIndex]['octave'],
          });
      }
    }
    return sequence;
  }

  note_to_numeral(noteName, noteOctave) {
    // Convert to MIDI numeral
    // Paraphrased from https://github.com/danilobellini/audiolazy/blob/master/audiolazy/lazy_midi.py
    var letter = noteName.trim().toUpperCase();
    
    if (noteName.length == 2) {
        letter = noteName.trim().replace('s','#');
        letter = letter[0].ToUpperCase() + letter.slice(1);
    }
    
    var noteString = letter + noteOctave;
    if (noteString == "?") {
      return NaN;
    }
    
    let data = noteString.trim().toLowerCase();
    let name2delta = {"c": -9, "d": -7, "e": -5, "f": -4, "g": -2, "a": 0, "b": 2};
    let accident2delta = {"b": -1, "#": 1, "x": 2};
    
    let accidents = [];
    if (data.slice(-1) == "b" || data.slice(-1) == "#") {
      accidents.push(accident2delta[data.slice(-1)]);
    }
    let octave_delta = parseInt(data.slice(accidents.length + 1)) - 4;

    const reducer = (accumulator, currentValue) => accumulator + currentValue;
  	let arr = accidents.map((ac) => accident2delta[ac]);
    var MIDI_A4 = 69
    return (MIDI_A4 + name2delta[data[0]] + arr.reduce(reducer, 0) + 
      12 * octave_delta);
  }

  numeral_to_note(midiNumeral) {
    // Given a MIDI pitch number, returns its note string name (e.g. "C3").
    // Paraphrased from https://github.com/danilobellini/audiolazy/blob/master/audiolazy/lazy_midi.py
    
    var MIDI_A4 = 69
    let num = midiNumeral - (MIDI_A4 - 4 * 12 - 9)
    let note = (num + .5) % 12 - .5
    let rnote = Math.round(note)
    let error = note - rnote
    let octave = Math.round((num - note) / 12.).toString();
    var namesArr = ["c", "cs", "d", "ds", "e", "f", "fs", "g", "gs", "a", "as", "b"]
    var names = namesArr[rnote] + octave
    
    return names;
  }
}

