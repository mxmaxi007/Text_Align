#!/bin/bash

source_dir=/search/maxi/jiangshan/wav/wav_raw
target_dir=/search/maxi/jiangshan/wav/wav

for file in ${source_dir}/*.mp3
do
	name=${file##*/}
	name=${name%.*}
	ffmpeg -i ${file} -ar 16000 -ac 1 ${target_dir}/${name}.wav
done


