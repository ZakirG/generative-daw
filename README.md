# GenerativeDAW

GenerativeDAW is a digital audio workstation webapp that provides generative composition tools informed by music theory.

Built with Flask, Angular 8, and Python 3. Tested with Jasmine. This project is in pre-release.

## Overview

GenerativeDAW is a suite of tools for automated music composition.

In contrast with similar generative tools out there, this application does not apply machine learning algorithms to generate music. Instead, constraints from classical music theory are applied to create randomized compositions that are inherently more musically sensible. After editing the result to taste, application state can be downloaded as a MIDI file and loaded into a conventional DAW like Logic Pro X or FL.

#### General features:
- Add tracks and edit notes in a resizable piano roll window
- Export application state to a MIDI file
- Automatic chord labeling with common names and scale degrees
- Logging panel in UI provides step-by-step explanations of the result generation method

#### Music generation features so far:
- Generate & play back random melodies and chord progressions in a key, scale, and octave of choice
- Chord progressions can be constrained to follow classical chord leading
- Specify allowed chord sizes in generated output
- Option to disallow consecutive identical notesets

<!-- <img src="./screenshots/desktopScreenshot.png" alt="App Screenshot on Desktop" width="850"/>  -->

<img src="./screenshots/desktopScreenshot2.png" alt="App Screenshot on Desktop" width="850"/>

## Installation

#### To build and run the application:
Install Python 3, <a href='https://angular.io/guide/quickstart'>Angular</a>, and <a href="http://flask.pocoo.org/docs/1.0/installation/" target="_blank">Flask</a>. Clone the repo:
```
git clone https://github.com/ZakirG/generative-daw.git
```

In one terminal window, install dependencies and run the server application:
```
cd generative-daw/ServerApp
pip install -r requirements.txt
export FLASK_APP=main.py
export FLASK_ENV=development
flask run
```

In another terminal window, install dependencies and run the client application:
```
cd generative-daw/ClientApp
npm install
ng serve --open
```
A tab will automatically open in your default web browser at localhost:4200. 

#### Overview of technologies used:
- The client-side audio-manipulation application is an Angular app that uses the WebAudio API
- The server-side generative-composition tools are Python 3 in a Flask framework
- The frontend layout makes use of Bootstrap 4, glyphicons from Bootstrap 3, and CSS3
- Client-side tests use the Jasmine framework and Karma test runner

#### Possible future development:
- Chord generation informed by voice leading principles
- Melody generation informed by stable/unstable tone analysis, structural tone/embellishment principles
- Rhythm generation informed by selections of culturally specific macro-rhythms (clave 3/2, clave 2/3, reggaeton bounce, trap rhythms, ...)
- Unit tests for the Flask/Python backend
- Draggable and resizable piano roll notes with http://interactjs.io/


#### Resources:
- Credit to <a href='https://ankursethi.in/2016/01/13/build-a-sampler-with-angular-2-webaudio-and-webmidi-lesson-1-introduction-to-the-webaudio-api/'>Ankur Sethi</a>
for their examples on audio manipulation in Angular. Code snippets of theirs are used in this application.

This project's interface is based on Logic Pro X.
