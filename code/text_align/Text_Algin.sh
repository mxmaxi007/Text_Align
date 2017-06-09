#! /bin/bash

limit=0.1
limit_char=0.6

origin=$1
reco=$2
align=$3

lex=$4

python3 text_align_phone_segment.py ${lex} ${origin} ${reco} align.txt.segment ${limit} &
python3 text_align_phone_sentence.py ${lex} ${origin} ${reco} align.txt.sentence ${limit} & 
python3 text_align_phone_char.py ${lex} ${origin} ${reco} align.txt.char ${limit_char} & 
 
wait


python3 merge_align.py align.txt.char align.txt.segment ch_seg.txt
python3 merge_align.py ch_seg.txt align.txt.sentence align.txt

cp align.txt ${align}
rm align.txt.segment align.txt.sentence align.txt.char ch_seg.txt align.txt

