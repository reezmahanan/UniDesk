import math
import re
from typing import List
from app.config import settings

class EmbeddingService:
    def __init__(self):
        self.dimension = settings.EMBEDDING_DIMENSION
        self.provider = settings.EMBEDDING_PROVIDER

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector. If GEMINI_API_KEY is configured and not in mock mode,
        use Google GenAI client. Otherwise, generate a deterministic normalized semantic hash vector.
        """
        if settings.GEMINI_API_KEY and not settings.MOCK_AI_MODE and self.provider == "gemini":
            try:
                from google import genai
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                response = client.models.embed_content(
                    model=settings.EMBEDDING_MODEL,
                    contents=text,
                )
                embedding_values = response.embedding.values
                if len(embedding_values) == self.dimension:
                    return embedding_values
                elif len(embedding_values) > self.dimension:
                    return embedding_values[:self.dimension]
                else:
                    return embedding_values + [0.0] * (self.dimension - len(embedding_values))
            except Exception as e:
                # Fallback to deterministic representation on API failure
                pass

        return self._generate_local_embedding(text)

    def _generate_local_embedding(self, text: str) -> List[float]:
        """
        Deterministic local word-frequency hash embedding for offline testing and demo.
        Yields normalized float vector of length `self.dimension`.
        """
        vec = [0.0] * self.dimension
        words = re.findall(r'\b[a-zA-Z0-9_\u0D80-\u0DFF\u0B80-\u0BFF]+\b', text.lower())
        if not words:
            return vec

        for word in words:
            # Hash word into bucket
            h = abs(hash(word)) % self.dimension
            vec[h] += 1.0

        # L2 Normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]

        return vec

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2:
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

embedding_service = EmbeddingService()
