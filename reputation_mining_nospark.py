import json
import gzip
import sys
import re
import pprint
import requests
import nltk
import os
from nltk import sent_tokenize, word_tokenize, pos_tag, ne_chunk, tree
from nltk.tag.stanford import StanfordNERTagger
from nytimesarticle import articleAPI
from pprint import pprint
from bs4 import BeautifulSoup



api_key = "01e07bd2b8034b81bc9bef8d3e35df3a"
api_interface = articleAPI(api_key)


warc_type_regex = re.compile(r'((WARC-Type:).*)')
warc_record_id_regex = re.compile(r'((WARC-Record-ID:) <.*>)')
html_regex = re.compile(r'<html\s*(((?!<html|<\/html>).)+)\s*<\/html>', re.DOTALL)


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

def casualTokenizing(text):
	sentences = sent_tokenize(text)
	sentences = filter(lambda sent: sent != "", sentences)
	tokens = word_tokenize(text)

	return sentences, tokens

def extractUniqueEntities(tokens):
	unique_entities = []
	entity_count = {}
	tagged_entities = ne_chunk(tokens, binary=False)
	# st = StanfordNERTagger('./stan_files/english.all.3class.distsim.crf.ser.gz','./stan_files/stanford-ner.jar')
	# print st.tag("The Washington Monument is the most prominent structure in Washington, D.C. and one of the city's early attractions. It was built in honor of George Washington, who led the country to independence and then became its first President.".split())
	# raw_input()
	for entity in tagged_entities:
		if isinstance(entity, tree.Tree):
			if entity not in unique_entities:
				unique_entities.append(entity)
			entity_buff=""
			for leaf in entity.leaves():
				entity_buff+=leaf[0]+" "
			entity_buff = entity_buff.strip()
			## In case of case sensitivity issues, replace this with the bellow code.
			# if entity_buff.lower() not in entity_count.keys():
			# 	entity_count[entity_buff.lower()] = 1
			# else:
			# 	entity_count[entity_buff.lower()] += 1
			if entity_buff not in entity_count.keys():
				entity_count[entity_buff] = 1
			else:
				entity_count[entity_buff] += 1
	return unique_entities, entity_count


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

def get_articles(args):
	articles = api_interface.search( 
		q = 'Barack Obama',
		fq = {'headline':'Obama','body':'Barack Obama','source':'The New York Times'},
		sort = 'newest',
		begin_date=20081125
		# Date 2008/11/25 onwards
		#filter query : Headline Related to Obama
	)
	return articles

## ============Article Keys=============
##[u'type_of_material', u'blog', u'news_desk', u'lead_paragraph', u'headline', u'abstract',\
## u'print_page', u'word_count', u'_id', u'snippet', u'source', u'slideshow_credits', u'web_url',\
## u'multimedia', u'subsection_name', u'keywords', u'byline', u'document_type', u'pub_date', u'section_name']

def filter_articles(articles):
	docs = articles['response']['docs']
	filtered = []
	for d in docs:
		d['headline']['main'] = d['headline']['main'].encode('utf-8')
		keyword_buffer = []
		for k in d['keywords']:
			if (k['name']!='subject'):
				keyword_buffer.append(k)

		d['keywords'] = keyword_buffer
		d.pop('multimedia', None)
		d.pop('slideshow_credits', None)
		d.pop('snippet', None)
		d.pop('lead_paragraph', None)
		if (d['section_name'].encode('utf-8') != 'Opinion'):
			filtered.append(d)
		
	return filtered

def runProcedure(argv):
	WARC_RECORD_ID = argv[0]
	file_name = validateInput(argv[1])
	output_name = argv[2]

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

			##Tokening first into sentences and then into words.
			sentence, tokens = casualTokenizing(text)
			
			tagged_tokens = pos_tag(tokens)

			##Discovering and tagging Named Entities (NER)
			warc_index+=3
			# warc_id = ((warc_records_ids[warc_index][0]).split(' '))[1]
			
			entities, entity_count = extractUniqueEntities(tagged_tokens)
			# linked_entities = linkEntities(entities)

			
			for entity in entities:	##linked_entities should go here.
				entity = "Obama"
				api_response = get_articles(entity)
				# articles = toy_parser(api_response)
				filtered_articles = filter_articles(api_response)
				r = ''
				print len(api_response)
				print len(filtered_articles)
				for article in filtered_articles:
					article_entities = []
					article_entities_count = {}
					print article['web_url']
					r = requests.get(article['web_url'])
					soup = BeautifulSoup(r.text, 'html.parser')
					# text = soup.get_text('p class="story-body-text story-content"')
					text = soup.find_all('p', {'class':'story-body-text story-content'})
					merged_text = ''
					for t in text:
						# print t.get_text()
						merged_text+=t.get_text()
					# merged_text=merged_text.decode('utf-8').encode('utf-8')
					article_sentences, article_tokens = casualTokenizing(merged_text)
					article_tagged_tokens = pos_tag(article_tokens)
					article_entities, article_entities_count = extractUniqueEntities(article_tagged_tokens)
					print "------ Title: "+article['headline']['main']+" ----------"
					print "\n***Entity Trees Found:***\n"+str(article_entities)
					print "\n***Entity Occurance Rate:***\n"+str(article_entities_count)
					print "\n(press return for next article.)"
					raw_input()

				return 0


			# write_file = open(output_name, 'a')
			# for linked in linked_entities:
			# 	write_file.write("{0}\t{1}\t{2}\n".format(warc_id,linked['entity_label'],linked['entity_id']))
			# write_file.close()

				

def main(argv):
	runProcedure(argv)
	exit(0)



if __name__ == "__main__":
	argv = sys.argv
	if len(argv)<3:
		print "Provide the .warc.gz file as the second argument along with the script call.\nE.g.: python ~/parser.py sample.warc.gz"
	else:
		main(sys.argv[1:])
	exit(0)