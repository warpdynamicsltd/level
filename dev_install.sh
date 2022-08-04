if which python3 > /dev/null
then
    python3 -m pip install -e .
    level setup .
    level test
    level install test_include
    exit
fi

if which python > /dev/null
then
    python -m pip install -e .
    level setup .
    level test
    level install test_include
    exit
fi