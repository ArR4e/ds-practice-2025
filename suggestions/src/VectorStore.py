import json
from embedding_models import get_vector
import numpy as np
from numpy.linalg import norm
from heapq import nlargest

class VectorStore:
    def __init__(self):
        import os
        current_path = os.getcwd()
        print(current_path)
        with open('suggestions/data/data.json') as f:
            data = json.load(f)
        self.vectors = {bookId:get_vector(book['summary'], book['subjects'])  for bookId, book in data.items()}


    def get_top_similar(self, book_id: str, k = 5) -> list[(str, float)]:
        vec = self.vectors.get(book_id)
        if vec is None:
            return list()
        ranked_books = [(book_id, self.cosine_similarity(vec, cur_vec)) for (book_id, cur_vec) in self.vectors.items()]

        return nlargest(k, ranked_books, key = lambda ranked_book: ranked_book[1])

    def get_score(self, book_id: str, book_ids) -> list[str, float] | None :
        # To score arbitrary book, we score it against relevant (bought) books and take maximum of the score
        vec = self.vectors.get(book_id)
        if vec is None:
            return None
        similarities = [self.cosine_similarity(self.vectors[cur_book_id], vec) for cur_book_id in book_ids if self.vectors[cur_book_id] is not None]
        return (book_id, max(similarities)) if similarities else None


    def cosine_similarity(self, vec1, vec2):
        """Returns the cosine similarity between two vectors."""
        return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))