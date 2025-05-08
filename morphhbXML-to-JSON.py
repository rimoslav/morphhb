# !/usr/bin/python3
# encoding=utf8

import re
import copy
import sys
import getopt
import json
import os
from xml.etree import ElementTree as ET

bookNameData = {}

bookNameData['Gen'] = 'genesis'
bookNameData['Exod'] = 'exodus'
bookNameData['Lev'] = 'leviticus'
bookNameData['Num'] = 'numbers'
bookNameData['Deut'] = 'deuteronomy'
bookNameData['Josh'] = 'joshua'
bookNameData['Judg'] = 'judges'
bookNameData['Ruth'] = 'ruth'
bookNameData['1Sam'] = '1samuel'
bookNameData['2Sam'] = '2samuel'
bookNameData['1Kgs'] = '1kings'
bookNameData['2Kgs'] = '2kings'
bookNameData['1Chr'] = '1chronicles'
bookNameData['2Chr'] = '2chronicles'
bookNameData['Ezra'] = 'ezra'
bookNameData['Neh'] = 'nehemiah'
bookNameData['Esth'] = 'esther'
bookNameData['Job'] = 'job'
bookNameData['Ps'] = 'psalms'
bookNameData['Prov'] = 'proverbs'
bookNameData['Eccl'] = 'ecclesiastes'
bookNameData['Song'] = 'songofsolomon'
bookNameData['Isa'] = 'isaiah'
bookNameData['Jer'] = 'jeremiah'
bookNameData['Lam'] = 'lamentations'
bookNameData['Ezek'] = 'ezekiel'
bookNameData['Dan'] = 'daniel'
bookNameData['Hos'] = 'hosea'
bookNameData['Joel'] = 'joel'
bookNameData['Amos'] = 'amos'
bookNameData['Obad'] = 'obadiah'
bookNameData['Jonah'] = 'jonah'
bookNameData['Mic'] = 'micah'
bookNameData['Nah'] = 'nahum'
bookNameData['Hab'] = 'habakkuk'
bookNameData['Zeph'] = 'zephaniah'
bookNameData['Hag'] = 'haggai'
bookNameData['Zech'] = 'zechariah'
bookNameData['Mal'] = 'malachi'

stripAllPointing = False
removeLemmaTypes = False
stripHFromMorph = False
prefixLemmasWithH = False
remapVerses = False
splitByBook = False
stripCantillationOnly = False


def getBookData(filename):
    tree = ET.parse(filename)
    namespaces = {
        'osis': 'http://www.bibletechnologies.net/2003/OSIS/namespace'}

    chapters = tree.getroot().findall('.//osis:chapter', namespaces)

    bookData = []

    for chapter in chapters:
        verses = chapter.findall('.//osis:verse', namespaces)
        verseArray = []

        for verse in verses:
            words = verse.findall('.//osis:w', namespaces)
            wordArray = []

            for word in words:
                singleWordArray = []
                
                processed_word_text = word.text

                if stripCantillationOnly:
                    if processed_word_text:
                        processed_word_text = stripCantillationOnlyFunc(processed_word_text)
                elif stripAllPointing:
                    if processed_word_text:
                        processed_word_text = stripVowelsAndCantillationFunc(processed_word_text)

                lemma = word.attrib.get('lemma')

                if removeLemmaTypes:
                    lemma = removeLemmaTypesFunc(lemma)
                if prefixLemmasWithH:
                    # print(lemma)
                    lemma = prefixLemmasWithHFunc(lemma)
                    # print(lemma)

                morph = word.attrib.get('morph')

                if morph and stripHFromMorph:
                    morph = stripHFromMorphFunc(morph)

                singleWordArray.append(processed_word_text)
                singleWordArray.append(lemma)
                singleWordArray.append(morph)

                wordArray.append(singleWordArray)

            verseArray.append(wordArray)

        bookData.append(verseArray)

    return bookData


def prefixLemmasWithHFunc(lemmaString):
    lemmaArray = lemmaString.split('/')
    returnArray = []
    for lemma in lemmaArray:
        returnArray.append('H' + lemma)
    returnString = '/'.join(returnArray)
    return returnString


def stripHFromMorphFunc(string):
    if string.find('H') == 0:
        return string[1:]

    return string


def removeLemmaTypesFunc(string):
    return re.sub(r" [abcdef]|\+", "", string)


def stripVowelsAndCantillationFunc(string):
    return re.sub(r"[\u0591-\u05c7]", "", string)


def stripCantillationOnlyFunc(string):
    return re.sub(r"[\u0591-\u05AF\u05C0\u05C3\u05C6]", "", string)


def getCommandOptions(argv):
    global stripAllPointing
    global stripCantillationOnly
    global removeLemmaTypes
    global stripHFromMorph
    global prefixLemmasWithH
    global remapVerses
    global splitByBook

    try:
        opts, args = getopt.getopt(argv, "h:",
                                   [
                                       "stripAllPointing",
                                       "stripCantillationOnly",
                                       "removeLemmaTypes",
                                       "stripHFromMorph",
                                       "prefixLemmasWithH",
                                       "remapVerses",
                                       "splitByBook",
                                   ])
    except getopt.GetoptError:
        print('python3 morphhbXML-to-JSON.py --stripAllPointing --stripCantillationOnly --removeLemmaTypes --stripHFromMorph --prefixLemmasWithH --remapVerses --splitByBook')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('python3 morphhbXML-to-JSON.py --stripAllPointing --stripCantillationOnly --removeLemmaTypes --stripHFromMorph --prefixLemmasWithH --remapVerses --splitByBook')
            print('--stripAllPointing: Removes ALL pointing (vowels and cantillation marks) from the Hebrew text.')
            print('--stripCantillationOnly: Removes only cantillation marks, keeping vowels (niqqud).')
            sys.exit()
        elif opt in ("--stripAllPointing"):
            print('stripAllPointing (vowels and cantillation) enabled')
            stripAllPointing = True
        elif opt in ("--removeLemmaTypes"):
            print('removeLemmaTypes')
            removeLemmaTypes = True
        elif opt in ("--stripHFromMorph"):
            print('stripHFromMorph')
            stripHFromMorph = True
        elif opt in ("--prefixLemmasWithH"):
            print('prefixLemmasWithH')
            prefixLemmasWithH = True
        elif opt in ("--remapVerses"):
            print('remapVerses')
            remapVerses = True
        elif opt in ("--splitByBook"):
            print('splitByBook')
            splitByBook = True
        elif opt in ("--stripCantillationOnly"):
            print('stripCantillationOnly (keep vowels)')
            stripCantillationOnly = True


def main():

    hebrew = {}
    for bookNameShort in bookNameData.keys():
        hebrew[bookNameData[bookNameShort]] = getBookData(
            'wlc/' + bookNameShort + '.xml')

    # map hebrew to english verses
    filename = 'wlc/VerseMap.xml'
    tree = ET.parse(filename)
    namespaces = {'vm': 'http://www.APTBibleTools.com/namespace'}
    books = tree.getroot().findall('.//vm:book', namespaces)

    # must use deep copy here
    remapped = copy.deepcopy(hebrew)

    for book in books:
        verses = book.findall('.//vm:verse', namespaces)

        for verse in verses:
            if verse.attrib['type'] == 'full':
                # take the wlc verse and move it to the kjv position
                wlcRef = verse.attrib['wlc']
                wlcVerseArray = wlcRef.split('.')
                kjvRef = verse.attrib['kjv']
                kjvVerseArray = kjvRef.split('.')

                kjvBook = bookNameData[kjvVerseArray[0]]
                kjvChapter = int(kjvVerseArray[1]) - 1
                kjvVerse = int(kjvVerseArray[2]) - 1

                wlcBook = bookNameData[wlcVerseArray[0]]
                wlcChapter = int(wlcVerseArray[1]) - 1
                wlcVerse = int(wlcVerseArray[2]) - 1

                wlcData = hebrew[wlcBook][wlcChapter][wlcVerse]

                if kjvBook == 'psalms' and kjvVerse == 0:
                    remapped[kjvBook][kjvChapter][kjvVerse] = hebrew[wlcBook][wlcChapter][wlcVerse - 1] + wlcData
                    remapped[wlcBook][wlcChapter][wlcVerse] = []
                else:
                    if kjvChapter >= len(remapped[kjvBook]):
                        remapped[kjvBook].append([])
                    if kjvVerse >= len(remapped[kjvBook][kjvChapter]):
                        remapped[kjvBook][kjvChapter].append([])
                    remapped[kjvBook][kjvChapter][kjvVerse] = wlcData.copy()
                    if wlcChapter < kjvChapter or (wlcChapter == kjvChapter and wlcVerse > kjvVerse) or wlcChapter > kjvChapter:
                        remapped[wlcBook][wlcChapter][wlcVerse] = []

        # delete those empty entries now
        verses.reverse()
        for verse in verses:
            if verse.attrib['type'] == 'full':
                wlcRef = verse.attrib['wlc']
                wlcVerseArray = wlcRef.split('.')

                wlcBook = bookNameData[wlcVerseArray[0]]
                wlcChapter = int(wlcVerseArray[1]) - 1
                wlcVerse = int(wlcVerseArray[2]) - 1

                if len(remapped[wlcBook][wlcChapter][wlcVerse]) == 0:
                    del remapped[wlcBook][wlcChapter][wlcVerse]

    # Fix partial verses manually
    remapped['1kings'][17][32] = hebrew['1kings'][17][32] + \
        hebrew['1kings'][17][33]
    remapped['1kings'][17][32][19:43] = []
    remapped['1kings'][17][33][0:10] = []
    remapped['1kings'][19][1] = hebrew['1kings'][19][1] + \
        hebrew['1kings'][19][2]
    remapped['1kings'][19][1][13:34] = []
    remapped['1kings'][19][2][0:6] = []

    remapped['1kings'][21][20][8:19] = []
    remapped['1kings'][21][21] = hebrew['1kings'][21][20] + \
        hebrew['1kings'][21][21]
    remapped['1kings'][21][21][0:8] = []

    remapped['1kings'][21][42] = hebrew['1kings'][21][42] + \
        hebrew['1kings'][21][43]

    remapped['isaiah'][63][0] = hebrew['isaiah'][62][18].copy()
    remapped['isaiah'][62][18][8:23] = []
    remapped['isaiah'][63][0][0:8] = []

    remapped['psalms'][12][4] = hebrew['psalms'][12][4].copy()
    remapped['psalms'][12].append([])
    remapped['psalms'][12][5] = hebrew['psalms'][12][4].copy()
    remapped['psalms'][12][4][6:16] = []
    remapped['psalms'][12][5][0: 6] = []

    if remapVerses:
        final = remapped
    else:
        final = hebrew

    # Determine the base name for output file or subdirectory
    output_base_name = None
    if stripCantillationOnly:
        output_base_name = 'niqqud'
    elif stripAllPointing:
        output_base_name = 'clean'
    else:
        output_base_name = 'remapped' if remapVerses else 'hebrew'

    if splitByBook:
        output_dir = os.path.join('./json', output_base_name)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for book_key_name in final:
            target_file_path = os.path.join(output_dir, book_key_name)
            with open(target_file_path + '.json', 'w', encoding='utf8') as f:
                json.dump(final[book_key_name], f, ensure_ascii=False)
    else:
        single_json_filename = output_base_name + '.json'
        with open(single_json_filename, 'w', encoding='utf8') as f:
            json.dump(final, f, ensure_ascii=False)


if __name__ == "__main__":
    getCommandOptions(sys.argv[1:])
    main()

# Example usage with all parameters:
# python3 morphhbXML-to-JSON.py --stripAllPointing  --removeLemmaTypes --stripHFromMorph --prefixLemmasWithH --remapVerses --splitByBook
# or:
# python3 morphhbXML-to-JSON.py --stripCantillationOnly --removeLemmaTypes --stripHFromMorph --prefixLemmasWithH --remapVerses --splitByBook
# because --stripAllPointing also strips cantillation marks