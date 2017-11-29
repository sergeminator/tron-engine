
CALL "C:\Program Files (x86)\Microsoft Visual Studio 14.0"\VC\vcvarsall.bat

cl /EHsc testbot.c tronlib.c /link  /SUBSYSTEM:CONSOLE

PAUSE
