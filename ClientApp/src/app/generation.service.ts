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

    melodyGenerationURL = this.serverURL + 'generate/melody';
    chordsGenerationURL = this.serverURL + 'generate/chords';
    midiFileGenerationURL = this.serverURL + 'midi';

    generate(generationOptions) {
        if (typeof generationOptions.scale != 'string') generationOptions.scale = generationOptions.scale.code;
        var URL_endpoint = (generationOptions.generationType == 'chords') ? this.chordsGenerationURL : this.melodyGenerationURL;
        generationOptions.length = this.configDataService.numBeatsInProject;
        return this.http.post(URL_endpoint, generationOptions);
    }

    exportToMidi(dawState) {
        return this.http.post(this.midiFileGenerationURL, dawState, {responseType: 'blob'});
    }
}
