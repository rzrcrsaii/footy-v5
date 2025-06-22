'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { apiClient, queryKeys, type LiveStats } from '@/lib/api/client'
import { useWebSocket } from '@/lib/websocket/provider'
import { useEffect, useState } from 'react'
import { BarChart3, TrendingUp } from 'lucide-react'
import { Progress } from '@/components/ui/progress'

interface LiveStatsChartProps {
  fixtureId: number
}

export function LiveStatsChart({ fixtureId }: LiveStatsChartProps) {
  const [realtimeStats, setRealtimeStats] = useState<LiveStats[]>([])
  const { lastMessage } = useWebSocket()

  const { data: stats, isLoading } = useQuery({
    queryKey: queryKeys.live.stats(fixtureId),
    queryFn: () => apiClient.getLiveStats(fixtureId, { limit: 10 }),
    refetchInterval: 30000,
  })

  // Handle real-time stats updates
  useEffect(() => {
    if (lastMessage && lastMessage.type === 'stats_update' && lastMessage.fixture_id === fixtureId) {
      setRealtimeStats(prev => {
        const newStats = [...prev]
        const existingIndex = newStats.findIndex(
          stat => stat.team_id === lastMessage.data.team_id
        )
        
        if (existingIndex >= 0) {
          newStats[existingIndex] = { ...newStats[existingIndex], ...lastMessage.data }
        } else {
          newStats.push(lastMessage.data)
        }
        
        return newStats
      })
    }
  }, [lastMessage, fixtureId])

  // Combine API data with real-time updates
  const allStats = [...(stats || []), ...realtimeStats]
  
  // Get latest stats for each team
  const latestStats = allStats.reduce((acc, stat) => {
    if (!acc[stat.team_id] || new Date(stat.timestamp) > new Date(acc[stat.team_id].timestamp)) {
      acc[stat.team_id] = stat
    }
    return acc
  }, {} as Record<number, LiveStats>)

  const teamStats = Object.values(latestStats)

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Live Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-2 w-full" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (teamStats.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Live Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-8">
            <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No statistics available yet.</p>
            <p className="text-sm mt-2">Match statistics will appear here during the game.</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Prepare data for comparison
  const homeTeam = teamStats[0]
  const awayTeam = teamStats[1] || teamStats[0] // Fallback if only one team

  const statCategories = [
    {
      label: 'Ball Possession',
      homeValue: homeTeam?.ball_possession || 0,
      awayValue: awayTeam?.ball_possession || 0,
      unit: '%',
      max: 100
    },
    {
      label: 'Total Shots',
      homeValue: homeTeam?.total_shots || 0,
      awayValue: awayTeam?.total_shots || 0,
      unit: '',
      max: Math.max((homeTeam?.total_shots || 0) + (awayTeam?.total_shots || 0), 10)
    },
    {
      label: 'Shots on Goal',
      homeValue: homeTeam?.shots_on_goal || 0,
      awayValue: awayTeam?.shots_on_goal || 0,
      unit: '',
      max: Math.max((homeTeam?.shots_on_goal || 0) + (awayTeam?.shots_on_goal || 0), 5)
    },
    {
      label: 'Corner Kicks',
      homeValue: homeTeam?.corner_kicks || 0,
      awayValue: awayTeam?.corner_kicks || 0,
      unit: '',
      max: Math.max((homeTeam?.corner_kicks || 0) + (awayTeam?.corner_kicks || 0), 5)
    },
    {
      label: 'Fouls',
      homeValue: homeTeam?.fouls || 0,
      awayValue: awayTeam?.fouls || 0,
      unit: '',
      max: Math.max((homeTeam?.fouls || 0) + (awayTeam?.fouls || 0), 10)
    },
    {
      label: 'Pass Accuracy',
      homeValue: homeTeam?.passes_percentage || 0,
      awayValue: awayTeam?.passes_percentage || 0,
      unit: '%',
      max: 100
    }
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Live Statistics
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Team Headers */}
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="font-medium text-sm">
              {homeTeam?.team_name || 'Home Team'}
            </div>
            <div className="text-xs text-muted-foreground">
              Statistics
            </div>
            <div className="font-medium text-sm">
              {awayTeam?.team_name || 'Away Team'}
            </div>
          </div>

          {/* Statistics */}
          <div className="space-y-4">
            {statCategories.map((category) => (
              <StatComparison
                key={category.label}
                label={category.label}
                homeValue={category.homeValue}
                awayValue={category.awayValue}
                unit={category.unit}
                max={category.max}
              />
            ))}
          </div>

          {/* Last Updated */}
          <div className="text-xs text-muted-foreground text-center pt-4 border-t">
            Last updated: {teamStats[0] ? new Date(teamStats[0].timestamp).toLocaleTimeString() : 'N/A'}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

interface StatComparisonProps {
  label: string
  homeValue: number
  awayValue: number
  unit: string
  max: number
}

function StatComparison({ label, homeValue, awayValue, unit, max }: StatComparisonProps) {
  const homePercentage = max > 0 ? (homeValue / max) * 100 : 0
  const awayPercentage = max > 0 ? (awayValue / max) * 100 : 0

  return (
    <div className="space-y-2">
      <div className="grid grid-cols-3 gap-4 text-center">
        <div className="text-sm font-medium">
          {homeValue}{unit}
        </div>
        <div className="text-xs text-muted-foreground">
          {label}
        </div>
        <div className="text-sm font-medium">
          {awayValue}{unit}
        </div>
      </div>
      
      <div className="grid grid-cols-3 gap-4 items-center">
        {/* Home Team Progress */}
        <div className="flex justify-end">
          <div className="w-full max-w-24">
            <Progress 
              value={homePercentage} 
              className="h-2 [&>div]:bg-blue-500 transform rotate-180"
            />
          </div>
        </div>
        
        {/* Center Divider */}
        <div className="flex justify-center">
          <div className="w-px h-4 bg-border" />
        </div>
        
        {/* Away Team Progress */}
        <div className="flex justify-start">
          <div className="w-full max-w-24">
            <Progress 
              value={awayPercentage} 
              className="h-2 [&>div]:bg-red-500"
            />
          </div>
        </div>
      </div>
    </div>
  )
}
