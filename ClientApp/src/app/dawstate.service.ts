import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpHeaders } from '@angular/common/http';

@Injectable({
    providedIn: 'root',
})
export class DawStateService {

    constructor(private http: HttpClient) { }

    serverURL = 'http://localhost:5000/'
    dawStateURL = this.serverURL + 'daw-state'

    updateDawState(dawState) {
        var urlEndpoint = this.dawStateURL;
        var postData = JSON.stringify(dawState);

        const httpOptions = {
            headers: new HttpHeaders({
            'Content-Type':  'application/json',
            'Authorization': ''
            })
        };

        return this.http.post(urlEndpoint, postData, httpOptions);
    }
}
