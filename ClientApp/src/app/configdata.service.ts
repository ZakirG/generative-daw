import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class ConfigDataService {
    inPlayState : boolean;
    timeStateLength : number;
    constants: any;
    tempo : number;
    key : string;
    scales: any;
    scale : any;
    dawState : any;
    stateWidth: string;
    serverURL: string;
    constantsURL: string;
    
    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

    scales = [
        {'name' : 'major', 'intervals' : [2,2,1,2,2,2,1 ], 'code' : 'maj' },
        {'name' : 'minor', 'intervals' : [2,1,1,2,2,1,2 ], 'code' : 'min' },
        {'name' : 'maj (b2 b6)', 'intervals' : [1,3,1,2,1,3,1 ], 'code' : 'dhmaj' },
    ];

    getConstants() {
        this.http.get(this.constantsURL).subscribe((data) => {
            this.constants = data;
            this.scales = Object.values(this.constants.scales);
            this.scale = this.scales[0];
        });
    }

    constructor(private http: HttpClient) {
        // this.scales = [];
        //this.scale = {'name' : 'major', 'intervals' : [2,2,1,2,2,2,1 ], 'code' : 'maj' };
        this.scale = this.scales[0];
        this.serverURL = 'http://localhost:5000/'
        this.constantsURL = this.serverURL + 'constants';

        this.getConstants();
        
        this.key = this.keys[0];
        this.tempo = 100;
        this.inPlayState = false;
        this.timeStateLength = 8;
        this.dawState = {};
        this.stateWidth = (100 / this.timeStateLength)  + '%';
        this.dawState.chord_names = [[]];
    }
}

