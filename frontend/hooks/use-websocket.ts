import { useState, useEffect, useCallback } from 'react';
import { connectWebSocket } from '@/lib/api';

interface ProgressData {
  stage: string;
  stageIndex: number;
  totalStages: number;
  status: 'running' | 'completed' | 'failed';
  message?: string;
  error?: string;
}

interface Result {
  generationId?: number;
  markdown?: string;
  error?: string;
}

interface WebSocketMessage {
  type: 'progress' | 'result';
  task_id: string;
  stage?: string;
  stage_index?: number;
  total_stages?: number;
  status?: 'running' | 'completed' | 'failed';
  message?: string;
  error?: string;
  generation_id?: number;
  markdown?: string;
}

export function useWebSocket(taskId: string) {
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [result, setResult] = useState<Result | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const socketRef = useRef<WebSocket | null>(null);

  const connectWebSocket = useCallback(() => {
    if (!taskId) return;

    // Close existing connection
    if (socketRef.current) {
      socketRef.current.close();
    }

    try {
      const ws = new WebSocket(`ws://localhost:8000/api/generate/ws/${taskId}`);
      socketRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
      };

      ws.onmessage = (event: MessageEvent) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);

          if (message.type === 'progress') {
            setProgress({
              stage: message.stage || '',
              stageIndex: message.stage_index || 0,
              totalStages: message.total_stages || 0,
              status: message.status || 'running' as 'completed' | 'failed',
              message: message.message || undefined,
              error: message.error || undefined,
            });
          } else if (message.type === 'result') {
            setResult({
              generationId: message.generation_id,
              markdown: message.markdown,
              error: message.error,
            });

            // Close connection on completion or failure
            if (message.status === 'completed' || message.status === 'failed') {
              setTimeout(() => ws.close(), 500);
            }
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
          setError(err instanceof Error ? err.message : 'Failed to parse message');
        }
      };

      ws.onerror = (error: Event) => {
        console.error('WebSocket error:', error);
        setError('Connection error');
        setIsConnected(false);
      };

      ws.onclose = () => {
        console.log('WebSocket closed');
        setIsConnected(false);
      };

    } catch (err) {
      console.error('Failed to create WebSocket:', err);
      setError(err instanceof Error ? err.message : 'Failed to connect');
      setIsConnected(false);
    }
  }, [taskId]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [taskId]);

  return { progress, result, isConnected, error };
}
