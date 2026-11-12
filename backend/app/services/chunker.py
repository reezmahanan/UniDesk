from typing import List, Dict, Any

class ChunkerService:
    def __init__(self, target_chunk_size: int = 350, chunk_overlap: int = 50):
        self.target_chunk_size = target_chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        chunk_idx = 0

        for sec in sections:
            content = sec.get("content", "").strip()
            page_num = sec.get("page_number")
            heading = sec.get("section_heading", "General")

            if not content:
                continue

            words = content.split()
            if len(words) <= self.target_chunk_size:
                chunks.append({
                    "chunk_index": chunk_idx,
                    "content": content,
                    "page_number": page_num,
                    "section_heading": heading,
                    "token_count": len(words),
                })
                chunk_idx += 1
            else:
                # Sliding window chunking
                start = 0
                while start < len(words):
                    end = min(start + self.target_chunk_size, len(words))
                    chunk_words = words[start:end]
                    chunk_text = " ".join(chunk_words)

                    chunks.append({
                        "chunk_index": chunk_idx,
                        "content": chunk_text,
                        "page_number": page_num,
                        "section_heading": heading,
                        "token_count": len(chunk_words),
                    })
                    chunk_idx += 1

                    if end == len(words):
                        break
                    start += (self.target_chunk_size - self.chunk_overlap)

        return chunks

chunker = ChunkerService()
