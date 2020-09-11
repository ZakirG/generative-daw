import { Component, Input, Output, EventEmitter } from '@angular/core';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ConfigDataService } from './configdata.service';

@Component({
    selector:    'track',
    templateUrl: './track.component.html',
    providers:  [ /*NoteService*/ ],
    styleUrls: ['./track.component.css', './app.component.css']
})

export class TrackComponent {
    @Input() trackNumber: number;
    @Input() key: string;
    @Input() scale: Object;
    @Input() pianoRollOpen: boolean;
    @Input() gridState: any;
    @Input() timeStateLength: number;
    @Input() notes: Array<any>;
    @Input() thisTrackIsSelected: boolean;
    _ref: any;

    @Output()
    noteDrawn = new EventEmitter<any>();

    @Output()
    trackChange = new EventEmitter<any>();

    constructor(public configDataService: ConfigDataService) { }

    initializeEmptyGridState() {
        var stateWidth = (100 / this.timeStateLength) + "%";

        this.notes =this.configDataService.notes;

        this.gridState = [];
        for (let note of this.notes) {
            var noteRow = {
                'color' : note.color,
                'octave' : note.octave,
                'note' : note.note,
                'timeStates' : Array.apply(null, Array(this.timeStateLength)).map(Number.prototype.valueOf,0),
                'stateWidth' : stateWidth,
                'id' : note.note + note.octave
            };
            this.gridState.push(noteRow);
        }
    }

    clearPianoRoll() {
        for (var i = 0; i < this.gridState.length; i++) {
            this.gridState[i]['timeStates'] = Array.apply(null, Array(this.timeStateLength)).map(Number.prototype.valueOf,0);
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
