import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class ConfigDataService {
    inPlayState : boolean;
    timeStateLength : number;
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
        this.timeStateLength = 4;
        this.viewStateLength = 8
        this.dawState = {};
        this.stateWidth = (100 / this.viewStateLength)  + '%';
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
}

