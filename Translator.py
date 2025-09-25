#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 23:42:15 2025

@author: f5cggsfwED
"""
max_chars = 6000
folder = ""
bookname = ""
translator1 = "translator"
translator2 = "translator2"

def log_events(text, path):
    if len(text)<200:
        print(text)
    try:
        f = open(path + "translator_log.txt", mode="r")
        f = open(path + "translator_log.txt", mode="a")
        f.write(text+"\n")
        f.close()   
    except:
        f= open(path + "translator_log.txt", mode="w")
        f.write(text+"\n")
        f.close()
    del f

def find_closest(sorted_list, target):
    closest = sorted_list[0]
    min_diff = abs(target - closest)

    for num in sorted_list:
        diff = abs(target - num)
        if diff < min_diff:
            closest = num
            min_diff = diff
        elif diff == min_diff and num < closest:
            # Optional: Break ties by choosing the smaller number
            closest = num

    return closest

def check_overlap(text1, text2):
    """
    This function does a very quick check if there are any overlapping pieces between texts.
    It returns true if overlap, false if not
    It just scans for 30 character overlaps every 50 characters
    This definitely isnt perfect but I would be expecting an identical text if translation fails so it works
    """
    text1 = text1.replace('\n', '')
    text2 = text2.replace('\n', '')
    text1 = text1.replace(chr(8220), '"')
    text1 = text1.replace(chr(8221), '"')
    text2 = text2.replace(chr(8220), '"')
    text2 = text2.replace(chr(8221), '"')
    text1 = text1.replace('»','"')
    text1 = text1.replace('«', '"')
    text2 = text2.replace('»','"')
    text2 = text2.replace('«', '"')
    L = len(text1)
    if L<100:
        return(False)
    for x in range(0,(L-L%50), 50):
        if text2.find(text1[x:(x+30)]) >= 0:
            return(True)
    return(False)

def split_text_by_sentence(text, n):
    """
    text is obviously the text you want to split up
    n is the number of characters per chunk
    This takes a large chunk of text, and returns a list of the chunk broken up into roughly equally sized fragments
    it is written so that fragments are always at the ends of sentences.

    """
    n = int(n)
    text = text+" "
    text = text.replace(chr(8220), '"')
    text = text.replace(chr(8221), '"')
    text = text.replace('»','"')
    text = text.replace('«', '"')
    n_chunks = int(len(text)/n)+1
    if n_chunks <= 1:
        return([text])
    positions = []
    start = 0
    while True:
        ind = start + text[start::].find(". ")
        if (ind-start) == -1:
            break
        positions.append(ind)
        start = ind+1
    start = 0
    while True:
        ind = start + text[start::].find("! ")
        if (ind-start) == -1:
            break
        positions.append(ind)
        start = ind+1
    start = 0
    while True:
        ind = start + text[start::].find("? ")
        if (ind-start) == -1:
            break
        positions.append(ind)
        start = ind+1
    start = 0
    while True:
        ind = start + text[start::].find('!"')
        if (ind-start) == -1:
            break
        positions.append(ind)
        start = ind+1
    start = 0
    while True:
        ind = start + text[start::].find('."')
        if (ind-start) == -1:
            break
        positions.append(ind)
        start = ind+1
    start = 0
    while True:
        ind = start + text[start::].find('?"')
        if (ind-start) == -1:
            break
        positions.append(ind)
        start = ind+1
    positions.sort()
    positions = [x+2 for x in positions]
    positions.insert(0,0)
    parts = []
    start = 0    
    for x in range(1,n_chunks+1):
        if x == n_chunks:
            parts.append(text[start::])
        else:
            end =  start + n
            end = find_closest(positions, end)
            parts.append(text[start:end])
            start = end
    return parts

from ebooklib import epub
from bs4 import BeautifulSoup


book = epub.read_epub(folder+bookname)

#estimate about 12000 words per 16000 tokens
import os
content = {}
files = os.listdir(folder)
if 'translator_log.txt' in files:
    import pandas as pd
    headers =pd.read_csv(folder+'translator_log.txt',sep='\t')
    headers = list(headers.iloc[:,0])
else:
    headers =[]
for item in book.get_items():
    soup = BeautifulSoup(item.get_content(), 'html.parser') 
    if len(soup.get_text()) > 250:
        text = soup.get_text()
        if text[:20].replace('\n','') in headers:
            continue
        mean_unicode = sum(ord(char) for char in text) / len(text)
        if mean_unicode <250:
            content[id(item)] = text.strip()
del item, soup, text, files,headers

from langchain_ollama import OllamaLLM


def get_translation(text, n_chars):
    llm = OllamaLLM(model=translator1, request_timeout=300.0)
    if len(text) > 1.5*n_chars:
        pieces = split_text_by_sentence(text, n_chars)
        text2 = ""
        for x in pieces:
            text2 = text2 + get_translation(x, n_chars)
            time.sleep(90)
            log_events("section done!", folder)
    else:
        success = False
        while success == False:
            try:
                text2 = llm.invoke(text)
                success = True
                break
            except:
                log_events("timed out", folder)
        if "</think>" in text2:
            index = text2.find("</think>")
            text2 = text2[index + len("</think>")::]
        if (("Community"  in text2) and ("standards" in text2) and (len(text2) < 100)) or (len(text2) < int(.66*len(text))):
            text2 = get_translation2(text)
        if check_overlap(text2, text):
            text2 = get_translation2(text)
        if len(text2) <= .66*len(text):
            log_events("looks like something didnt translate all the way:\n" + text, folder)
    return(text2)

def get_translation2(text):
    llm2 = OllamaLLM(model=translator2, request_timeout=300.0)
    log_events("used: " +translator2, folder)
    success = False
    while success == False:
        try:
            text2 = llm2.invoke(text)
            success = True
            break
        except:
            log_events("timed out", folder)
    if "</think>" in text2:
        index = text2.find("</think>")
        text2 = text2[index + len("</think>")::]
    if (("Community"  in text2) and ("standards" in text2) and (len(text2) < 100)) or (len(text2) < int(.66*len(text))):
        text2 = "Translation error:" + text2
    if check_overlap(text2, text):
        log_events("some text could not be translated:\n" + text, folder)
    return(text2)

import time
for x in content:
    z = get_translation(content[x], max_chars)
    heading= z[:20].replace('\n','')
    z = z.replace('\n', '<br class="calibre6"/>')
    content[x] = z
    for item in book.get_items():
        if id(item)==x:
            item.set_content(content[x])
            epub.write_epub(folder+bookname[0:-5]+"2.epub", book)
            break
    log_events("Chapter done:\n"+heading, folder)
    time.sleep(240)
del z
print("Finished!")
