"use client"

import React, { useEffect, useMemo, lazy, Suspense } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  BarChart3,
  Users,
  Clock,
  History,
  Trophy,
  Loader2,
  AlertCircle,
  Wifi,
  WifiOff
} from 'lucide-react'

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
// Lazy load heavy components for better performance
const FixtureStatistics = lazy(() => import('./fixture-statistics').then(m => ({ default: m.FixtureStatistics })))
const FixtureEvents = lazy(() => import('./fixture-events').then(m => ({ default: m.FixtureEvents })))
const FixtureLineups = lazy(() => import('./fixture-lineups').then(m => ({ default: m.FixtureLineups })))
const FixtureH2H = lazy(() => import('./fixture-h2h').then(m => ({ default: m.FixtureH2H })))
const FixturePlayerStats = lazy(() => import('./fixture-player-stats').then(m => ({ default: m.FixturePlayerStats })))

import { useWebSocket } from '@/lib/websocket/provider'
import { apiClient, queryKeys, Fixture } from '@/lib/api/client'

interface FixtureDetailTabsProps {
  fixture: Fixture
  defaultTab?: string
}

export function FixtureDetailTabs({ fixture, defaultTab = "statistics" }: FixtureDetailTabsProps) {
  const queryClient = useQueryClient()
  const { isConnected, subscribe, unsubscribe, lastMessage, connectionStatus } = useWebSocket()

  // Memoize expensive calculations
  const isLiveMatch = useMemo(() => {
    return ['1H', '2H', 'HT', 'ET', 'BT', 'P'].includes(fixture.status_short)
  }, [fixture.status_short])

  const refetchIntervals = useMemo(() => ({
    statistics: isConnected ? (isLiveMatch ? 15000 : 30000) : (isLiveMatch ? 30000 : 60000),
    events: isConnected ? (isLiveMatch ? 10000 : 15000) : (isLiveMatch ? 20000 : 30000),
    lineups: isConnected ? 60000 : 120000, // Less frequent for lineups
    playerStats: isConnected ? (isLiveMatch ? 30000 : 45000) : (isLiveMatch ? 60000 : 90000),
  }), [isConnected, isLiveMatch])

  // Subscribe to real-time updates for this fixture
  useEffect(() => {
    if (fixture.id && isConnected) {
      subscribe(fixture.id)
      console.log(`🔔 Subscribed to real-time updates for fixture ${fixture.id}`)
    }

    return () => {
      if (fixture.id) {
        unsubscribe(fixture.id)
        console.log(`🔕 Unsubscribed from fixture ${fixture.id}`)
      }
    }
  }, [fixture.id, isConnected, subscribe, unsubscribe])

  // Handle real-time updates
  useEffect(() => {
    if (lastMessage && lastMessage.fixture_id === fixture.id) {
      console.log(`📡 Real-time update for fixture ${fixture.id}:`, lastMessage.type)

      // Invalidate and refetch relevant queries based on message type
      switch (lastMessage.type) {
        case 'live_stats':
          queryClient.invalidateQueries({ queryKey: queryKeys.fixtures.statistics(fixture.id) })
          break
        case 'live_events':
          queryClient.invalidateQueries({ queryKey: queryKeys.fixtures.events(fixture.id) })
          break
        case 'live_odds':
          // Could invalidate odds-related queries if we had them
          break
        case 'live_frame':
          // General update - invalidate all fixture detail queries
          queryClient.invalidateQueries({ queryKey: queryKeys.fixtures.statistics(fixture.id) })
          queryClient.invalidateQueries({ queryKey: queryKeys.fixtures.events(fixture.id) })
          queryClient.invalidateQueries({ queryKey: queryKeys.fixtures.playerStats(fixture.id) })
          break
      }
    }
  }, [lastMessage, fixture.id, queryClient])

  // Query for fixture statistics with optimized caching
  const {
    data: statisticsData,
    isLoading: statisticsLoading,
    error: statisticsError
  } = useQuery({
    queryKey: queryKeys.fixtures.statistics(fixture.id),
    queryFn: () => apiClient.getFixtureStatistics(fixture.id),
    enabled: !!fixture.id,
    refetchInterval: refetchIntervals.statistics,
    staleTime: isLiveMatch ? 10000 : 60000, // Shorter stale time for live matches
    gcTime: 5 * 60 * 1000, // Keep in cache for 5 minutes
  })

  // Query for fixture lineups with optimized caching
  const {
    data: lineupsData,
    isLoading: lineupsLoading,
    error: lineupsError
  } = useQuery({
    queryKey: queryKeys.fixtures.lineups(fixture.id),
    queryFn: () => apiClient.getFixtureLineups(fixture.id),
    enabled: !!fixture.id,
    refetchInterval: refetchIntervals.lineups,
    staleTime: 2 * 60 * 1000, // Lineups don't change often
    gcTime: 10 * 60 * 1000, // Keep in cache longer
  })

  // Query for fixture events with optimized caching
  const {
    data: eventsData,
    isLoading: eventsLoading,
    error: eventsError
  } = useQuery({
    queryKey: queryKeys.fixtures.events(fixture.id),
    queryFn: () => apiClient.getFixtureEvents(fixture.id),
    enabled: !!fixture.id,
    refetchInterval: refetchIntervals.events,
    staleTime: isLiveMatch ? 5000 : 30000, // Very fresh for live matches
    gcTime: 5 * 60 * 1000,
  })

  // Query for fixture H2H with optimized caching
  const {
    data: h2hData,
    isLoading: h2hLoading,
    error: h2hError
  } = useQuery({
    queryKey: queryKeys.fixtures.h2h(fixture.id),
    queryFn: () => apiClient.getFixtureH2H(fixture.id),
    enabled: !!fixture.id,
    staleTime: 10 * 60 * 1000, // H2H data doesn't change often
    gcTime: 30 * 60 * 1000, // Keep in cache for 30 minutes
  })

  // Query for fixture player stats with optimized caching
  const {
    data: playerStatsData,
    isLoading: playerStatsLoading,
    error: playerStatsError
  } = useQuery({
    queryKey: queryKeys.fixtures.playerStats(fixture.id),
    queryFn: () => apiClient.getFixturePlayerStats(fixture.id),
    enabled: !!fixture.id,
    refetchInterval: refetchIntervals.playerStats,
    staleTime: isLiveMatch ? 15000 : 60000,
    gcTime: 5 * 60 * 1000,
  })

  const renderLoadingState = (title: string) => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Loader2 className="h-4 w-4 animate-spin" />
          {title} Yükleniyor...
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </div>
      </CardContent>
    </Card>
  )

  const renderErrorState = (title: string, error: any) => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-destructive">
          <AlertCircle className="h-4 w-4" />
          {title} Hatası
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
          {error?.message || 'Veri yüklenirken bir hata oluştu.'}
        </p>
      </CardContent>
    </Card>
  )

  const renderEmptyState = (title: string, description: string) => (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
          Bu maç için henüz veri bulunmuyor.
        </p>
      </CardContent>
    </Card>
  )

  return (
    <div className="w-full">
      {/* Match Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <img
                src={fixture.home_team_logo || '/placeholder-team.png'}
                alt={fixture.home_team_name}
                className="w-8 h-8 object-contain"
              />
              <span className="font-semibold">{fixture.home_team_name}</span>
            </div>

            <div className="flex items-center gap-2 px-3 py-1 bg-muted rounded-lg">
              <span className="text-lg font-bold">{fixture.home_goals}</span>
              <span className="text-muted-foreground">-</span>
              <span className="text-lg font-bold">{fixture.away_goals}</span>
            </div>

            <div className="flex items-center gap-2">
              <span className="font-semibold">{fixture.away_team_name}</span>
              <img
                src={fixture.away_team_logo || '/placeholder-team.png'}
                alt={fixture.away_team_name}
                className="w-8 h-8 object-contain"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Real-time Connection Status */}
            <Badge
              variant={isConnected ? 'default' : 'secondary'}
              className="flex items-center gap-1"
            >
              {isConnected ? (
                <>
                  <Wifi className="h-3 w-3" />
                  <span className="hidden sm:inline">Canlı</span>
                </>
              ) : (
                <>
                  <WifiOff className="h-3 w-3" />
                  <span className="hidden sm:inline">Bağlantı Yok</span>
                </>
              )}
            </Badge>

            <Badge variant={fixture.status_short === 'FT' ? 'default' : 'secondary'}>
              {fixture.status_long || fixture.status_short}
            </Badge>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue={defaultTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="statistics" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            İstatistikler
          </TabsTrigger>
          <TabsTrigger value="events" className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Olaylar
          </TabsTrigger>
          <TabsTrigger value="lineups" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            Kadrolar
          </TabsTrigger>
          <TabsTrigger value="h2h" className="flex items-center gap-2">
            <History className="h-4 w-4" />
            Karşılaşma
          </TabsTrigger>
          <TabsTrigger value="players" className="flex items-center gap-2">
            <Trophy className="h-4 w-4" />
            Oyuncular
          </TabsTrigger>
        </TabsList>

        <TabsContent value="statistics" className="mt-6">
          {statisticsLoading && renderLoadingState("İstatistikler")}
          {statisticsError && renderErrorState("İstatistikler", statisticsError)}
          {!statisticsLoading && !statisticsError && !statisticsData?.data &&
            renderEmptyState("İstatistikler", "Maç istatistikleri henüz mevcut değil.")}
          {statisticsData?.data && (
            <Suspense fallback={renderLoadingState("İstatistikler")}>
              <FixtureStatistics data={statisticsData.data} />
            </Suspense>
          )}
        </TabsContent>

        <TabsContent value="events" className="mt-6">
          {eventsLoading && renderLoadingState("Olaylar")}
          {eventsError && renderErrorState("Olaylar", eventsError)}
          {!eventsLoading && !eventsError && !eventsData?.data &&
            renderEmptyState("Olaylar", "Maç olayları henüz mevcut değil.")}
          {eventsData?.data && (
            <Suspense fallback={renderLoadingState("Olaylar")}>
              <FixtureEvents data={eventsData.data} />
            </Suspense>
          )}
        </TabsContent>

        <TabsContent value="lineups" className="mt-6">
          {lineupsLoading && renderLoadingState("Kadrolar")}
          {lineupsError && renderErrorState("Kadrolar", lineupsError)}
          {!lineupsLoading && !lineupsError && !lineupsData?.data &&
            renderEmptyState("Kadrolar", "Takım kadroları henüz mevcut değil.")}
          {lineupsData?.data && (
            <Suspense fallback={renderLoadingState("Kadrolar")}>
              <FixtureLineups data={lineupsData.data} />
            </Suspense>
          )}
        </TabsContent>

        <TabsContent value="h2h" className="mt-6">
          {h2hLoading && renderLoadingState("Karşılaşma Geçmişi")}
          {h2hError && renderErrorState("Karşılaşma Geçmişi", h2hError)}
          {!h2hLoading && !h2hError && !h2hData?.data &&
            renderEmptyState("Karşılaşma Geçmişi", "Takımlar arası geçmiş maçlar henüz mevcut değil.")}
          {h2hData?.data && (
            <Suspense fallback={renderLoadingState("Karşılaşma Geçmişi")}>
              <FixtureH2H data={h2hData.data} />
            </Suspense>
          )}
        </TabsContent>

        <TabsContent value="players" className="mt-6">
          {playerStatsLoading && renderLoadingState("Oyuncu İstatistikleri")}
          {playerStatsError && renderErrorState("Oyuncu İstatistikleri", playerStatsError)}
          {!playerStatsLoading && !playerStatsError && !playerStatsData?.data &&
            renderEmptyState("Oyuncu İstatistikleri", "Oyuncu performans verileri henüz mevcut değil.")}
          {playerStatsData?.data && (
            <Suspense fallback={renderLoadingState("Oyuncu İstatistikleri")}>
              <FixturePlayerStats data={playerStatsData.data} />
            </Suspense>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
