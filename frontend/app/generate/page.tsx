import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function GeneratePage() {
  const router = useRouter();
  const [keyword, setKeyword] = useState('');
  const [contentType, setContentType] = useState('blog');
  const [client, setClient] = useState('default');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!keyword.trim()) {
      setError('Keyword is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword: keyword.trim(),
          content_type: contentType,
          client: client,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to start generation');
      }

      const data = await response.json();

      // Redirect to progress page
      router.push(`/progress?task_id=${data.task_id}`);
    } catch (err) {
      setLoading(false);
      setError(err instanceof Error ? err.message : 'Failed to start generation');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
              Generate Content
            </h1>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
                <div className="font-bold">Error:</div>
                <div>{error}</div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="keyword" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Keyword
                </label>
                <input
                  id="keyword"
                  type="text"
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  placeholder="e.g., AI副業, 投資信託, 犬の飼い方"
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:bg-gray-400 disabled:text-gray-400"
                  disabled={loading}
                />
              </div>

              <div>
                <label htmlFor="content-type" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Content Type
                </label>
                <select
                  id="content-type"
                  value={contentType}
                  onChange={(e) => setContentType(e.target.value as any)}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  disabled={loading}
                >
                  <option value="blog">Blog Article</option>
                  <option value="youtube">YouTube Script</option>
                  <option value="yukkuri">Yukkuri Script</option>
                </select>
              </div>

              <div>
                <label htmlFor="client" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Client Configuration
                </label>
                <input
                  id="client"
                  type="text"
                  value={client}
                  onChange={(e) => setClient(e.target.value)}
                  placeholder="default"
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  disabled={loading}
                />
              </div>

              <button
                type="submit"
                disabled={loading || !keyword.trim()}
                className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold rounded-lg transition-colors"
              >
                {loading ? 'Starting...' : 'Generate Content'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <a
                href="/"
                className="text-blue-600 hover:text-blue-700 text-sm"
              >
                ← Back to Dashboard
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
