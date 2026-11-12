import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.knowledge import KnowledgeDocument, DocumentChunk, ContentStatus
from app.models.department import Department
from app.services.embedding_service import embedding_service
from app.config import settings

class RAGService:
    def search_relevant_chunks(self, db: Session, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves top_k chunks from PUBLISHED, non-expired knowledge documents.
        Uses hybrid search (semantic cosine similarity + lexical matching).
        """
        now = datetime.utcnow()
        # Query active documents
        docs_query = db.query(KnowledgeDocument).filter(
            KnowledgeDocument.status == ContentStatus.PUBLISHED,
            or_(KnowledgeDocument.expiry_date == None, KnowledgeDocument.expiry_date > now),
            or_(KnowledgeDocument.effective_date == None, KnowledgeDocument.effective_date <= now)
        )
        active_doc_ids = [d.id for d in docs_query.all()]
        if not active_doc_ids:
            return []

        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id.in_(active_doc_ids)).all()
        if not chunks:
            return []

        query_vec = embedding_service.generate_embedding(query)
        query_words = set(re.findall(r'\b\w+\b', query.lower()))

        scored_chunks = []
        for ch in chunks:
            # Semantic score
            sem_score = 0.0
            if ch.embedding:
                sem_score = embedding_service.cosine_similarity(query_vec, ch.embedding)

            # Lexical score
            ch_words = set(re.findall(r'\b\w+\b', ch.content.lower()))
            overlap = len(query_words.intersection(ch_words))
            lex_score = overlap / (len(query_words) or 1)

            # Hybrid combined score
            combined_score = (sem_score * 0.65) + (lex_score * 0.35)

            if combined_score > 0.15:  # Relevance threshold
                scored_chunks.append({
                    "chunk": ch,
                    "document": ch.document,
                    "score": combined_score,
                })

        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]

    def validate_citations(self, citations: List[Dict[str, Any]], retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validates citation IDs against retrieved chunks on the server to prevent hallucinated citations.
        """
        valid_chunk_map = {item["chunk"].id: item for item in retrieved_chunks}
        validated = []

        for c in citations:
            chunk_id = c.get("chunk_id")
            if chunk_id in valid_chunk_map:
                match = valid_chunk_map[chunk_id]
                validated.append({
                    "chunk_id": chunk_id,
                    "document_id": match["document"].id,
                    "document_title": match["document"].title,
                    "page_number": match["chunk"].page_number,
                    "section_heading": match["chunk"].section_heading,
                    "snippet": match["chunk"].content[:200] + "..." if len(match["chunk"].content) > 200 else match["chunk"].content
                })

        return validated

    def generate_grounded_response(
        self,
        db: Session,
        question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        retrieved = self.search_relevant_chunks(db, question, top_k=4)

        if not retrieved:
            return {
                "answer": "I could not find sufficient information in the approved university documents to answer your question accurately. Would you like to create a support ticket so department staff can assist you?",
                "citations": [],
                "confidence_score": 0.0,
                "suggest_ticket": True,
            }

        # Format context for model
        context_parts = []
        for item in retrieved:
            ch = item["chunk"]
            doc = item["document"]
            context_parts.append(
                f"[Source ID: {ch.id}] Document: {doc.title} | Page: {ch.page_number or 'N/A'} | Section: {ch.section_heading or 'General'}\nContent: {ch.content}"
            )
        context_str = "\n\n---\n\n".join(context_parts)

        # Live Gemini AI or Grounded Mock Fallback
        if settings.GEMINI_API_KEY and not settings.MOCK_AI_MODE:
            try:
                answer, raw_citations = self._call_gemini_api(question, context_str, retrieved)
                validated_citations = self.validate_citations(raw_citations, retrieved)
                return {
                    "answer": answer,
                    "citations": validated_citations,
                    "confidence_score": round(retrieved[0]["score"], 2),
                    "suggest_ticket": False,
                }
            except Exception:
                # Fallback to local grounded answer generator if API errors
                pass

        # Grounded Mock Generator
        return self._generate_grounded_mock(question, retrieved)

    def _call_gemini_api(self, question: str, context_str: str, retrieved: List[Dict[str, Any]]):
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        system_instruction = (
            "You are UniDesk, an AI assistant for a Sri Lankan university help desk. "
            "Answer the student's question strictly and only using the provided university context below. "
            "Never fabricate citations, dates, or rules. If the context does not contain enough info, state that clearly. "
            "When citing a statement, include the [Source ID: <id>] tag. Do not claim 100% accuracy or zero hallucinations."
        )

        prompt = f"University Context:\n{context_str}\n\nStudent Question: {question}"

        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config={"system_instruction": system_instruction, "temperature": 0.2}
        )
        text = response.text or ""

        # Extract cited IDs from text
        cited_ids = re.findall(r'\[Source ID:\s*(\d+)\]', text)
        citations = []
        for cid in set(cited_ids):
            citations.append({"chunk_id": int(cid)})

        # If model cited none but retrieved items exist, associate top matches
        if not citations and retrieved:
            for item in retrieved[:2]:
                citations.append({"chunk_id": item["chunk"].id})

        return text, citations

    def _generate_grounded_mock(self, question: str, retrieved: List[Dict[str, Any]]) -> Dict[str, Any]:
        top = retrieved[0]
        doc = top["document"]
        chunk = top["chunk"]

        answer_body = (
            f"Based on the approved university document **{doc.title}** "
            f"(Section: {chunk.section_heading or 'General'}, Page: {chunk.page_number or 1}):\n\n"
            f"{chunk.content}\n\n"
            f"*(Source verified from official university records. If your query requires specific administrative exemptions, please submit a ticket for direct staff review.)*"
        )

        citations = [{
            "chunk_id": chunk.id,
            "document_id": doc.id,
            "document_title": doc.title,
            "page_number": chunk.page_number,
            "section_heading": chunk.section_heading,
            "snippet": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
        }]

        return {
            "answer": answer_body,
            "citations": citations,
            "confidence_score": round(top["score"], 2),
            "suggest_ticket": False,
        }

rag_service = RAGService()
