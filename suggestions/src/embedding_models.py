from gensim.models.doc2vec import Doc2Vec, TaggedDocument, Word2Vec
import string
import json
from functools import reduce
import os
import numpy as np

def tokenize(document):
    return document.split()

def remove_punctuation(text):
    return text.translate(str.maketrans('', '', string.punctuation))

def pre_process(document):
    return remove_punctuation(document).lower()

def normalize(vec):
    norm = np.linalg.norm(vec)
    return vec if norm == 0 else vec / norm


def get_vector(summary, subjects):
    global summary_model
    summary_vector = normalize(summary_model.infer_vector(tokenize(pre_process(summary))))
    subjects_vector = normalize(infer_subjects(subjects))
    return np.concatenate((summary_vector, subjects_vector))

def infer_subjects(subjects):
    global subject_model
    subjects_flat = ' '.join(subjects)
    tokens = tokenize(pre_process(subjects_flat))
    vectors = [subject_model.wv[token] for token in tokens if token in subject_model.wv]
    return np.mean(vectors, axis=0) if vectors else np.zeros(subject_model.vector_size)


if os.path.exists("suggestions/models/summary_doc2vec.model"):
    print("loading summary model")
    summary_model = Doc2Vec.load("suggestions/models/summary_doc2vec.model")

if os.path.exists("suggestions/models/subjects_word2vec.model"):
    print("loading subjects model")
    subject_model = Word2Vec.load("suggestions/models/subjects_word2vec.model")


def main():
    with open('data.json') as f:
        data = json.load(f)

    books = [v for _, v in data.items()]
    summaries  = [*map(lambda book: book['summary'], books)]
    subjects = reduce(set.union, map(lambda book: set(book['subjects']), books))

    # As summaries are large enough we use doc2vec model
    tagged_data = [TaggedDocument(words=tokenize(pre_process(doc)), tags=[str(i)]) for i, doc in enumerate(summaries)]
    summary_model = Doc2Vec(vector_size=702, window=5, min_count=1, workers=4, epochs=40)
    summary_model.build_vocab(tagged_data)
    summary_model.train(tagged_data, total_examples=summary_model.corpus_count, epochs=summary_model.epochs)
    summary_model.save('suggestions/models/doc2vec_summary.model')

    # Subjects are small, so we use word2vec and do mean-aggregation on all subjects
    tokenized_subjects = [*map(lambda subject: tokenize(pre_process(subject)), subjects)]
    subject_model = Word2Vec(sentences=tokenized_subjects, vector_size=50, window=2, min_count=1, workers=4, epochs=50)
    subject_model.save("suggestions/models/word2vec_summary.model")


if __name__ == 'main':
    main()