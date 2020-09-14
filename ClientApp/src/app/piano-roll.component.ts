import { Component, Input, Output, EventEmitter } from '@angular/core';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { GenerationService } from './generation.service';
import { ConfigDataService } from './configdata.service';
import { interact } from '../assets/js/interact.min.js';
import { config } from 'process';
declare var require: any
const interact = require('interactjs');

@Component({
    selector:    'piano-roll',
    templateUrl: './piano-roll.component.html',
    providers:  [ ],
    styleUrls: ['./piano-roll.component.css']
})

export class PianoRollComponent {
    timeStateLength = 8;
    gridState = [];
    conformToKeyScale = true;
    generationType = 'chords';
    octaveUpperBound = 4;
    octaveLowerBound = 3;
    chordSizeLowerBound = 3;
    chordSizeUpperBound = 7;
    disallowRepeats = true;
    chanceToUseChordLeadingChart = 0.7;
    chanceToUseCommonVoicing = 0.95;
    VMustBeDominant7 = false;
    chanceToAllowNonDiatonicChord = 0.001;
    chanceToAllowBorrowedChord = 0.001;
    chanceToAllowAlteredDominantChord = 0.7;
    notes: Array<any>;
    _ref: any;

    @Input() trackNumber: number;
    @Input() key: string;
    @Input() scale: Object;
    @Input() pianoRollOpen: boolean;

    @Output() noteDrawn = new EventEmitter<any>();
    @Output() newLogs = new EventEmitter<any>();

    @Output()
    trackChange = new EventEmitter<any>();

    constructor(public generationService: GenerationService, public configDataService: ConfigDataService) {
        this.initializeEmptyGridState();
        this.scale = this.configDataService.scale;
        this.key = this.configDataService.key;
    }

    initializeEmptyGridState() {
        var stateWidth = (100 / this.timeStateLength) + "%";

        this.notes = this.configDataService.notes;

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

    ngOnInit() {
        interact('.resize-drag').draggable({
            onmove: window['dragMoveListener'],
            restrict: {
                restriction: 'parent',
                elementRect: { top: 0, left: 0, bottom: 1, right: 1 }
            },
        }).resizable({
            // resize from only top edge
            edges: { left: false, right: false, bottom: false, top: true },
            // keep the edges inside the parent
            restrictEdges: {
                outer: 'parent',
                endOnly: true,
            },

        inertia: true,
        }).on('resizemove', function (event) {
            var target = event.target,
            y = (parseFloat(target.getAttribute('data-y')) || 0);
            target.style.height = event.rect.height + 'px';
            y += event.deltaRect.top;
        });
    }

    clearPianoRoll() {
        for (var i = 0; i < this.gridState.length; i++) {
            this.gridState[i]['timeStates'] = Array.apply(null, Array(this.timeStateLength)).map(Number.prototype.valueOf,0);
        }
        this.noteDrawn.emit({'event': 'clear', 'track' : this.trackNumber});
    }

    noteDrawnHandler(noteName, noteOctave, noteState) {
        this.noteDrawn.emit({
            'event' : 'noteDrawn', 'note' : noteName + noteOctave,
            'state' : noteState, 'track' : this.trackNumber
        });
    }

    destroyReference() {
        this._ref.destroy();
    }

    generate(generationOptions) {
        var generatedNotes = [];
        generationOptions.length = this.timeStateLength;
        this.generationService.generate(generationOptions).subscribe((data) => {
            generatedNotes = data['generationResult'];
            let logs = data['logs']
            this.renderNotes(generatedNotes);
            this.noteDrawn.emit({'event': 'generation', 'track' : this.trackNumber});
            this.newLogs.emit({'event': 'writeLogs', 'logs' : logs});
        });
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
