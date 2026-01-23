import { useState, useEffect } from 'react';
import { getHistory, getStats } from '@/lib/api';

interface GenerationListItem {
  id: number;
  keyword: string;
  content_type: string;
  title?: string;
  sections_count: number;
  images_count: number;
  created_at: string;
}

interface Stats {
  total_generations: number;
  total_images: number;
  by_content_type: Record<string, number>;
  by_provider: Record<string, number>;
  db_size_bytes: number;
}

export function useDashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [history, setHistory] = useState<GenerationListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [statsData, historyData] = await Promise.all([
        getStats(),
        getHistory(),
      ]);

      setStats(statsData);
      setHistory(historyData);
    } catch (err) {
      setLoading(false);
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchData();
  };

  return { stats, history, loading, error, refresh: handleRefresh };
}
