# GenerativeDAW

### A Digital Audio Workstation webapp focused on generative music composition. 

#### Built with Flask, Angular 2, and Python 3.

This project will be a <a href='https://en.wikipedia.org/wiki/Digital_audio_workstation'>digital audio workstation (DAW)</a> webapp that provides a suite of tools
for <a href='https://en.wikipedia.org/wiki/Generative_music' target='_blank'>generative music composition</a>, in which the software system itself will compose the music.

The primary use case: a composer specifies generative settings they are interested in, 
which the software system responds to with a randomized piece of music. The composer then
edits the result to their taste and continues work on the composition in their usual music creation
domain of choice (an instrument, sheet music, or a more high-powered DAW).

#### To build and run the application:
Install Python 3 and <a href="http://flask.pocoo.org/docs/1.0/installation/" target="_blank">Flask</a> and then run
```
git clone https://github.com/ZakirG/generative-daw.git
cd generative-daw/ClientApp
ng serve --open
```

#### Current functionalities:
- A piano roll module where you can draw in melodies and chords
- A control bar with tempo selection and play/pause buttons

#### Overview of technologies used:
- The client-side audio-manipulation application is Angular 2 app that uses the WebAudio API
- The server-side generative-composition tools are Python 3 in a Flask framework
- The frontend design uses Bootstrap 4, glyphicons from Bootstrap 3, and CSS3

#### Feature goals for version 0.01:
- A responsive DAW-like interface wrapped in a modern Bootstrap layout
- An editable piano roll that can play back melodies
- A sampler with stock drum sounds that can play back rhythms
- Ability to bounce and export tracks to .wav files


Credit to <a href='https://ankursethi.in/2016/01/13/build-a-sampler-with-angular-2-webaudio-and-webmidi-lesson-1-introduction-to-the-webaudio-api/'>Ankur Sethi</a>
for their examples on audio manipulation in Angular 2; code snippets of theirs are used in this application.
