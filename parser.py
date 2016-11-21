import json
import gzip
import sys
import re
import pprint
from nltk import sent_tokenize, word_tokenize, pos_tag, ne_chunk, tree
from bs4 import BeautifulSoup

html_regex = re.compile(r'<html>(.*)<\/html>', re.DOTALL)

def casual_tokenizing(text):
	sentences = sent_tokenize(text)
	sentences = filter(lambda sent: sent != "", sentences)
	tokens = word_tokenize(text)
	tagged_tokens = pos_tag(tokens)
	# print sentences, len(sentences)
	# raw_input("Hit enter to continue.")
	# print tokens, len(tokens)
	# raw_input("Hit enter to continue.")
	# print tagged_tokens
	# raw_input("Hit enter to continue.")
	return tagged_tokens


def main(argv):
	file_name = argv[0]
	if "warc.gz" not in file_name:
		print file_name+" is of unsupported type. Supported type is .warc.gz!"
		return 0
	with gzip.open(file_name, 'rb') as f:
		warc_content = f.read()
		responses = re.findall(html_regex, warc_content)
		for resp in responses:
			soup = BeautifulSoup("<html>"+resp+"</html>", 'html.parser')
			text = soup.get_text()
			tagged_tokens = casual_tokenizing(text)
			tagged_entities = ne_chunk(tagged_tokens, binary=True)
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