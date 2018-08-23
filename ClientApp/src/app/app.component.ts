import { Component, ViewChild, AfterViewInit } from '@angular/core';
import { Title }     from '@angular/platform-browser';

import { PianoRollComponent } from './piano-roll.component';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css']
})

export class AppComponent {
    private audioContext: AudioContext;
    @ViewChild(PianoRollComponent) pianoRoll;

    public constructor(private titleService: Title ) { }

    public setTitle( newTitle: string) {
        this.titleService.setTitle( newTitle );
    }

    ngOnInit() {
        this.setTitle('GenerativeDAW');
        this.audioContext = new AudioContext();
        this.tempo = 167;
        this.tracks = [];

        this.fetchSample().then(audioBuffer => {
            this.loadingSample = false;
            this.audioBuffer = audioBuffer;
        })
        .catch(error => throw error);

    }

    ngAfterViewInit() {
        this.tracks[0] = this.pianoRoll.gridState;
        console.log("tracks: ", this.tracks);
    }

    togglePlayState() {
        console.log('play');
        this.playNote();
    }

    playNote() { //noteName : string, noteOctave : number) {
        let bufferSource = this.audioContext.createBufferSource();
        bufferSource.buffer = this.audioBuffer;
        bufferSource.connect(this.audioContext.destination);
        bufferSource.start(0);
    }

    fetchSample(): Promise<AudioBuffer> {
        return fetch('assets/c3.wav')
            .then(response => response.arrayBuffer())
            .then(buffer => {
                return new Promise((resolve, reject) => {
                    this.audioContext.decodeAudioData(
                        buffer,
                        resolve,
                        reject
                    );
                })
            });
    }

}
