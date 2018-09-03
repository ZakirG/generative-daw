import { Component, Input, Output, EventEmitter } from '@angular/core';
import {FormControl, FormGroup} from '@angular/forms';
import { ConfigDataService } from './configdata.service';

@Component({
    selector:    'track',
    templateUrl: './track.component.html',
    providers:  [ /*NoteService*/ ],
    styleUrls: ['./track.component.css']
})

export class TrackComponent {
    @Input() trackNumber: number;
    @Input() key: string;
    @Input() scale: Object;
    @Input() pianoRollOpen: boolean;
    @Input() gridState: any;
    @Input() timeStateLength: number;
    @Input() notes: Array<any>;
    _ref: any;

    @Output()
    noteDrawn = new EventEmitter<any>();

    @Output()
    trackChange = new EventEmitter<any>();

    constructor(public configDataService: ConfigDataService) {

    }

    initializeEmptyGridState() {
        var stateWidth = (100 / this.timeStateLength) + "%";

        this.notes = [
            {'color' : 'white', 'note' : 'b', 'octave' : 2},
            {'color' : 'black', 'note' : 'as', 'octave' : 2},
            {'color' : 'white', 'note' : 'a', 'octave' : 2},
            {'color' : 'black', 'note' : 'gs', 'octave' : 2},
            {'color' : 'white', 'note' : 'g', 'octave' : 2},
            {'color' : 'black', 'note' : 'fs', 'octave' : 2},
            {'color' : 'white', 'note' : 'f', 'octave' : 2},
            {'color' : 'white', 'note' : 'e', 'octave' : 2},
            {'color' : 'black', 'note' : 'ds', 'octave' : 2},
            {'color' : 'white', 'note' : 'd', 'octave' : 2},
            {'color' : 'black', 'note' : 'cs', 'octave' : 2},
            {'color' : 'white', 'note' : 'c', 'octave' : 2},

            {'color' : 'white', 'note' : 'b', 'octave' : 1},
            {'color' : 'black', 'note' : 'as', 'octave' : 1},
            {'color' : 'white', 'note' : 'a', 'octave' : 1},
            {'color' : 'black', 'note' : 'gs', 'octave' : 1},
            {'color' : 'white', 'note' : 'g', 'octave' : 1},
            {'color' : 'black', 'note' : 'fs', 'octave' : 1},
            {'color' : 'white', 'note' : 'f', 'octave' : 1},
            {'color' : 'white', 'note' : 'e', 'octave' : 1},
            {'color' : 'black', 'note' : 'ds', 'octave' : 1},
            {'color' : 'white', 'note' : 'd', 'octave' : 1},
            {'color' : 'black', 'note' : 'cs', 'octave' : 1},
            {'color' : 'white', 'note' : 'c', 'octave' : 1}
        ]

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

    ngOnInit() {

    }

    togglePianoRollOpen() {
        console.log('hey');
    }

    deleteTrack() {
        this.trackChange.emit({'event' : 'deleteTrack', 'trackNumber' : this.trackNumber});
    }

    destroyReference() {
        this._ref.destroy();
    }

    refresh() {
        console.log('daw state: ', this.configDataService.dawState);
        var track = this.configDataService.dawState.tracks[this.trackNumber];
        this.gridState = track;
        console.log(this.gridState);
        //this.renderNotes(track);
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
