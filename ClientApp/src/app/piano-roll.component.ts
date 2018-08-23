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
    this.notes = [] // this.service.getNotes();
    }

    addNote(note: Note) { this.selectedNotes.append(note); }
}
