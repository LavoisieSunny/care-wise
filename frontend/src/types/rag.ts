import { ClauseCitation } from './policy';

export interface GroundedAnswerResponse {
  query: string;
  answer: string;
  confidence: number;
  citations: ClauseCitation[];
  grounded_clauses: string[];
  suggested_actions: string[];
  policy_name: string;
  language?: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  citations?: ClauseCitation[];
  suggested_actions?: string[];
}
