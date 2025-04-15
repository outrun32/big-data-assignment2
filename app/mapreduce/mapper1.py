#!/usr/bin/env python3
import sys
import os
import re
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

pattern = re.compile(r'\w+')

for line in sys.stdin:
    try:
        filepath, content = line.strip().split('\t', 1)
        doc_id = os.path.basename(filepath).split('.')[0]
    except ValueError:
        continue
    
    tokens = pattern.findall(content.lower())
    
    # Process tokens: remove stopwords and stem
    position = 0
    for token in tokens:
        if len(token) > 2 and token not in stop_words:
            stemmed_token = stemmer.stem(token)
            print(f"{stemmed_token}\t{doc_id}\t{position}\t1")
            position += 1