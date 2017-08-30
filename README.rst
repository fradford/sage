Sage
====

Sage is a python project that aims to convert an input image into some kind of
pleasing "music" and to convert music files back into images.

Why the name Sage?
------------------

Sound + Image = Sage

Usage
-----
:Command:             ``python sage/src/main.py [-h | --help] [-f | --framerate FRAMERATE]
                      [-l | --duration DURATION] [-c | --chunksize CHUNKSIZE] [-t | --threading] mode infile outfile``
:mode:                0: Convert image into sound.
                          1: Convert sound into image. Doesn't really work currently.
:infile:              Path to the input file, should be an image if mode is 0 or a sound file if mode
                      is 1.
:outfile:             Path to the output file, must be a .wav file if mode is 0 or an image file if
                      mode is 1.
:-h:                  Shows usage help with brief descriptions of each option
:-f FRAMERATE:        Specifies the bitrate of the output file in hertz. Default is 48,000Hz.
:-l DURATION:         Specifies the length of the output file in seconds. Default is 180.
:-c CHUNKSIZE:        Number of frames to hold in memory. Default is 1,000,000.
:-t THREADING:        If specified multiprocessing is enabled. Speeds up large images massively, can cause significant
                      delay on small images due to I/O overhead and low individual processing time.
