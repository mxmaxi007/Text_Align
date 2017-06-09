#! /bin/bash

pcm=$1
wav=$2

sox -t raw -c 1 -b 16 -r 16000 -e signed-integer ${pcm} ${wav}

