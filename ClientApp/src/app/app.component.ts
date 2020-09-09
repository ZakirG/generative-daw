import {Component, NgModule,Input,ComponentFactory,ComponentRef, AfterViewInit, ComponentFactoryResolver, ViewContainerRef, ChangeDetectorRef, TemplateRef, ViewChild, Output, EventEmitter} from '@angular/core';
import { Title }     from '@angular/platform-browser';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { TrackComponent } from './track.component';
import { PianoRollComponent } from './piano-roll.component';
import { ConfigDataService } from './configdata.service';
import { GenerationService } from './generation.service';
import { DawStateService } from './dawstate.service';
import { HttpClient } from '@angular/common/http';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css']
})

export class AppComponent {
    private audioContext: AudioContext;
    @ViewChild("newTrack", { read: ViewContainerRef, static: true }) container;
    @ViewChild("pianoRoll", { read: ViewContainerRef, static: true }) pianoRollContainer;
    notes: Array<any>;
    tracks: Array<any>;
    pianoRoll: any;
    audioBuffers: Object;
    queuedSounds: Array<any>;
    controlPanelForm: FormGroup;
    constants: any;
    
    pageLoaded = false;
    pageReady = false;
    showLogs = false;
    appLogs = ['Welcome to GenerativeDAW ~'];
    serverURL = 'http://localhost:5000/'
    constantsURL = this.serverURL + 'constants';

    public constructor(
        public titleService: Title,
        public configDataService: ConfigDataService,
        public generationService: GenerationService,
        public dawStateService: DawStateService,
        public resolver: ComponentFactoryResolver,
        private http: HttpClient) { }

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
        
        this.http.get(this.constantsURL).subscribe((data) => {
            let constants = data;
            let scales = Object.values(constants['scales']);
            this.configDataService.scales = scales;
            this.configDataService.scale = scales[0];
            let scale = scales[0];
            this.controlPanelForm.controls.scale.setValue(scale);
        });

        this.addTrack();
        this.showPianoRoll(0);
        this.updateDawState();
    }

    updateConfigState() {
        this.configDataService.tempo = this.controlPanelForm.value.tempo;
        this.configDataService.scale = this.controlPanelForm.value.scale;
        this.configDataService.key = this.controlPanelForm.value.key;
    }

    ngAfterViewInit() {
        this.notes = this.tracks[0].notes;

        for (let note of this.notes) {
            let bufferName = note.note + note.octave;
            this.audioBuffers[bufferName] = 0;
        }

        this.fetchNoteSamples();
        
        var _this = this;
        window.setTimeout(function(){
            _this.pageLoaded = true;
        }, 1500);

        window.setTimeout(function(){
            _this.pageReady = true;
        }, 1700);
        
    }

    registerNoteDrawn(event) {
        if(event['event'] == 'noteDrawn' && event['state']) {
            this.playSound(event['note'], 0);
        }

        var trackNumber = event['track'];
        var track = this.tracks[trackNumber];
        track.gridState = this.pianoRoll.gridState;

        this.updateDawState();
    }

    registerTrackChange(event) {
        if(event['event'] == 'deleteTrack') {
            var trackInstance = this.tracks[event['trackNumber']];
            trackInstance.destroyReference();
            this.tracks.splice(event['trackNumber'], 1);
            for (var i = event['trackNumber']; i < this.tracks.length; i++) {
                this.tracks[i].trackNumber = i;
            }
            this.pianoRoll.trackNumber = -1;
        } else if (event['event'] == 'regionSelected') {
            var trackInstance = this.tracks[event['trackNumber']];
            var oldSelectedTrack = this.pianoRoll.trackNumber;
            this.pianoRoll.gridState = trackInstance.gridState;
            this.pianoRoll.trackNumber = trackInstance.trackNumber;
            this.tracks[oldSelectedTrack].thisTrackIsSelected = false;
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
            var filename = 'assets/sounds/' + note.note + (note.octave) + '.wav';

            this.fetchNoteSample(filename).then(audioBuffer => {
                this.audioBuffers[note.note + note.octave] = audioBuffer;
            }).catch(error => { throw error; });
        }
    }

    addTrack() {
        const factory = this.resolver.resolveComponentFactory(TrackComponent);
        var newTrack = this.container.createComponent(factory);
        newTrack.instance._ref = newTrack;
        newTrack.instance.key = this.configDataService.key;
        newTrack.instance.scale = this.configDataService.scale.name;
        newTrack.instance.trackNumber = this.tracks.length;
        newTrack.instance.timeStateLength = this.configDataService.timeStateLength;
        newTrack.instance.noteDrawn.subscribe((event) => {
            this.registerNoteDrawn(event);
        });
        newTrack.instance.trackChange.subscribe((event) => {
            this.registerTrackChange(event);
        });
        newTrack.instance.initializeEmptyGridState();
        this.tracks.push(newTrack.instance);
    }

    showPianoRoll(trackNumber) {
        const factory = this.resolver.resolveComponentFactory(PianoRollComponent);
        var pianoRoll = this.container.createComponent(factory);
        pianoRoll.instance._ref = pianoRoll;
        pianoRoll.instance.key = this.configDataService.key;
        pianoRoll.instance.scale = this.configDataService.scale.name;
        pianoRoll.instance.trackNumber = trackNumber;
        this.tracks[trackNumber].thisTrackIsSelected = true;
        pianoRoll.instance.noteDrawn.subscribe((event) => {
            this.registerNoteDrawn(event);
        });
        pianoRoll.instance.trackChange.subscribe((event) => {
            this.registerTrackChange(event);
        });
        this.pianoRoll = pianoRoll.instance;
    }

    updateDawState() {
        var dawState = {};

        var minimizedTracks = [];
        for (let track of this.tracks) {
            var minTrack = track.gridState;
            // var minTrack = trackGridState.map((x, i, trackGridState) => ({'note' : x.note, 'octave' : x.octave, 'timeStates' : x.timeStates }));
            minimizedTracks.push(minTrack);
        }

        dawState['tracks'] = minimizedTracks;
        dawState['scale'] = this.configDataService.scale;
        dawState['key'] = this.configDataService.key;
        dawState['tempo'] = this.configDataService.tempo;

        this.dawStateService.updateDawState(dawState).subscribe((data) => {
            this.configDataService.dawState = data;
        });
    }

    downloadFile(data) {
        const blob = new Blob([data], { type: 'audio/midi' });
        const url= window.URL.createObjectURL(blob);
        let anchor = document.createElement("a");
        anchor.download = "autocomposer-export.midi";
        anchor.href = url;
        anchor.click();
    }

    exportToMidi() {
        this.generationService.exportToMidi(this.configDataService.dawState).subscribe((data) => {
            this.downloadFile(data)
        });
    }
}
