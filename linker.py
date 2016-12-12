import json
import gzip
import sys
import re
import pprint
import requests
import nltk
from nltk import sent_tokenize, word_tokenize, pos_tag, ne_chunk, tree
from nltk.corpus import stopwords, state_union, wordnet, conll2000
from nltk.stem import PorterStemmer, WordNetLemmatizer
from bs4 import BeautifulSoup

#
#"http://node001:16XX/sparql" -d "print=true" --data-urlencode "query=select ?p ?o where { \"<http:\/\/rdf.freebase.com\/ns\/m.02mjmr>\" ?p ?o}"
#
from SPARQLWrapper import SPARQLWrapper, JSON

node = "\"http://node001:1671/sparql\" --data-urlencode "
query = "\"query=select ?p ?o where { \"<http:\/\/rdf.freebase.com\/ns\/m.02mjmr>\" ?p ?o}\""


sparql = SPARQLWrapper("http://node071:1606/sparql")
sparql.setQuery("""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT *
    WHERE { ?p ?s ?o }
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    print(result["label"]["value"])