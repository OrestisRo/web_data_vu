import json
import os
import gzip
import sys
import re
import pprint
from nltk import sent_tokenize, word_tokenize, pos_tag, ne_chunk, tree
from bs4 import BeautifulSoup
from pyspark import SparkContext

warc_type_regex = re.compile(r'((WARC-Type:).*)')
warc_record_id_regex = re.compile(r'((WARC-Record-ID:) <.*>)')
html_regex = re.compile(r'<html\s*(((?!<html|<\/html>).)+)\s*<\/html>', re.DOTALL)

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


def validateInput(file_name):
	if "warc.gz" not in file_name:
		print file_name+" is of unsupported type. Supported type is .warc.gz!"
		return 0
	else:
		return file_name


def getText(html_page):
	soup = BeautifulSoup("<html>"+html_page+"</html>", 'html.parser')
	text = soup.get_text()
	return text		


def linkEntities(entities):
	linked_entities=[]
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
					try:
						entity_label = str(hit['_source']['label'])
					except Exception as e:
						continue
					entity_id = '/'+str(hit['_source']['resource'].split('fbase:')[1].replace('.','/'))
		print "================================================"
		if entity_id:
			linked_entities.append({'entity_label':entity_label,'entity_id':entity_id})
		else:
			# print "Got results but no hits for "+entity[1:].strip()
			continue
	return linked_entities			



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
	WARC_RECORD_ID = argv[0]
	file_name = validateInput(argv[1])
	output_name = argv[2]
	unique_entities = []

	with gzip.open(file_name, 'rb') as f:
		warc_id = "Warc_id pending."
		warc_content = f.read()

		warc_types = re.findall(warc_type_regex, warc_content)
		warc_records_ids = re.findall(warc_record_id_regex,warc_content)
		warc_index = -1
		##Getting all html text and putting it in the responsive array.
		html_pages_array = re.findall(html_regex, warc_content)

		##For each element in array:
		write_file = open(output_name, 'w')
		# write_file.write("{0}\t{1}\t{2}\n".format("WARC-RECORD-ID","Entity Labe;","Freebase Entity ID"))
		write_file.close()
		for html_page in html_pages_array:
			warc_id=''
			##Extracting all text with BS
			##I'm appending the tags to the front and the back as they are getting stripped cause of our warc regex.
			text = getText(html_page[0])
	
	text_rdd = sc.parallelize(text.split(' '))
	tokens_rdd = text_rdd.map(lambda t: tokenize(t))
	tagged_tokens_rdd = tokens_rdd.map(lambda tt: tag(tt))
	tagged_entities_rdd = tagged_tokens_rdd.map(lambda x: chunk(x))
	tagged_entities = tagged_entities_rdd.collect()

	for entity in tagged_entities:
		if isinstance(entity, tree.Tree):
			if entity not in unique_entities:
				unique_entities.append(entity)


	warc_index+=3
	warc_id = ((warc_records_ids[warc_index][0]).split(' '))[1]
			

	write_file = open(output_name, 'a')

	linked_entities = linkEntities(unique_entities)

	for linked in linked_entities:
		write_file.write("{0}\t{1}\t{2}\n".format(warc_id,linked['entity_label'],linked['entity_id']))

	write_file.close()
			

			
				

if __name__ == "__main__":
	argv = sys.argv
	if len(argv)<3:
		print "Provide the .warc.gz file as the first argument along with the script call.\nE.g.: python ~/parser.py sample.warc.gz"
	else:
		main(sys.argv[1:])
	exit(0)