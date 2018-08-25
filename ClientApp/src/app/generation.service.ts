import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';

@Injectable({
    providedIn: 'root',
})
export class GenerationService {

    constructor(private http: HttpClient) { }

    serverURL = 'http://localhost:5000/'

    melodyGenerationURL = this.serverURL + 'generate/melody';
    chordsGenerationURL = this.serverURL + 'generate/chords';

    getMelody() : Observable<[]> {
        console.log('inside melody generator');
        return this.http.get(this.melodyGenerationURL);
    }

    getChords() {
        console.log('inside chords generator');
        return this.http.get(this.chordsGenerationURL);
    }

}
