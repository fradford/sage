Sage
====

Sage is a python project that aims to convert an input image into some kind of
pleasing "music" and to convert music files back into images.

Why the name Sage?
------------------

It's simply the most pleasing combination of sound and image I could think of.

Usage
-----
:Command:             ``python sage/src/main.py [-h | --help] [-a | --all_pixels]
                      [-d | --disk_db] [-f | --framerate FRAMERATE]
                      [-l | --note_length NOTE_LENGTH] mode infile outfile``
:-h:                  Shows usage help with brief descriptions of each option
:-a:                  If specified all pixels in an image will be used to generate frequencies,
                      otherwise rows in the image are averaged and used as frequencies. If this is
                      specified the process will take considerably longer.
:-d:                  If specified the storage database will be saved to the disk. Slower than storing
                      in memory but the process will not stop due to a memory error. Usually only
                      necessary on larger files or when -a is specified. If the process stops due to
                      a memory error try running it again with this specified.
:-f FRAMERATE:        Specifies the bitrate of the output file in hertz, default is 48000Hz.
:-l NOTE_LENGTH:      Specifies the length of each note in seconds, default is 1/4.
:mode:                0: Convert image into sound.
                      1: Convert sound into image.
:infile:              Path to the input file, should be an image if mode is 0 or a sound file if mode
                      is 1.
:outfile:             Path to the output file, must be a .wav file if mode is 0 or an image file if
                      mode is 1.
