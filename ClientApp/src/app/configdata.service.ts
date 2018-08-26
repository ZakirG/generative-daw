import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class ConfigDataService {
    public key ='C';
    data : string;
    scale : string = 'C';
    conformToKeyScale : boolean = true;

    getKey() : string {
        return this.key;
    }

    getScale() : string {
        return this.scale;
    }

    constructor() { }

}

