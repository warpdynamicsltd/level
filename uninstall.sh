if which python3 > /dev/null
then
    level clear -y
    python3 -m pip uninstall -y level
    exit
fi

if which python > /dev/null
then
    level clear -y
    python3 -m pip uninstall -y level
    exit
fi
