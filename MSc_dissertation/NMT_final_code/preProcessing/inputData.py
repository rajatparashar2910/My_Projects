import pandas as pd
import string
import os

def readLines(numLines):
    filedir = os.getcwd()
    engPath = os.path.join(filedir, 'preProcessing/IITB.en-hi.en')
    hinPath = os.path.join(filedir, 'preProcessing/IITB.en-hi.hi')
    eng_sents = (open(engPath, encoding='utf-8', errors='ignore').read()).split("\n")[:-1]
    hi_sents = (open(hinPath, encoding='utf-8', errors='ignore').read()).split("\n")[:-1]

    lines = pd.DataFrame(columns=['eng', 'hindi'])

    lines.eng = eng_sents
    lines.hindi = hi_sents

    return lines[:numLines]