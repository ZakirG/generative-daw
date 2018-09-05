import { TestBed, async } from '@angular/core/testing';
import {BrowserDynamicTestingModule} from '@angular/platform-browser-dynamic/testing';

import { AppComponent } from './app.component';
import { NgModule, ViewContainerRef } from '@angular/core';
import { BrowserModule, Title } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { TrackComponent } from './track.component';
import { PianoRollComponent } from './piano-roll.component';

describe('AppComponent', () => {
  beforeEach(async(() => {
    TestBed.configureTestingModule({
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
    }).overrideModule(BrowserDynamicTestingModule, {
      set: {
        entryComponents: [TrackComponent, PianoRollComponent]
      }
    }).compileComponents();
  }));

  it('should create the app', async(() => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.debugElement.componentInstance;
    expect(app).toBeTruthy();
  }));

  it('should render default values in the control bar', async(() => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
    const compiled = fixture.debugElement.nativeElement;
    expect(compiled.querySelector('input#tempo').value).toEqual('100');
    expect(compiled.querySelector("select[name='key'] option:checked").textContent.trim()).toEqual('C');
    expect(compiled.querySelector("select[name='scale'] option:checked").textContent.trim()).toEqual('major');
  }));
});
