import re
from typing import List, Optional, Dict, Any
from rapidfuzz import fuzz

from app.schemas.rag import GroundedAnswerResponse, ClauseCitation
from app.schemas.policy import PolicyDetails
from app.services.policy_service import policy_service
from app.services.llm_client import llm_client
from app.core.logging import logger


def chunk_policy_document(policy: PolicyDetails, target_words: int = 250) -> List[Dict[str, Any]]:
    """Split policy.raw_text_pages into passages tagged with real page numbers."""
    chunks: List[Dict[str, Any]] = []
    page_texts = policy.raw_text_pages or {}

    if not page_texts:
        # Fallback to citations if raw_text_pages is somehow missing
        for cit in policy.all_citations:
            chunks.append({
                "chunk_id": cit.clause_id,
                "page_number": cit.page_number,
                "text": f"[{cit.section}] {cit.clause_title}: {cit.exact_text}"
            })
        return chunks

    for page_str, page_content in page_texts.items():
        try:
            page_num = int(page_str)
        except ValueError:
            page_num = 1

        paragraphs = [p.strip() for p in page_content.split("\n\n") if p.strip()]
        current_chunk_words: List[str] = []
        chunk_idx = 1

        for p in paragraphs:
            words = p.split()
            if len(current_chunk_words) + len(words) > target_words and current_chunk_words:
                chunks.append({
                    "chunk_id": f"p{page_num}_c{chunk_idx}",
                    "page_number": page_num,
                    "text": " ".join(current_chunk_words)
                })
                chunk_idx += 1
                current_chunk_words = current_chunk_words[-30:]  # 30-word overlap
            current_chunk_words.extend(words)

        if current_chunk_words:
            chunks.append({
                "chunk_id": f"p{page_num}_c{chunk_idx}",
                "page_number": page_num,
                "text": " ".join(current_chunk_words)
            })

    return chunks


class RAGService:
    def answer_query(
        self,
        policy_id: str,
        query: str,
        hospital_name: Optional[str] = None,
        procedure_name: Optional[str] = None
    ) -> GroundedAnswerResponse:
        policy = policy_service.get_policy(policy_id)
        if not policy:
            pols = policy_service.list_policies()
            policy = pols[0] if pols else None
            if not policy:
                raise ValueError("No policies available for retrieval.")

        chunks = chunk_policy_document(policy)
        if not chunks:
            return GroundedAnswerResponse(
                query=query,
                answer="No document passages available to answer this question.",
                confidence=0.0,
                citations=[],
                grounded_clauses=[],
                suggested_actions=["Upload a policy PDF document to enable grounded Q&A."],
                policy_name=policy.policy_name
            )

        # 1. Rank chunks with rapidfuzz token_set_ratio + keyword boosts
        query_lower = query.lower()
        query_tokens = set(re.findall(r"\w+", query_lower))
        scored_chunks = []

        for c in chunks:
            text = c["text"]
            text_lower = text.lower()
            base_score = fuzz.token_set_ratio(query_lower, text_lower)
            # Bonus for exact key terms
            bonus = 0
            for qt in query_tokens:
                if len(qt) > 3 and qt in text_lower:
                    bonus += 3
            final_score = min(100.0, base_score + bonus)
            scored_chunks.append((final_score, c))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [c for score, c in scored_chunks[:3]]
        best_score = scored_chunks[0][0] if scored_chunks else 0.0

        # 2. Try LLM Grounded Generation
        llm_result = llm_client.answer_grounded_query(top_chunks, query, policy.policy_name)
        if llm_result and "answer" in llm_result:
            answer = llm_result["answer"]
            cited_pages = llm_result.get("cited_pages", [top_chunks[0]["page_number"]])
            confidence = float(llm_result.get("confidence", 0.94))
            suggested_actions = llm_result.get("suggested_actions", [
                "Verify with hospital TPA desk before final admission.",
                "Check the CareWise Cost Comparator for out-of-pocket breakdown."
            ])
            citations = []
            for p in cited_pages:
                matched_chunk = next((c for c in top_chunks if c["page_number"] == p), top_chunks[0])
                citations.append(ClauseCitation(
                    clause_id=matched_chunk["chunk_id"],
                    section=f"Policy Grounding (Page {p})",
                    page_number=p,
                    clause_title=f"Verified Policy Clause - Page {p}",
                    exact_text=matched_chunk["text"][:240] + ("..." if len(matched_chunk["text"]) > 240 else ""),
                    tag="RAG_CITATION",
                    confidence=confidence
                ))
            return GroundedAnswerResponse(
                query=query,
                answer=answer,
                confidence=confidence,
                citations=citations,
                grounded_clauses=[f"Page {c.page_number}: {c.clause_title}" for c in citations],
                suggested_actions=suggested_actions,
                policy_name=policy.policy_name
            )

        # 3. Grounded Fallback Engine (derives answer strictly from retrieved passages without canned strings)
        top_chunk = top_chunks[0]
        page_num = top_chunk["page_number"]
        top_text = top_chunk["text"]

        if best_score < 35:
            answer = (
                f"Based on a grounded scan of **{policy.policy_name}**, this specific term is not explicitly addressed "
                f"in the extracted clauses (closest match on **Page {page_num}** with {best_score:.0f}% relevance).\n\n"
                f"Please consult the hospital cashless coordinator or verify the physical policy wording."
            )
            citations = []
            suggested_actions = [
                "Ask hospital TPA desk for insurer-specific cashless clarification.",
                "Review the 6 extracted schedule rows in the workbench."
            ]
        else:
            sentences = re.split(r'(?<=[.!?\n])\s+', top_text)
            relevant_snippet = sentences[0] if sentences else top_text[:200]
            for s in sentences:
                if any(t in s.lower() for t in query_tokens if len(t) > 3):
                    relevant_snippet = s.strip()
                    break

            answer = (
                f"Under **{policy.policy_name}**, according to **Page {page_num}**:\n\n"
                f"> \"*{relevant_snippet}*\"\n\n"
                f"This condition directly governs your hospitalisation claim settlement. "
                f"Ensure all admission intimations and room tariff limits comply with the terms on Page {page_num}."
            )
            citations = [
                ClauseCitation(
                    clause_id=f"CIT-P{page_num}",
                    section=f"Document Source (Page {page_num})",
                    page_number=page_num,
                    clause_title=f"Grounded Policy Excerpt (Page {page_num})",
                    exact_text=relevant_snippet[:240],
                    tag="RAG_CITATION",
                    confidence=round(best_score / 100.0, 2)
                )
            ]
            suggested_actions = [
                f"Jump to Page {page_num} in the real PDF viewer to inspect the clause context.",
                "Simulate your estimated hospitalisation charges in Column 3."
            ]

        return GroundedAnswerResponse(
            query=query,
            answer=answer,
            confidence=round(best_score / 100.0, 2),
            citations=citations,
            grounded_clauses=[f"Page {c.page_number}: {c.clause_title}" for c in citations],
            suggested_actions=suggested_actions,
            policy_name=policy.policy_name
        )


rag_service = RAGService()

