import sys
from nytimesarticle import articleAPI
from pprint import pprint
import requests

api_key = "01e07bd2b8034b81bc9bef8d3e35df3a"
api_interface = articleAPI(api_key)


##This is gonna be modified in order to make the request for the exact entity we want.
def get_articles(args):
	articles = api_interface.search( 
		q = 'Obama',
		fq = {'headline':'Obama','body':'Barack Obama','source':'The New York Times'},
		begin_date=20081125
		# Date 2008/11/25 onwards
		#filter query : Headline Related to Obama
	)
	return articles


def parser(articles):
	article_list = []
	article_buffer={}
	for article in articles['response']['docs']:
		article_buffer['abstract'] = article['abstract']
		article_buffer['headline'] = article['headline']['main'].encode("utf8")
		article_buffer['desk'] = article['news_desk']
		article_buffer['date'] = article['pub_date'][0:10] # cutting time of day.
		article_buffer['section'] = article['section_name'].encode("utf8")

		article_buffer['source'] = article['source']
		article_buffer['type'] = article['type_of_material']
		article_buffer['url'] = article['web_url']
		article_buffer['word_count'] = article['word_count']
		

		locations = []
		persons = []
		for x in range(0,len(article['keywords'])):
			if 'glocations' in article['keywords'][x]['name']:
				locations.append(article['keywords'][x]['value'])
			elif 'persons' in article['keywords'][x]['name']:
				persons.append(article['keywords'][x]['value'])
			else:
				pass
		article_buffer['locations'] = locations
		article_buffer['persons'] = persons

		article_list.append(article_buffer)

	return article_list

def main(argv):
	##The following entity is just explanatory on how it is going to work in the near future
	entity = "Obama"
	api_response = get_articles(entity)
	articles = parser(api_response)

	pprint(articles)


if __name__ == "__main__":
	argv = sys.argv
	if argv:
		main(sys.argv[1:])
	else:
		main()
	exit(0)