#!/bin/bash
EXIT_CODE_FLAG=0
SOURCE="imorph_updater"

run_command() {
    echo -e "\n$@" 
    command $@
    if [ $? -ne 0 ]; then
        EXIT_CODE_FLAG=1
    fi
}

run_command black --check $SOURCE
run_command mypy $SOURCE
run_command ruff check $SOURCE

exit $EXIT_CODE_FLAG