import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class ConfigDataService {
    inPlayState : boolean;
    timeStateLength : number;
    tempo : number;
    key : string;
    scale : any;
    dawState : any;
    stateWidth: string;

    scales = [
            {'name' : 'major', 'intervals' : [2,2,1,2,2,2,1 ], 'code' : 'maj' },
            {'name' : 'minor', 'intervals' : [2,1,1,2,2,1,2 ], 'code' : 'min' },
            {'name' : 'maj (b2 b6)', 'intervals' : [1,3,1,2,1,3,1 ], 'code' : 'dhmaj' },
        ];

    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

    constructor() {
        this.scale = this.scales[2];
        this.key = this.keys[2];
        this.tempo = 100;
        this.inPlayState = false;
        this.timeStateLength = 8;
        this.dawState = {};
        this.stateWidth = (100 / this.timeStateLength)  + '%';
        this.dawState.chord_names = [[]];
    }

}

