if which python3 > /dev/null
then
    python3 -m pip install .
    level setup .
    exit
fi

if which python > /dev/null
then
    python -m pip install .
    level setup .
    exit
fi