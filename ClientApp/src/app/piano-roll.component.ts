import { Component } from '@angular/core';

@Component({
    selector:    'piano-roll',
    templateUrl: './piano-roll.component.html',
    providers:  [ /*NoteService*/ ],
    styleUrls: ['./piano-roll.component.css']
})

export class PianoRollComponent implements OnInit {
    notes: Note[];
    selectedNotes: Note[];

    // constructor(private service: NoteService) { }

    ngOnInit() {
        var timeStateLength = 8;
        var stateWidth = (100 / timeStateLength) + "%";

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
                'timeStates' : Array.apply(null, Array(timeStateLength)).map(Number.prototype.valueOf,0),
                'stateWidth' : stateWidth,
                'id' : note.note + note.octave
            };
            this.gridState.push(noteRow);
        }
        console.log(this.gridState);

    }

    gridStateToggle(event : any) {
        if(!event.target.getAttribute('data-step')) {
            return;
        }
        // console.log(event.target);
        // console.log("#" + event.target.id + "[data-step='" + event.target.getAttribute('data-step') + "']");
        var associated_checkbox = document.querySelector("#" + event.target.id +
            "[data-step='" + event.target.getAttribute('data-step') + "']" + " input");
        // console.log(associated_checkbox);
        associated_checkbox.click();
        console.log(this.gridState);
    }

    addNote(note: Note) { this.selectedNotes.append(note); }
}
