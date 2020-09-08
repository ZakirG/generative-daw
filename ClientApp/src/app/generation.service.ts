import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { ConfigDataService } from './configdata.service';

@Injectable({
    providedIn: 'root',
})
export class GenerationService {

    constructor(private http: HttpClient, public configDataService: ConfigDataService) { }

    serverURL = this.configDataService.serverURL;

    melodyGenerationURL = this.serverURL + 'generate/melody/random';
    chordsGenerationURL = this.serverURL + 'generate/chords/random';
    midiFileGenerationURL = this.serverURL + 'midi';

    generate(generationOptions, length) {
        var scale_code = (generationOptions.scale == 'any') ? 'any' : generationOptions.scale.code;
        var URL_endpoint = encodeURI(this.serverURL
            + 'generate/'
            + generationOptions.generationType + '/'
            + generationOptions.key + '/'
            + scale_code + '/'
            + generationOptions.octaveConstraint + '/'
            + 'random/'
            + length);

        return this.http.get(URL_endpoint);
    }

    exportToMidi(dawState) {
        return this.http.post(this.midiFileGenerationURL, dawState, {responseType: 'blob'});
    }
}
