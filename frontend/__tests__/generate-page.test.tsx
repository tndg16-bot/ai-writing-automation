import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import GeneratePage from '../app/generate/page';

// Mock useRouter
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock fetch
global.fetch = jest.fn() as jest.MockedFunction<typeof fetch>;

describe('GeneratePage', () => {
  const mockRouter = {
    push: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (require('next/navigation').useRouter as jest.Mock).mockReturnValue(mockRouter);
  });

  it('renders the generate form', () => {
    render(<GeneratePage />);
    expect(screen.getByText('Generate Content')).toBeInTheDocument();
    expect(screen.getByLabelText('Keyword')).toBeInTheDocument();
    expect(screen.getByLabelText('Content Type')).toBeInTheDocument();
    expect(screen.getByLabelText('Client Configuration')).toBeInTheDocument();
  });

  it('shows error when keyword is empty', () => {
    render(<GeneratePage />);

    const submitButton = screen.getByText('Generate Content');
    fireEvent.click(submitButton);

    expect(screen.getByText(/Error:/i)).toBeInTheDocument();
    expect(screen.getByText('Keyword is required')).toBeInTheDocument();
  });

  it('disables submit button when keyword is empty', () => {
    render(<GeneratePage />);

    const submitButton = screen.getByText('Generate Content') as HTMLButtonElement;
    expect(submitButton).toBeDisabled();
  });

  it('enables submit button when keyword is entered', () => {
    render(<GeneratePage />);

    const keywordInput = screen.getByLabelText('Keyword');
    const submitButton = screen.getByText('Generate Content') as HTMLButtonElement;

    fireEvent.change(keywordInput, { target: { value: 'AI副業' } });

    expect(submitButton).toBeEnabled();
  });

  it('submits form and navigates to progress page', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ task_id: 'test-task-id' }),
    });

    render(<GeneratePage />);

    const keywordInput = screen.getByLabelText('Keyword');
    const contentTypeSelect = screen.getByLabelText('Content Type');
    const clientInput = screen.getByLabelText('Client Configuration');
    const submitButton = screen.getByText('Generate Content');

    fireEvent.change(keywordInput, { target: { value: 'AI副業' } });
    fireEvent.change(contentTypeSelect, { target: { value: 'youtube' } });
    fireEvent.change(clientInput, { target: { value: 'custom' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword: 'AI副業',
          content_type: 'youtube',
          client: 'custom',
        }),
      });

      expect(mockRouter.push).toHaveBeenCalledWith('/progress?task_id=test-task-id');
    });
  });

  it('displays error when API request fails', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
    });

    render(<GeneratePage />);

    const keywordInput = screen.getByLabelText('Keyword');
    const submitButton = screen.getByText('Generate Content');

    fireEvent.change(keywordInput, { target: { value: 'AI副業' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Error:/i)).toBeInTheDocument();
      expect(screen.getByText('Failed to start generation')).toBeInTheDocument();
    });
  });

  it('handles network errors', async () => {
    (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

    render(<GeneratePage />);

    const keywordInput = screen.getByLabelText('Keyword');
    const submitButton = screen.getByText('Generate Content');

    fireEvent.change(keywordInput, { target: { value: 'AI副業' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Error:/i)).toBeInTheDocument();
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  it('disables inputs and button while loading', async () => {
    let resolvePromise: (value: any) => void;
    (global.fetch as jest.Mock).mockImplementation(() => {
      return new Promise((resolve) => {
        resolvePromise = resolve;
      });
    });

    render(<GeneratePage />);

    const keywordInput = screen.getByLabelText('Keyword');
    const submitButton = screen.getByText('Generate Content');

    fireEvent.change(keywordInput, { target: { value: 'AI副業' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(keywordInput).toBeDisabled();
      expect(submitButton).toHaveTextContent('Starting...');
      expect(submitButton).toBeDisabled();
    });

    resolvePromise!({ ok: true, json: () => Promise.resolve({ task_id: '123' }) });
  });

  it('has all content type options', () => {
    render(<GeneratePage />);

    const contentTypeSelect = screen.getByLabelText('Content Type');
    expect(screen.getByText('Blog Article')).toBeInTheDocument();
    expect(screen.getByText('YouTube Script')).toBeInTheDocument();
    expect(screen.getByText('Yukkuri Script')).toBeInTheDocument();
  });

  it('trim whitespace from keyword', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ task_id: 'test-task-id' }),
    });

    render(<GeneratePage />);

    const keywordInput = screen.getByLabelText('Keyword');
    const submitButton = screen.getByText('Generate Content');

    fireEvent.change(keywordInput, { target: { value: '  AI副業  ' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword: 'AI副業',
          content_type: 'blog',
          client: 'default',
        }),
      });
    });
  });

  it('shows back link to dashboard', () => {
    render(<GeneratePage />);

    const backLink = screen.getByText('← Back to Dashboard');
    expect(backLink).toHaveAttribute('href', '/');
  });
});
