# encoding=UTF-8

import os
import io
import sys
import re
import time

def Remove_Invalid_Symbol(line):
    #pattern=re.compile("[^a-z0-9ａ-ｚ０-９\u4e00-\u9fa5\,\.\!\:\?\;\，\。\！\：\？\；]+");
    pattern=re.compile("[^\u4e00-\u9fa5]+");
    result=pattern.sub("", line);
    
    return result;

def Test_Result(true_file, align_file):
    true_dict=dict();
    
    true_fp=open(true_file, "r", encoding="UTF-8");
    for line in true_fp:
        line=line.strip();
        if len(line)==0:
            continue;
        line_split=re.split(" +|\t+", line);
        result=Remove_Invalid_Symbol("".join(line_split[1:]));
        if len(result)>0:
            true_dict[line_split[0]]=result;
    true_fp.close();

    right_num=0;
    align_num=0;
    align_fp=open(align_file, "r", encoding="UTF-8");
    for line in align_fp:
        line=line.strip();
        if len(line)==0:
            continue;
        line_split=re.split(" +|\t+", line);
        result=Remove_Invalid_Symbol("".join(line_split[1:]));
        if line_split[0] in true_dict:
            if result==true_dict[line_split[0]]:
                right_num+=1;
            else:
                print(line_split[0]);
                print(true_dict[line_split[0]]);
                print(result);
        align_num+=1;
    align_fp.close();

    print("Accuracy: {}".format(float(right_num)/align_num));
    print("Alignment Proportion: {}".format(float(right_num)/len(true_dict)));

def main():
    if len(sys.argv)!=3:
        print('Usage: python3 ' + sys.argv[0] + ' true_text algin_text\n');
        sys.exit(2);
        
    start=time.time();

    true_file=sys.argv[1];
    align_file=sys.argv[2];

    Test_Result(true_file, align_file);


if __name__=="__main__":
    main();
