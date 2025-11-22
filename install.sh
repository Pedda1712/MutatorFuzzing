#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Abort: Activate a VENV before installing"
    exit
fi

pip install -e $SCRIPT_DIR/Libraries/MutatorFuzzing

