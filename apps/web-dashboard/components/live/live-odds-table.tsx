'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { apiClient, queryKeys, type LiveOdds } from '@/lib/api/client'
import { useWebSocket } from '@/lib/websocket/provider'
import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface LiveOddsTableProps {
  fixtureId: number
}

export function LiveOddsTable({ fixtureId }: LiveOddsTableProps) {
  const [realtimeOdds, setRealtimeOdds] = useState<LiveOdds[]>([])
  const { lastMessage } = useWebSocket()

  const { data: odds, isLoading } = useQuery({
    queryKey: queryKeys.live.odds(fixtureId),
    queryFn: () => apiClient.getLiveOdds(fixtureId, { limit: 50 }),
    refetchInterval: 30000,
  })

  // Handle real-time odds updates
  useEffect(() => {
    if (lastMessage && lastMessage.type === 'odds_update' && lastMessage.fixture_id === fixtureId) {
      setRealtimeOdds(prev => {
        const newOdds = [...prev]
        const existingIndex = newOdds.findIndex(
          odd => odd.bookmaker_id === lastMessage.data.bookmaker_id && 
                 odd.bet_market_id === lastMessage.data.bet_market_id &&
                 odd.bet_value === lastMessage.data.bet_value
        )
        
        if (existingIndex >= 0) {
          newOdds[existingIndex] = { ...newOdds[existingIndex], ...lastMessage.data }
        } else {
          newOdds.push(lastMessage.data)
        }
        
        return newOdds.slice(0, 50) // Keep only latest 50 odds
      })
    }
  }, [lastMessage, fixtureId])

  // Combine API data with real-time updates
  const allOdds = [...(odds || []), ...realtimeOdds]
  
  // Group odds by market
  const oddsByMarket = allOdds.reduce((acc, odd) => {
    const marketKey = odd.bet_market_name || `Market ${odd.bet_market_id}`
    if (!acc[marketKey]) {
      acc[marketKey] = []
    }
    acc[marketKey].push(odd)
    return acc
  }, {} as Record<string, LiveOdds[]>)

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Live Odds</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-6 w-32" />
                <div className="grid grid-cols-3 gap-4">
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (Object.keys(oddsByMarket).length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Live Odds</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-8">
            <TrendingUp className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No odds data available for this match.</p>
            <p className="text-sm mt-2">Odds will appear here when available.</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Live Odds
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {Object.entries(oddsByMarket).map(([marketName, marketOdds]) => (
            <OddsMarketSection 
              key={marketName} 
              marketName={marketName} 
              odds={marketOdds} 
            />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

interface OddsMarketSectionProps {
  marketName: string
  odds: LiveOdds[]
}

function OddsMarketSection({ marketName, odds }: OddsMarketSectionProps) {
  // Group odds by bet value (e.g., Home, Draw, Away)
  const oddsByValue = odds.reduce((acc, odd) => {
    if (!acc[odd.bet_value]) {
      acc[odd.bet_value] = []
    }
    acc[odd.bet_value].push(odd)
    return acc
  }, {} as Record<string, LiveOdds[]>)

  return (
    <div className="space-y-3">
      <h3 className="font-medium text-sm text-muted-foreground uppercase tracking-wide">
        {marketName}
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {Object.entries(oddsByValue).map(([betValue, betOdds]) => {
          // Get the latest odd for this bet value
          const latestOdd = betOdds.sort((a, b) => 
            new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
          )[0]
          
          // Calculate trend if we have multiple odds
          const trend = betOdds.length > 1 ? calculateTrend(betOdds) : 'stable'
          
          return (
            <OddCard 
              key={betValue} 
              betValue={betValue} 
              odd={latestOdd} 
              trend={trend}
            />
          )
        })}
      </div>
    </div>
  )
}

interface OddCardProps {
  betValue: string
  odd: LiveOdds
  trend: 'up' | 'down' | 'stable'
}

function OddCard({ betValue, odd, trend }: OddCardProps) {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-600" />
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-600" />
      default:
        return <Minus className="h-4 w-4 text-muted-foreground" />
    }
  }

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/10'
      case 'down':
        return 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/10'
      default:
        return 'border-border bg-background'
    }
  }

  return (
    <div className={`p-4 rounded-lg border transition-colors ${getTrendColor()}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="font-medium text-sm">{betValue}</span>
        {getTrendIcon()}
      </div>
      
      <div className="space-y-1">
        <div className="text-2xl font-bold">
          {odd.odd_value.toFixed(2)}
        </div>
        
        <div className="text-xs text-muted-foreground">
          {odd.bookmaker_name || `Bookmaker ${odd.bookmaker_id}`}
        </div>
        
        <div className="text-xs text-muted-foreground">
          {new Date(odd.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}

function calculateTrend(odds: LiveOdds[]): 'up' | 'down' | 'stable' {
  if (odds.length < 2) return 'stable'
  
  const sorted = odds.sort((a, b) => 
    new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  )
  
  const latest = sorted[sorted.length - 1]
  const previous = sorted[sorted.length - 2]
  
  if (latest.odd_value > previous.odd_value) return 'up'
  if (latest.odd_value < previous.odd_value) return 'down'
  return 'stable'
}
