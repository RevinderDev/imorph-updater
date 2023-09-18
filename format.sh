#!/bin/bash
SOURCE="imorph_updater"

run_command() {
    echo -e "\n$@" 
    command $@
}

run_command black $SOURCE
run_command ruff $SOURCE --fix
