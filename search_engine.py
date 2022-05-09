from glob import glob
import spacy
import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KDTree

def lcp(a: str, b:str):
    '''
    Computes the longest common prefix of the strings `a` and `b`
    '''
    lcp = 0
    while lcp < len(a) and lcp < len(b) and a[lcp] == b[lcp]:
        lcp += 1
    return lcp

class SearchEngine(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SearchEngine, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm", disable=["parser", "ner", "tagger"])

        def spacy_tokenizer(text):
            return [t.lemma_ for t in self.nlp(text)]
        
        template = "https://en.wikipedia.org/wiki/"
        self.documents, self.links = [], []

        for fname in glob('wiki_data/texts*.txt'):
            with open(fname) as f:
                document = ""
                lines = f.readlines()
                self.links.append(template + lines[0][2:-3])
                for line in lines:
                    document = document + line.strip()
                
                self.documents.append(document)


        self.vec = TfidfVectorizer(tokenizer=spacy_tokenizer)
        self.trained_vectors = self.vec.fit_transform(self.documents).todense()
        self.tree = KDTree(self.trained_vectors)

        self.all_words = self.vec.vocabulary_

    def most_similar(self, text: str):
        '''
        Returns the most similar word to `text` in the training vocabulary 
        by using Edit Distance* (ED from now on) and Longest Common Prefix
        (LCP from now).

        In general:
        - the lower the ED, the more similar the words are.
        - the greater the LCP, the more similar the words are.

        Assumption:
        - Typos are more likely to happen in the middle and the end of the words.
        That's why the LCP plays a major role in comparing the similarity of words.

        Final Similarity criteria**:
        - the similarity of two words `a` and `b` is log(ED(a, b)) / (LCP(a, b) + 1)

        * Edit Distance is also called Levenshtein Distance
        ** It might change later
        '''

        result = min([[np.log(nltk.edit_distance(word, text)) / (lcp(word, text) + 1), word] for word in self.all_words])
        
        return result[1]
    

    def do_search(self, text: str):
        if len(text) == 0:
            return []
        text = text.lower()

        text2 = ""
        for t in self.nlp(text):
            word = t.lemma_
            if word not in self.all_words:
                word = self.most_similar(word)
            text2 += " "
            text2 += word 

        new_vector = self.vec.transform([text2]).todense()
        _, ind = self.tree.query(new_vector, k = 10)
        return [self.links[i] for i in list(ind[0])]


engine = SearchEngine()