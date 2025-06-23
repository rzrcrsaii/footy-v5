'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { apiClient, queryKeys, type Fixture } from '@/lib/api/client'
import { getMatchStatusColor, getMatchStatusText, formatTime } from '@/lib/utils'
import { useWebSocket } from '@/lib/websocket/provider'
import { useEffect } from 'react'

export function LiveMatches() {
  const { data: todayMatches, isLoading, error } = useQuery({
    queryKey: queryKeys.fixtures.todayLive(),
    queryFn: () => apiClient.getTodayLiveFixtures(),
    refetchInterval: 60000, // Refetch every minute
  })

  // Also fetch Premier League fixtures for more data
  const { data: premierLeagueFixtures } = useQuery({
    queryKey: queryKeys.fixtures.list({ league_id: 39, season_year: new Date().getFullYear(), per_page: 10 }),
    queryFn: () => apiClient.getFixtures({ league_id: 39, season_year: new Date().getFullYear(), per_page: 10 }),
    refetchInterval: 300000, // Refetch every 5 minutes
  })

  const { subscribe, unsubscribe } = useWebSocket()

  // Subscribe to live updates for all live matches
  useEffect(() => {
    if (todayMatches?.fixtures) {
      const liveFixtures = todayMatches.fixtures.filter(fixture =>
        ['1H', '2H', 'HT', 'ET', 'BT', 'P'].includes(fixture.status_short)
      )

      liveFixtures.forEach(fixture => {
        subscribe(fixture.id)
      })

      return () => {
        liveFixtures.forEach(fixture => {
          unsubscribe(fixture.id)
        })
      }
    }
    return () => {} // Empty cleanup function for when there are no fixtures
  }, [todayMatches?.fixtures, subscribe, unsubscribe])

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Live Matches</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="animate-pulse bg-gray-200 h-16 w-full rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Live Matches</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-red-600">
            <p>Error loading matches: {error.message}</p>
            <p className="text-sm text-gray-500 mt-2">
              Check if API server is running on port 8001
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Process real API data
  const processFixtures = (fixtures: any[]) => {
    return fixtures?.map((item: any) => {
      // Handle both direct fixture format and nested fixture format
      const fixture = item.fixture || item
      const teams = item.teams || {}
      const goals = item.goals || {}
      const league = item.league || {}

      return {
        id: fixture.id,
        date: fixture.date,
        status_short: fixture.status?.short || fixture.status_short,
        status_elapsed: fixture.status?.elapsed || fixture.status_elapsed,
        home_team_name: teams.home?.name || fixture.home_team_name,
        away_team_name: teams.away?.name || fixture.away_team_name,
        home_goals: goals.home ?? fixture.home_goals ?? 0,
        away_goals: goals.away ?? fixture.away_goals ?? 0,
        league_name: league.name || fixture.league_name,
        venue_name: fixture.venue?.name || fixture.venue_name,
      }
    }) || []
  }

  // Get fixtures from both sources
  const allFixtures = [
    ...processFixtures(todayMatches?.fixtures || []),
    ...processFixtures(premierLeagueFixtures?.items || [])
  ]

  // Remove duplicates by ID
  const uniqueFixtures = allFixtures.filter((fixture, index, self) =>
    index === self.findIndex(f => f.id === fixture.id)
  )

  const liveMatches = uniqueFixtures.filter(fixture =>
    ['1H', '2H', 'HT', 'ET', 'BT', 'P'].includes(fixture.status_short)
  )

  const upcomingMatches = uniqueFixtures.filter(fixture =>
    fixture.status_short === 'NS'
  ).slice(0, 5)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          Live Matches
          {liveMatches.length > 0 && (
            <div className="live-indicator h-2 w-2 rounded-full" />
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Live Matches */}
          {liveMatches.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-muted-foreground mb-3">
                Live Now ({liveMatches.length})
              </h4>
              <div className="space-y-3">
                {liveMatches.map((fixture) => (
                  <MatchCard key={fixture.id} fixture={fixture} isLive />
                ))}
              </div>
            </div>
          )}

          {/* Upcoming Matches */}
          {upcomingMatches.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-muted-foreground mb-3">
                Upcoming Today ({upcomingMatches.slice(0, 5).length})
              </h4>
              <div className="space-y-3">
                {upcomingMatches.slice(0, 5).map((fixture) => (
                  <MatchCard key={fixture.id} fixture={fixture} />
                ))}
              </div>
            </div>
          )}

          {liveMatches.length === 0 && upcomingMatches.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              No matches scheduled for today
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

interface MatchCardProps {
  fixture: Fixture
  isLive?: boolean
}

function MatchCard({ fixture, isLive = false }: MatchCardProps) {
  const isFinished = ['FT', 'AET', 'PEN'].includes(fixture.status_short)
  const isUpcoming = ['NS', 'TBD'].includes(fixture.status_short)

  // Format time from date string (Turkey timezone)
  const formatMatchTime = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleTimeString('tr-TR', {
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'Europe/Istanbul'
      })
    } catch {
      return '--:--'
    }
  }

  // Check if match is today (Turkey timezone)
  const isToday = (() => {
    try {
      const matchDate = new Date(fixture.date)
      const today = new Date()
      const matchDateTR = matchDate.toLocaleDateString('tr-TR', { timeZone: 'Europe/Istanbul' })
      const todayTR = today.toLocaleDateString('tr-TR', { timeZone: 'Europe/Istanbul' })
      return matchDateTR === todayTR
    } catch {
      return false
    }
  })()

  return (
    <Card className={`hover:shadow-md transition-shadow ${isToday ? 'ring-1 ring-primary/20 bg-primary/5' : ''}`}>
      <CardContent className="p-3">
        <div className="flex items-center gap-2 sm:gap-4">
          {/* Time & Status */}
          <div className="flex flex-col items-center min-w-[60px]">
            <div className="text-xs font-medium">
              {formatMatchTime(fixture.date)}
            </div>
            <Badge
              variant={isLive ? "destructive" : isFinished ? "secondary" : "outline"}
              className={`text-xs mt-1 ${isLive ? 'animate-pulse' : ''}`}
            >
              {isLive && '🔴 '}
              {getMatchStatusText(fixture.status_short)}
            </Badge>
          </div>

          {/* Home Team */}
          <div className="flex items-center gap-1 sm:gap-2 flex-1 min-w-0">
            <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-xs font-bold text-white shadow-sm">
              {fixture.home_team_name?.charAt(0) || 'H'}
            </div>
            <span className="font-medium truncate text-sm">
              {fixture.home_team_name || 'Home Team'}
            </span>
          </div>

          {/* Score */}
          <div className="flex items-center gap-1 min-w-[60px] justify-center">
            {isFinished || isLive ? (
              <div className="flex items-center gap-1 font-bold text-base">
                <span>{fixture.home_goals}</span>
                <span className="text-muted-foreground">-</span>
                <span>{fixture.away_goals}</span>
              </div>
            ) : (
              <div className="text-xs text-muted-foreground">vs</div>
            )}
            {isLive && fixture.status_elapsed && (
              <div className="text-xs text-red-600 font-medium ml-1">
                {fixture.status_elapsed}'
              </div>
            )}
          </div>

          {/* Away Team */}
          <div className="flex items-center gap-1 sm:gap-2 flex-1 min-w-0">
            <div className="w-6 h-6 bg-gradient-to-br from-red-500 to-red-600 rounded-full flex items-center justify-center text-xs font-bold text-white shadow-sm">
              {fixture.away_team_name?.charAt(0) || 'A'}
            </div>
            <span className="font-medium truncate text-sm">
              {fixture.away_team_name || 'Away Team'}
            </span>
          </div>

          {/* League */}
          <div className="text-right min-w-[80px]">
            <Badge variant="outline" className="text-xs">
              {fixture.league_name || `League ${fixture.league_id}`}
            </Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
