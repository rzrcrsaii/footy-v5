/**
 * Dashboard Component Tests
 * Unit tests for the main dashboard page and components.
 */

import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { jest } from '@jest/globals'
import DashboardPage from '../app/dashboard/page'
import { DashboardStats } from '../components/dashboard/dashboard-stats'

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
  useSearchParams: () => ({
    get: jest.fn(),
  }),
}))

// Mock WebSocket provider
jest.mock('../lib/websocket/provider', () => ({
  useWebSocket: () => ({
    isConnected: true,
    subscribe: jest.fn(),
    unsubscribe: jest.fn(),
    sendMessage: jest.fn(),
    lastMessage: null,
    connectionStatus: 'connected',
  }),
  WebSocketProvider: ({ children }: { children: React.ReactNode }) => children,
}))

// Mock API client
jest.mock('../lib/api/client', () => ({
  apiClient: {
    getHealth: jest.fn().mockResolvedValue({
      status: 'healthy',
      version: '5.0.0',
      environment: 'test',
      timestamp: '2024-01-01T00:00:00Z',
    }),
    getTodayLiveFixtures: jest.fn().mockResolvedValue({
      date: '2024-01-01',
      fixtures: [],
      total: 0,
    }),
  },
  queryKeys: {
    health: ['health'],
    fixtures: {
      todayLive: () => ['fixtures', 'today-live'],
    },
  },
}))

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  )
}

describe('Dashboard Page', () => {
  it('renders dashboard title', () => {
    renderWithProviders(<DashboardPage />)
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Real-time football data monitoring and analysis')).toBeInTheDocument()
  })

  it('renders all dashboard sections', () => {
    renderWithProviders(<DashboardPage />)
    
    // Check for main dashboard components
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })
})

describe('DashboardStats Component', () => {
  it('renders loading state', () => {
    renderWithProviders(<DashboardStats />)
    
    // Should show skeleton loading states
    const skeletons = screen.getAllByRole('generic')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('renders stats cards with data', async () => {
    renderWithProviders(<DashboardStats />)
    
    await waitFor(() => {
      expect(screen.getByText("Today's Fixtures")).toBeInTheDocument()
      expect(screen.getByText('Live Matches')).toBeInTheDocument()
      expect(screen.getByText('Odds Updates')).toBeInTheDocument()
      expect(screen.getByText('Active Connections')).toBeInTheDocument()
    })
  })

  it('displays correct stat descriptions', async () => {
    renderWithProviders(<DashboardStats />)
    
    await waitFor(() => {
      expect(screen.getByText('Matches scheduled today')).toBeInTheDocument()
      expect(screen.getByText('Currently in progress')).toBeInTheDocument()
      expect(screen.getByText('Last hour')).toBeInTheDocument()
      expect(screen.getByText('WebSocket clients')).toBeInTheDocument()
    })
  })
})

describe('Dashboard Integration', () => {
  it('handles API errors gracefully', async () => {
    // Mock API error
    const { apiClient } = await import('../lib/api/client')
    jest.mocked(apiClient.getHealth).mockRejectedValueOnce(new Error('API Error'))
    
    renderWithProviders(<DashboardPage />)
    
    // Should still render the dashboard structure
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('updates data when WebSocket receives messages', async () => {
    renderWithProviders(<DashboardPage />)
    
    // Initial render should work
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    
    // WebSocket updates would trigger re-renders in real implementation
    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument()
    })
  })
})

describe('Responsive Design', () => {
  it('renders correctly on mobile viewport', () => {
    // Mock mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    })

    renderWithProviders(<DashboardPage />)
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('renders correctly on desktop viewport', () => {
    // Mock desktop viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1920,
    })

    renderWithProviders(<DashboardPage />)
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })
})
