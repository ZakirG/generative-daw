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
    inCycleMode = true;
    pendingTimeouts = [];
    
    pageLoaded = false;
    pageReady = false;
    showLogs = false;
    serverURL = 'http://localhost:5000/'
    constantsURL = this.serverURL + 'constants';

    // For the webaudioapi piano roll
    actx : any;
    timestack: any;
    pendingIntervals : any;
    numTicksPerBar : any;
    gain : any;
    secondsPerTick : any;
    indexOfNextSequenceNoteToPlay : any;
    timeToPlayNextNote : any;
    cursor = 0;
    playcallback : any;
    totalNumberOfTicksInProject = 240;
    preload = 1.0;

    public constructor(
        public titleService: Title,
        public configDataService: ConfigDataService,
        public generationService: GenerationService,
        public dawStateService: DawStateService,
        public resolver: ComponentFactoryResolver,
        private http: HttpClient) {
            this.tracks = [];
            this.notes = [];
            this.audioBuffers = {};
            this.queuedSounds = [];
            // The default note length is 1 tick.
            // So if you want the smallest note length to be an eighth note,
            // and a bar is a whole note, there should be 8 ticks per bar.
            this.numTicksPerBar = 8; // 480;
        }

    public setTitle( newTitle: string) {
        this.titleService.setTitle( newTitle );
    }

    ngOnInit() {
        this.setTitle('GenerativeDAW');
        this.audioContext = new AudioContext();
        this.actx = new AudioContext();
        this.gain = this.actx.createGain();
        this.gain.gain.value = 0;

        this.controlPanelForm = new FormGroup({
            scale: new FormControl(this.configDataService.scale),
            key: new FormControl(this.configDataService.key),
            tempo: new FormControl(this.configDataService.tempo),
            numBeatsInProject: new FormControl(this.configDataService.numBeatsInProject)
        });
        
        this.http.get(this.constantsURL).subscribe((data) => {
            let constants = data;
            let scales = Object.values(constants['scales']);
            this.configDataService.scales = scales;
            this.configDataService.scale = scales[0];
            let scale = scales[1];
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
        this.configDataService.numBeatsInProject = this.controlPanelForm.value.numBeatsInProject;
    }

    toggleCycleMode() {
        this.inCycleMode = !this.inCycleMode;
    }

    ngAfterViewInit() {
        this.notes = this.configDataService.notes;

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
        console.log('app component register note drawn', event);
        if(event['event'] == 'noteDrawn' && event['state'] && event['playSound']) {
            console.log('135 playing sound');
            this.playSound(event['note'], 0);
        }

        var trackNumber = event['track'];
        var track = this.tracks[trackNumber];
        this.tracks[trackNumber].gridState = this.pianoRoll.gridState;
        this.tracks[trackNumber].sequence = this.pianoRoll.sequence;

        this.updateDawState();
    }

    registerTriggerQuickGenerate() {
        this.togglePlayState();
    }
    
    registerNewLogs(event) {
        this.configDataService.appLogs.push(...event['logs']);
        this.configDataService.appLogs.push(this.configDataService.logSeparator)
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
            this.stopSequence();
            this.configDataService.inPlayState = false;
            for(let i = 0; i < this.pendingTimeouts.length; i++) {
                clearTimeout(this.pendingTimeouts[i]);
            }
            for (var i = 0; i < this.queuedSounds.length; i++) {
                this.queuedSounds[i].stop(0);
            }
            this.queuedSounds = [];
            return;
        }

        this.queuedSounds = [];
        this.configDataService.inPlayState = true;
        
        // Build chords
        for (let track of this.tracks) {
            this.playSequence(track.sequence);
            // for (var timeStateIndex = 0; timeStateIndex < this.configDataService.numDivisions; timeStateIndex++) {
            //     let playOffsetDueToRoll = 0;
            //     for (var noteIndex = this.notes.length - 1; noteIndex >= 0;  noteIndex--) {
            //         var note = track.gridState[noteIndex];
            //         if(note['timeStates'][timeStateIndex]) {
            //             // beat number * seconds per beat
            //             var timeToPlay = (timeStateIndex / this.configDataService.numSubdivisionsPerBeat) * (60 / this.configDataService.tempo) + playOffsetDueToRoll;
            //             this.playNote(note.note, note.octave, timeToPlay);
            //             playOffsetDueToRoll += this.configDataService.playOffsetPerNoteDueToRoll
            //         }
            //     }
            // }
        }
        

        var root = this;
    
        if(this.inCycleMode) {
            var pendingTimeout = setTimeout(function(){
                console.log('cycling...');
                root.configDataService.inPlayState = false;
                root.togglePlayState();
            }, 1000 * root.configDataService.numBeatsInProject * (60 / root.configDataService.tempo) );
            this.pendingTimeouts.push(pendingTimeout);
        }
        else {
            setTimeout(function(){
                root.configDataService.inPlayState = false;
            }, 1000 * root.configDataService.numBeatsInProject * (60 / root.configDataService.tempo) );
        }
    }

    updateSecondsPerTick() {
        /* 
            (60 seconds / minute) * (1/tempo in minutes / beat) * (4 beats / bar) = 
            (60 * 4 / tempo) seconds / bar.
            So ((60 * 4 / tempo) seconds / bar) / (numTicksPerBar in ticks / bar) = 
            (60 * 4 / tempo / numTicksPerBar) in (seconds / bar) * (bar / ticks ).
            So secondsPerTick = (60 * 4 / tempo / numTicksPerBar) in seconds / tick
            is the number of seconds in a tick. Use this value to convert ticks into seconds.
        */
        // this.secondsPerTick = 4 * 60 / this.configDataService.tempo / this.numTicksPerBar;
        // taking the 4 away, so bars are the same thing as beats.
        // (seconds / beat) / (ticks / beat) = (seconds / tick)
        this.secondsPerTick = 60 / this.configDataService.tempo / this.numTicksPerBar;
    }

    playSequence(sequence) {
        // if (this.actx.state === 'suspended') {
        //     this.actx.resume();
        // }

        console.log('playing sequence: ', sequence);
        if (!this.configDataService.inPlayState) {
            return;
        }
        this.cursor = 0;
        this.updateSecondsPerTick();
        
        function Interval() {
            if (!this.configDataService.inPlayState) {
                return;
            }
            const currentTime = this.actx.currentTime;
            // Update the secondsPerTick just in case the tempo was changed
            this.updateSecondsPerTick();
            // Remove elements from the front of the array until the second event
            // of the timestack occurs in the future.
            while(this.timestack.length > 1 && currentTime >= this.timestack[1][0]){
                this.timestack.shift();
            }
            // Shift the cursor up to the first event's tick, which may be a value in the past.
            this.cursor = this.timestack[0][1] + (currentTime - this.timestack[0][0]) / this.secondsPerTick;
            // this.redrawMarker();
            while(this.timeToPlayNextNote <= currentTime + this.preload){
                let nextNote = sequence[this.indexOfNextSequenceNoteToPlay];
                if( !nextNote || nextNote.t >= this.totalNumberOfTicksInProject){
                    // If the next note is missing or out of bounds, go back to
                    // the project's beginning.
                    this.timestack.push([this.timeToPlayNextNote, 0]);
                    const nextEvent = this.findNextEventAfterTick(0, sequence);
                    this.timeToPlayNextNote += nextEvent.dt * this.secondsPerTick;
                    this.indexOfNextSequenceNoteToPlay = nextEvent.i;
                }
                else {
                    // Case where the next note is playable
                    this.timestack.push([this.timeToPlayNextNote, nextNote.t]);
                    let gmax = Math.min(nextNote.t + nextNote.g, this.totalNumberOfTicksInProject) - nextNote.t;
                    const nextNoteInGlobalTimeForm = {
                        t: this.timeToPlayNextNote,
                        g: this.timeToPlayNextNote + gmax * this.secondsPerTick,
                        n: nextNote.n,
                        note: nextNote.note,
                        octave: nextNote.octave
                    };
                    this.playSequenceNote(nextNoteInGlobalTimeForm, this.timeToPlayNextNote);
                    let previousNote = nextNote;
                    nextNote = sequence[++this.indexOfNextSequenceNoteToPlay];
                    if(!nextNote || nextNote.t >= this.totalNumberOfTicksInProject){
                        this.timeToPlayNextNote += (this.totalNumberOfTicksInProject - previousNote.t) * this.secondsPerTick;
                        const nextEvent = this.findNextEventAfterTick(0, sequence);
                        this.timestack.push([this.timeToPlayNextNote, 0]);
                        this.timeToPlayNextNote += nextEvent.dt * this.secondsPerTick;
                        this.indexOfNextSequenceNoteToPlay = nextEvent.i;
                    }
                    else {
                        this.timeToPlayNextNote += (nextNote.t - previousNote.t) * this.secondsPerTick;
                    }
                }
            }
        }
        // The timestack is a list of lists. Each sublist has 2 elements:
        // timestack_element[0] is the global time the note will be played, in seconds. 
        // timestack_element[1] is the time relative time the note will be played, in ticks.
        this.timestack = [];
        this.timeToPlayNextNote = this.actx.currentTime + 0.1;

        const nextEvent = this.findNextEventAfterTick(this.cursor, sequence);
        
        this.indexOfNextSequenceNoteToPlay = nextEvent.i;
        this.timestack.push([0, this.cursor]);
        this.timestack.push([this.actx.currentTime + 0.1, this.cursor]);
        // Set timeToPlayNextNote to represent the time at which the next note will be played.
        this.timeToPlayNextNote += nextEvent.dt * this.secondsPerTick;
        if(nextEvent.i < 0) {
            // The next note is out of bounds; this event will result in a loop. (?)
            this.timestack.push([this.timeToPlayNextNote, 0]);
        } 
        else {
            this.timestack.push([this.timeToPlayNextNote, nextEvent.t1]);
        }
        this.pendingIntervals = setInterval(Interval.bind(this), 25);
    }

    findNextEventAfterTick(tick, sequence) {
        /* 
        Returns an object of this form:
        {
            t1 -- The tick input to this function. Points at the preceding "event" or position
            t2 -- When the new event will occur.
            dt -- The number of ticks between the next event (t2) and the previous event (t1).
            i  -- The position of this event in the play sequence.
        }
        */

        for(let i = 0; i < sequence.length; ++i) {
            const nev = sequence[i];
            if(nev.t >= this.totalNumberOfTicksInProject) {
                // The next note is beyond the end of the project.
                return {t1: tick, dt: this.totalNumberOfTicksInProject - tick, i: -1};
            }
            if(nev.t >= tick) {
                // Successfully found a playable note at sequence[i].
                return {t1: tick, t2: nev.t, dt:nev.t - tick, i: i};
            }
        }
        return {t1: tick, t2: this.totalNumberOfTicksInProject, dt: this.totalNumberOfTicksInProject - tick, i: -1};
    };

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

    playSequenceNote(ev, timeToPlay=0) {
        let note = this.configDataService.numeral_to_note(ev.n - 24);
        console.log('playing sequence note: ', note);
        
        let bufferSource = this.actx.createBufferSource();
        this.queuedSounds.push(bufferSource);
        bufferSource.buffer = this.audioBuffers[note];
        bufferSource.connect(this.actx.destination);
        bufferSource.start(ev.t);
        // this.gain.gain.setTargetAtTime(0.5, ev.t, 0.005);
        // this.gain.gain.setTargetAtTime(0, ev.g, 0.1);

        console.log('ev.t: ', ev.t);
        console.log('ev.g: ', ev.g);
        console.log('this.actx.currentTime: ', this.actx.currentTime);

        // this.gain.gain.setTargetAtTime(0.5, ev.t, 0.005);
        // this.gain.gain.setTargetAtTime(0, ev.g, 0.1);
        


        // var o=actx.createOscillator();
        // var g=actx.createGain();
        // o.type="sawtooth";
        // o.detune.value=(ev.n-69)*100;
        // g.gain.value=0;
        // o.start(actx.currentTime);
        // g.gain.setTargetAtTime(0.2,ev.t,0.005);
        // g.gain.setTargetAtTime(0,ev.g,0.1);
        // o.connect(g);
        // g.connect(actx.destination);
    }

    stopSequence(){
        if(this.pendingIntervals) {
            clearInterval(this.pendingIntervals);
        }
        this.pendingIntervals = null;
    };

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
        newTrack.instance.numBeatsInProject = this.configDataService.numBeatsInProject;
        newTrack.instance.noteDrawn.subscribe((event) => {
            this.registerNoteDrawn(event);
        });
        newTrack.instance.trackChange.subscribe((event) => {
            this.registerTrackChange(event);
        });
        // newTrack.instance.triggerQuickGenerate.subscribe((event) => {
        //     this.registerTriggerQuickGenerate();
        // });
        newTrack.instance.gridState = this.configDataService.initializeEmptyGridState();
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
        pianoRoll.instance.triggerQuickGenerate.subscribe((event) => {
            this.registerTriggerQuickGenerate();
        });
        pianoRoll.instance.newLogs.subscribe((event) => {
            this.registerNewLogs(event);
        });
        pianoRoll.instance.trackChange.subscribe((event) => {
            this.registerTrackChange(event);
        });
        this.pianoRoll = pianoRoll.instance;
    }

    updateDawState(callback=null) {
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

        return this.dawStateService.updateDawState(dawState).subscribe((data) => {
            this.configDataService.dawState = data;
            if (typeof callback !== 'undefined' && callback !== null) {
                callback.apply(this);
            }
        });
    }

    downloadFile(data, type, filename) {
        const blob = new Blob([data], { type: type });
        const url= window.URL.createObjectURL(blob);
        let anchor = document.createElement("a");
        anchor.download = filename;
        anchor.href = url;
        anchor.click();
    }

    niceDateTimeStamp() {
        var currentDate = new Date();
        var dateDay = currentDate.getDate();
        var month = currentDate.getMonth();
        var year = currentDate.getFullYear();
        var dateString = (month + 1) + "-" + dateDay + '-' + year;
        let time = currentDate.toLocaleTimeString(undefined, {
            hour: '2-digit',
            minute: '2-digit'
        });
        time = time.replace(/\s/g, '-').replace(/:/g, "-").replace(/_/g, "-");
        return dateString + '-' + time;
    }

    exportMidiFile() {
        var timestamp = this.niceDateTimeStamp();
        this.generationService.exportToMidi(this.configDataService.dawState).subscribe((data) => {
            this.downloadFile(data, 'audio/midi', 'composition-' + timestamp + '.midi');
        });
    }

    exportToMidi() {
        this.updateDawState(this.exportMidiFile);
    }

    exportMidiAndLog() {
        var logs = this.configDataService.appLogs.slice();
        logs.pop();
        let finalSeparator = logs.lastIndexOf(this.configDataService.logSeparator);
        let lastGenerationLog = logs.slice(finalSeparator + 1).join("\n");

        var timestamp = this.niceDateTimeStamp();
        this.generationService.exportToMidi(this.configDataService.dawState).subscribe((data) => {
            this.downloadFile(data, 'audio/midi', 'composition-' + timestamp + '.midi');
            this.downloadFile(lastGenerationLog, 'text/plain;charset=utf-8', 'composition-' + timestamp + '.txt');
        });
    }

    exportToMidiWithLog() {
        this.updateDawState(this.exportMidiAndLog);
    }
}
