import { Component, Input, Output, EventEmitter } from '@angular/core';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { GenerationService } from './generation.service';
import { ConfigDataService } from './configdata.service';
import { interact } from '../assets/js/interact.min.js';
declare var require: any
const interact = require('interactjs');

@Component({
    selector:    'piano-roll',
    templateUrl: './piano-roll.component.html',
    providers:  [ /*NoteService*/ ],
    styleUrls: ['./piano-roll.component.css']
})

export class PianoRollComponent {
    timeStateLength = 8;
    gridState = [];
    conformToKeyScale = true;
    generationType = 'melody';
    octaveConstraint = 3;
    octaveConstraintCheck = true;
    notes: Array<any>;
    _ref: any;

    @Input() trackNumber: number;
    @Input() key: string;
    @Input() scale: Object;
    @Input() pianoRollOpen: boolean;

    @Output()
    noteDrawn = new EventEmitter<any>();

    @Output()
    trackChange = new EventEmitter<any>();

    constructor(public generationService: GenerationService, public configDataService: ConfigDataService) {
        this.initializeEmptyGridState();
    }

    initializeEmptyGridState() {
        var stateWidth = (100 / this.timeStateLength) + "%";

        this.notes = [
            {'color' : 'white', 'note' : 'b', 'octave' : 4},
            {'color' : 'black', 'note' : 'as', 'octave' : 4},
            {'color' : 'white', 'note' : 'a', 'octave' : 4},
            {'color' : 'black', 'note' : 'gs', 'octave' : 4},
            {'color' : 'white', 'note' : 'g', 'octave' : 4},
            {'color' : 'black', 'note' : 'fs', 'octave' : 4},
            {'color' : 'white', 'note' : 'f', 'octave' : 4},
            {'color' : 'white', 'note' : 'e', 'octave' : 4},
            {'color' : 'black', 'note' : 'ds', 'octave' : 4},
            {'color' : 'white', 'note' : 'd', 'octave' : 4},
            {'color' : 'black', 'note' : 'cs', 'octave' : 4},
            {'color' : 'white', 'note' : 'c', 'octave' : 4},

            {'color' : 'white', 'note' : 'b', 'octave' : 3},
            {'color' : 'black', 'note' : 'as', 'octave' : 3},
            {'color' : 'white', 'note' : 'a', 'octave' : 3},
            {'color' : 'black', 'note' : 'gs', 'octave' : 3},
            {'color' : 'white', 'note' : 'g', 'octave' : 3},
            {'color' : 'black', 'note' : 'fs', 'octave' : 3},
            {'color' : 'white', 'note' : 'f', 'octave' : 3},
            {'color' : 'white', 'note' : 'e', 'octave' : 3},
            {'color' : 'black', 'note' : 'ds', 'octave' : 3},
            {'color' : 'white', 'note' : 'd', 'octave' : 3},
            {'color' : 'black', 'note' : 'cs', 'octave' : 3},
            {'color' : 'white', 'note' : 'c', 'octave' : 3}
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

        // minimum size
        // restrictSize: {
//             min: { width: 500, height: 500 },
//         },
        inertia: true,
        }).on('resizemove', function (event) {
            var target = event.target,
            x = (parseFloat(target.getAttribute('data-x')) || 0),
            y = (parseFloat(target.getAttribute('data-y')) || 0);

            // update the element's style
            // target.style.width  = event.rect.width + 'px';
            target.style.height = event.rect.height + 'px';

            // translate when resizing from top or left edges
            // x += event.deltaRect.left;
            y += event.deltaRect.top;

            // target.style.webkitTransform = target.style.transform = 'translate(' + x + 'px,' + y + 'px)';

            // target.setAttribute('data-x', x);
            // target.setAttribute('data-y', y);
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
        console.log(generationOptions);

        generationOptions.key = generationOptions.conformToKeyScale ? this.configDataService.key : 'any';
        generationOptions.scale = generationOptions.conformToKeyScale ? this.configDataService.scale : 'any';
        generationOptions.octaveConstraint = generationOptions.octaveConstraintCheck ? generationOptions.octaveConstraint : 'any';


        var generatedNotes = [];
        this.generationService.generate(generationOptions, this.timeStateLength).subscribe((data) => {
            generatedNotes = data['generationResult'];
            this.renderNotes(generatedNotes);
            this.noteDrawn.emit({'event': 'generation', 'track' : this.trackNumber});
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
