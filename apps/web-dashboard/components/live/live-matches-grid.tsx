'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { apiClient, queryKeys, type Fixture } from '@/lib/api/client'
import { getMatchStatusText, formatTime } from '@/lib/utils'
import { useWebSocket } from '@/lib/websocket/provider'
import { useEffect } from 'react'
import { Activity, Clock, TrendingUp, BarChart3, Eye } from 'lucide-react'
import Link from 'next/link'

export function LiveMatchesGrid() {
  const { data: todayMatches, isLoading, error } = useQuery({
    queryKey: queryKeys.fixtures.todayLive(),
    queryFn: () => apiClient.getTodayLiveFixtures(),
    refetchInterval: 30000, // Refetch every 30 seconds for live data
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
    return () => {}
  }, [todayMatches?.fixtures, subscribe, unsubscribe])

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-muted-foreground">
            <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Error loading live data. Please try again later.</p>
            <Button 
              variant="outline" 
              className="mt-4"
              onClick={() => window.location.reload()}
            >
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  const liveMatches = todayMatches?.fixtures?.filter(fixture =>
    ['1H', '2H', 'HT', 'ET', 'BT', 'P'].includes(fixture.status_short)
  ) || []

  const upcomingMatches = todayMatches?.fixtures?.filter(fixture =>
    fixture.status_short === 'NS'
  ).slice(0, 6) || []

  const recentMatches = todayMatches?.fixtures?.filter(fixture =>
    ['FT', 'AET', 'PEN'].includes(fixture.status_short)
  ).slice(0, 6) || []

  return (
    <div className="space-y-6">
      {/* Live Matches Section */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <h2 className="text-xl font-semibold">Live Matches</h2>
          {liveMatches.length > 0 && (
            <div className="live-indicator h-2 w-2 rounded-full" />
          )}
        </div>
        
        {isLoading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Card key={i}>
                <CardContent className="p-4">
                  <Skeleton className="h-20 w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : liveMatches.length === 0 ? (
          <Card>
            <CardContent className="p-6">
              <div className="text-center text-muted-foreground">
                <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No live matches at the moment.</p>
                <p className="text-sm mt-2">Check back later for live updates.</p>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {liveMatches.map((fixture) => (
              <LiveMatchCard key={fixture.id} fixture={fixture} />
            ))}
          </div>
        )}
      </section>

      {/* Upcoming Matches Section */}
      <section>
        <h2 className="text-xl font-semibold mb-4">Upcoming Matches</h2>
        {upcomingMatches.length === 0 ? (
          <Card>
            <CardContent className="p-6">
              <div className="text-center text-muted-foreground">
                <p>No upcoming matches today.</p>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {upcomingMatches.map((fixture) => (
              <UpcomingMatchCard key={fixture.id} fixture={fixture} />
            ))}
          </div>
        )}
      </section>

      {/* Recent Results Section */}
      <section>
        <h2 className="text-xl font-semibold mb-4">Recent Results</h2>
        {recentMatches.length === 0 ? (
          <Card>
            <CardContent className="p-6">
              <div className="text-center text-muted-foreground">
                <p>No recent results today.</p>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {recentMatches.map((fixture) => (
              <RecentMatchCard key={fixture.id} fixture={fixture} />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

interface MatchCardProps {
  fixture: Fixture
}

function LiveMatchCard({ fixture }: MatchCardProps) {
  return (
    <Card className="border-red-200 bg-red-50/50 dark:border-red-800 dark:bg-red-900/10">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <Badge variant="destructive" className="text-xs">
            LIVE
          </Badge>
          <Badge variant="outline" className="text-xs">
            {fixture.league_name || `League ${fixture.league_id}`}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-medium">{fixture.home_team_name || 'Home Team'}</span>
            <span className="font-bold text-lg">{fixture.home_goals}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="font-medium">{fixture.away_team_name || 'Away Team'}</span>
            <span className="font-bold text-lg">{fixture.away_goals}</span>
          </div>
        </div>
        
        <div className="flex items-center justify-between pt-2 border-t">
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="text-xs">
              {getMatchStatusText(fixture.status_short)}
              {fixture.status_elapsed && ` ${fixture.status_elapsed}'`}
            </Badge>
          </div>
          <div className="flex items-center gap-1">
            <Button size="sm" variant="outline" asChild>
              <Link href={`/live/${fixture.id}`}>
                <Eye className="h-3 w-3 mr-1" />
                View
              </Link>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function UpcomingMatchCard({ fixture }: MatchCardProps) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <Badge variant="outline" className="text-xs">
            {formatTime(fixture.date)}
          </Badge>
          <Badge variant="outline" className="text-xs">
            {fixture.league_name || `League ${fixture.league_id}`}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-medium">{fixture.home_team_name || 'Home Team'}</span>
            <span className="text-muted-foreground">vs</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="font-medium">{fixture.away_team_name || 'Away Team'}</span>
          </div>
        </div>
        
        <div className="flex items-center justify-between pt-2 border-t">
          <Badge variant="secondary" className="text-xs">
            {getMatchStatusText(fixture.status_short)}
          </Badge>
          <Button size="sm" variant="outline" asChild>
            <Link href={`/live/${fixture.id}`}>
              <TrendingUp className="h-3 w-3 mr-1" />
              Odds
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

function RecentMatchCard({ fixture }: MatchCardProps) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <Badge variant="outline" className="text-xs">
            {getMatchStatusText(fixture.status_short)}
          </Badge>
          <Badge variant="outline" className="text-xs">
            {fixture.league_name || `League ${fixture.league_id}`}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-medium">{fixture.home_team_name || 'Home Team'}</span>
            <span className="font-bold text-lg">{fixture.home_goals}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="font-medium">{fixture.away_team_name || 'Away Team'}</span>
            <span className="font-bold text-lg">{fixture.away_goals}</span>
          </div>
        </div>
        
        <div className="flex items-center justify-between pt-2 border-t">
          <span className="text-xs text-muted-foreground">
            {formatTime(fixture.date)}
          </span>
          <Button size="sm" variant="outline" asChild>
            <Link href={`/live/${fixture.id}`}>
              <BarChart3 className="h-3 w-3 mr-1" />
              Stats
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
