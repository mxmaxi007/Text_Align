# **************自动音库构建程序说明文档**************

## ***简单操作流程***

1. 配置code目录下align.conf中的变量。
2. 进入wav_reco目录，执行命令 sh run.sh，会在对应目录生成vad切分的语音文件，识别出的文本，以及识别文本中句子标签和语音文件路径的映射表。
3. 进入text_split目录，执行命令 sh run.sh，会在对应目录生成切分好的原文本，以及重新切分过的识别文本。
4. 进入text_align目录，执行命令 sh run.sh，会在对应目录生成对齐好的原文本，对齐文本中的句子标签和识别文本保持一致。

**Notes:**

- 上面流程中生成的文件名和目录名均与初始语音文件的名称保持一致。
- 切分程序是按照初始语音文件名称的字典序进行排列，所以需要让语音文件名的顺序和朗读顺序相同。
- 存在潜在的内存消耗过大的问题，20min的语音需要2G的内存，增加幅度为N^2，所以如果语音过长，可以将识别文本切分为多个文件，然后再进行步骤2的操作，但注意切分时仍然需要让文件名保持字典序。
- 上面步骤所有脚本的执行均需要进入指定目录后再执行，因为脚本中存在执行当前目录的其他程序的命令。

## ***code目录介绍***

### 1. 配置文件（align.conf）变量介绍  
*prefix*	语音和文本数据存储的总目录  
*text_name*		处理的小说名称，用于后面生成句子标签

*wav_dir*	小说语音文件存储的目录（wav格式）  
*wav_vad_dir*	经过vad切分后的语音文件存储的目录，存储格式为pcm  
*text_reco_dir*	识别文本的存储目录  
*text_wav_map_dir*	识别文本中句子标签和语音文件路径的映射表储的目录  

*lex*	发音词典（lexicon）文件路径  

*origin_text*	原小说文本的存储路径  
*text_split_dir*	进行切分后小说文本存储的目录  
*te	xt_reco_dir_new*	重新切分过的识别文本存储的目录  

*text_align_dir*	对齐好的原文本存储的目录  

### 2. 语音识别模块介绍（wav_reco目录）  
*run.sh*	总体执行脚本，其中包含需要导入的配置文件，默认为align.conf  
*butter-oil-tool*	vad切分工具的目录  
*Batch_VAD.sh*	批处理对一个目录中的语音文件进行vad切分，并将切分好的语音文件输出到指定目录  
*speech_recognition*	语音识别的接口程序  
*Batch_Reco.sh*	批处理对一个目录中切分好的语音进行识别，并将识别文本和映射表输出到指定目录  
*wav_trans.sh*	将pcm格式文件转为wav格式文件  
*Batch_Tran.sh*	将目录中的语音转为16khz，16bit，单声道的语音  


### 3. 文本切分模块介绍（text_split目录）  
*run.sh*	总体执行脚本，其中包含需要导入的配置文件，默认为align.conf  
*text_split.py*	文本切分程序  
*Text_Split.sh*	文本切分执行脚本  


#### 4. 文本对齐模块介绍（text_align目录）
*run.sh*	总体执行脚本，其中包含需要导入的配置文件，默认为align.conf  
*text_align_phone_char.py*	以字为基本单元的对齐程序  
*text_align_phone_segment.py*	以标点切分文本段为基本单元的对齐程序  
*text_align_phone_sentence.py*	以换行符切分文本段为基本单元的对齐程序  
*merge_align.py*	将两个对齐文本去重后合并为一个  
*Text_Algin.sh*	文本对齐执行脚本  


## ***data目录介绍***

data目录中存储了一个小说的原文本，原语音，vad切分后语音，识别文本，句子标签映射表，切分后的原文本，切分后的识别文本，以及对齐后的原文本，文件存储路径与配置文件中的默认设置相同。


