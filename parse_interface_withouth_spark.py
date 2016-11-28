import json
import gzip
import sys
import re
import pprint
import requests
import nltk
import os
from nltk import sent_tokenize, word_tokenize, pos_tag, ne_chunk, tree
# from nltk.corpus import stopwords, state_union, wordnet, conll2000
# from nltk.stem import PorterStemmer, WordNetLemmatizer
from bs4 import BeautifulSoup

html_regex = re.compile(r'<html>(.*)<\/html>', re.DOTALL)

##TODO Check how to include ACE for relation extraction.
##TODO http://www.nltk.org/_modules/nltk/sem/relextract.html

##For testing
# test_sents = conll2000.chunked_sents('test.txt', chunk_types=['NP'])
# train_sents = conll2000.chunked_sents('train.txt', chunk_types=['NP'])

def validateInput(file_name):
	if "warc.gz" not in file_name:
		print file_name+" is of unsupported type. Supported type is .warc.gz!"
		return 0
	else:
		return file_name

# def getChunker():
#       chunkGram = r"""Chunk: {<RB.?>*<VB.?>*<NNP>+<NN>?}"""
#       return nltk.RegexpParser(chunkGram)

def getText(html_page):
	soup = BeautifulSoup("<html>"+html_page+"</html>", 'html.parser')
	text = soup.get_text()
	return text

def casualTokenizing(text):
	sentences = sent_tokenize(text)
	sentences = filter(lambda sent: sent != "", sentences)
	tokens = word_tokenize(text)

	return sentences, tokens

# def filterTokens(tokens):
#       stop_words = set(stopwords.words("english"))
#       filtered_tokens = []
#       for t in tokens:
#               if t not in stop_words:
#                       filtered_tokens.append(t)
#       return filtered_tokens

# def stemmatizeTokens(tokens):
#       stem = PorterStemmer()
#       stemmed_tokens = []
#       for f in tokens:
#               stemmed_tokens.append(stem.stem(f))
#       return stemmed_tokens


# def lemmatizeTokens(tokens,pos):
#       lemmatizer = WordNetLemmatizer()
#       lemmatized_tokens=[]
#       for f in tokens:
#               lemmatized_tokens.append(lemmatizer.lemmatize(f,pos))
#       return lemmatized_tokens

# class bigramChunker(nltk.ChunkParserI):
#       def __init__(self, train_sents):
#               train_data = [[(t,c) for w,t,c in nltk.chunk.tree2conlltags(sent)] for sent in train_sents]
#               self.tagger = nltk.BigramTagger(train_data)

#       def parse(self, sentence):
#               pos_tags = [pos for (word,pos) in sentence]
#               tagged_pos_tags = self.tagger.tag(pos_tags)
#               chunktags = [chunktag for (pos, chunktag) in tagged_pos_tags]
#               conlltags = [(word, pos, chunktag) for ((word,pos),chunktag) in zip(sentence, chunktags)]
#               return nltk.chunk.conlltags2tree(conlltags)

# def runEvaluation():
#       global train_sents, test_sents
#       bigram_chunker = bigramChunker(train_sents)
#       print(bigram_chunker.evaluate(test_sents))

def extractUniqueEntities(tokens):
	unique_entities = []
	tagged_entities = ne_chunk(tokens, binary=False)
	for entity in tagged_entities:
		if isinstance(entity, tree.Tree):
			if entity not in unique_entities:
				unique_entities.append(entity)
	return unique_entities



def runProcedure(argv):
	file_name = validateInput(argv[0])
	assert(file_name)
	##Iitialization
	# stop_words = set(stopwords.words("english"))
	# chunkParser = getChunker()

	##Procedure per warc.gz
	with gzip.open(file_name, 'rb') as f:
		warc_id = "Warc_id pending."
		warc_content = f.read()

		##Getting all html text and putting it in the responsive array.
		html_pages_array = re.findall(html_regex, warc_content)

		##For each element in array:
		for html_page in html_pages_array:
			##Extracting all text with BS
			##I'm appending the tags to the front and the back as they are getting stripped cause of our warc regex.
			text = getText(html_page)

			##Tokening first into sentences and then into words.
			sentence, tokens = casualTokenizing(text)
			
			##Removing stopwords
			##Couldn't fix an indexing error making it a function, and I'll do it another time.
			# filtered_tokens = filterTokens(tokens)

			# ##Stemming
			# stemmed_tokens = stemmatizeTokens(tokens)

			# ##Lemmatizing
			# ##For the lemmatization we are using the "n", cause we are getting the nouns. This can change if we make a different decision.
			# lemmatized_tokens=lemmatizeTokens(tokens,"n")

			##Pos-tagging the pre-processed words
			tagged_tokens = pos_tag(tokens)

			##Chunking
			# chunked_tokens = chunkParser.parse(tagged_tokens)
			
			# runEvaluation()

			##Discovering and tagging Named Entities (NER)
			entities = extractUniqueEntities(tagged_tokens)
			write_file = open('output.tsv', 'w')
			for entry in entities:
				label = entry.label()
				leaves = entry.leaves()
				size = len(leaves)
				entity = ""
				entity_id = ""
				for leaf in leaves:
					entity += '-'+leaf[0].lower()
				if entity=="":
					continue
				response = os.popen('curl "http://10.149.0.127:9200/freebase/label/_search?q={0}"'.format(entity[1:].strip()))
				try:
					json_res = json.loads(response.read())
				except Exception as e:
					print "No response for "+entity
					continue
				##Here we need to add some validity check in case we get an empty response, to continue to the next entity
				if json_res['hits']['total']==0:
					print "Got 0 hits for: "+entity[1:].strip()
					continue
				max_score = json_res['hits']['max_score']
				hits = json_res['hits']['hits']
				freebase_id = ""
				for hit in hits:
					print hit
					if hit['_score']==max_score:
						if hit['_index']=="freebase":
							entity_label = str(hit['_source']['label'])
							entity_id = '/'+str(hit['_source']['resource'].split('fbase:')[1].replace('.','/'))
				print "================================================"
				if entity_id:
					write_file.write("{0}\t{1}\t{2}\n".format(warc_id,entity_label,entity_id))
				else:
					print "Got results but no hits for "+entity[1:].strip()


				

def main(argv):
	runProcedure(argv)
	exit(0)



if __name__ == "__main__":
	argv = sys.argv
	if len(argv)<2:
		print "Provide the .warc.gz file as the first argument along with the script call.\nE.g.: python ~/parser.py sample.warc.gz"
	else:
		main(sys.argv[1:])
	exit(0)