#!/bin/bash

mkdir level
cp ../* level
cp -r ../level level/level
cp -r ../examples level/examples
cp -r ../include level/include
cp -r ../test_include level/test_include
cp -r ../scripts level/scripts


docker build --no-cache -t level .
docker run -it level
rm -rf level
