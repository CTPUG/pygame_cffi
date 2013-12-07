#!/bin/bash

# This is a very "works on my machine" build script for the OSX display preinit
# magic.

echo "Compiling..."
gcc -c -fpic -I/usr/local/include/SDL pygame/sdlmain_osx.m -o pygame/sdlmain_osx.o
echo "Linking..."
gcc -lobjc -framework Cocoa -lSDL -shared -o pygame/libsdlmain_osx.so pygame/sdlmain_osx.o
echo "Cleanup..."
rm -rf pygame/__pycache__/
