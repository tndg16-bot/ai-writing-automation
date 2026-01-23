import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import HomePage from '../app/page';

// Mock the API module
jest.mock('@/lib/api', () => ({
  getStats: jest.fn(),
}));

// Mock fetch
global.fetch = jest.fn() as jest.MockedFunction<typeof fetch>;

describe('HomePage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the dashboard title', () => {
    render(<HomePage />);
    expect(screen.getByText('AI Writing Dashboard')).toBeInTheDocument();
  });

  it('renders the description', () => {
    render(<HomePage />);
    expect(
      screen.getByText('Generate blog articles, YouTube scripts, and more with AI')
    ).toBeInTheDocument();
  });

  it('shows loading state initially', () => {
    const { getStats } = require('@/lib/api');
    (getStats as jest.Mock).mockImplementation(() => new Promise(() => {}));
    (global.fetch as jest.Mock).mockImplementation(() => new Promise(() => {}));

    render(<HomePage />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders stats cards when data is loaded', async () => {
    const { getStats } = require('@/lib/api');
    const mockStats = {
      total_generations: 10,
      total_images: 25,
      by_content_type: { blog: 5, youtube: 3, yukkuri: 2 },
      db_size_bytes: 1000000,
    };
    (getStats as jest.Mock).mockResolvedValue(mockStats);

    const mockHistory = [
      {
        id: 1,
        keyword: 'AI副業',
        content_type: 'blog',
        title: 'AI副業で月収10万円を目指す方法',
        sections_count: 5,
        images_count: 3,
        created_at: '2025-01-23T10:00:00Z',
      },
    ];
    (global.fetch as jest.Mock).mockResolvedValue({
      json: () => Promise.resolve(mockHistory),
    });

    render(<HomePage />);

    await waitFor(() => {
      expect(screen.getByText('Total Generations')).toBeInTheDocument();
      expect(screen.getByText('10')).toBeInTheDocument();
    });
  });

  it('renders history table with data', async () => {
    const { getStats } = require('@/lib/api');
    (getStats as jest.Mock).mockResolvedValue({ total_generations: 1 });

    const mockHistory = [
      {
        id: 1,
        keyword: 'AI副業',
        content_type: 'blog',
        title: 'AI副業で月収10万円を目指す方法',
        sections_count: 5,
        images_count: 3,
        created_at: '2025-01-23T10:00:00Z',
      },
    ];
    (global.fetch as jest.Mock).mockResolvedValue({
      json: () => Promise.resolve(mockHistory),
    });

    render(<HomePage />);

    await waitFor(() => {
      expect(screen.getByText('Recent Generations')).toBeInTheDocument();
      expect(screen.getByText('AI副業')).toBeInTheDocument();
    });
  });

  it('displays error message when API fails', async () => {
    const { getStats } = require('@/lib/api');
    (getStats as jest.Mock).mockRejectedValue(new Error('Failed to fetch'));

    render(<HomePage />);

    await waitFor(() => {
      expect(screen.getByText(/Error:/i)).toBeInTheDocument();
      expect(screen.getByText('Failed to fetch')).toBeInTheDocument();
    });
  });

  it('shows no generations message when history is empty', async () => {
    const { getStats } = require('@/lib/api');
    (getStats as jest.Mock).mockResolvedValue({ total_generations: 0 });
    (global.fetch as jest.Mock).mockResolvedValue({
      json: () => Promise.resolve([]),
    });

    render(<HomePage />);

    await waitFor(() => {
      expect(screen.getByText('No generations yet')).toBeInTheDocument();
      expect(screen.getByText('Create your first generation →')).toBeInTheDocument();
    });
  });

  it('refreshes data when refresh button is clicked', async () => {
    const { getStats } = require('@/lib/api');
    let callCount = 0;
    (getStats as jest.Mock).mockImplementation(() => {
      callCount++;
      return Promise.resolve({ total_generations: callCount });
    });
    (global.fetch as jest.Mock).mockResolvedValue({
      json: () => Promise.resolve([]),
    });

    render(<HomePage />);

    await waitFor(() => {
      expect(screen.getByText('1')).toBeInTheDocument();
    });

    const refreshButton = screen.getByText('Refresh');
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(screen.getByText('2')).toBeInTheDocument();
    });
  });

  it('truncates long keywords in table', async () => {
    const { getStats } = require('@/lib/api');
    (getStats as jest.Mock).mockResolvedValue({ total_generations: 1 });

    const mockHistory = [
      {
        id: 1,
        keyword: 'これは非常に長いキーワードですべてを表示しようとするとテーブルが崩れる可能性があります',
        content_type: 'blog',
        title: 'テスト',
        sections_count: 1,
        images_count: 1,
        created_at: '2025-01-23T10:00:00Z',
      },
    ];
    (global.fetch as jest.Mock).mockResolvedValue({
      json: () => Promise.resolve(mockHistory),
    });

    render(<HomePage />);

    await waitFor(() => {
      const keywordText = screen.getByText((content) =>
        content.includes('これは非常に長いキーワードですすべ')
      );
      expect(keywordText).toBeInTheDocument();
    });
  });

  it('displays content type badges correctly', async () => {
    const { getStats } = require('@/lib/api');
    (getStats as jest.Mock).mockResolvedValue({ total_generations: 3 });

    const mockHistory = [
      {
        id: 1,
        keyword: 'test1',
        content_type: 'blog',
        title: 'テスト',
        sections_count: 1,
        images_count: 1,
        created_at: '2025-01-23T10:00:00Z',
      },
      {
        id: 2,
        keyword: 'test2',
        content_type: 'youtube',
        title: 'テスト',
        sections_count: 1,
        images_count: 1,
        created_at: '2025-01-23T10:00:00Z',
      },
      {
        id: 3,
        keyword: 'test3',
        content_type: 'yukkuri',
        title: 'テスト',
        sections_count: 1,
        images_count: 1,
        created_at: '2025-01-23T10:00:00Z',
      },
    ];
    (global.fetch as jest.Mock).mockResolvedValue({
      json: () => Promise.resolve(mockHistory),
    });

    render(<HomePage />);

    await waitFor(() => {
      expect(screen.getByText('blog')).toBeInTheDocument();
      expect(screen.getByText('youtube')).toBeInTheDocument();
      expect(screen.getByText('yukkuri')).toBeInTheDocument();
    });
  });

  it('navigates to generate page when "New Generation" button is clicked', () => {
    render(<HomePage />);
    const newGenerationButton = screen.getByText('New Generation');
    expect(newGenerationButton).toHaveAttribute('href', '/generate');
  });
});
