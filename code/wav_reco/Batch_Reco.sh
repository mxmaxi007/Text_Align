#! /bin/bash

#source ../align.conf
wav_vad_dir=$1
text_reco_dir=$2
text_wav_map_dir=$3
text_name=$4

for dir in ${wav_vad_dir}/*
do
	name=${dir##*/}
	rm ${text_reco_dir}/${name}.txt
	rm ${text_wav_map_dir}/${name}.map
	for file in ${dir}/*.pcm
	do
		id=${file##*/}
		id=${id%.*}	
		str=`./speech_recognition -d 32000 --ip 10.142.99.65 --port 8980 --wav ${file} -t -l 44 | iconv -f gbk -t utf-8`
		echo ${text_name}_${id} ${str} | awk '{print $1, $2}' >> ${text_reco_dir}/${name}.txt
		echo ${text_name}_${id} ${file} >> ${text_wav_map_dir}/${name}.map
	done
done


