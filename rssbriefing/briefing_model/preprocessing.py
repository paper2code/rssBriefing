"""
    Module with functions for preprocessing

"""
import os
from datetime import datetime

import en_core_web_sm
from gensim.corpora import Dictionary
from gensim.models import Phrases
from spacy.lang.en import English
from spacy.lang.en.stop_words import STOP_WORDS

from rssbriefing.briefing_model.configs import stop_words, stop_words_to_remove, common_terms

module_path = os.path.abspath(os.path.dirname(__file__))


def preprocess(post):
    """ Preprocessing logic for a single document. Identical with the preprocessing logic used for LDA model training.

    :param post: [rssbriefing.models.Briefing]
    :return: doc: [Lst[str]]
    """
    nlp = load_language_model()
    doc = preprocess_document(post, nlp)
    doc = compute_bigrams(single_doc=doc)
    return doc


def initiate_language_model():
    nlp = en_core_web_sm.load()

    # Update stop words according to custom use case
    nlp.Defaults.stop_words.update(stop_words)
    for word in stop_words_to_remove:
        nlp.Defaults.stop_words.remove(word)

    for word in STOP_WORDS:
        lexeme = nlp.vocab[word]
        lexeme.is_stop = True

    nlp.to_disk(os.path.join(module_path, "models", f"spaCy_language_model_{datetime.now().strftime('%Y-%m-%d')}"))
    return nlp


def load_language_model():
    return English().from_disk(
        os.path.join(module_path, "models", f"spaCy_language_model_{datetime.now().strftime('%Y-%m-%d')}"))


# def entity_recognition(doc):
#     full_string = doc.text
#     for entity in doc.ents:
#
#     return doc

def preprocess_document(post, nlp):
    """ Perform preprocessing on a single document.

    Preprocessing covers:
        - Normalization: lowering all string
        - Tokenization
        - Lemmatization
        - custom filtering

    :param post: [rssbriefing.models.Briefing]
    :param nlp:
    :return:
    """

    doc = post.title + ' ' + post.description

    doc = doc.lower()

    doc = nlp(doc)

    # doc = entity_recognition(doc)

    doc = [word.lemma_ for word in doc
           if word.text != '\n' and
           word.text != '\n ' and
           word.text != '\n\n' and
           word.lemma_ not in STOP_WORDS and  # compare lemmatized string against stopwords list
           not word.is_punct and
           word.lemma_ != '-PRON-' and
           not word.like_num]

    # Custom filter for some RSS posts
    if doc[-2] == 'continue' and doc[-1] == 'reading':
        doc = doc[:-2]

    return doc


def tokenize_and_lemmatize(posts):
    """

    :param posts: [Lst[rssbriefing.models.Briefing]]
    :return:
    """
    nlp = initiate_language_model()

    corpus = [preprocess_document(post, nlp) for post in posts]

    return corpus


def train_phrases(tokenized_corpus):
    # If no pretrained Phrases model is available, instantiate one:
    if not os.path.isfile(os.path.join(module_path, 'models', 'Phrases_model')):
        bigram = Phrases(tokenized_corpus,
                         min_count=5,  # Ignore all words and bigrams with total collected count lower than this value.
                         common_terms=common_terms)  # List of stop words that won’t affect frequency count of expressions containing them.
        save_phrases(bigram)

    # Otherwise load the pretrained model and update it
    else:
        bigram = load_phrases()
        bigram.add_vocab(tokenized_corpus)
        save_phrases(bigram)

    return bigram


def load_phrases():
    phrases_model = Phrases.load(os.path.join(module_path, 'models', 'Phrases_model'))
    return phrases_model


def save_phrases(model):
    model.save(os.path.join(module_path, 'models', 'Phrases_model'))


def compute_bigrams(tokenized_corpus=None, single_doc=None):
    """ Enrich documents with composite tokens of bigrams such as "new_york". Takes either a corpus or a single doc.

    :param tokenized_corpus: [Lst[Lst[str]]] corpus consisting of documents, each document represented as list of tokens
    :param single_doc: [Lst[str]]
    :return: tokenized_corpus: [Lst[Lst[str]]] or single_doc: [Lst[str]]
    """
    if tokenized_corpus:
        bigram = train_phrases(tokenized_corpus)

        for idx in range(len(tokenized_corpus)):
            for token in bigram[tokenized_corpus[idx]]:
                if '_' in token:
                    # Token is a bigram, add to document.
                    tokenized_corpus[idx].append(token)

    elif single_doc:
        bigram = load_phrases()
        for token in bigram[single_doc]:
            if '_' in token:
                # Token is a bigram, add to document.
                single_doc.append(token)
    else:
        raise ValueError("compute_bigrams() expects either tokenized_corpus or single_doc. Neither was provided.")

    return tokenized_corpus if tokenized_corpus else single_doc


def get_dictionary(corpus):
    """ Construct a mapping between words/tokens and their respective integer ids - with gensim's Dictionary class

    :param corpus: [Lst[Lst[str]] corpus consisting of documents, each document represented as list of tokens
    :return: dictionary: [gensim.corpora.dictionary.Dictionary]
    """
    dictionary = Dictionary(corpus)

    # Filter out words that occur less than 4 documents, or more than 60% of the documents.
    dictionary.filter_extremes(no_below=4, no_above=0.6)

    dictionary.save(os.path.join(module_path, "models", f"dictionary_{datetime.now().strftime('%Y-%m-%d')}"))

    return dictionary


def load_current_dictionary():
    return Dictionary.load(os.path.join(module_path, "models", f"dictionary_{datetime.now().strftime('%Y-%m-%d')}"))
