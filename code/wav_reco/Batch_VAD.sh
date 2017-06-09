#!/bin/bash

#source ../align.conf

wav_dir=$1
wav_vad_dir=$2

vad_dir=./butter-oil-tool

cd ${vad_dir}
for file in ${wav_dir}/*.wav
do
	name=${file##*/}
	name=${name%.*}
	echo ${file} > wavelist.txt
	rm segwav/*
	sh split_vad.sh
	rm -r ${wav_vad_dir}/${name}
	cp -r segwav ${wav_vad_dir}/${name}
done

