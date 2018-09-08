import { TestBed, async, ComponentFixture, ComponentFixtureAutoDetect } from '@angular/core/testing';
import {BrowserDynamicTestingModule} from '@angular/platform-browser-dynamic/testing';

import { AppComponent } from './app.component';
import { NgModule, ViewContainerRef } from '@angular/core';
import { BrowserModule, Title } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { TrackComponent } from './track.component';
import { PianoRollComponent } from './piano-roll.component';
import { ConfigDataService } from './configdata.service';
import { DawStateService } from './dawstate.service';

import {By} from "@angular/platform-browser";

describe('AppComponent', () => {
    let app: AppComponent;
    let fixture: ComponentFixture<AppComponent>;

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
            providers: [
                Title,
                { provide: ComponentFixtureAutoDetect, useValue: true }
            ],
            }).overrideModule(BrowserDynamicTestingModule, {
                set: {
                    entryComponents: [TrackComponent, PianoRollComponent]
                }
            }).compileComponents();

            fixture = TestBed.createComponent(AppComponent);
            app = fixture.componentInstance;
            fixture.detectChanges();
        }));

    it('should create the app', async(() => {
        expect(app).toBeTruthy();
    }));

    it('should render default values in the control bar', async(() => {
        expect(fixture.nativeElement.querySelector('input#tempo').value).toEqual('100');
        expect(fixture.nativeElement.querySelector("select[name='key'] option:checked").textContent.trim()).toEqual('C');
        expect(fixture.nativeElement.querySelector("select[name='scale'] option:checked").textContent.trim()).toEqual('major');
    }));

    it('should initialize the app state correctly', async(() => {
        expect(app.tracks.length).toEqual(1);
        expect(app.tracks[0] instanceof TrackComponent).toBeTruthy();

        expect(app.queuedSounds.length).toEqual(0);

        expect(app.pianoRoll instanceof PianoRollComponent).toBeTruthy();

        expect(app.configDataService instanceof ConfigDataService).toBeTruthy();
        expect(app.configDataService.scale).toEqual({'name' : 'major', 'intervals' : [2,2,1,2,2,2,1 ], 'code' : 'maj' });
    }));

    it('should update configDataService on user input events', async(() => {
        const controlPanelForm = app.controlPanelForm;

        expect(fixture.debugElement.componentInstance.configDataService.tempo).toEqual(100);
        expect(fixture.debugElement.componentInstance.configDataService.key).toEqual('C');

        controlPanelForm.controls['tempo'].setValue(150);
        controlPanelForm.controls['key'].setValue('D');

        const controlPanelFormElement = fixture.debugElement.query(By.css('#control-panel-form')).nativeElement;
        controlPanelFormElement.dispatchEvent(new Event('change'));
        fixture.detectChanges();
        fixture.whenStable().then(() => {
            expect(fixture.debugElement.componentInstance.configDataService.tempo).toEqual(150);
            expect(fixture.debugElement.componentInstance.configDataService.key).toEqual('D');
        });
    }));

    it('should create a TrackComponent on add-track-button click', () => {
        fixture.detectChanges();

        expect(app.tracks.length).toEqual(1);
        expect(app.tracks[0] instanceof TrackComponent).toBeTruthy();

        const el = fixture.debugElement.nativeElement;

        el.querySelector('#add-track-button').click();
        el.querySelector('#add-track-button').click();

        fixture.detectChanges();

        expect(app.tracks.length).toEqual(3);
        for (var trackNumber in app.tracks) {
            expect(app.tracks[trackNumber] instanceof TrackComponent).toBeTruthy();
        }
      });

});

