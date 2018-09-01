//import { Component, ViewChild, AfterViewInit, ViewContainerRef } from '@angular/core';
import {Component, NgModule,Input,ComponentFactory,ComponentRef, AfterViewInit, ComponentFactoryResolver, ViewContainerRef, ChangeDetectorRef, TemplateRef, ViewChild, Output, EventEmitter} from '@angular/core';
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
    @ViewChild("newPianoRoll", { read: ViewContainerRef }) container;
    notes: Array<any>;
    tracks: Array<any>;
    audioBuffers: Object;
    queuedSounds: Array<any>;
    controlPanelForm: FormGroup;

    public constructor(
        private titleService: Title,
        private configDataService: ConfigDataService,
        private dawStateService: DawStateService,
        private resolver: ComponentFactoryResolver) { }

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

        this.addTrack();
    }

    updateConfigState() {
        this.configDataService.tempo = this.controlPanelForm.value.tempo;
        this.configDataService.scale = this.controlPanelForm.value.scale;
        this.configDataService.key = this.controlPanelForm.value.key;
    }

    ngAfterViewInit() {
        this.notes = this.tracks[0].notes;

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

    registerTrackChange(event) {
        if(event['event'] == 'deleteTrack') {
            var trackInstance = this.tracks[event['trackNumber']]
            trackInstance.destroyReference();
            this.tracks.splice(event['trackNumber'], 1);
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

        for (var noteIndex = 0; noteIndex < this.notes.length; noteIndex++) {
            for (var timeStateIndex = 0; timeStateIndex < this.configDataService.timeStateLength; timeStateIndex++) {
                for (let track of this.tracks) {
                    var note = track.gridState[noteIndex];
                    if(note['timeStates'][timeStateIndex]) {
                        // beat number * seconds per beat
                        var timeToPlay = timeStateIndex * (60 / this.configDataService.tempo);
                        this.playNote(note.note, note.octave, timeToPlay);
                    }
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

    addTrack() {
        const factory: ComponentFactory = this.resolver.resolveComponentFactory(PianoRollComponent);
        var newPianoRoll : ComponentRef = this.container.createComponent(factory);
        newPianoRoll.instance._ref = newPianoRoll;
        newPianoRoll.instance.key = this.configDataService.key;
        newPianoRoll.instance.scale = this.configDataService.scale.name;
        newPianoRoll.instance.trackNumber = this.tracks.length;
        newPianoRoll.instance.noteDrawn.subscribe((event) => {
            this.registerNoteDrawn(event);
        });
        newPianoRoll.instance.trackChange.subscribe((event) => {
            this.registerTrackChange(event);
        });
        this.tracks.push(newPianoRoll.instance);
    }

    updateDawState() {
        // Daw State: data in the interface that the server needs to know
        var dawState = {};

        var minimizedTracks = [];
        for (let track of this.tracks) {
            var trackGridState = track.gridState;
            var minTrack = trackGridState.map((x, i, trackGridState) => ({'note' : x.note, 'octave' : x.octave, 'timeStates' : x.timeStates }));
            minimizedTracks.push(minTrack);
        }

        dawState['tracks'] = minimizedTracks;
        dawState['scale'] = this.configDataService.scale;
        dawState['key'] = this.configDataService.key;

        this.dawStateService.updateDawState(dawState).subscribe((data) => {
            console.log(data);
            this.configDataService.dawState = data;
        });
    }
}
