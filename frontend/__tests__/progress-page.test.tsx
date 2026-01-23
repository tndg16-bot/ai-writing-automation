import { render, screen, act, fireEvent, waitFor } from '@testing-library/react';
import ProgressPage from '../app/progress/page';

// Mock useSearchParams
jest.mock('next/navigation', () => ({
  useSearchParams: jest.fn(),
}));

// Mock WebSocket
class MockWebSocket {
  url: string;
  readyState: number = 0;
  onopen: ((event: any) => void) | null = null;
  onmessage: ((event: any) => void) | null = null;
  onerror: ((event: any) => void) | null = null;
  onclose: ((event: any) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    setTimeout(() => {
      if (this.onopen) {
        this.onopen({ type: 'open' });
      }
    }, 0);
  }

  send(data: string) {
    // Mock implementation
  }

  close() {
    this.readyState = 3;
    if (this.onclose) {
      this.onclose({ type: 'close' });
    }
  }
}

global.WebSocket = MockWebSocket as any;

describe('ProgressPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (require('next/navigation').useSearchParams as jest.Mock).mockReturnValue({
      get: jest.fn((key: string) => {
        if (key === 'task_id') return 'test-task-id';
        return null;
      }),
    });
  });

  it('renders progress page with task ID', () => {
    render(<ProgressPage />);

    expect(screen.getByText('Generation Progress')).toBeInTheDocument();
    expect(screen.getByText('Connection Status')).toBeInTheDocument();
  });

  it('shows no task ID message when task_id is missing', () => {
    (require('next/navigation').useSearchParams as jest.Mock).mockReturnValue({
      get: jest.fn(() => null),
    });

    render(<ProgressPage />);

    expect(screen.getByText('No task ID provided')).toBeInTheDocument();
    expect(screen.getByText('← Back to Dashboard')).toBeInTheDocument();
  });

  it('updates connection status when WebSocket connects', async () => {
    render(<ProgressPage />);

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 10));
    });

    await screen.findByText('Connected');
  });

  it('displays progress information from WebSocket messages', async () => {
    render(<ProgressPage />);

    const ws = new MockWebSocket('ws://localhost:8000/api/generate/ws/test-task-id');

    await act(async () => {
      if (ws.onmessage) {
        ws.onmessage({
          data: JSON.stringify({
            type: 'progress',
            stage: 'Generating content',
            stage_index: 1,
            total_stages: 5,
            status: 'running',
            message: 'Processing...',
          }),
        });
      }
    });

    await waitFor(() => {
      expect(screen.getByText('Generating content')).toBeInTheDocument();
      expect(screen.getByText('Processing...')).toBeInTheDocument();
      expect(screen.getByText('2 / 5')).toBeInTheDocument();
    });
  });

  it('displays result when generation completes', async () => {
    render(<ProgressPage />);

    const ws = new MockWebSocket('ws://localhost:8000/api/generate/ws/test-task-id');

    await act(async () => {
      if (ws.onmessage) {
        ws.onmessage({
          data: JSON.stringify({
            type: 'result',
            status: 'completed',
            generation_id: 123,
            markdown: '# Test Content\n\nThis is a test article.',
          }),
        });
      }
    });

    await waitFor(() => {
      expect(screen.getByText('Result')).toBeInTheDocument();
      expect(screen.getByText('# Test Content')).toBeInTheDocument();
      expect(screen.getByText('Generation ID:')).toBeInTheDocument();
      expect(screen.getByText('123')).toBeInTheDocument();
    });
  });

  it('shows error message when generation fails', async () => {
    render(<ProgressPage />);

    const ws = new MockWebSocket('ws://localhost:8000/api/generate/ws/test-task-id');

    await act(async () => {
      if (ws.onmessage) {
        ws.onmessage({
          data: JSON.stringify({
            type: 'progress',
            stage: 'Generating content',
            status: 'failed',
            error: 'API rate limit exceeded',
          }),
        });
      }
    });

    await waitFor(() => {
      expect(screen.getByText(/Error:/i)).toBeInTheDocument();
      expect(screen.getByText('API rate limit exceeded')).toBeInTheDocument();
    });
  });

  it('toggles markdown visibility when button is clicked', async () => {
    render(<ProgressPage />);

    const ws = new MockWebSocket('ws://localhost:8000/api/generate/ws/test-task-id');

    await act(async () => {
      if (ws.onmessage) {
        ws.onmessage({
          data: JSON.stringify({
            type: 'result',
            status: 'completed',
            markdown: '# Test Content',
          }),
        });
      }
    });

    await waitFor(() => {
      const showButton = screen.getByText('Show Markdown');
      expect(showButton).toBeInTheDocument();
    });

    const showButton = screen.getByText('Show Markdown');
    fireEvent.click(showButton);

    await waitFor(() => {
      expect(screen.getByText('# Test Content')).toBeInTheDocument();
      expect(screen.getByText('Hide Markdown')).toBeInTheDocument();
    });

    const hideButton = screen.getByText('Hide Markdown');
    fireEvent.click(hideButton);

    await waitFor(() => {
      expect(screen.queryByText('# Test Content')).not.toBeInTheDocument();
      expect(screen.getByText('Show Markdown')).toBeInTheDocument();
    });
  });

  it('handles WebSocket errors', async () => {
    render(<ProgressPage />);

    const ws = new MockWebSocket('ws://localhost:8000/api/generate/ws/test-task-id');

    await act(async () => {
      if (ws.onerror) {
        ws.onerror({ type: 'error' });
      }
    });

    await waitFor(() => {
      expect(screen.getByText(/Error:/i)).toBeInTheDocument();
      expect(screen.getByText('Connection error')).toBeInTheDocument();
    });
  });

  it('closes WebSocket on unmount', () => {
    const { unmount } = render(<ProgressPage />);

    const closeSpy = jest.fn();
    const ws = new MockWebSocket('ws://localhost:8000/api/generate/ws/test-task-id');
    ws.close = closeSpy;

    unmount();

    // WebSocket should be cleaned up
    expect(closeSpy).toHaveBeenCalled();
  });

  it('shows progress bar width correctly', async () => {
    render(<ProgressPage />);

    const ws = new MockWebSocket('ws://localhost:8000/api/generate/ws/test-task-id');

    await act(async () => {
      if (ws.onmessage) {
        ws.onmessage({
          data: JSON.stringify({
            type: 'progress',
            stage: 'Stage 2',
            stage_index: 2,
            total_stages: 5,
            status: 'running',
          }),
        });
      }
    });

    await waitFor(() => {
      const progressBar = document.querySelector('.bg-blue-600') as HTMLElement;
      expect(progressBar).toHaveStyle({ width: '60%' });
    });
  });

  it('shows back link to dashboard', () => {
    render(<ProgressPage />);

    const backLink = screen.getByText('← Back to Dashboard');
    expect(backLink).toHaveAttribute('href', '/');
  });
});
