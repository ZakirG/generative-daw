import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
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
        console.log(urlEndpoint);

        var postData = JSON.stringify(dawState);
        console.log(postData);

        const httpOptions = {
            headers: new HttpHeaders({
            'Content-Type':  'application/json',
            'Authorization': ''
            })
        };

        console.log('posting');

        return this.http.post(urlEndpoint, postData, httpOptions);
    }
}
