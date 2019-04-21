# Movie-Analyzer
Web application that analyses movies scraped from the web given a user query. 

Uses Scrapy to gather movie recommendations from Google and a simple version of the PageRank algorithm was implemented to rank the results. Finally a Naive Bayes classifier is used to classify the reviews into posive or negative and give a general view about the popularity of the movie.

###PG Rank

After the sentiment analysis results are displayed, the user can rank the movie review pages by clicking "Calculate Rank".
A crawler gathers and travels through each of the review urls with a max depth of 2, saves the pages and creates links between the visited pages.
To rank each page in the collected set, a version of the PageRank algorithm was implemted using the power iteration method.

###Sentiment analysis

By querying a movie title the engine makes an automated query to Google or Bing.
It saves the urls of the search results and a spider collects the reviews of each page.
A Multinomial Naive Bayes Classifier is used for sentiment analysis.
A graphic is displayed with the classification results.</li>

####-Framework details.

This engine is written in Python, Scikit-Learn and NLTK on top of NumPy and SciPy stack. It uses Django for webserver backend.
