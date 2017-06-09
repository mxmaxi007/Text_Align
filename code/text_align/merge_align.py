# encoding=UTF-8

import os
import io
import sys
import re
import time

def Merge(seg_file, sentence_file, target_file):
    id_dict=dict();
    
    seg_fp=open(seg_file, "r", encoding="UTF-8");
    for line in seg_fp:
        line=line.strip();
        line_split=re.split(" +|\t+", line);
        if line_split[0] not in id_dict:
            id_dict[line_split[0]]=line;
    seg_fp.close();

    sentence_fp=open(sentence_file, "r", encoding="UTF-8");
    for line in sentence_fp:
        line=line.strip();
        line_split=re.split(" +|\t+", line);
        if line_split[0] not in id_dict:
            id_dict[line_split[0]]=line;
    sentence_fp.close();

    target_fp=open(target_file, "w", encoding="UTF-8");
    for line in sorted(id_dict.values()):
        target_fp.write(line+"\n");
    target_fp.close();

def main():
    if len(sys.argv)!=4:
        print('Usage: python3 ' + sys.argv[0] + ' seg_align_text sentence_align_text target_text\n');
        sys.exit(2);
        

    seg_file=sys.argv[1];
    sentence_file=sys.argv[2];
    target_file=sys.argv[3];

    Merge(seg_file, sentence_file, target_file);

if __name__=="__main__":
    main();
