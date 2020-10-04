import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';

import { WebAudioPianoRollComponent } from './webaudio-pianoroll.component';

@NgModule({
  declarations: [ WebAudioPianoRollComponent ],
  exports: [ WebAudioPianoRollComponent ],
  imports: [ CommonModule ],
  schemas: [ CUSTOM_ELEMENTS_SCHEMA ]
})
export class WebAudioPianoRollModule {}