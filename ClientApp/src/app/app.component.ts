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
    timer : any;
    timebase : any;
    gain : any;
    tick2time : any;
    index1 : any;
    time1 : any;
    tick0 : any;
    time0:  any;
    tick1 : any;
    cursor = 0;
    playcallback : any;
    markstart = 0;
    markend = 240;
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
            this.timebase = 480;
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
        if(event['event'] == 'noteDrawn' && event['state']) {
            this.playSound(event['note'], 0);
        }

        var trackNumber = event['track'];
        var track = this.tracks[trackNumber];
        this.tracks[trackNumber].gridState = this.pianoRoll.gridState;
        this.tracks[trackNumber].sequence = this.pianoRoll.sequence;
        console.log('app set this.tracks: ', this.tracks);

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

    playSequence(sequence) {
        if (this.actx.state === 'suspended') {
            this.actx.resume();
        }
        console.log('playing sequence: ', sequence);
        let tick = null;
        function Interval(){
            const current=this.actx.currentTime;
            while(this.timestack.length>1 && current>=this.timestack[1][0]){
                this.timestack.shift();
            }
            this.cursor=this.timestack[0][1]+(current-this.timestack[0][0])/this.timestack[0][2];
            // this.redrawMarker();
            while(current + this.preload >= this.time1){
                this.time0=this.time1;
                this.tick0=this.tick1;
                let e = sequence[this.index1];
                if(!e || e.t>=this.markend){
                    this.timestack.push([this.time1,this.markstart,this.tick2time]);
                    const p=this.findNextEv(this.markstart, sequence);
                    this.time1+=p.dt*this.tick2time;
                    this.index1=p.i;
                }
                else{
                    this.tick1=e.t;
                    this.timestack.push([this.time1,e.t,this.tick2time]);
                    let gmax=Math.min(e.t+e.g,this.markend)-e.t;
                    const cbev={t:this.time1,g:this.time1+gmax*this.tick2time,n:e.n, note:e.note, octave:e.octave};
                    this.playSequenceNote(cbev, this.time1);
                    e = sequence[++this.index1];
                    if(!e || e.t>=this.markend){
                        this.time1+=(this.markend-this.tick1)*this.tick2time;
                        const p=this.findNextEv(this.markstart, sequence);
                        this.timestack.push([this.time1,this.markstart,this.tick2time]);
                        this.time1+=p.dt*this.tick2time;
                        this.index1=p.i;
                    }
                    else
                        this.time1+=(e.t-this.tick1)*this.tick2time;
                }
            }
        }
        if(typeof(tick)!="undefined")
            this.locate(tick);
        if(this.timer!=null)
            return;
        this.timestack=[];
        this.time0=this.time1=this.actx.currentTime+0.1;
        this.tick0=this.tick1=this.cursor;
        this.updateTimer();
        const p=this.findNextEv(this.cursor, sequence);
        
        this.index1=p.i;
        this.timestack.push([0,this.cursor,0]);
        this.timestack.push([this.time0,this.cursor,this.tick2time]);
        this.time1+=p.dt*this.tick2time;
        if(p.i<0)
            this.timestack.push([this.time1,this.markstart,this.tick2time]);
        else
            this.timestack.push([this.time1,p.t1,this.tick2time]);
        this.timer=setInterval(Interval.bind(this),25);
        console.log('285');
    }

    findNextEv(tick, sequence) {
        for(let i = 0; i < sequence.length; ++i) {
            const nev = sequence[i];
            if(nev.t >= this.markend) {
                return {t1:tick,n2:this.markend,dt:this.markend-tick,i:-1};
            }
            if(nev.t >= tick) {
                return {t1:tick,t2:nev.t,dt:nev.t-tick,i:i};
            }
        }
        return {t1:tick,t2:this.markend,dt:this.markend-tick,i:-1};
    };

    locate(tick){
        this.cursor=tick;
    };

    updateTimer(){
        this.tick2time=4*60/this.configDataService.tempo/this.timebase;
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
        console.log('playing sound ', note);
        
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
        if(this.timer) {
            clearInterval(this.timer);
        }
        this.timer = null;
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
