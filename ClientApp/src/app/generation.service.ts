import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';

@Injectable({
    providedIn: 'root',
})
export class GenerationService {

    constructor(private http: HttpClient) { }

    serverURL = 'http://localhost:5000/'

    melodyGenerationURL = this.serverURL + 'generate/melody/random';
    chordsGenerationURL = this.serverURL + 'generate/chords/random';

    generate(generationOptions, length) {
        console.log(this.serverURL
            + 'generate/'
            + generationOptions.generationType + '/'
            + generationOptions.key + '/'
            + generationOptions.scale.code + '/'
            + 'random/'
            + length);

        return this.http.get(this.serverURL
            + 'generate/'
            + generationOptions.generationType + '/'
            // + generationOptions.key + '/'
            // + generationOptions.scale + '/'
            + 'random/'
            + length
        );
    }

}
