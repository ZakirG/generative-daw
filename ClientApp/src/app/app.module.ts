import { NgModule, ViewContainerRef } from '@angular/core';
import { BrowserModule, Title } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { TrackComponent } from './track.component';

@NgModule({
  declarations: [
    AppComponent,
    TrackComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule
  ],
  providers: [Title],
  bootstrap: [AppComponent],
  entryComponents: [ TrackComponent ],
})

export class AppModule { }
