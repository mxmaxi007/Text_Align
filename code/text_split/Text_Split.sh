#! /bin/bash

#source ../align.conf

text_split_dir=$1
text_reco_dir_new=$2
lex=$3
origin_text=$4
text_reco_dir=$5

rm -r ${text_split_dir} ${text_reco_dir_new}
mkdir ${text_split_dir} ${text_reco_dir_new}
python3 text_split.py ${lex} ${origin_text} ${text_reco_dir} ${text_split_dir} ${text_reco_dir_new}
