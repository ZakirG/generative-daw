import { NgModule } from '@angular/core';
import { BrowserModule, Title } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';

import { AppComponent } from './app.component';
import { PianoRollComponent } from './piano-roll.component';

@NgModule({
  declarations: [
    AppComponent,
    PianoRollComponent
  ],
  imports: [
    BrowserModule,
    FormsModule
  ],
  providers: [Title],
  bootstrap: [AppComponent]
})
export class AppModule { }
