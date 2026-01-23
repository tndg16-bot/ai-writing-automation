'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';

export default function ProgressPage() {
  const searchParams = useSearchParams();
  const taskId = searchParams.get('task_id');

  const [progress, setProgress] = useState({
    stage: '',
    stageIndex: 0,
    totalStages: 0,
    status: 'connecting' as 'running' | 'completed' | 'failed' | 'connected' | 'disconnected',
    message: null as string | null,
    error: null as string | null,
  });

  const [result, setResult] = useState<{
    generationId: number | null;
    markdown: string | null;
    error: string | null;
  }>({
    generationId: null,
    markdown: null,
    error: null,
  });

  const [showMarkdown, setShowMarkdown] = useState(false);
  const [socket, setSocket] = useState<WebSocket | null>(null);

  // WebSocket connection
  useEffect(() => {
    if (!taskId) return;

    const ws = new WebSocket(`ws://localhost:8000/api/generate/ws/${taskId}`);
    setSocket(ws);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setProgress(prev => ({ ...prev, status: 'connected' }));
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);

        if (message.type === 'progress') {
          setProgress({
            stage: message.stage || '',
            stageIndex: message.stage_index || 0,
            totalStages: message.total_stages || 0,
            status: message.status || 'running',
            message: message.message || null,
            error: message.error || null,
          });
        } else if (message.type === 'result') {
          setResult({
            generationId: message.generation_id ?? null,
            markdown: message.markdown || null,
            error: message.error || null,
          });

          if (message.status === 'completed' || message.status === 'failed') {
            setTimeout(() => ws.close(), 1000);
          }
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setProgress(prev => ({
        ...prev,
        status: 'failed',
        error: 'Connection error',
      }));
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
      setProgress(prev => ({ ...prev, status: 'disconnected' }));
    };

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [taskId]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
              Generation Progress
            </h1>

            {!taskId && (
              <div className="text-center text-gray-600 dark:text-gray-400">
                <h2 className="text-2xl font-bold mb-4">No task ID provided</h2>
                <p className="text-lg mb-6">
                  <a href="/" className="text-blue-600 hover:text-blue-700">
                    ← Back to Dashboard
                  </a>
                </p>
              </div>
            )}

            {taskId && (
              <>
                {/* Connection Status */}
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Connection Status
                    </span>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      progress.status === 'connected' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}
                    }`}>
                      {progress.status === 'connected' ? 'Connected' : 'Disconnected'}
                    </span>
                  </div>
                </div>

                {/* Error Display */}
                {progress.error && (
                  <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
                    <strong>Error:</strong> {progress.error}
                  </div>
                )}

                {/* Progress Bar */}
                {progress.stage && (
                  <div className="mb-6">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Current Stage
                      </span>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {progress.stageIndex + 1} / {progress.totalStages}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 overflow-hidden">
                      <div
                        className="bg-blue-600 h-full transition-all duration-300"
                        style={{
                          width: `${((progress.stageIndex + 1) / progress.totalStages) * 100}%`,
                        }}
                      />
                    </div>
                    <div className="mt-2 text-center">
                      <p className="text-lg font-semibold text-gray-900 dark:text-white">
                        {progress.stage}
                      </p>
                      {progress.message && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          {progress.message}
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* Result Display */}
                {result.markdown && (
                  <div className="mb-6">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                        Result
                      </h2>
                      <button
                        onClick={() => setShowMarkdown(!showMarkdown)}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                      >
                        {showMarkdown ? 'Hide' : 'Show'} Markdown
                      </button>
                    </div>

                    {showMarkdown && (
                      <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-6 overflow-x-auto">
                        <pre className="whitespace-pre-wrap text-sm text-gray-800 dark:text-gray-200">
                          {result.markdown}
                        </pre>
                      </div>
                    )}

                    {result.generationId && (
                      <div className="p-4 bg-green-50 dark:bg-green-900 rounded-lg">
                        <strong>Generation ID:</strong> {result.generationId}
                      </div>
                    )}
                  </div>
                )}

                {/* Navigation */}
                <div className="text-center">
                  <a
                    href="/"
                    className="text-blue-600 hover:text-blue-700 text-sm"
                  >
                    ← Back to Dashboard
                  </a>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
