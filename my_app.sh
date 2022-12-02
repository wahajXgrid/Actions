#!/bin/bash
# Add this before your app's code
PYTHON_REF=$(source ./check_python.sh) # change path if necessary
if [[ "$PYTHON_REF" == "NoPython" ]]; then
    echo "Python3.7+ is not installed."
    exit
fi

# This is your app
# PYTHON_REF is python or python3
$PYTHON_REF -c "print('hello from python 3.7+')";