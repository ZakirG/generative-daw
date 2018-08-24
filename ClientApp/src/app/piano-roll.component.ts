import { Component, Output, EventEmitter } from '@angular/core';

@Component({
    selector:    'piano-roll',
    templateUrl: './piano-roll.component.html',
    providers:  [ /*NoteService*/ ],
    styleUrls: ['./piano-roll.component.css']
})

export class PianoRollComponent implements OnInit {
    notes: Note[];
    selectedNotes: Note[];

    @Output()
    noteDrawn = new EventEmitter<string>();

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
        this.timeStateLength = 8;
        this.initializeEmptyGridState();
    }

    clearPianoRoll() {
        for (var i = 0; i < this.gridState.length; i++) {
            this.gridState[i]['timeStates'] = Array.apply(null, Array(this.timeStateLength)).map(Number.prototype.valueOf,0);
        }
    }

    // showGenerationModal() {
//         $('#generationModal').modal('show');
//     }

    previewNoteSound(noteName, noteOctave, noteState) {
        if(noteState) {
            // If we are switching from a drawn to not-drawn state, don't play the sound.
            return;
        }
        this.noteDrawn.emit(noteName + noteOctave);
    }
}
