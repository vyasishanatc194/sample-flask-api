from collections import Counter
import re
import os
import nltk
from wordsegment import Segmenter as BaseSegmenter


WORDS = nltk.corpus.brown.words()
COUNTS = Counter(WORDS)


def pdist(counter):
    "Make a probability distribution, given evidence from a Counter."
    N = sum(counter.values())
    return lambda x: counter[x]/N


P = pdist(COUNTS)


def Pwords(words):
    "Probability of words, assuming each word is independent of others."
    return product(P(w) for w in words)


def product(nums):
    "Multiply the numbers together.  (Like `sum`, but with multiplication.)"
    result = 1
    for x in nums:
        result *= x
    return result


def splits(text, start=0, l=20):
    "Return a list of all (first, rest) pairs; start <= len(first) <= l."
    return [(text[:i], text[i:]) 
            for i in range(start, min(len(text), l)+1)]


def segment_func(text):
    "Return a list of words that is the most probable segmentation of text."
    if not text: 
        return []
    else:
        candidates = ([first] + segment(rest) 
                      for (first, rest) in splits(text, 1))
        return max(candidates, key=Pwords)


class Segmenter(BaseSegmenter):

    UNIGRAMS_FILENAME = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'unigrams.txt',
    )


_segmenter = Segmenter()        # pylint: disable=invalid-name
clean = _segmenter.clean        # pylint: disable=invalid-name
load = _segmenter.load          # pylint: disable=invalid-name
isegment = _segmenter.isegment  # pylint: disable=invalid-name
segment = _segmenter.segment    # pylint: disable=invalid-name
UNIGRAMS = _segmenter.unigrams
BIGRAMS = _segmenter.bigrams
WORDS = _segmenter.words


if __name__ == "__main__":
    load()
    print(segment("United Healthcare"))
