import { Injectable } from '@angular/core';

@Injectable({
    providedIn: 'root',
})
export class GenerationService {

    constructor() { }

    getNotes() {
        return [2];
    }

}
