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

html_regex = re.compile(r'<html>(.*)<\/html>', re.DOTALL)

##TODO Check how to include ACE for relation extraction.
##TODO http://www.nltk.org/_modules/nltk/sem/relextract.html

class BigramChunker(nltk.ChunkParserI):
	def __init__(self, train_sents):
		train_data = [[(t,c) for w,t,c in nltk.chunk.tree2conlltags(sent)] for sent in train_sents]
        	self.tagger = nltk.BigramTagger(train_data)

	def parse(self, sentence):
		pos_tags = [pos for (word,pos) in sentence]
		tagged_pos_tags = self.tagger.tag(pos_tags)
		chunktags = [chunktag for (pos, chunktag) in tagged_pos_tags]
		conlltags = [(word, pos, chunktag) for ((word,pos),chunktag) in zip(sentence, chunktags)]
		return nltk.chunk.conlltags2tree(conlltags)


def casual_tokenizing(text):
	sentences = sent_tokenize(text)
	sentences = filter(lambda sent: sent != "", sentences)
	tokens = word_tokenize(text)

	return tokens


##For testing
test_sents = conll2000.chunked_sents('test.txt', chunk_types=['NP'])
train_sents = conll2000.chunked_sents('train.txt', chunk_types=['NP'])

def main(argv):
	file_name = argv[0]
	if "warc.gz" not in file_name:
		print file_name+" is of unsupported type. Supported type is .warc.gz!"
		return 0

	##Iitialization
	stem = PorterStemmer()
	lemmatizer = WordNetLemmatizer()
	stop_words = set(stopwords.words("english"))
	chunkGram = r"""Chunk: {<RB.?>*<VB.?>*<NNP>+<NN>?}"""
	chunkParser = nltk.RegexpParser(chunkGram)

	

	##Procedure per warc.gz
	with gzip.open(file_name, 'rb') as f:
		warc_content = f.read()
		##Getting all html text and putting it in the responses array.
		responses = re.findall(html_regex, warc_content)
		##For each element in array:
		for resp in responses:
			##Extracting all text with BS
			soup = BeautifulSoup("<html>"+resp+"</html>", 'html.parser')
			text = soup.get_text()

			##Tokening first into sentences and then into words.
			tokens = casual_tokenizing(text)

			##Removing stopwords
			filtered_tokens = []
			for t in tokens:
				if t not in stop_words:
					filtered_tokens.append(t)

			##Stemming
			stemmed_tokens = []
			for f in filtered_tokens:
				stemmed_tokens.append(stem.stem(f))

			##Lemmatizing
			lemmatized_tokens=[]
			for f in filtered_tokens:
				lemmatized_tokens.append(lemmatizer.lemmatize(f,"n"))
			##Pos-tagging the pre-processed words
			tagged_tokens = pos_tag(tokens)
			##Chunking
			chunked_tokens = chunkParser.parse(tagged_tokens)
			

			bigram_chunker = BigramChunker(train_sents)
			print(bigram_chunker.evaluate(test_sents))

			##Discovering and tagging Named Entities (NER)
			tagged_entities = ne_chunk(tagged_tokens, binary=False)
			for entity in tagged_entities:
				if isinstance(entity, tree.Tree):
					print entity
				




if __name__ == "__main__":
	argv = sys.argv
	if len(argv)<2:
		print "Provide the .warc.gz file as the first argument along with the script call.\nE.g.: python ~/parser.py sample.warc.gz"
	else:
		main(sys.argv[1:])
	exit(0)