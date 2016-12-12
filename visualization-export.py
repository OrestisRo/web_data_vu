import pandas as pd
import matplotlib.pyplot as plt;plt.rcdefaults()
import matplotlib as mpl
import numpy as np
import matplotlib.lines as mlines
import random


list1 = ['Entity1', 'Entity2', 'Entity3', 'Entity4', 'Entity5', 'Entity6','Entity7', 'Entity8', 'Entity9', 'Entity10']
list2 = [1,2,3,21,5,6,7,8,9,20]




for i in range(1,5):
	plt.figure(i)
	
	random.shuffle(list2)
	
	dictionary = dict(zip(list1,list2))
	s = pd.Series(
		dictionary.values(),
		dictionary.keys()
	)
	mpl.rcParams['legend.numpoints'] = 1
	
	
	#Set descriptions:
	plt.title("Entity Relation")
	plt.ylabel('Extracted Entities')
	plt.xlabel('Popularity', color='blue')

	#Set tick colors:
	ax = plt.gca()
	ax.tick_params(axis='x', colors='blue')
	ax.tick_params(axis='y', colors='purple')

	
	#Plot the data:
	my_colors = 'rgbkymc'  #red, green, blue, black, etc.

	s.plot( 
		kind='barh', 
		color=my_colors,
		legend=True,
	)
	
	max_val = dictionary.values().index(max(dictionary.values()))
	if max_val > 7: max_val=-7
	
	blue_line = mlines.Line2D([], [], color="rgbkymc"[max_val], marker='*',
                          markersize=20, label='Most Popular Entity')
	
	plt.legend(handles=[blue_line])
	file = 'temp'+str(i)+'png'
	plt.savefig(file)