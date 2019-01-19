#!/bin/sh

# Usage:
#   make.sh clean
#   make.sh build

case $1 in
    build)
            pyinstaller pyle.spec
            read
            ;;
    clean)
            rm -rf ./build/
            rm -rf ./dist/
            ;;
    *)
            echo "Unknown: $1"
            read
            ;;
esac
