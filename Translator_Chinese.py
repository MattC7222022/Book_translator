#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is the same script adopted for chinese specifically
@author: FEXcaxasSA
"""
max_chars = 3000
folder = "/home/"
bookname = ".epub"
translator1 = "translator"
translator2 = "translator2"


def get_chapter_num(text):
    line1 = text.split('\n')[0]
    line1 = line1.split(' ')[0]
    line1 = line1[1::]
    line1 = line1[:-1]
    return(chinese_to_int(line1))

import re
from datetime import datetime

def chinese_to_int(chinese: str) -> int:
    chinese = chinese.strip()
    if not chinese:
        return 0
    digits = {"零":0, "〇":0, "一":1, "二":2, "两":2, "三":3, "四":4, "五":5,
              "六":6, "七":7, "八":8, "九":9}
    small_units = {"十":10, "百":100, "千":1000}
    large_units = {"万":10**4, "亿":10**8}
    # direct arabic digits
    if re.fullmatch(r'\d+', chinese):
        return int(chinese)

    result = 0
    section = 0
    number = 0

    for ch in chinese:
        if ch in digits:
            number = digits[ch]
        elif ch in small_units:
            unit = small_units[ch]
            if number == 0:
                number = 1
            section += number * unit
            number = 0
        elif ch in large_units:
            unit = large_units[ch]
            if number != 0:
                section += number
            result += section * unit
            section = 0
            number = 0
        else:
            # ignore non-numeric characters
            continue

    section += number
    return result + section

def log_events(text, path):
    if len(text)<200:
        print(text)
    try:
        f = open(path + "translator_log.txt", mode="r")
        f = open(path + "translator_log.txt", mode="a")
        f.write(text+' '+str(datetime.now().time())[:8]+"\n")
        f.close()   
    except:
        f= open(path + "translator_log.txt", mode="w")
        f.write(text+' '+str(datetime.now().time())[:8]+"\n")
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
    text = text.replace(chr(12290), '.')
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
        ind = start + text[start::].find(".\n")
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
    while True:
        ind = start + text[start::].find('\n\n')
        if (ind-start) == -1:
            break
        positions.append(ind)
        start = ind+1
    positions.sort()
    positions = [x+2 for x in positions]
    positions.insert(0,0)
    parts = []
    start = 0  
    text = text.replace('.', chr(12290))
    for x in range(1,n_chunks+1):
        if x == n_chunks:
            parts.append(text[start::])
        else:
            end =  start + n/n_chunks
            end = find_closest(positions, end)
            parts.append(text[start:end])
            start = end
    return parts

from ebooklib import epub
from bs4 import BeautifulSoup


book = epub.read_epub(folder+bookname)

#estimate about 12000 words per 16000 tokens
content = []
for spine_item in book.spine:
    try:
        item_id = spine_item[0]
        doc = book.get_item_with_id(item_id)
        soup = BeautifulSoup(doc.get_content().decode("utf-8"), "html.parser")
        text = soup.get_text().strip()
        unicodes = [ord(x) for x in text[0:50]]
        if len(unicodes) <1:
            continue
        if (sum(unicodes)/len(unicodes) > 500):
            content.append((id(doc), text))
    except UnicodeDecodeError:
        print(f"Decoding error in {doc.get_name()}")
del text, doc, unicodes, spine_item, item_id


from langchain_ollama import OllamaLLM


def get_translation(text, n_chars):
    llm = OllamaLLM(model=translator1, request_timeout=300.0)
    if len(text) > n_chars:
        pieces = split_text_by_sentence(text, n_chars)
        text2 = ""
        for x in pieces:
            text2 = text2 + get_translation(x, n_chars)
            time.sleep(120)
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
        if (("Community"  in text2) and ("standards" in text2) and ("translate" in text2)):
            text2 = get_translation2(text)
        if ("e" not in text2.lower()) and ("a" not in text2.lower()):
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
    if ("e" not in text2.lower()) and ("a" not in text2.lower()):
        log_events("some text could not be translated:\n" + text, folder)
    return(text2)

import time
from pypinyin import pinyin, Style
for x in content:
    z = x[1]
    #saves a few seconds by automatically translating chapter headings
    if '节' in z[0:20]:
        chapter = 'Chapter ' + str(get_chapter_num(z[0:20])) + ': '
        z= z[0:20].split('节')[1] + z[20::]
    else:
        chapter = ''
    z= z.replace('\n\n\n\n\n', '\n\n')
    z = get_translation(z, max_chars)
    z = z.replace('\n', '<br class="calibre6"/>')
    #whatever isnt translated is transliterated to latin alphabet
    z = "".join([s[0] for s in pinyin(z, style=Style.TONE)])
    if (z[:2] == '\n') and (len(z)>2):
        z = z[2::]
    z = f"<h2>{chapter}</h2>"+z
    for item in book.get_items():
        if id(item)==x[0]:
            print("FINAL CHAPTER STRING:" + z[:20])
            item.set_content(z.encode("utf-8"))
            epub.write_epub(folder+bookname[0:-5]+"2.epub", book)
            break
    log_events("Chapter done: "+ z[:20], folder)
    time.sleep(300)
del z
print("Finished!")


