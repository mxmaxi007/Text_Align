# encoding=UTF-8

import os
import io
import sys
import re
import time
from collections import deque
import threading
import copy

# ************ Remove Invalid Symbol.************
def Remove_Invalid_Symbol(line):
    #pattern=re.compile("[\s\'\"\,\.\/\\\;\:\<\>\?\\+\=\-\_\`\~\!\@\#\$\%\^\&\(\)]+");
    pattern=re.compile("[^\u4e00-\u9fa5\,\.\!\:\?\;\，\。\！\：\？\；\…\-\、\—]+");
    return pattern.sub("", line);

# ************Split sentences into segments.************
def Sentence_Split(line):
    pattern=re.compile("[^\u4e00-\u9fa5\,\.\!\:\?\;\，\。\！\：\？\；\…\-\、\—]+");
    line=pattern.sub("", line);
    line_split=re.split("[\,\.\!\:\?\;\，\。\！\：\？\；\…\-\、\—]+", line);
    return line_split;

# ************Split sentence into chars.************
def Char_Split(line):
    if not re.search("[\u4e00-\u9fa5]+", line): # if no chinese in string, then return.
        return [];
    
    #pattern=re.compile("[^a-z0-9ａ-ｚ０-９\u4e00-\u9fa5\,\.\!\:\?\;\，\。\！\：\？\；]+");
    pattern=re.compile("[^0-9０-９\u4e00-\u9fa5]+");
    result=pattern.sub("", line);
    
    return list(result);

# ************Preprocess the original file and recognition file.************
def Pre_Process(lex_file, origin_file, reco_dir_path, lex_dict, origin_seg_list, reco_dict, reco_seg_dict):
    # Store the lexicon into a dictionary.
    lex_fp=open(lex_file, "r", encoding="UTF-8");
    for line in lex_fp:
        line=line.strip();
        if len(line)==0:
            continue;
        line_split=re.split(" +|\t+", line);
        if len(line_split[0])==1:
            lex_dict[line_split[0]]=line_split[1:];
    lex_fp.close();

    clean_text="";
    origin_fp=open(origin_file, "r", encoding="UTF-8");
    for line in origin_fp:
        line=line.strip();
        if len(line)==0:
            continue;
        seg_list=Sentence_Split(line);
        for seg in seg_list:
            if len(seg)>0:
                origin_seg_list.append(seg);
    origin_fp.close();
    #origin_seg_list.extend(Sentence_Split(clean_text));
    print("Length of Original Text Segment: {}".format(len(origin_seg_list)));


    reco_dir=os.listdir(reco_dir_path);
    for file_name in reco_dir:
        file_path=os.path.join(reco_dir_path, file_name);
        if os.path.isfile(file_path) and re.match(".*.txt", file_name):
            reco_list=[];
            reco_seg_list=[];
            fp=open(file_path, "r", encoding="UTF-8");
            for line in fp:
                line=line.strip();
                if len(line)==0:
                    continue;
                line_split=re.split(" +|\t+", line);
                if len(line_split)<=1:
                    continue;
                char_list=Char_Split(line_split[1]);
                reco_list.extend(char_list);
                if len(char_list)>0:
                    reco_seg_list.append([line_split[0], "".join(char_list)]);
            fp.close();
            reco_dict[file_name]=reco_list;
            reco_seg_dict[file_name]=reco_seg_list;

# ************Calculate the edit distance of the phone sequences between s1 and s2 .************
def Cal_Edit_Dist(s1, s2, lex_dict):
    s1_len=len(s1);
    s2_len=len(s2);

    s1_phone=[];
    for i in range(s1_len):
        if s1[i] in lex_dict:
            s1_phone.extend(lex_dict[s1[i]]);
    s1_phone_len=len(s1_phone);
        
    s2_phone=[];
    for j in range(s2_len):
        if s2[j] in lex_dict:
            s2_phone.extend(lex_dict[s2[j]]);
    s2_phone_len=len(s2_phone);
    
    dp=[[0 for _ in range(s2_phone_len+1)] for _ in range(s1_phone_len+1)];

    for i in range(1, s1_phone_len+1):
        dp[i][0]=dp[i-1][0]+1;

    for j in range(1, s2_phone_len+1):
        dp[0][j]=dp[0][j-1]+1;

    for i in range(1, s1_phone_len+1):
        for j in range(1, s2_phone_len+1):
            if s1_phone[i-1]==s2_phone[j-1]:
                dp[i][j]=dp[i-1][j-1];
            else:
                dp[i][j]=1+min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]);

    return dp[s1_phone_len][s2_phone_len];
    #dist_matrix[x][y]=dp[s1_len][s2_len];
    #max_len=max(s1_phone_len, s2_phone_len);
    #if(max_len>0):
    #    return float(dp[s1_phone_len][s2_phone_len])/max_len;
    #else:
    #    return sys.maxsize;

# ************Detect the start point of the recognition text.************  
def Detect_Valid_Segment(line, seg_list, lex_dict, direction):
    front_limit=20;
    seg_list_len=len(seg_list);
    dist_limit=0.5;
    letter_limit=2;

    if seg_list_len<front_limit:
        return -1;
    
    if direction:
        for i in range(front_limit):
            length=min(len(line), len(seg_list[i]));
            if length>letter_limit and Cal_Edit_Dist(line[:length], seg_list[i][:length], lex_dict)/float(length)<dist_limit:
                return i;
    else:
        for i in range(seg_list_len-1, seg_list_len-front_limit-1, -1):
            length=min(len(line), len(seg_list[i]));
            if length>letter_limit and Cal_Edit_Dist(line[-length:], seg_list[i][-length:], lex_dict)/float(length)<dist_limit:
                return i;
    return -1;

# ************Find the split point of original text by using dynamic programming.************
def Text_Split(lex_dict, origin_seg_list, reco_dict, reco_seg_dict, split_dir_path, reco_dir_new_path):
    for key in sorted(reco_dict.keys()):
        cur_pos=0;
        min_pos=0;
        min_dist=sys.maxsize;
        reco_list=reco_dict[key];
        reco_len=len(reco_list);
        origin_len=0;
        
        pre_dp=[val for val in range(reco_len+1)];
        dp=[0 for _ in range(reco_len+1)];
        char_limit=100;
        phone_dist=1;

        print("Length of Recognition Text: {}".format(reco_len));
        while cur_pos<len(origin_seg_list) and origin_len-reco_len<char_limit:    
            for i in range(len(origin_seg_list[cur_pos])):
                for j in range(reco_len+1):
                    if j==0:
                        dp[j]=pre_dp[j]+1;
                    else:
                        dist=Cal_Edit_Dist(origin_seg_list[cur_pos][i], reco_list[j-1], lex_dict);
                        if dist<=phone_dist:
                            dp[j]=pre_dp[j-1];
                        else:
                            dp[j]=1+min(pre_dp[j], dp[j-1], pre_dp[j-1]);

                origin_len+=1;
                pre_dp=copy.deepcopy(dp);

            if pre_dp[reco_len]<min_dist:
                min_dist=pre_dp[reco_len];
                min_pos=cur_pos;
            cur_pos+=1;

           
        if origin_seg_list:
            min_pos+=2;
            result_list=[];
            for i in range(0, min_pos+1):
                result_list.append(origin_seg_list[i]);

                
            # Find the start point of recognition text and original text.
            origin_pos=0;
            reco_pos=0;
            for i in range(len(reco_seg_dict[key])):
                origin_pos=Detect_Valid_Segment(reco_seg_dict[key][i][1], result_list, lex_dict, True);
                if origin_pos!=-1:
                    reco_pos=i;
                    break;

            if origin_pos!=-1:
                del result_list[:origin_pos];
                del reco_seg_dict[key][:reco_pos];
                del origin_seg_list[:origin_pos];

            # Find the end point of recognition text and original text.
            for i in range(len(reco_seg_dict[key])-1, -1, -1):
                origin_pos=Detect_Valid_Segment(reco_seg_dict[key][i][1], result_list, lex_dict, False);
                if origin_pos!=-1:
                    reco_pos=i;
                    break;

            if origin_pos!=-1:
                #del result_list[origin_pos+1:];
                #del reco_seg_dict[key][reco_pos+1:];
                del origin_seg_list[:origin_pos+1];
            else:
                del origin_seg_list[:min_pos+1];

            file_path=os.path.join(split_dir_path, key);
            fp=open(file_path, "w", encoding="UTF-8");
            for line in result_list:
                fp.write(line+"\n");
            fp.close();

            file_path=os.path.join(reco_dir_new_path, key);
            fp=open(file_path, "w", encoding="UTF-8");
            for val in reco_seg_dict[key]:
                fp.write(val[0]+" "+val[1]+"\n");
            fp.close();          
            
        print("{} finished".format(key));
    
    
def main():
    if len(sys.argv)!=6:
        print('Usage: python3 ' + sys.argv[0] + ' lexicon original_text reco_dir split_dir reco_dir_new\n');
        sys.exit(2);
        
    start=time.time();

    lex_file=sys.argv[1];
    origin_file=sys.argv[2];
    reco_dir_path=sys.argv[3];
    split_dir_path=sys.argv[4];
    reco_dir_new_path=sys.argv[5];

    lex_dict=dict();
    origin_seg_list=[];
    reco_dict=dict();
    reco_seg_dict=dict();

    pre_start=time.time();
    Pre_Process(lex_file, origin_file, reco_dir_path, lex_dict, origin_seg_list, reco_dict, reco_seg_dict);
    pre_end=time.time();
    print("Pre_Process Time: {}s".format(pre_end-pre_start));

    split_start=time.time();
    Text_Split(lex_dict, origin_seg_list, reco_dict, reco_seg_dict, split_dir_path, reco_dir_new_path);
    split_end=time.time();
    print("Text_Split Time: {}s".format(split_end-split_start));    

    end=time.time();
    print("Total Time: {}s".format(end-start));


if __name__=="__main__":
    main();
