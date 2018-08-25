import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
    providedIn: 'root',
})
export class GenerationService {

    constructor(private http: HttpClient) { }

    melodyGenerationURL = '/generate/melody';
    chordsGenerationURL = '/generate/chords';

    getMelody() {
        console.log('inside melody generator');
        return this.http.get(this.melodyGenerationURL);
    }

    getChords() {
        console.log('inside chords generator');
        return this.http.get(this.chordsGenerationURL);
    }

}
