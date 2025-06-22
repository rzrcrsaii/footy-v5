'use client'

import { Activity, Wifi, WifiOff, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useWebSocket } from '@/lib/websocket/provider'
import { useQuery } from '@tanstack/react-query'
import { apiClient, queryKeys } from '@/lib/api/client'

export function LiveDataHeader() {
  const { isConnected, connectionStatus } = useWebSocket()
  
  const { data: todayMatches, refetch } = useQuery({
    queryKey: queryKeys.fixtures.todayLive(),
    queryFn: () => apiClient.getTodayLiveFixtures(),
    refetchInterval: 30000,
  })

  const liveMatchesCount = todayMatches?.fixtures?.filter(fixture =>
    ['1H', '2H', 'HT', 'ET', 'BT', 'P'].includes(fixture.status_short)
  ).length || 0

  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <Activity className="h-8 w-8 text-red-500" />
          Live Data
        </h1>
        <p className="text-muted-foreground">
          Real-time match data, odds movements, and live statistics
        </p>
      </div>
      
      <div className="flex items-center gap-4">
        {/* Live Matches Count */}
        <div className="flex items-center gap-2">
          <Badge variant={liveMatchesCount > 0 ? "destructive" : "secondary"}>
            {liveMatchesCount} Live Matches
          </Badge>
        </div>

        {/* WebSocket Status */}
        <div className="flex items-center gap-2">
          {isConnected ? (
            <Wifi className="h-4 w-4 text-green-600" />
          ) : (
            <WifiOff className="h-4 w-4 text-red-600" />
          )}
          <span className="text-xs text-muted-foreground capitalize">
            {connectionStatus}
          </span>
        </div>

        {/* Refresh Button */}
        <Button variant="outline" size="sm" onClick={() => refetch()}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>
    </div>
  )
}
