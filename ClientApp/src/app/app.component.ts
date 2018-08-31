import { Component, ViewChild, AfterViewInit } from '@angular/core';
import { Title }     from '@angular/platform-browser';
import { FormControl, FormGroup } from '@angular/forms';
import { PianoRollComponent } from './piano-roll.component';
import { ConfigDataService } from './configdata.service';
import { DawStateService } from './dawstate.service';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css']
})

export class AppComponent {
    private audioContext: AudioContext;
    @ViewChild(PianoRollComponent) pianoRoll;
    notes: Array<any>;
    tracks: Array<any>;
    audioBuffers: Object;
    queuedSounds: Array<any>;
    controlPanelForm: FormGroup;

    public constructor(
        private titleService: Title,
        private configDataService: ConfigDataService,
        private dawStateService: DawStateService) { }

    public setTitle( newTitle: string) {
        this.titleService.setTitle( newTitle );
    }

    ngOnInit() {
        this.setTitle('GenerativeDAW');
        this.audioContext = new AudioContext();
        this.tracks = [];
        this.notes = [];
        this.audioBuffers = {};
        this.queuedSounds = [];

        this.controlPanelForm = new FormGroup({
            scale: new FormControl(this.configDataService.scale),
            key: new FormControl(this.configDataService.key),
            tempo: new FormControl(this.configDataService.tempo)
        });
    }

    updateConfigState() {
        this.configDataService.tempo = this.controlPanelForm.value.tempo;
        this.configDataService.scale = this.controlPanelForm.value.scale;
        this.configDataService.key = this.controlPanelForm.value.key;
    }

    ngAfterViewInit() {
        this.tracks[0] = this.pianoRoll.gridState;
        this.notes = this.pianoRoll.notes;

        for (let note of this.notes) {
            this.audioBuffers[note.note + note.octave] = 0;
        }

        this.fetchNoteSamples();
    }

    registerNoteDrawn(event) {
        if(event['event'] == 'noteDrawn' && event['state']) {
            this.playSound(event['note'], 0);
        }

        this.updateDawState();
    }

    togglePlayState() {
        if(this.configDataService.inPlayState) {
            this.configDataService.inPlayState = false;
            for (var i = 0; i < this.queuedSounds.length; i++) {
                this.queuedSounds[i].stop(0);
            }
            this.queuedSounds = [];
            return;
        }

        this.queuedSounds = [];
        this.configDataService.inPlayState = true;
        for (let note of this.tracks[0]) {
            for (var timeStateIndex = 0; timeStateIndex < note.timeStates.length; timeStateIndex++) {
                if(note.timeStates[timeStateIndex]) {
                    // beat number * seconds per beat
                    var timeToPlay = timeStateIndex * (60 / this.configDataService.tempo);
                    this.playNote(note.note, note.octave, timeToPlay);
                }
            }
        }
        var root = this;
        setTimeout(function(){
            root.configDataService.inPlayState = false;
        }, 1000 * root.configDataService.timeStateLength * (60 / root.configDataService.tempo) );
    }

    playNote(noteName : string, noteOctave : number, time : number) {
        this.playSound(noteName + noteOctave, time);
    }

    playSound(soundName, time) {
        let bufferSource = this.audioContext.createBufferSource();
        this.queuedSounds.push(bufferSource);
        bufferSource.buffer = this.audioBuffers[soundName];
        bufferSource.connect(this.audioContext.destination);
        bufferSource.start(this.audioContext.currentTime + time);
    }

    fetchNoteSample(filename) : Promise<any> {
        return fetch(filename)
                .then(response => response.arrayBuffer())
                .then(buffer => {
                    return new Promise((resolve, reject) => {
                        this.audioContext.decodeAudioData(buffer, resolve, reject);
                    })
                });
    }

    fetchNoteSamples() {
        for (let note of this.notes) {
            var filename = 'assets/sounds/' + note.note + (note.octave + 1) + '.wav';

            this.fetchNoteSample(filename).then(audioBuffer => {
                this.audioBuffers[note.note + note.octave] = audioBuffer;
            }).catch(error => { throw error; });
        }
    }

    updateDawState() {
        // Daw State: data in the interface that the server needs to know
        var dawState = {};

        var minimizedTracks = [];
        for (let track of this.tracks) {
            var minTrack = track.map((x, i, track) => ({'note' : x.note, 'octave' : x.octave, 'timeStates' : x.timeStates }));
            minimizedTracks.push(minTrack);
        }

        dawState['tracks'] = minimizedTracks;
        dawState['scale'] = this.configDataService.scale;
        dawState['key'] = this.configDataService.key;

        this.dawStateService.updateDawState(dawState).subscribe((data) => {
            // console.log(data);
            this.configDataService.dawState = data;
        });
    }

}
