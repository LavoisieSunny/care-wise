import api from './client';

export interface MarketInsightSource {
  title: string;
  url: string;
}

export interface MarketInsightResult {
  answer: string;
  sources: MarketInsightSource[];
}

export const getMarketInsight = async (query: string): Promise<MarketInsightResult> => {
  const res = await api.get<MarketInsightResult>('/market/insight', { params: { query } });
  return res.data;
};
