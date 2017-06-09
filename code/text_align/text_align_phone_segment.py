# encoding=UTF-8

import os
import io
import sys
import re
import time
from collections import deque
import threading

# ************Split sentence by using punctuation.************
def Sentence_Split(line):
    if not re.search("[\u4e00-\u9fa5]+", line): # if no chinese in string, then return.
        return [];
    
    pattern=re.compile("[^0-9０-９\u4e00-\u9fa5\,\.\!\:\?\;\，\。\！\：\？\；\…]+");
    line=pattern.sub("", line);
    line_split=re.split("[\,\.\!\:\?\;\，\。\！\：\？\；\…]+", line);
    return line_split;

# ************Store segments into list.************
def Pre_Process(lex_file, origin_file, reco_file, lex_dict, origin_list, reco_list):
    origin_fp=open(origin_file, "r", encoding="UTF-8");
    for line in origin_fp:
        line=line.strip();
        if len(line)>0:
            origin_list.append(line);
    origin_fp.close();

    reco_fp=open(reco_file, "r", encoding="UTF-8");
    for line in reco_fp:
        line=line.strip();
        if len(line)==0:
            continue;
        line_split=re.split(" +|\t+", line);
        seg_list=Sentence_Split(line_split[1]);
        for seg in seg_list:
            if len(seg)>0:
                reco_list.append(tuple([seg, line_split[0]]));
    reco_fp.close();

    # Store the lexicon into a dictionary.
    lex_fp=open(lex_file, "r",encoding="UTF-8");
    for line in lex_fp:
        line=line.strip();
        if len(line)==0:
            continue;
        line_split=re.split(" +|\t+", line);
        if len(line_split[0])==1:
            lex_dict[line_split[0]]=line_split[1:];
    lex_fp.close();
        

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

    #dist_matrix[x][y]=dp[s1_len][s2_len];
    max_len=max(s1_phone_len, s2_phone_len);
    if(max_len>0):
        return float(dp[s1_phone_len][s2_phone_len])/max_len;
    else:
        return sys.maxsize;

### ************Calculate the matrix of edit distance in different segments.************ 
##def Cal_Dist_Matrix(origin_list, reco_list, dist_matrix, lex_dict):
##    thread_list=[];
##    for i in range(len(origin_list)):
##        for j in range(len(reco_list)):
##            dist_matrix[i][j]=Cal_Edit_Dist(origin_list[i], reco_list[j][0], lex_dict);
##            #t=threading.Thread(target=Cal_Edit_Dist, args=(origin_list[i], reco_list[j][0], dist_matrix, i, j));
##            #t.setDaemon(True);
##            #thread_list.append(t);
##                
##    #for t in thread_list:
##    #    t.start();
##
##    #for t in thread_list:
##    #    t.join();

# ************After the force alignment, the sentence from original text were writed into file.************
def Force_Alignment(origin_list, reco_list, align_file, dist_limit, lex_dict):
    origin_len=len(origin_list);
    reco_len=len(reco_list);

    # Find the shortest path in the matirx of edit distance by using dynamic programming. 
    dp=[[sys.maxsize for _ in range(reco_len)] for _ in range(origin_len)];
    pre=[[[-1, -1] for _ in range(reco_len)] for _ in range(origin_len)];

    dp[0][0]=Cal_Edit_Dist(origin_list[0], reco_list[0][0], lex_dict);
    
    for i in range(1, origin_len):
        dp[i][0]=dp[i-1][0]+Cal_Edit_Dist(origin_list[i], reco_list[0][0], lex_dict);
        pre[i][0]=[i-1, 0];

    for j in range(1, reco_len):
        dp[0][j]=dp[0][j-1]+Cal_Edit_Dist(origin_list[0], reco_list[j][0], lex_dict);
        pre[0][j]=[0, j-1];

    for i in range(1, origin_len):
        for j in range(1, reco_len):
            pre[i][j]=min([i-1, j], [i, j-1], [i-1, j-1], key=lambda x:dp[x[0]][x[1]]);
            dp[i][j]=Cal_Edit_Dist(origin_list[i], reco_list[j][0], lex_dict)+min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]);

    # Get the recognition sentence id and corresponding original sentence.
    pos=[origin_len-1, reco_len-1];
    align_list=[deque() for _ in range(reco_len)];
    while pos[0]>=0 and pos[1]>=0:
        align_list[pos[1]].appendleft(pos[0]);
        pos=pre[pos[0]][pos[1]];

    align_fp=open(align_file, "w", encoding="UTF-8");
    pre_id="";
    origin_str="";
    reco_str="";
    out_str="";
    for i in range(reco_len):
        temp_reco_str=reco_list[i][0];
        temp_list=[];
        for index in align_list[i]:
            temp_list.append(origin_list[index]);
            
        temp=",".join(temp_list);
        temp_origin_str="".join(temp_list);
        
        if pre_id!=reco_list[i][1]:
            dist=Cal_Edit_Dist(origin_str, reco_str, lex_dict);
            #print(dist);
            if pre_id!="" and dist<dist_limit: # Edit distance of the sentence is less than dist_limit. 
                #align_fp.write(origin_str+"\n");
                #align_fp.write(reco_str+"\n");
                align_fp.write(out_str+"。\n");
            out_str=reco_list[i][1]+" "+temp;
            origin_str="";
            reco_str="";
            pre_id=reco_list[i][1];
        else:
            out_str+="，"+temp;
            
        origin_str+=temp_origin_str;
        reco_str+=temp_reco_str;

    dist=Cal_Edit_Dist(origin_str, reco_str, lex_dict);
    if pre_id!="" and dist<dist_limit:
        #align_fp.write(origin_str+"\n");
        #align_fp.write(reco_str+"\n");
        align_fp.write(out_str+"。");
            
    align_fp.close();

def main():
    if len(sys.argv)!=6:
        print('Usage: python3 ' + sys.argv[0] + ' lexicon original_text reco_text align_text dist_limit\n');
        sys.exit(2);
        
    start=time.time();

    lex_file=sys.argv[1];
    origin_file=sys.argv[2];
    reco_file=sys.argv[3];
    align_file=sys.argv[4];
    dist_limit=float(sys.argv[5]);

    lex_dict=dict();
    origin_list=[];
    reco_list=[];
    
    
    pre_start=time.time();
    Pre_Process(lex_file, origin_file, reco_file, lex_dict, origin_list, reco_list);
    pre_end=time.time();
    print("Pre_Process Time: {}s".format(pre_end-pre_start));
    
##    dist_matrix=[[sys.maxsize for _ in range(len(reco_list))] for _ in range(len(origin_list))];
##
##    dist_start=time.time();
##    Cal_Dist_Matrix(origin_list, reco_list, dist_matrix, lex_dict);
##    dist_end=time.time();
##    print("Cal_Dist_Matrix Time: {}s".format(dist_end-dist_start));

    align_start=time.time();
    Force_Alignment(origin_list, reco_list, align_file, dist_limit, lex_dict);
    align_end=time.time();
    print("Force_Alignment Time: {}s".format(align_end-align_start));

    end=time.time();
    print("Total Time: {}s".format(end-start));

if __name__=="__main__":
    main();

