#!/bin/bash

PIP=pip

if ! $PIP > /dev/null
then
    echo "package installer pip required"
    exit
fi

PIP=pip3

if ! $PIP > /dev/null
then
    echo "package installer pip required"
    exit
fi

$PIP install -e .
level setup .
level test
level install test_include