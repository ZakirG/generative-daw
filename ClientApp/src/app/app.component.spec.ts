import { TestBed, async } from '@angular/core/testing';
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

    it('should initialize the app state correctly', async(() => {
        const fixture = TestBed.createComponent(AppComponent);
        const app = fixture.debugElement.componentInstance;
        app.ngOnInit();
        expect(app.tracks.length).toEqual(1);
        expect(app.tracks[0] instanceof TrackComponent).toBeTruthy();

        expect(app.queuedSounds.length).toEqual(0);

        expect(app.pianoRoll instanceof PianoRollComponent).toBeTruthy();

        expect(app.configDataService instanceof ConfigDataService).toBeTruthy();
        expect(app.configDataService.scale).toEqual({'name' : 'major', 'intervals' : [2,2,1,2,2,2,1 ], 'code' : 'maj' });
    }));

    it('should update configDataService on user input events', async(() => {
        const fixture = TestBed.createComponent(AppComponent);
        fixture.detectChanges();
        fixture.whenStable().then(() => {
            const app = fixture.debugElement.componentInstance;
            app.ngOnInit();
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
        });
    }));
});

