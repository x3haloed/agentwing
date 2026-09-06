# Record reader
The documented `sh tools/verify.sh` currently fails outside the repository. Fix
its path handling (including spaces) using the maintained tools/check.py; do not
weaken that Python validator. records.lines(path) returns decoded UTF-8 lines,
stripping one leading BOM and line terminators, dropping lines that are empty
after stripping whitespace. Preserve spaces on nonblank lines. Accept LF/CRLF.
