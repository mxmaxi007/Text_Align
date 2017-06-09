#! /bin/bash

source ../align.conf

sh Batch_VAD.sh $wav_dir $wav_vad_dir
sh Batch_Reco.sh $wav_vad_dir $text_reco_dir $text_wav_map_dir $text_name



