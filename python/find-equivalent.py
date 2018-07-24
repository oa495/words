import json
# from gensim.models import KeyedVectors
# filename = 'GoogleNews-vectors-negative300.bin'
# model = KeyedVectors.load_word2vec_format(filename, binary=True)
import re
from dotenv import load_dotenv
from wordnik import *
import collections
from PyDictionary import PyDictionary
import requests
from wiktionaryparser import WiktionaryParser
from get_all_data import getWordDefinition

# wordnik api stuff
apiUrl = 'http://api.wordnik.com/v4'
apiKey = os.getenv('API_KEY')
client = swagger.ApiClient(apiKey, apiUrl)

# open files
with open('words/all.json') as f:
    all = json.load(f)

femaleTerms = r'\b[\w-]*woman\b|\bfemale\b|\b[\w-]girl\b|\bgirls\b|\b[\w-]*women\b|\blady\b|\b[\w-]*mother\b|\b[\w-]*daughter\b|\bwife\b'
femaleRegex = re.compile(femaleTerms)

maleTerms = r'\bman\b|\bmale\b|\bboy\b|\bmen\b|\bboys\b|\bson\b|\b[\w-]*father\b|\bhusband\b'
maleRegex = re.compile(maleTerms)

all_words_only = [entry['word'] for entry in all]
wordOpposites = {}


def writeToJson(path, arr):
	with open(path + '.json', 'w') as outfile:
	    json.dump(arr, outfile)


def defineWordEquivalent():
    obj = {
        'male': 'female',
        'man': 'woman',
        'father': 'mother',
        'wife': 'husband',
        'boy': 'girl'
    }

    for term in obj:
        equiv = obj[term]
        wordOpposites[term] = equiv
        wordOpposites[equiv] = term

def findGenderEquivalent(word, gender):
    # Check if opposite of word can be found using the word itself.
    # E.g words like grandfather, grandmother
    def checkWordForEquivalent():
        gendered = r'woman|man|father|mother|wife|husband|boy|girl'
        rgex = re.compile(gendered)
        termsInString = rgex.search(word)
        if termsInString is not None:
            word_copy = word
            startIndex = termsInString.start(0)
            endIndex = termsInString.end(0)
            toReplace = word[startIndex:endIndex]
            equivalent = word_copy.replace(toReplace, wordOpposites[toReplace])
            if equivalent in all_words_only:
                return equivalent
            definition = getWordDefinition(equivalent)
            if gender == 'female':
                opp_gender = 'male'
            else:
                opp_gender = 'female'
            if definition != ' ':
                all.append({
                    'word': equivalent,
                    'definition': definition,
                    'gender': opp_gender
                })
                return equivalent
            return ' '


    def getGoogleNews():      
        if word in model.vocab:
            if (gender == 'female'):
                pos = 'man'
                neg = 'woman'
            else:
                pos = 'woman'
                neg = 'man'
            result = model.most_similar(positive=[pos, word], negative=[neg], topn=1)
            if result is not None:
                result = result[0]
                equivalent = result[0]
                score = result[1]
                if score > 0.6:
                    if equivalent in all_words_only:
                        return equivalent
                    else:
                        definition = getWordDefinition(equivalent)
                        if definition != ' ':
                            if gender == 'female':
                                opp_gender = 'male'
                                termsInString = maleRegex.search(definition)
                            else:
                                opp_gender = 'female'
                                termsInString = femaleRegex.search(definition)
                            if termsInString is not None:
                                 all.append({
                                    'word': equivalent,
                                    'definition': definition,
                                    'gender': opp_gender
                                })
                        return equivalent
        return ' '

    
    for term in wordOpposites:
        if term == 'word':
            return wordOpposites[term]
    equiv = checkWordForEquivalent()
    if equiv != ' ':
        return equiv
    # getGoogleNews()

defineWordEquivalent()
for entry in all:
    word = entry['word']
    gender = entry['gender']
    equiv = findGenderEquivalent(word, gender)
    if genderOpp != ' ':
        entry['equivalent'] = equiv

writeToJson('words/all-pairs', all)