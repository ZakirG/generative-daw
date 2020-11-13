import { Component, Input, Output, EventEmitter, ComponentFactoryResolver, ViewContainerRef, ViewChild, AfterViewInit, ElementRef } from '@angular/core';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { GenerationService } from './generation.service';
import { ConfigDataService } from './configdata.service';
import { interact } from '../assets/js/interact.min.js';
import { WebAudioPianoRollComponent } from './webaudio-pianoroll.component';
import { config } from 'process';
declare var require: any
const interact = require('interactjs');

@Component({
    selector:    'piano-roll',
    templateUrl: './piano-roll.component.html',
    providers:  [ ],
    styleUrls: ['./piano-roll.component.css', './app.component.css', './form-styles.css'],
})

export class PianoRollComponent implements AfterViewInit{
    @ViewChild("webAudioPianoRoll", { read: ViewContainerRef, static: true }) container : ViewContainerRef;
    webAudioPianoRoll : any;
    gridState = [];
    sequence = [];
    conformToKeyScale = true;
    generationType = 'chords';
    octaveUpperBound = 4;
    octaveLowerBound = 3;
    chordSizeLowerBound = 3;
    chordSizeUpperBound = 7;
    disallowRepeats = true;
    chanceToUseChordLeadingChart = 0.7;
    chanceToUseCommonVoicing = 0.95;
    chanceToUseCommonProgression = 0.3;
    chanceToAllowNonDiatonicChord = 0.001;
    chanceToAllowBorrowedChord = 0.001;
    chanceToAllowAlteredDominantChord = 0.7;

    maxToplineDistance = 3;
    // A ii-V-I voiced using three-note voicings changes two notes between ii and V
    // noteChangesLowerBound = 2;
    // noteChangesUpperBound = 5;
    toplineContour: any;
    
    notes: Array<any>;
    _ref: any;

    @Input() trackNumber: number;
    @Input() key: string;
    @Input() scale: Object;
    @Input() pianoRollOpen: boolean;

    @Output() noteDrawn = new EventEmitter<any>();
    @Output() newLogs = new EventEmitter<any>();
    @Output() triggerQuickGenerate = new EventEmitter<any>();

    @Output()
    trackChange = new EventEmitter<any>();

    constructor(
            public generationService: GenerationService, 
            public configDataService: ConfigDataService,
            public resolver: ComponentFactoryResolver) {
        this.gridState = this.configDataService.initializeEmptyGridState();
        this.scale = this.configDataService.scale;
        this.key = this.configDataService.key;
        this.toplineContour = this.configDataService.toplineContour;
    }

    ngOnInit() {
        interact('.resize-drag').draggable({
            onmove: window['dragMoveListener'],
            restrict: {
                restriction: 'parent',
                elementRect: { top: 0, left: 0, bottom: 1, right: 1 }
            },
        }).resizable({
            // resize from only top edge
            edges: { left: false, right: false, bottom: false, top: true },
            // keep the edges inside the parent
            restrictEdges: {
                outer: 'parent',
                endOnly: true,
            },

        inertia: true,
        }).on('resizemove', function (event) {
            var target = event.target,
            y = (parseFloat(target.getAttribute('data-y')) || 0);
            target.style.height = event.rect.height + 'px';
            y += event.deltaRect.top;
        });
    }

    ngAfterViewInit(){
        const factory = this.resolver.resolveComponentFactory(WebAudioPianoRollComponent);
        this.webAudioPianoRoll = this.container.createComponent(factory);
        this.webAudioPianoRoll.instance._ref = this.webAudioPianoRoll;
        this.webAudioPianoRoll.instance.trackNumber = this.trackNumber;
        this.webAudioPianoRoll.instance.noteDrawn.subscribe((event) => {
            this.registerNoteDrawn(event);
        });
        
        // this.loadWebAudioPianoRollScript();
    }

    registerNoteDrawn(event) {
        this.sequence = event['sequence'];

        // this.updateDawState();
        event['track'] = this.trackNumber;
        if(event['event'] == 'noteDrawn' && event['state']) {
            this.noteDrawn.emit(event);
        }
    }

    clearPianoRoll() {
        for (var i = 0; i < this.gridState.length; i++) {
            this.gridState[i]['timeStates'] = this.configDataService.makeEmptyTimeState();
        }
        this.webAudioPianoRoll.instance.clear();
        this.sequence = [];
        this.noteDrawn.emit({'event': 'clear', 'track' : this.trackNumber});
    }

    destroyReference() {
        this._ref.destroy();
    }

    generate(generationOptions, isQuickGenerate) {
        var generatedNotes = [];
        return this.generationService.generate(generationOptions).subscribe((data) => {
            generatedNotes = data['generationResult'];
            this.renderNotesDeprecated(generatedNotes);
            // this.noteDrawn.emit({'event': 'generation', 'track' : this.trackNumber});
            let logs = data['logs'];
            
            if(isQuickGenerate) {
                this.triggerQuickGenerate.emit({
                    'event' : 'triggerQuickGenerate',
                    'track' : this.trackNumber,
                    'logs' : logs
                });
            } else {
                this.noteDrawn.emit({'event': 'generation', 'track' : this.trackNumber});
                // let logs = data['logs'];
                this.newLogs.emit({'event': 'writeLogs', 'logs' : logs});
            }

            // let logs = data['logs'];
            // this.newLogs.emit({'event': 'writeLogs', 'logs' : logs});
        });
    }

    quickGenerate(formValue) {
        this.configDataService.appLogs = [];
        this.generate(formValue, true);
    }

    renderNotes(sequence) {
        this.webAudioPianoRoll.instance.renderNotes(sequence, false);
    }

    setSequence(input) {
        this.sequence = input;
    }

    // TODO: refactor
    renderNotesDeprecated(notesToRender) {
        this.clearPianoRoll();
        this.sequence = this.configDataService.convertNoteListToSequence(notesToRender);
        this.renderNotes(this.sequence);
        this.webAudioPianoRoll.instance.renderNotes(this.sequence, false);
    }

    refresh() {
        this.webAudioPianoRoll.instance.clear();
        this.renderNotes(this.sequence);
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
