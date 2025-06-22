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
    queryKey: queryKeys.fixtures.list({ league_id: 39, season_year: 2024, per_page: 10 }),
    queryFn: () => apiClient.getFixtures({ league_id: 39, season_year: 2024, per_page: 10 }),
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
  return (
    <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors">
      <div className="flex items-center gap-3">
        <div className="flex flex-col items-center min-w-[60px]">
          <Badge 
            className={`text-xs ${getMatchStatusColor(fixture.status_short)}`}
          >
            {getMatchStatusText(fixture.status_short)}
          </Badge>
          {fixture.status_elapsed && (
            <span className="text-xs text-muted-foreground mt-1">
              {fixture.status_elapsed}'
            </span>
          )}
        </div>

        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <span className="font-medium text-sm">
                {fixture.home_team_name}
              </span>
              {isLive && (
                <span className="font-bold text-lg">
                  {fixture.home_goals}
                </span>
              )}
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="font-medium text-sm">
                {fixture.away_team_name}
              </span>
              {isLive && (
                <span className="font-bold text-lg">
                  {fixture.away_goals}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="text-right min-w-[80px]">
          <div className="text-sm text-muted-foreground">
            {fixture.league_name}
          </div>
          {!isLive && (
            <div className="text-sm font-medium">
              {formatTime(fixture.date)}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
