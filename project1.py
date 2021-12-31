import requests
import json
import nltk
import math
import time

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

nltk.download('stopwords')
nltk.download('punkt')

ps = PorterStemmer()
stop_words = set(stopwords.words("english"))

def run(JsonApiKey, EngineID, query):

    #runs the google search and takes feedback from user
    #returns a consolidated list of dictionaries

    # SEARCH USING REST TO INVOKE THE API: https://developers.google.com/custom-search/v1/using_rest
    url = "https://www.googleapis.com/customsearch/v1?key=" + JsonApiKey + "&cx=" + EngineID + "&q=" + query
    response = requests.get(url)
    GoogleResults = json.loads(response.text)['items']

    # STORE THE REQUIRED INFORMATION AS A LIST OF MAP
    i = 1
    res = []
    for entry in GoogleResults:
        title, link, website, snippet = "", "", "", "--(empty)--"
        if 'title' in entry.keys ():
            title = entry['title']
        if 'link' in entry.keys():
            link = entry['link']
        if 'snippet' in entry.keys():
            snippet = entry['snippet']
        entry = {"title": title, "link": link, "snippet": snippet, "relevance": False}
        res.append(entry)

    for entry in res:
        print("RESULT NUMBER = " + str(i))
        i += 1
        print("TITLE: " + entry['title'])
        print("WEBSITE: " + entry['link'])
        print("SUMMARY: " + entry['snippet'])
        print("-------IS IT RELEVANT (ENTER 'Y/N' or 'y/n')------: ")
        check = input()
        print()
        if check == 'Y' or check == 'y':
            entry ['relevance'] = True
        else:
            entry ['relevance'] = False
    return res

def calculate(res):
    #calculates precision@10
    #returns precision
    count = 0.0
    for entry in res:
        if entry['relevance'] == True:
            count += 1
    return count/10

def relevanceFeedback(currentPrecision, precision, extraWords, query):
    #Exapands the query
    #returns the new query
    print("-----RELEVANCE FEEDBACK SUMMARY-----")
    print()
    print("CURRENT PRECISION = " + str(currentPrecision))

    flag = False
    words=""
    if currentPrecision < precision:
        flag = True
        words = ""
        for word in extraWords:
            words += word + " "
        query += " " + words
    else:
        print("REQUIRED PRECISION ACHIEVED")
        print("QUERY: ", end=" ")
        print(list(query.split()))
    if flag:
        print("REQUIRED PRECISION = 0.9")
        print("EXPANDED QUERY TERMS: ", end=" ")
        print(list(words.split ()))
    print()
    return query

def clean(words):
    #Removes stop words and non alpha numeric characters
    #returns cleaned word list
    clean_words = []
    for w in words:
        alnum = ""
        for character in w:
            if character.isalnum():
                alnum += character
        if len(alnum) > 0:
            if alnum not in stop_words:
                clean_words.append(ps.stem(alnum))
    return clean_words

def queryExpansion(res, query):

    # CREATING INVERTED LIST
    # Reference 1: https://www.geeksforgeeks.org/create-inverted-index-for-file-using-python/
    # Reference 2: https://www.geeksforgeeks.org/python-nltk-nltk-tokenizer-word_tokenize/

    #calculates inverted document frequency
    #returns the extra words to expand the query with

    invertedList = {}
    for i in range(len(res)):
        words = word_tokenize(res[i]["snippet"]) + word_tokenize(res[i]["title"])
        words = clean(words)

        res[i]['freq'] = {}
        for word in words:
            res[i]['freq'][word] = res[i]['freq'].get(word, 0) + 1
            invertedList[word] = invertedList.get(word, set())
            invertedList[word].add(i)

    # FIND QUERY WEIGHTS USING ROCCHIO'S ALGORITHM AND GENERATE NEW QUERY

    newQueryWeights = rocchioAlgorithm(invertedList, res, query)
    current = query.split(" ")
    highWeightTerms = sorted(newQueryWeights, key = newQueryWeights.get, reverse = True)
    nextQuery = [word for word in highWeightTerms if word not in current]
    return nextQuery[0:3]

def L2norm(DocFreq, word, docCount):
    #calculates L2 norm
    #returns the value
    ans = (float(DocFreq[word]) / docCount)
    return ans

def rocchioAlgorithm(documentList, res, query):

    # Reference 1: https://www.cl.cam.ac.uk/teaching/1718/InfoRtrv/slides/lecture7-relevance-feedback.pdf
    # Reference 2: https://www.coursera.org/lecture/text-retrieval/lesson-5-2-feedback-in-vector-space-model-rocchio-PyTkW

    #calculates weights for each word
    #returns dictionary with words and their weights

    # EMPIRICAL VALUES OF ALPHA (A), BETA (B), AND GAMMA (G)
    A, B, G = 1.0, 0.85, 0.4
    originalQueryWeights, searchResultWeights, newQueryWeights, relevantDocFreq, nonRelevantDocFreq = {}, {}, {}, {}, {}
    relevantCount, nonRelevantCount = 0, 0
    for word in query.split():
        originalQueryWeights[word] = 1.0
    for word in documentList:
        searchResultWeights[word] = 0.0

    for entry in res:
        if entry["relevance"] == True:
            relevantCount += 1
            for word in entry["freq"]:
                if word in relevantDocFreq.keys():
                    relevantDocFreq[word]=relevantDocFreq[word]+entry["freq"][word]
                else:
                    relevantDocFreq[word]=entry["freq"][word]

    for entry in res:
        if entry["relevance"] == False:
            nonRelevantCount += 1
            for word in entry["freq"]:
                if word in nonRelevantDocFreq.keys():
                    nonRelevantDocFreq[word]=nonRelevantDocFreq[word]+entry["freq"][word]
                else:
                    nonRelevantDocFreq[word]=entry["freq"][word]


    for word in documentList:
        inverseDocFreq = math.log(float(len(res) / len(documentList[word])), 10)
        for entry in documentList[word]:
            if res[entry]['relevance'] == True:
                searchResultWeights[word] += B * inverseDocFreq * L2norm(relevantDocFreq, word, relevantCount)
            else:
                searchResultWeights[word] -= G * inverseDocFreq * L2norm(nonRelevantDocFreq, word, nonRelevantCount)
        if word in originalQueryWeights:
            newQueryWeights[word] = A * originalQueryWeights[word] + searchResultWeights[word]
        else:
            if searchResultWeights[word] > 0:
                newQueryWeights[word] = searchResultWeights[word]
    return newQueryWeights

def main():
    JsonApiKey, EngineID, precision = "AIzaSyDFLI4iu83nBdeuUJkQTDH739PIyUqKuVM", "3ad87265822f5240e", 0.9
    print("ENTER THE SEARCH QUERY: ")
    query = input()
    print()
    print("FOR EACH OF THE SEARCH RESULTS RETURNED BY THE SYSTEM BELOW:")
    print("IF IT IS RELEVANT TO THE QUERY    : TYPE 'y' OR 'Y'")
    print("IF IT IS NOT RELEVANT TO THE QUERY: TYPE 'n' OR 'N'")
    print()
    time.sleep(1)
    currentPrecision = 0.0
    while currentPrecision < precision:
        res = run(JsonApiKey, EngineID, query)
        currentPrecision = float(calculate(res))
        if currentPrecision == 0.0:
            print("NO RELEVANT DOCUMENT FOUND TO EXPAND THE QUERY WITH")
            exit()
        extraWords = queryExpansion(res, query)
        query = relevanceFeedback(currentPrecision, precision, extraWords, query)


if __name__ == '__main__':
    main()