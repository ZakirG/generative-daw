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
        var scale_code = (generationOptions.scale == 'any') ? 'any' : generationOptions.scale.code;
        var URL_endpoint = this.serverURL
            + 'generate/'
            + generationOptions.generationType + '/'
            + generationOptions.key + '/'
            + scale_code + '/'
            + generationOptions.octaveConstraint + '/'
            + 'random/'
            + length;

        console.log(URL_endpoint);

        return this.http.get(URL_endpoint);
    }

}
