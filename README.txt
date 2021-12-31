A.
Mehul Goel
mg4260
Aayush Kumar Verma
av2955


B. 

List of files in the tar.gz
project1MehulAayush.py


C. 
Commands necessary to install the required software and dependencies and then to run the program
pip3 install --upgrade google-api-python-client
pip3 install nltk
//upload our program onto the VM and run it by the following command
python3 project1MehulAayush.py


D.
Description:

First a google search for the input query is done

Feedback is taken from the user for each of the 10 results returned

The title, url, snippet, relevance feedback of each result is stored in a dictionary

Precision is calculated by observing how many out of the 10 results were relevant

If precision is below the desired precision of 0.9 then the query is expanded

For expansion of the query a list is created for each word listing the number of search items that word was found in

Expanding the query with the top three words that were not in the original query 

Query is rerun for search results, feedback is taken and query expansion done until desired precision is reached


E.
Query Expansion:

For expansion of the query a list is created for each word listing the number of search items that the word was found in

Amongst these words, stop words are removed and in each word only alpha numeric characters are allowed to remain. Words are stemmed down. For stopword removal nltk's stopword list is searched and if the word is found there it is taken further. For stemming down nltk's PorterStemmer is used.

For each of these words we calculate the number of times they appear in relevant documents and in non relevant documents

Inverse document frequency is calculated

Rocchio's Algorithm is applied and weights calculated for each word

These words are sorted in descending order of their weights and the top three words that were not in the original query are picked to expand the query recursively until we reach the desired precision


F.
Google Custom Search Engine JSON API Key:AIzaSyDFLI4iu83nBdeuUJkQTDH739PIyUqKuVM
Engine ID:3ad87265822f5240e