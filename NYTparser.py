from nytimesarticle import articleAPI
api = articleAPI('01e07bd2b8034b81bc9bef8d3e35df3a')


articles = api.search( 
	q = 'Obama',
	fq = {'headline':'Obama','body':'Barack Obama','source':'The New York Times'},
	begin_date=20081125
	# Date 2008/11/25 onwards
	#filter query : Headline Related to Obama	

)


def parser():
	dic={}
	for article in articles['response']['docs']:
		dic['abstract'] = article['abstract']
        dic['headline'] = article['headline']['main'].encode("utf8")
        dic['desk'] = article['news_desk']
        dic['date'] = article['pub_date'][0:10] # cutting time of day.
        dic['section'] = article['section_name'].encode("utf8")

        dic['source'] = article['source']
        dic['type'] = article['type_of_material']
        dic['url'] = article['web_url']
        dic['word_count'] = article['word_count']
        #locations --- people related
        locations = []
        persons = []
        for x in range(0,len(article['keywords'])):
        	if 'glocations' in article['keywords'][x]['name']:
        		locations.append(article['keywords'][x]['value'])
        	elif 'persons' in article['keywords'][x]['name']:
        		persons.append(article['keywords'][x]['value'])
        	else:
        		pass
        dic['locations'] = locations
        dic['persons'] = persons

	return dic 


if __name__ == "__main__":
	news = parser()
	print news