# Music-Metadata
Personal multiprocess program to update song metadata (song, author, etc) for all flac files in a directory, by parsing their filename.

# Expectations
1. Python 3.7+
2. A shell that supports the `ls` command. (e.g. BASH, SH)
3. A shell that can use command `mid3v2`, which comes via installation of one of the following packages, `python-mutagen` or `python3-mutagen`. \
(e.g. on Ubuntu use `apt-get update -y`, and then `apt install python-mutagen`, but if that fails then try `apt install python3-mutagen`)
4. Flac files to have filename format of `Song_-_Artist_-_{videoID}.flac` , \
though the `_-_{videoID}` part is optional.

# Syntax:
Assuming this repo is in your `~/Scipts/` directory, and your songs are in your `~/music/` directory, then use the following:

`python ~/Scipts/Music-Metadata/music_update.py ~/music/`

Though, if your songs are in the current directory, then you may omit the last part, `~/music/`.

