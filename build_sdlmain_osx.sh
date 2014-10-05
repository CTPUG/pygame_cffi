#!/bin/bash

# This is a very "works on my machine" build script for the OSX display preinit
# magic.

echo "Compiling..."
gcc -arch i386 -arch x86_64 -c -fpic -I/usr/local/include/SDL `pwd`/pygame/sdlmain_osx.m -o `pwd`/pygame/sdlmain_osx.o
echo "Linking..."
gcc -arch i386 -arch x86_64 -lobjc -framework Cocoa -lSDL -shared -o `pwd`/pygame/libsdlmain_osx.so `pwd`/pygame/sdlmain_osx.o
echo "Cleanup..."
rm -rf pygame/__pycache__/
