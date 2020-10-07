import { Component, Input, Output, EventEmitter } from '@angular/core';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ConfigDataService } from './configdata.service';
import { PianoRollComponent } from './piano-roll.component';

@Component({
    selector:    'track',
    templateUrl: './track.component.html',
    providers:  [ ],
    styleUrls: ['./track.component.css', './app.component.css']
})

export class TrackComponent {
    @Input() trackNumber: number;
    @Input() key: string;
    @Input() scale: Object;
    @Input() pianoRollOpen: boolean;
    @Input() gridState: any;
    @Input() sequence: any;
    @Input() notes: Array<any>;
    @Input() thisTrackIsSelected: boolean;
    _ref: any;

    @Output()
    noteDrawn = new EventEmitter<any>();

    @Output()
    trackChange = new EventEmitter<any>();


    constructor(public configDataService: ConfigDataService) { }

    clearPianoRoll() {
        for (var i = 0; i < this.gridState.length; i++) {
            this.gridState[i]['timeStates'] = this.configDataService.makeEmptyTimeState();
        }
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

    refresh() {
        var track = this.configDataService.dawState.tracks[this.trackNumber];
        this.gridState = track;
    }

    renderNotes(notesToRender) {
        this.clearPianoRoll();
        var timeStateIndex = 0;
        for (var timeStateIndex = 0; timeStateIndex < notesToRender.length; timeStateIndex++) {
            this.renderNotesInOneTimeStep(notesToRender[timeStateIndex], timeStateIndex);
        }
    }

    renderNotesInOneTimeStep(notesToRenderInThisTimeStep, timeStateIndex) {
        for (let noteToRender of notesToRenderInThisTimeStep) {
            for (var noteIndex = 0; noteIndex < this.gridState.length; noteIndex++) {
                if(this.gridState[noteIndex].note == noteToRender.note && this.gridState[noteIndex].octave == noteToRender.octave) {
                    this.gridState[noteIndex]['timeStates'][timeStateIndex] = true;
                    break;
                }
            }
        }
    }
}
