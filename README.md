# GenerativeDAW

### A mobile-friendly webapp focused on generative music composition. 

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

#### Feature goals for version 0.01:
- A responsive DAW-like interface wrapped in a modern Bootstrap layout
- An editable piano roll that can play back melodies
- A sampler with stock drum sounds that can play back rhythms
- Ability to bounce and export tracks to .wav files