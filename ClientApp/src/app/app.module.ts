import { NgModule, ViewContainerRef } from '@angular/core';
import { BrowserModule, Title } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { TrackComponent } from './track.component';
import { PianoRollComponent } from './piano-roll.component';

@NgModule({
  declarations: [
    AppComponent,
    TrackComponent,
    PianoRollComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule
  ],
  providers: [Title],
  bootstrap: [AppComponent],
  entryComponents: [ TrackComponent, PianoRollComponent ],
  exports: [ TrackComponent ]
})

export class AppModule { }
