import pandas as pd
import string
from string import digits
import re
import numpy as np


#Clean up sentences
def clean_sentences(lines):
    hindi_clean = []
    eng_clean = []

    #Cleaning up Hindi sentences
    for line in lines.hindi:
        nstr = re.sub('\s+_\s+[A-Za-z]','',line)
        nstr = re.sub('\(*\)*','',nstr)
        nstr = re.sub('%.*?[A-Za-z]','',nstr)
        nstr = re.sub('[A-Za-z]','',nstr)
        nstr = nstr.strip()
        nstr = re.sub('\s+',' ',nstr)
        hindi_clean.append(nstr)

    #Cleaning up English sentences
    for line in lines.eng:
        estr = re.sub('\s+_\s','',line)
        estr = re.sub(r'[^\x00-\x7F]+',' ', estr)
        estr = estr.strip()
        estr = re.sub('\s+',' ',estr)
        eng_clean.append(estr)

    #Loading clean sentences into dataframe
    lines.hindi = hindi_clean
    lines.eng = eng_clean

    #Converting to lower case
    lines.eng=lines.eng.apply(lambda x: x.lower())
    lines.hindi=lines.hindi.apply(lambda x: x.lower())

    #Remove punctuations
    exclude = set(string.punctuation)
    lines.eng=lines.eng.apply(lambda x: ''.join(ch for ch in x if ch not in exclude))
    lines.hindi=lines.hindi.apply(lambda x: ''.join(ch for ch in x if ch not in exclude))

    #Remove digits
    remove_digits = str.maketrans('', '', digits)
    lines.eng=lines.eng.apply(lambda x: x.translate(remove_digits))
    lines.hindi=lines.hindi.apply(lambda x: x.translate(remove_digits))

    return lines

#Function to pick sentences upto length 30
def pick_short_sent(lines, numSent=150000):

    englist = []
    hindilist = []

    for index, row in lines.iterrows():
        eng1 = row['eng']
        eng1 = eng1.strip()
        eng1 = re.sub('\s+',' ',eng1)
        hindi1 = row['hindi']
        hindi1 = hindi1.strip()
        hindi1 = re.sub('\s+',' ',hindi1)
        ctr1 = 0
        ctr2 = 0
        HinWords = hindi1.split(' ')
        for wrd in HinWords:
            newWrd1 = wrd.strip()
            if len(newWrd1) > 0:
                ctr1 = ctr1 + 1
        EngWords = eng1.split(' ')
        for wrd in EngWords:
            newWrd2 = wrd.strip()
            if len(newWrd2) > 0:
                ctr2 = ctr2 + 1
        if ctr1 <= 30 and ctr2 <= 30:
            englist.append(eng1)
            hindilist.append(hindi1)

    shortSent = pd.DataFrame(columns=['eng', 'hindi'])
    shortSent.eng = englist
    shortSent.hindi = hindilist
    return shortSent[:numSent]


#Function to generate tokens
def generate_tokens(procFrame):

    procFrame.eng = procFrame.eng.apply(lambda x : 'START_ '+ x + ' _END')

    all_eng_words=set()
    for eng in procFrame.eng:
        for word in eng.split(' '):
            if word not in all_eng_words:
                all_eng_words.add(word)
        
    all_hindi_words=set()
    for hindi in procFrame.hindi:
        for word in hindi.split(' '):
            if word not in all_hindi_words:
                all_hindi_words.add(word)

    return (procFrame, all_hindi_words, all_eng_words)

#Function to maximum length of sentences
def find_max_len(procFrame):
    
    hindi_length_list = []
    eng_length_list = []

    for l in procFrame.hindi:
        hindi_length_list.append(len(l.split(' ')))

    for l in procFrame.eng:
        eng_length_list.append(len(l.split(' ')))

    return (np.max(hindi_length_list) , np.max(eng_length_list))

#Function to create index
def create_index(procFrame):

    all_words = generate_tokens(procFrame)
    newFrame = all_words[0]
    all_hindi_words = all_words[1]
    all_eng_words = all_words[2]

    input_words = sorted(list(all_hindi_words))
    target_words = sorted(list(all_eng_words))

    num_encoder_tokens = len(all_hindi_words)
    num_decoder_tokens = len(all_eng_words)
    
    input_token_index = dict([(word, i) for i, word in enumerate(input_words)])
    target_token_index = dict([(word, i) for i, word in enumerate(target_words)])

    return (newFrame, num_encoder_tokens, num_decoder_tokens, input_token_index, target_token_index)


#Final Pre-processing
def pre_process_final(lines, numSent=150000):

    finalFrame = pd.DataFrame(columns=['eng', 'hindi'])

    clean_lines = clean_sentences(lines)
    finalFrame = pick_short_sent(clean_lines, numSent)

    indices = create_index(finalFrame)
    # num_encoder_tokens = indices[0]
    # num_decoder_tokens = indices[1]
    # input_token_index = indices[2]
    # target_token_index = indices[3]

    maxLen = find_max_len(indices[0])
    # maxHindi = maxLen[0]
    # maxEng = maxLen[1]

    return (maxLen, indices)

