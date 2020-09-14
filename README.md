# GenerativeDAW

GenerativeDAW is an automated music composition tool.

Built with Flask, Angular 8, and Python 3. Tested with Jasmine. This project is in pre-release.

## Overview

GenerativeDAW is a digital audio workstation webapp that provides generative composition tools informed by music theory.

In contrast with similar generative tools out there, this application does not apply machine learning algorithms to generate music. Instead, constraints from classical music theory are applied to create randomized compositions that are inherently more musically sensible. After editing the result to taste, application state can be downloaded as a MIDI file and loaded into a conventional DAW like Logic Pro X or FL.


#### Music generation features:
- Generates melodies and chord progressions in a given key, scale, and octave
- Configurable chance to use a chord leading chart to select the next chord in progression
- Configurable chance to use a chord voicing from the included library of tasteful voicings
- Configure probabilities for the inclusion of non-diatonic chords, borrowed chords, altered dominant chords
- Logging panel in UI provides step-by-step explanations of the result generation method

#### General features:
- Add tracks and edit notes in a resizable piano roll window
- Chord can be rolled bottom-up during playback with a configurable note roll offset. This feature is useful for gauging chord quality
- Export application state to a MIDI file and a logs file explaining the generation pathway
- UI automatically labels chords with names and scale degrees


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

#### Discussion
"People respond favorably to music that is well-structured." - The Jazz Piano Book by Mark Levine (97)

This app bakes ideas from melody theory, classical chord approaches, and jazz theory into a set of configurable music generation algorithms. For the most part, these algorithms resemble processes that I use as a composer -- the process of selecting a key, scale, set of chord voicings of interest, chord progression form, selecting melody notes from the chords, and other techniques. As a result, the music that this application outputs is highly structured, and often resembles the set of pieces that a human reading a textbook on such theory might compose.

Much of the composition process I use as a human is automatable -- picking a voicing to use, translating chord numerals to notes, testing out chord progressions that apply pop progressions in a given scale domain. As a piano player, recalling voicings of interest and transposing them to the root of interest while creating a chord progression is a process that often feels less about taste and more about memorization. I designed this tool with that problem in mind, and I'm surprised with the quality of the compositions that this program has been creating for me for so far. I hope to grow the codebase as I learn new composition techniques from contemporary music.
