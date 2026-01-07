import numpy as np
import pandas as pd
from flask import Flask, render_template, request
import matplotlib.pyplot as plt



# Reads the two datasets and turns them into pandas dataframes
nodes = pd.read_csv('nodes.csv', usecols=[1,2,3,4,5])
listeners = pd.read_csv('listeners.csv', header=0, names=['name','followers','Daily Trend','Peak','PkListeners'])

# Nodes is not listed in any sort of order, so this orders it
# by artists' follower counts
nodes.sort_values('followers', ascending=False, inplace=True, ignore_index=True)

# Changes the index to start at 1 instead of 0 for both dataframes so that the index 
# reflects a correctly numbered ranking of artists starting at 1
nodes.index = np.arange(1,len(nodes)+1)
listeners.index = np.arange(1,len(listeners)+1)

# Converts symbols that are incorrectly displayed into the correct text encoding (ChatGPT-plus 29 May 2025)
listeners['name'] = listeners['name'].apply(lambda x: x.encode('latin1').decode('utf-8') if isinstance(x, str) else x)




def object_to_list(object):
	"""Converts values in a given column that were meant to be lists but are interpreted as 
	strings back into lists.

	This function is meant to be used with the apply() method for pandas dataframes.

	The object parameter is interpreted by apply() as going through every value in the
	given column one by one and applying this function.
	Returns a list of strings without any extra characters or spaces. 
	"""
	object_list = str(object).strip('[]').replace("'",'').split(',')
	return [item.lstrip(' ') for item in object_list]


# converts necessary fields into lists row by row using the object_to_list function
nodes['genres'] = nodes['genres'].apply(object_to_list)
nodes['chart_hits'] = nodes['chart_hits'].apply(object_to_list)



def desired_value(dataset, column):
	"""Outputs the specified column value for the searched artist from a specified dataset.

	Dataset is either nodes or listeners, column can be any column from any dataset written as 
	a string (e.g 'names','followers','genres').
	Returns a string or list depending on the specified field.  

	If the artist or column value for the artist does not appear in the listeners dataset, 
	an IndexError exception is raised and it looks for the information within nodes 
	(which is a larger dataset).

	If the artist is in nodes, but the column isn't, a KeyError is raised, and 'Data Not Available'
	is returned
	If the artist doesn't exist in either dataset, there will be an IndexError.
	"""
	try:
		return dataset.loc[dataset[dataset.columns[0]]==request.args.get("search"), column].iloc[0]
	except IndexError:
		try:
			return nodes.loc[nodes[nodes.columns[0]]==request.args.get("search"), column].iloc[0]
		except KeyError:
			return 'Data Not Available'



def same_genre_artists(less_than, genres=0):
	"""Outputs 10 similar artists to the searched artist

	The paremeter less_than accepts an integer, and genres accepts a string.
	Returns a list ordered by follower count of the names of 10 artists who have 
	one or more of the genres specified in their genre list. 

	The list will only include artists with a follower count below less_than.

	By default, genres will be considered as the list of genres for the searched artist.
	If a specific genre is inputted, will return a list of artists for that genre only. 
	"""
	if genres == 0:
		genres = desired_value(nodes, 'genres')

		for genre in genres:
			nodes['similar'] = nodes['genres'].apply(lambda x: genre in x)

	else:
		nodes['similar'] = nodes['genres'].apply(lambda x: genres in x)
	
	new_frame = nodes[nodes['similar']!=False]
	new_frame = new_frame[new_frame['name'] != request.args.get("search")]
	new_frame = new_frame[new_frame['followers'] < less_than]
	similar_artists = new_frame['name'].head(10).unique().tolist()

	return similar_artists


def plt_format(_y,sample_size):
	"""Formats a basic plot template with artist rankings as the x axis, and 
	_y as the y axis.

	The parameter _y takes in a nodes dataframe column name as a string,
	sample_size is an integer that indicates how many artists to include. 
	"""
	df = nodes.head(sample_size).copy()

	# Changes the name of the artist Joey Bada$$ to Joey Badass, since matplotlib reads
	# dollar signs as the part of a LaTeX expression
	df.loc[868,'name'] ='Joey Badass'

	x=df.index.tolist()
	y = df[_y]

	plt.figure(figsize=(9, 6))
	plt.plot(x,y, color='#1DB954', linewidth=2.5)

	plt.title('Top ' + format(sample_size,',') + ' Artists ' + _y.capitalize() + ' Distribution',
	           pad=13, fontdict={'family':'geneva','size':18})
	plt.xlabel('Artist Ranking', labelpad=7, fontdict={'family':'geneva', 'size':14})

	# Makes the label of the y axis the same as _y but with the first letter capitalized
	# for consistency across all labels in the plot
	plt.ylabel(_y.capitalize(), labelpad=7, fontdict={'family':'geneva', 'size':14})
	plt.fill_between(x,y, color = '#1DB954', alpha=0.3)

	# Makes x axis labels start at 1 instead of 0, since 0 is not an artist ranking value
	step_size = int(sample_size/10)
	plt.xticks(np.arange(0,sample_size+1,step_size),[1] + [i*step_size for i in range(1,11)])



plt_format('followers',1000)
plt.savefig('static/plt1.png')
plt_format('popularity',10000)
plt.savefig('static/plt2.png')








