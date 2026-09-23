from typing import Dict, Any, Optional
from app.services.llm_client import LLMClient

MARKET_INSIGHT_SYSTEM_PROMPT = """You are CareWise's market intelligence assistant.
Search the web for current, publicly available health insurance information relevant to the user's need.
Summarize objectively what different insurers/plans typically offer for this situation.
Always state this is general market information, NOT personalized financial/insurance advice,
and recommend the person confirm details directly with the insurer or a licensed advisor before buying.
Cite your sources."""

class MarketInsightService:
    def __init__(self):
        self.llm = LLMClient()
        self._cache: Dict[str, Dict[str, Any]] = {}  # simple in-memory cache, see note below

    def get_market_insight(self, query: str) -> Optional[Dict[str, Any]]:
        cache_key = query.strip().lower()
        if cache_key in self._cache:
            return self._cache[cache_key]

        result = self.llm.call_claude_with_web_search(MARKET_INSIGHT_SYSTEM_PROMPT, query)
        if result:
            self._cache[cache_key] = result
        return result


market_insight_service = MarketInsightService()
