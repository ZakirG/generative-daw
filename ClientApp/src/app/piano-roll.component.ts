import { Component, Input, Output, EventEmitter } from '@angular/core';
import {FormControl, FormGroup} from '@angular/forms';
import { GenerationService } from './generation.service';
import { ConfigDataService } from './configdata.service';

@Component({
    selector:    'piano-roll',
    templateUrl: './piano-roll.component.html',
    providers:  [ /*NoteService*/ ],
    styleUrls: ['./piano-roll.component.css']
})

export class PianoRollComponent implements OnInit {
    timeStateLength = 8;
    gridState = [];
    conformToKeyScale = true;

    @Input() key: string;
    @Input() scale: Object;

    @Output()
    noteDrawn = new EventEmitter<string>();

    constructor(public generationService: GenerationService, public configDataService: ConfigDataService) { }

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

    ngOnInit() {
        this.getConfigData();
        this.initializeEmptyGridState();
    }

    clearPianoRoll() {
        for (var i = 0; i < this.gridState.length; i++) {
            this.gridState[i]['timeStates'] = Array.apply(null, Array(this.timeStateLength)).map(Number.prototype.valueOf,0);
        }
    }

    previewNoteSound(noteName, noteOctave, noteState) {
        if(noteState) {
            // If we are switching from a drawn to not-drawn state, don't play the sound.
            return;
        }
        this.noteDrawn.emit(noteName + noteOctave);
    }

    getConfigData() {
        this.key = this.configDataService.getKey();
        this.scale = this.configDataService.getScale().name;
    }

    generate(generationOptions) {
        console.log(this.configDataService.key);

        generationOptions.key = generationOptions.conformToKeyScale ? this.configDataService.getKey() : 'any';
        generationOptions.scale = generationOptions.conformToKeyScale ? this.scale : 'any';

        var generatedNotes = [];
        this.generationService.generate(generationOptions, this.timeStateLength).subscribe((data) => {
            generatedNotes = data['generationResult'];
            this.renderNotes(generatedNotes);
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
