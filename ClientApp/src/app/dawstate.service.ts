import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpHeaders } from '@angular/common/http';
import { ConfigDataService } from './configdata.service';

@Injectable({
    providedIn: 'root',
})
export class DawStateService {

    constructor(private http: HttpClient, public configDataService: ConfigDataService) { }

    serverURL = this.configDataService.serverURL;
    dawStateURL = this.serverURL + 'daw-state'
    midiFileGenerationURL = this.serverURL + 'sequence-to-midi';
    midiToSequenceURL = this.serverURL + 'midi-to-sequence';

    updateDawState(dawState) {
        var urlEndpoint = this.dawStateURL;
        var postData = JSON.stringify(dawState);

        console.log('daw state chord names: ', dawState['chord_names']);

        const httpOptions = {
            headers: new HttpHeaders({
            'Content-Type':  'application/json',
            'Authorization': ''
            })
        };

        return this.http.post(urlEndpoint, postData, httpOptions);
    }

    exportToMidi(dawState) {
        return this.http.post(this.midiFileGenerationURL, dawState, {responseType: 'blob'});
    }

    midiToSequence(formData) {
        return this.http.post(this.midiToSequenceURL, formData, {responseType: 'json'});
    }
}
