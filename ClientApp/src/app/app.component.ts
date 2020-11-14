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
    styleUrls: ['./app.component.css', './form-styles.css']
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
    inCycleMode = false;
    pendingTimeouts = [];
    sequences = [];
    
    pageLoaded = false;
    pageReady = false;
    showLogs = false;
    serverURL = 'http://localhost:5000/'
    constantsURL = this.serverURL + 'constants';

    // For the webaudioapi piano roll
    actx : any;
    timestack: any;
    numTicksPerBar : any;
    secondsPerTick : any;
    indexOfNextSequenceNoteToPlay : any;
    timeToPlayNextNote : any;
    cursor = 0;
    playcallback : any;
    totalNumberOfTicksInProject = 240;
    preload = 1.0;
    pendingIntervals = [];
    releaseTime : number;
    changeTempoWithMidiImport = true;
    importedMidiSequence = [];
    importedMidiTempo : number;
    importedMidiFileName : string;
    selectedTrackNumber = 0;

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
            this.sequences = [];
        }

    public setTitle( newTitle: string) {
        this.titleService.setTitle( newTitle );
    }

    ngOnInit() {
        this.setTitle('GenerativeDAW');
        this.audioContext = new AudioContext();
        this.actx = new AudioContext();

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
        this.createPianoRoll();
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
        if(event['event'] == 'noteDrawn' && event['state'] && event['playSound'] && event['noteName']) {
            this.playSound(event['noteName'] + event['noteOctave'], 0);
        }

        var trackNumber = event['track'];
        this.tracks[trackNumber].gridState = this.pianoRoll.gridState;
        this.tracks[trackNumber].sequence = this.pianoRoll.sequence;
        this.tracks[trackNumber].triggerNoteDraw();
        
        this.updateDawState();
    }

    registerTriggerQuickGenerate(event) {
        this.registerNoteDrawn(event);
        this.registerNewLogs(event);

        var _this = this;
        setTimeout(function(){
            if(_this.configDataService.inPlayState) {
                _this.togglePlayState();
            }
            _this.togglePlayState();
        }, 1000);
    }
    
    registerNewLogs(event) {
        this.configDataService.appLogs.push(...event['logs']);
        this.configDataService.appLogs.push(this.configDataService.logSeparator)
    }

    refreshTrackView() {
        for (var i = 0; i < this.tracks.length; i++) { 
            this.tracks[i].thisTrackIsSelected = false;
        }
        this.tracks[this.selectedTrackNumber].thisTrackIsSelected = true;

    }

    registerTrackChange(event, updateDawState=true) {
        if(event['event'] == 'deleteTrack') {
            var trackInstance = this.tracks[event['trackNumber']];
            trackInstance.destroyReference();
            this.tracks.splice(event['trackNumber'], 1);
            this.sequences.splice(event['trackNumber'], 1);
            for (var i = event['trackNumber']; i < this.tracks.length; i++) {
                this.tracks[i].trackNumber = i;
            }
            this.selectedTrackNumber = 0;
            this.refreshTrackView();
            this.refreshPianoRoll();
        } else if (event['event'] == 'regionSelected') {
            this.selectedTrackNumber = event['trackNumber'];
            var trackInstance = this.tracks[this.selectedTrackNumber];
            this.refreshTrackView();
            this.refreshPianoRoll();
        }

        this.configDataService.dawState.sequences = this.sequences;

        if(updateDawState) {
            this.updateDawState();
        }
    }

    togglePlayState() {
        if(this.configDataService.inPlayState) {
            this.stopSequence();
            this.configDataService.inPlayState = false;
            for(let i = 0; i < this.pendingTimeouts.length; i++) {
                clearTimeout(this.pendingTimeouts[i]);
            }
            for (var i = 0; i < this.queuedSounds.length; i++) {
                this.queuedSounds[i]['gainNode'].gain.linearRampToValueAtTime(0, this.actx.currentTime + 0.2)
                // this.queuedSounds[i]['bufferSource'].stop(0, this.actx.currentTime + 1.01);
            }
            this.queuedSounds = [];
            this.pianoRoll.setCursor(0);
            return;
        }

        this.queuedSounds = [];
        this.configDataService.inPlayState = true;
        
        // Build chords
        for (let track of this.tracks) {
            this.playSequence(track.sequence);
        }
        

        var root = this;
    
        if(this.inCycleMode) {
            console.log('setting play toggle in cycle mode');
            var pendingTimeout = setTimeout(function(){
                root.configDataService.inPlayState = false;
                root.togglePlayState();
            }, 1000 * root.configDataService.numBeatsInProject * (60 / root.configDataService.tempo) );
            this.pendingTimeouts.push(pendingTimeout);
        }
        else {
            // setTimeout(function() {
            //     this.togglePlayState();
            // }, 1000 * root.configDataService.numBeatsInProject * (60 / root.configDataService.tempo) );
        }
    }

    updateTimeConstants() {
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
        this.releaseTime = this.secondsPerTick * 2; // 1 tick of release
    }

    rollSequence(sequence) {
        // Preprocess sequence: add user-supplied note roll offsets to make the play-style sound prettier
        var lastTimeStep = -1;
        let currentOffset = this.configDataService.playOffsetPerNoteDueToRoll;
        for(let i = 0; i < sequence.length; i++) {
            let note = sequence[i];
            if(lastTimeStep != note['t']) {
                currentOffset += this.configDataService.playOffsetPerNoteDueToRoll;
                lastTimeStep = note['t'];
                sequence[i]['t'] = sequence[i]['t'] + currentOffset;
            }
        }
        return sequence;
    }

    playSequence(sequence) {
        sequence = this.rollSequence(sequence);

        function Interval() {
            const currentTime = this.actx.currentTime;
            // Update the secondsPerTick just in case the tempo was changed
            this.updateTimeConstants();
            // Remove elements from the front of the array until the second event
            // of the timestack occurs in the future.
            while(this.timestack.length > 1 && currentTime >= this.timestack[1][0]){
                this.timestack.shift();
            }
            // Shift the cursor up to the first event's tick, which may be a value in the past.
            this.cursor = this.timestack[0][1] + (currentTime - this.timestack[0][0]) / this.secondsPerTick;
            this.pianoRoll.setCursor(this.cursor);
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

        this.cursor = 0;
        this.updateTimeConstants();

        // The timestack is a list of lists. Each sublist has 2 elements:
        // timestack_element[0] is the global time the note will be played, in seconds. 
        // timestack_element[1] is the time relative time the note will be played, in ticks.
        this.timestack = [];

        const nextEvent = this.findNextEventAfterTick(this.cursor, sequence);
        
        this.indexOfNextSequenceNoteToPlay = nextEvent.i;
        this.timestack.push([0, this.cursor]);
        this.timeToPlayNextNote = this.actx.currentTime + 0.05;
        this.timestack.push([this.timeToPlayNextNote, this.cursor]);
        // Set timeToPlayNextNote to represent the time at which the next note will be played.
        this.timeToPlayNextNote += nextEvent.dt * this.secondsPerTick;
        if(nextEvent.i < 0) {
            // The next note is out of bounds; this event will result in a loop. (?)
            this.timestack.push([this.timeToPlayNextNote, 0]);
        } 
        else {
            this.timestack.push([this.timeToPlayNextNote, nextEvent.t1]);
        }
        this.pendingIntervals.push(setInterval(Interval.bind(this), 25));
        this.pianoRoll.setCursor(this.cursor);
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

    playSound(soundName, time) {
        let bufferSource = this.audioContext.createBufferSource();
        this.queuedSounds.push(bufferSource);
        bufferSource.buffer = this.audioBuffers[soundName];
        
        // Give this note its own gain node
        var gainNode = this.audioContext.createGain();
        gainNode.gain.value = 0.5;
        bufferSource.connect(gainNode);

        bufferSource.connect(this.audioContext.destination);
        bufferSource.start(this.audioContext.currentTime + time);
    }

    playSequenceNote(ev, timeToPlay=0) {
        let note = this.configDataService.numeral_to_note(ev.n - 24);
        
        let bufferSource = this.actx.createBufferSource();
        bufferSource.buffer = this.audioBuffers[note];
        
        // Give this note its own gain node
        var gainNode = this.actx.createGain();
        gainNode.gain.value = 0.5;
        bufferSource.connect(gainNode);
        gainNode.connect(this.actx.destination);
        bufferSource.start(ev.t);

        // The sound should stop after the note-up plus some release time.
        gainNode.gain.setTargetAtTime(0.7, ev.g, 0.5);
        gainNode.gain.linearRampToValueAtTime(0, ev.g + this.releaseTime);
        bufferSource.stop( ev.g + this.releaseTime );
        this.queuedSounds.push({ 'bufferSource': bufferSource, 'gainNode': gainNode});
    }

    stopSequence(){
        if(this.pendingIntervals.length > 0) {
            for (let i = 0; i < this.pendingIntervals.length; i++) {
                clearInterval(this.pendingIntervals[i]);
            }
        }
        this.pendingIntervals = [];
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

    addTrack(trackNameToAdd='') {
        const factory = this.resolver.resolveComponentFactory(TrackComponent);
        var newTrack = this.container.createComponent(factory);
        newTrack.instance._ref = newTrack;
        newTrack.instance.key = this.configDataService.key;
        newTrack.instance.scale = this.configDataService.scale.name;
        newTrack.instance.trackNumber = this.tracks.length;
        
        let trackName = 'Piano';
        if (trackNameToAdd) {
            trackName = trackNameToAdd;
        }

        newTrack.instance.trackName = trackName;
        
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
        this.sequences.push([]);

        if(this.tracks.length > 1) {
            this.selectedTrackNumber = newTrack.instance.trackNumber;
            this.refreshTrackView();
            this.refreshPianoRoll();
        }
    }

    createPianoRoll() {
        let trackNumber = 0;
        const factory = this.resolver.resolveComponentFactory(PianoRollComponent);
        var pianoRoll = this.container.createComponent(factory);
        pianoRoll.instance._ref = pianoRoll;
        pianoRoll.instance.key = this.configDataService.key;
        pianoRoll.instance.scale = this.configDataService.scale.name;
        pianoRoll.instance.trackNumber = trackNumber;
        pianoRoll.instance.setSequence(this.sequences[trackNumber]);
        this.tracks[trackNumber].thisTrackIsSelected = true;
        pianoRoll.instance.noteDrawn.subscribe((event) => {
            this.registerNoteDrawn(event);
        });
        pianoRoll.instance.triggerQuickGenerate.subscribe((event) => {
            this.registerTriggerQuickGenerate(event);
        });
        pianoRoll.instance.newLogs.subscribe((event) => {
            this.registerNewLogs(event);
        });
        pianoRoll.instance.trackChange.subscribe((event) => {
            this.registerTrackChange(event);
        });
        this.pianoRoll = pianoRoll.instance;
    }

    refreshPianoRoll() {
        this.pianoRoll.trackNumber = this.selectedTrackNumber;
        
        this.pianoRoll.setSequence(this.sequences[this.selectedTrackNumber]);
        this.pianoRoll.refresh();
        
        this.registerTrackChange(null);
        // this.pianoRoll.key = this.configDataService.key;
        // this.pianoRoll.scale = this.configDataService.scale.name;
        // this.pianoRoll.trackNumber = trackNumber;
        // this.pianoRoll.setSequence(this.sequences[trackNumber]);
        // this.tracks[trackNumber].thisTrackIsSelected = true;
        // this.pianoRoll.noteDrawn.subscribe((event) => {
        //     this.registerNoteDrawn(event);
        // });
        // this.pianoRoll.triggerQuickGenerate.subscribe((event) => {
        //     this.registerTriggerQuickGenerate(event);
        // });
        // this.pianoRoll.newLogs.subscribe((event) => {
        //     this.registerNewLogs(event);
        // });
        // this.pianoRoll.trackChange.subscribe((event) => {
        //     this.registerTrackChange(event);
        // });
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
        this.sequences = [];
        for(let trackNumber = 0; trackNumber < this.tracks.length; trackNumber++) {
            this.sequences.push(this.tracks[trackNumber].sequence)
        }
        dawState['sequences'] = this.sequences;

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
        this.dawStateService.exportToMidi(this.configDataService.dawState).subscribe((data) => {
            this.downloadFile(data, 'audio/midi', 'composition-' + timestamp + '.midi');
        });
    }

    exportToMidi() {
        this.updateDawState(this.exportMidiFile);
    }

    importMidi(file, target) {
        let formData = new FormData();

        formData.append("file", file, file.name);
        
        this.dawStateService.midiToSequence(formData).subscribe((data) => {
            let importMidiModalToggle = document.getElementById('import-midi-toggle');
            importMidiModalToggle.click();

            this.importedMidiSequence = data['sequence'].slice();
            this.importedMidiTempo = data['tempo'];
            this.importedMidiFileName = file.name;
        });

        target.value = '';
    }

    renderMidi() {
        if(this.changeTempoWithMidiImport){
            this.controlPanelForm.controls.tempo.setValue(this.importedMidiTempo);
            this.controlPanelForm.value.tempo = this.importedMidiTempo;
            this.configDataService.tempo = this.importedMidiTempo;
        }

        let trackNumber = 0;

        if(this.sequences && this.sequences.length > 0 && this.sequences[0].length != 0) {
            this.addTrack(this.importedMidiFileName);
            trackNumber = this.sequences.length - 1;
        } else {
            this.sequences = [];
        }

        this.sequences[trackNumber] = this.importedMidiSequence;
        this.tracks[trackNumber].sequence = this.importedMidiSequence;
        this.tracks[trackNumber].triggerNoteDraw();
        this.tracks[trackNumber].trackName = this.importedMidiFileName;
        this.selectedTrackNumber = trackNumber;
        this.refreshTrackView();
        this.refreshPianoRoll();
    }

    exportMidiAndLog() {
        var logs = this.configDataService.appLogs.slice();
        logs.pop();
        let finalSeparator = logs.lastIndexOf(this.configDataService.logSeparator);
        let lastGenerationLog = logs.slice(finalSeparator + 1).join("\n");

        var timestamp = this.niceDateTimeStamp();
        this.dawStateService.exportToMidi(this.configDataService.dawState).subscribe((data) => {
            this.downloadFile(data, 'audio/midi', 'composition-' + timestamp + '.midi');
            this.downloadFile(lastGenerationLog, 'text/plain;charset=utf-8', 'composition-' + timestamp + '.txt');
        });
    }

    exportToMidiWithLog() {
        this.updateDawState(this.exportMidiAndLog);
    }
}
