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

    constructor(private http: HttpClient) {
        this.serverURL = 'http://localhost:5000/'
        this.constantsURL = this.serverURL + 'constants';
        
        this.key = this.keys[0];
        this.scale = [];
        this.tempo = 100;
        this.inPlayState = false;
        this.timeStateLength = 8;
        this.dawState = {};
        this.stateWidth = (100 / this.timeStateLength)  + '%';
        this.dawState.chord_names = [[]];
        this.dawState.chord_degrees = [[]];
    }
}

