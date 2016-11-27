import json
import gzip
import sys
import re
import pprint
from nltk import sent_tokenize, word_tokenize, pos_tag, ne_chunk, tree
from bs4 import BeautifulSoup
from pyspark import SparkContext

html_regex = re.compile(r'<html>(.*)<\/html>', re.DOTALL)

sc = SparkContext("local", "knowledge-acquisition")

def extract_text(file_name):
	with gzip.open(file_name, 'rb') as f:
		warc_content = f.read()
		responses = re.findall(html_regex, warc_content)
		for resp in responses:
			soup = BeautifulSoup("<html>"+resp+"</html>", 'html.parser')
			text = soup.get_text()
			return text

def tokenize(x):
	return word_tokenize(x)

def tag(x):
	return pos_tag(x)


def chunk(tagged_tokens):
	return ne_chunk(tagged_tokens, binary=True)



#def casual_tokenizing(text):
	#sentences = sent_tokenize(text)
	#sentences = filter(lambda sent: sent != "", sentences)
	#tokens = word_tokenize(text)
	#tagged_tokens = pos_tag(tokens)
	# print sentences, len(sentences)
	# raw_input("Hit enter to continue.")
	# print tokens, len(tokens)
	# raw_input("Hit enter to continue.")
	# print tagged_tokens
	# raw_input("Hit enter to continue.")
	#return tagged_tokens


def main(argv):
	file_name = argv[0]
	text = extract_text(file_name)
	text_rdd = sc.parallelize(text.split(' '))
	tokens_rdd = text_rdd.map(lambda t: tokenize(t))
	tagged_tokens_rdd = tokens_rdd.map(lambda tt: tag(tt))
	tagged_entities_rdd = tagged_tokens_rdd.map(lambda x: chunk(x))
	tagged_entities = tagged_entities_rdd.collect()

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