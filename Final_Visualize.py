import pandas as pd
import matplotlib.pyplot as plt;plt.rcdefaults()
import matplotlib as mpl
import numpy as np
import matplotlib.lines as mlines
import sys
import operator

def visualize(main_entity_name, article_name, article_entities, output_name, bar_amount):
		#Initialize Values
		dictionary = dict()
		entities = list()
		values = list()
		for element in article_entities:
			if element == []:
				break
			else:
				dictionary[element['entity_label']] = element['count']
		
		#bar_amount check
		if(bar_amount != 0 and bar_amount < len(dictionary)):
			#Sort Dictionary As Iteretable .items(list) ,reverse=True Descending
			temp_sort_list = list(sorted(dictionary.items(),key=operator.itemgetter(1), reverse=True))
			
			counter=0
			#Create Sorted Entities - Values Lists
			for list_item in temp_sort_list:
				if( counter == bar_amount):
					break
				entities.append(list_item[0])
				values.append(list_item[1])
				counter+=1
		
		
		#Initialize the pd. set with Values - Keys
		s = pd.Series(
			values,
			entities
		)
		mpl.rcParams['legend.numpoints'] = 1
		#remove the second legend marker
		
		#Set descriptions:
		plt.title("Entity Relation")
		plt.ylabel('Extracted Entities')
		plt.xlabel('Popularity', color='blue')

		#Set tick colors:
		ax = plt.gca()
		ax.tick_params(axis='x', colors='blue')
		ax.tick_params(axis='y', colors='purple')

		
		#Plot the data:
		my_colors = 'rgbkymc'  #red, green, blue, black, etc. palete
		
		#plot Horizontal Bar & Colors & Legend
		s.plot( 
			kind='barh', 
			color=my_colors,
			legend=True,
		)
		#MAX RANKED ENTITY
		max_val = values.index(max(values))
		
		#Find the corresponded key/entity_name in the dictionary for the max valued entity 
		counter=0
		Entity = ''
		for j in entities:
			if counter == max_val:
				Entity = j
				break
			else:
				counter+=1

		#Adjust the entity in color palette (rgbkymc = 7)
		while( max_val - 7 >= 0): max_val-=7
		
		#Add Line2D objects to the Legend [Empty Line x2 , STAR]
		Article_name = mlines.Line2D([], [], color="b", marker=' ',
							  markersize=15, label="Article Name: " + article_name)
		Entity_name = mlines.Line2D([], [], color="b", marker=' ',
							  markersize=15, label="Related To: " + main_entity_name)
		Popular_Entity = mlines.Line2D([], [], color="rgbkymc"[max_val], marker='*',
							  markersize=15, label="Popular Entity: " + Entity)
		
							  
		#Initialize Legend's items and add it to Plot
		plt.legend(handles=[Article_name,Entity_name,Popular_Entity])

		#Export 
		plt.savefig(output_name)
		
"""
____________________________
            TEST DATA
____________________________


if __name__ == "__main__":
	#entities = ['Entity1', 'Entity2', 'Entity3', 'Entity4', 'Entity5', 'Entity6','Entity7', 'Entity8', 'Entity9', 'Entity10']
	#values = [0.01,0.2,1.3,0.1,0.45,0.66,0.7,0.67,0.15,0.34]
	#[{'entity_label':"obama", 'count': 5},{'entity_label':"trump", 'count': 2}]
	dict1 = {}
	dict2 = {}
	dict3 = {}
	dict4 = {}
	dict5 = {}
	dict6 = {}
	
	
	
	dict1['entity_label']='obama'
	dict1['count']=5
	
	dict2['entity_label']='tramp'
	dict2['count']=2
	
	dict3['entity_label']='hillary'
	dict3['count']=7
	
	dict4['entity_label']='Jefferson'
	dict4['count']=10
	
	dict5['entity_label']='Smith'
	dict5['count']=4
	
	dict6['entity_label']='Putin'
	dict6['count']=11
	
	
	article_entities = list()
	article_entities.append(dict1)
	article_entities.append(dict2)
	article_entities.append(dict3)
	article_entities.append(dict4)
	article_entities.append(dict5)
	article_entities.append(dict6)
	
	
	main_entity_name = "SOME ENTTY"
	article_name = "Article name"
	output_name = "FileX"
	
	visualize(main_entity_name,article_name,article_entities,output_name,bar_amount=4)
	
"""
