import { useState, useEffect } from 'react';
import { getStats } from '@/lib/api';

interface Stats {
  total_generations: number;
  total_images: number;
  by_content_type: Record<string, number>;
  by_provider: Record<string, number>;
  db_size_bytes: number;
}

export default function HomePage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [statsData, historyData] = await Promise.all([
        getStats(),
        fetch('/api/history').then(res => res.json()),
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

  useEffect(() => {
    fetchData();
  }, []);

  const handleRefresh = () => {
    fetchData();
  };

  const getContentTypeBadgeColor = (type: string) => {
    const colors: Record<string, string> = {
      blog: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      youtube: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      yukkuri: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    };
    return colors[type] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                AI Writing Dashboard
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Generate blog articles, YouTube scripts, and more with AI
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleRefresh}
                className="px-4 py-2 bg-white dark:bg-gray-800 text-gray-700 dark:border-gray-600 dark:text-gray-300 border border-transparent rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 dark:text-gray-900 transition-colors"
              >
                Refresh
              </button>
              <a
                href="/generate"
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                New Generation
              </a>
            </div>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
              <div className="font-bold">Error:</div>
              <div>{error}</div>
            </div>
          )}

          {/* Stats Cards */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <StatCard title="Total Generations" value={stats.total_generations} icon="📝" />
              <StatCard title="Total Images" value={stats.total_images} icon="🖼️" />
              <StatCard
                title="Blog Posts"
                value={stats.by_content_type.blog || 0}
                icon="📰"
              />
              <StatCard
                title="Videos"
                value={(stats.by_content_type.youtube || 0) + (stats.by_content_type.yukkuri || 0)}
                icon="🎥"
              />
            </div>
          )}

          {/* Recent History */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Recent Generations
              </h2>
            </div>

            {loading ? (
              <div className="p-12 text-center text-gray-600 dark:text-gray-400">
                Loading...
              </div>
            ) : history.length === 0 ? (
              <div className="p-12 text-center text-gray-600 dark:text-gray-400">
                <p className="text-lg mb-4">No generations yet</p>
                <p className="text-gray-600 dark:text-gray-400">
                  <a
                    href="/generate"
                    className="text-blue-600 hover:text-blue-700 font-medium"
                  >
                    Create your first generation →
                  </a>
                </p>
              </div>
            ) : (
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-900">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Keyword
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Title
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Sections
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Images
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Created
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {history.map((item) => (
                    <tr
                      key={item.id}
                      className="hover:bg-gray-50 dark:hover:bg-gray-100 dark:hover:bg-gray-900 dark:divide-y-200 dark:divide-gray-700 transition-colors"
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {item.keyword.length > 20 ? `${item.keyword.substring(0, 20)}...` : item.keyword}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <ContentTypeBadge type={item.content_type} />
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">
                        {item.title && item.title !== 'N/A' ? (
                          item.title.length > 30
                        ) : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                        {item.sections_count}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                        {item.images_count}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {new Date(item.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );

function StatCard({ title, value, icon }: { title: string; value: number; icon: string }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
          {title}
        </span>
        <span className="text-2xl">{icon}</span>
      </div>
      <p className="text-3xl font-bold text-gray-900 dark:text-white">{value}</p>
    </div>
  );
}

function ContentTypeBadge({ type }: { type: string }) {
  const colors: Record<string, string> = {
    blog: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    youtube: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    yukkuri: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  };
  return (
    <span className={`px-3 py-1 rounded-full text-xs font-medium ${colors[type] || 'bg-gray-100 text-gray-800'}`}>
      {type}
    </span>
  );
}
