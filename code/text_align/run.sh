#!/bin/bash

source ../align.conf

rm -r ${text_align_dir}
mkdir ${text_align_dir}
for file in ${text_split_dir}/*.txt
do
	name=${file##*/}
	#name=${name%.*}

	origin=${text_split_dir}/${name}
	reco=${text_reco_dir_new}/${name}
	align=${text_align_dir}/${name}
	sh Text_Algin.sh ${origin} ${reco} ${align} ${lex}
done

