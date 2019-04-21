import nltk.classify.util, nltk.metrics
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from nltk.corpus import stopwords
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist
import collections
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from django.core.cache import cache

stopwords = set(stopwords.words('english'))

feature_selection_method = 'best_words_features'

# python manage.py load_sentiment_classifier --num_best_words=20000

class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('--num_best_words', dest='num_best_words',
                             type=str, action='store',
                             help='Number of words with high information');


    #Filter words that are not stopwords
    def stopword_filtered_words_features(self, words):
        return dict([(word, True) for word in words if word not in stopwords])

    #Filter words that are the best words in the nltk movie_reviews corpus.
    #The best words are chosen according to the chi square score between words and their sentiment correlation.
    #that is, if a word is capable of differenciate from positve and negative examples then it will have a high score.
    def best_words_features(self, words):
        return dict([(word, True) for word in words if word in self.best_sentiment_words])

    #Filter words with the best chi_sq score given bigrams
    def best_bigrams_word_features(self, words, measure=BigramAssocMeasures.chi_sq, nbigrams=200):
        bigram_finder = BigramCollocationFinder.from_words(words)
        bigrams = bigram_finder.nbest(measure, nbigrams)
        #Create a dictionary with the best bigrams in the movie review.
        d = dict([(bigram, True) for bigram in bigrams])
        #Add the unigrams from the movie review  that also belong to the nltk reviews corpus.
        d.update(self.best_words_features(words))
        return d

    #Trains a Naive Bayes classifier
    #Preprocesses the words in each review, filters the best words according to the selected feature selection method
    #and trains a Naive Bayes classifier.
    def train_clf(self, feature_selection_method):
        negidxs = movie_reviews.fileids('neg')
        posidxs = movie_reviews.fileids('pos')
        if feature_selection_method == 'stopword_filtered_words_features':

            negfeatures = [(self.stopword_filtered_words_features(movie_reviews.words(fileids=[file])), 'neg') for file in
                           negidxs]
            posfeatures = [(self.stopword_filtered_words_features(movie_reviews.words(fileids=[file])), 'pos') for file in
                           posidxs]
        elif feature_selection_method == 'best_words_features':
            negfeatures = [(self.best_words_features(movie_reviews.words(fileids=[file])), 'neg') for file in negidxs]
            posfeatures = [(self.best_words_features(movie_reviews.words(fileids=[file])), 'pos') for file in posidxs]
        elif feature_selection_method == 'best_bigrams_words_features':
            negfeatures = [(self.best_bigrams_words_features(movie_reviews.words(fileids=[file])), 'neg') for file in
                           negidxs]
            posfeatures = [(self.best_bigrams_words_features(movie_reviews.words(fileids=[file])), 'pos') for file in
                           posidxs]

        trainfeatures = negfeatures + posfeatures
        clf = NaiveBayesClassifier.train(trainfeatures)
        return clf



    # Choose best words according to their correlation to being a positive or negative word.
    # Ej. Computer and buy are neutral words, so their score will be low; whereas excellent and bad will have a high score.
    def get_most_informative_words_chi(self, num_best_words):
        word_fd = FreqDist()
        label_word_fd = ConditionalFreqDist()

        for word in movie_reviews.words(categories=['pos']):
            word_fd[word.lower()] += 1
            label_word_fd['pos'][word.lower()] += 1

        for word in movie_reviews.words(categories=['neg']):
            word_fd[word.lower()] += 1
            label_word_fd['neg'][word.lower()] += 1

        pos_word_count = label_word_fd['pos'].N()
        neg_word_count = label_word_fd['neg'].N()
        total_word_count = pos_word_count + neg_word_count

        word_scores = {}

        for word, freq in word_fd.items():
            #https://stackoverflow.com/questions/32549376/can-someone-explain-the-syntax-of-bigramassocmeasures-chi-sq
            pos_score = BigramAssocMeasures.chi_sq(label_word_fd['pos'][word],
                                                   (freq, pos_word_count), total_word_count)
            neg_score = BigramAssocMeasures.chi_sq(label_word_fd['neg'][word],
                                                   (freq, neg_word_count), total_word_count)
            word_scores[word] = pos_score + neg_score

        best = sorted(word_scores.items(), key=lambda tuple: tuple[1], reverse=True)[:num_best_words]
        bestwords = set([w for w, s in best])
        return bestwords

    def handle(self, *args, **options):
        num_best_words = int(options['num_best_words'])
        self.best_sentiment_words = self.get_most_informative_words_chi(num_best_words)
        clf = self.train_clf(feature_selection_method)
        cache.set('clf', clf)
        print("Setting in clf", clf)
        cache.set('best_sentiment_words', self.best_sentiment_words)
        print("Setting sentiment_words", cache.get('best_sentiment_words'))
        cache.set("test_data", 2)
        print("Setting test data, ", cache.get('test_data'))