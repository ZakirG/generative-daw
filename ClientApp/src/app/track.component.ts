import { Component, Input, Output, EventEmitter } from '@angular/core';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ConfigDataService } from './configdata.service';
import { PianoRollComponent } from './piano-roll.component';

@Component({
    selector:    'track',
    templateUrl: './track.component.html',
    providers:  [ ],
    styleUrls: ['./track.component.css', './app.component.css', './form-styles.css']
})

export class TrackComponent {
    @Input() trackNumber: number;
    @Input() trackName: number;
    @Input() importedFileName: string;
    @Input() key: string;
    @Input() scale: Object;
    @Input() pianoRollOpen: boolean;
    @Input() sequence: any;
    @Input() notes: Array<any>;
    @Input() thisTrackIsSelected: boolean;
    
    _ref: any;

    @Output()
    noteDrawn = new EventEmitter<any>();

    @Output()
    trackChange = new EventEmitter<any>();


    constructor(public configDataService: ConfigDataService) { 
        this.sequence = [];
    }

    ngOnInit() { }

    toggleRegionSelected() {
        this.trackChange.emit({'event' : 'regionSelected', 'trackNumber' : this.trackNumber});
        this.thisTrackIsSelected = true;
    }

    deleteTrack() {
        this.trackChange.emit({'event' : 'deleteTrack', 'trackNumber' : this.trackNumber});
    }

    destroyReference() {
        this._ref.destroy();
    }
}
