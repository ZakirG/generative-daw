import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { BrowserModule, Title } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { TrackComponent } from './track.component';
import { PianoRollComponent } from './piano-roll.component';
import { WebAudioPianoRollComponent } from './webaudio-pianoroll.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { MatMenuModule } from '@angular/material/menu';
import { MatIconModule } from '@angular/material/icon';

@NgModule({
  declarations: [
    AppComponent,
    TrackComponent,
    PianoRollComponent,
    WebAudioPianoRollComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    NoopAnimationsModule,
    MatMenuModule,
    MatIconModule,
  ],
  providers: [Title],
  bootstrap: [AppComponent],
  entryComponents: [ TrackComponent, PianoRollComponent, WebAudioPianoRollComponent ],
  schemas: [ CUSTOM_ELEMENTS_SCHEMA ]
})

export class AppModule { }
