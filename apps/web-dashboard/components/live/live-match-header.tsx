'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { apiClient, queryKeys } from '@/lib/api/client'
import { getMatchStatusText, formatTime } from '@/lib/utils'
import { useWebSocket } from '@/lib/websocket/provider'
import { useEffect } from 'react'
import { ArrowLeft, Clock, MapPin, Users, Wifi, WifiOff } from 'lucide-react'
import Link from 'next/link'

interface LiveMatchHeaderProps {
  fixtureId: number
}

export function LiveMatchHeader({ fixtureId }: LiveMatchHeaderProps) {
  const { isConnected, subscribe, unsubscribe } = useWebSocket()

  const { data: fixture, isLoading } = useQuery({
    queryKey: queryKeys.fixtures.detail(fixtureId),
    queryFn: () => apiClient.getFixture(fixtureId),
    refetchInterval: 30000,
  })

  // Subscribe to live updates for this match
  useEffect(() => {
    if (fixture && ['1H', '2H', 'HT', 'ET', 'BT', 'P'].includes(fixture.status_short)) {
      subscribe(fixtureId)
      return () => unsubscribe(fixtureId)
    }
    return () => {}
  }, [fixture, fixtureId, subscribe, unsubscribe])

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-6 w-32" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!fixture) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-muted-foreground">
            <p>Match not found.</p>
            <Button variant="outline" className="mt-4" asChild>
              <Link href="/live">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Live Data
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  const isLive = ['1H', '2H', 'HT', 'ET', 'BT', 'P'].includes(fixture.status_short)
  const isFinished = ['FT', 'AET', 'PEN'].includes(fixture.status_short)

  return (
    <div className="space-y-4">
      {/* Navigation */}
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" asChild>
          <Link href="/live">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Live Data
          </Link>
        </Button>
        
        <div className="flex items-center gap-2">
          {isConnected ? (
            <Wifi className="h-4 w-4 text-green-600" />
          ) : (
            <WifiOff className="h-4 w-4 text-red-600" />
          )}
          <span className="text-xs text-muted-foreground">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Match Header */}
      <Card className={isLive ? 'border-red-200 bg-red-50/50 dark:border-red-800 dark:bg-red-900/10' : ''}>
        <CardContent className="p-6">
          <div className="space-y-4">
            {/* League and Status */}
            <div className="flex items-center justify-between">
              <Badge variant="outline">
                {fixture.league_name || `League ${fixture.league_id}`}
              </Badge>
              <div className="flex items-center gap-2">
                {isLive && <div className="live-indicator h-2 w-2 rounded-full" />}
                <Badge 
                  variant={isLive ? "destructive" : isFinished ? "secondary" : "outline"}
                >
                  {getMatchStatusText(fixture.status_short)}
                  {fixture.status_elapsed && ` ${fixture.status_elapsed}'`}
                </Badge>
              </div>
            </div>

            {/* Teams and Score */}
            <div className="grid grid-cols-3 items-center gap-4">
              {/* Home Team */}
              <div className="text-center">
                <h2 className="text-xl font-bold">
                  {fixture.home_team_name || 'Home Team'}
                </h2>
                {fixture.home_team_logo && (
                  <img 
                    src={fixture.home_team_logo} 
                    alt={fixture.home_team_name || 'Home Team'} 
                    className="h-16 w-16 mx-auto mt-2"
                  />
                )}
              </div>

              {/* Score */}
              <div className="text-center">
                {(isLive || isFinished) ? (
                  <div className="text-4xl font-bold">
                    {fixture.home_goals} - {fixture.away_goals}
                  </div>
                ) : (
                  <div className="text-2xl font-medium text-muted-foreground">
                    vs
                  </div>
                )}
                {fixture.status_short === 'HT' && (
                  <div className="text-sm text-muted-foreground mt-1">
                    HT: {fixture.home_goals_ht} - {fixture.away_goals_ht}
                  </div>
                )}
              </div>

              {/* Away Team */}
              <div className="text-center">
                <h2 className="text-xl font-bold">
                  {fixture.away_team_name || 'Away Team'}
                </h2>
                {fixture.away_team_logo && (
                  <img 
                    src={fixture.away_team_logo} 
                    alt={fixture.away_team_name || 'Away Team'} 
                    className="h-16 w-16 mx-auto mt-2"
                  />
                )}
              </div>
            </div>

            {/* Match Details */}
            <div className="flex items-center justify-center gap-6 text-sm text-muted-foreground border-t pt-4">
              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                {formatTime(fixture.date)}
              </div>
              {fixture.venue_name && (
                <div className="flex items-center gap-1">
                  <MapPin className="h-4 w-4" />
                  {fixture.venue_name}
                </div>
              )}
              {fixture.referee && (
                <div className="flex items-center gap-1">
                  <Users className="h-4 w-4" />
                  {fixture.referee}
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
