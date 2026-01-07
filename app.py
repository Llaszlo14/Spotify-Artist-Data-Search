from flask import Flask, render_template, request
from myProject import desired_value, same_genre_artists, nodes, listeners


# Establishes flask app
app = Flask(__name__)


@app.route('/')
def home():
	"""Renders the html template for the home page of webapp.

	Includes a search bar with 
	autofill suggestions and submit buttons that link to other pages. 
	"""
	return render_template("index.html", suggestions=nodes['name'].tolist())

@app.route('/artist')
def artist():
	"""Renders the html template for the searched artist's information.

	If the search value is not found in either Listeners or Nodes, will instead render 
	the html template for the incorrect search page. 
	"""
	try:
		return render_template("artist.html", name=request.args.get("search"), 
			followers=desired_value(listeners, 'followers'),
			peak_followers=desired_value(listeners, 'PkListeners'),
			popularity=desired_value(nodes, 'popularity'),

			# Finds the location of the searched artists in terms of its index number and then
			# adds 1, since index locations start at 0, but the actual index starts at 1 (ChatGPT-plus 31 May 2025)
			ranking=nodes.index.get_loc(nodes[nodes['name'] == request.args.get("search")].index[0]) + 1,

			genres=desired_value(nodes,'genres'),
			chart_hits=desired_value(nodes,'chart_hits'),

			# Includes every artist possible, since the top ranking artists has
			# just under 110 million followers
			top_similar_artists=same_genre_artists(110000000),

			lesser_similar_artists=same_genre_artists(500000))
	except:
		return render_template("unwelcome.html")
	
		
		

@app.route('/genre')
def genre():
	"""Renders the html template for the searched genre's information.

	If the searched value is not found in nodes, will instead render the html template
	for the incorrect search page. 
	"""
	if same_genre_artists(110000000, request.args.get("search")) == []:
		return render_template("unwelcome.html")
	else:
		return render_template("genre.html", name=request.args.get("search"),
			top_similar_artists=same_genre_artists(110000000,request.args.get("search")),
			lesser_similar_artists=same_genre_artists(500000,request.args.get("search")))

@app.route('/stats')
def stats():
	"""Renders the html template for the general stats page.

	Includes a dataframe of the top 100 artists in listeners, and displays two plots as well.
	"""
	return render_template("stats.html",
		# The top 100 artists are split in half and inputted as two different dataframes so they
		# can be displayed side by side to take up less space
		table1=listeners.loc[1:50,['name','followers','PkListeners']].head(100).to_html(table_id="table1", classes="dataframe"),
		table2=listeners.loc[51:100,['name','followers','PkListeners']].to_html(table_id="table2", classes="dataframe"))


if __name__ == '__main__':
	app.run(debug=True)