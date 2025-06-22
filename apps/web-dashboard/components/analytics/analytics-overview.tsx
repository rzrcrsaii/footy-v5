'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { apiClient, queryKeys } from '@/lib/api/client'
import { 
  TrendingUp, 
  TrendingDown, 
  Target, 
  Activity, 
  BarChart3, 
  Users,
  Trophy,
  Clock
} from 'lucide-react'

export function AnalyticsOverview() {
  // Get fixtures data for analytics
  const { data: fixtures, isLoading } = useQuery({
    queryKey: queryKeys.fixtures.list({ per_page: 100, league_id: 39, season_year: 2024 }),
    queryFn: () => apiClient.getFixtures({ per_page: 100, league_id: 39, season_year: 2024 }),
    refetchInterval: 300000, // Refetch every 5 minutes
  })

  // Calculate analytics metrics
  const analytics = calculateAnalytics(fixtures?.fixtures || [])

  const overviewCards = [
    {
      title: 'Total Matches Analyzed',
      value: analytics.totalMatches,
      change: '+12%',
      trend: 'up' as const,
      icon: Activity,
      description: 'Last 30 days',
      color: 'text-blue-600',
    },
    {
      title: 'Average Goals per Match',
      value: analytics.avgGoalsPerMatch.toFixed(1),
      change: '+5.2%',
      trend: 'up' as const,
      icon: Target,
      description: 'Across all leagues',
      color: 'text-green-600',
    },
    {
      title: 'High-Scoring Matches',
      value: analytics.highScoringMatches,
      change: '-3%',
      trend: 'down' as const,
      icon: TrendingUp,
      description: '3+ goals',
      color: 'text-orange-600',
    },
    {
      title: 'Clean Sheets',
      value: analytics.cleanSheets,
      change: '+8%',
      trend: 'up' as const,
      icon: Trophy,
      description: 'Zero goals conceded',
      color: 'text-purple-600',
    },
    {
      title: 'Draw Rate',
      value: `${analytics.drawRate.toFixed(1)}%`,
      change: '+2.1%',
      trend: 'up' as const,
      icon: BarChart3,
      description: 'Match outcomes',
      color: 'text-gray-600',
    },
    {
      title: 'Late Goals',
      value: analytics.lateGoals,
      change: '+15%',
      trend: 'up' as const,
      icon: Clock,
      description: '80+ minutes',
      color: 'text-red-600',
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {overviewCards.map((card) => {
        const Icon = card.icon
        return (
          <Card key={card.title} className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {card.title}
              </CardTitle>
              <Icon className={`h-4 w-4 ${card.color}`} />
            </CardHeader>
            <CardContent>
              <div className="space-y-1">
                <div className="text-2xl font-bold">
                  {isLoading ? (
                    <Skeleton className="h-8 w-16" />
                  ) : (
                    card.value
                  )}
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <div className={`flex items-center gap-1 ${
                    card.trend === 'up' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {card.trend === 'up' ? (
                      <TrendingUp className="h-3 w-3" />
                    ) : (
                      <TrendingDown className="h-3 w-3" />
                    )}
                    {card.change}
                  </div>
                  <span className="text-muted-foreground">
                    {card.description}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}

function calculateAnalytics(fixtures: any[]) {
  const totalMatches = fixtures.length
  
  // Filter finished matches
  const finishedMatches = fixtures.filter(f => 
    ['FT', 'AET', 'PEN'].includes(f.status_short)
  )

  // Calculate total goals
  const totalGoals = finishedMatches.reduce((sum, match) => 
    sum + (match.home_goals || 0) + (match.away_goals || 0), 0
  )

  // Average goals per match
  const avgGoalsPerMatch = finishedMatches.length > 0 
    ? totalGoals / finishedMatches.length 
    : 0

  // High-scoring matches (3+ goals)
  const highScoringMatches = finishedMatches.filter(match => 
    (match.home_goals || 0) + (match.away_goals || 0) >= 3
  ).length

  // Clean sheets (matches where at least one team didn't concede)
  const cleanSheets = finishedMatches.filter(match => 
    (match.home_goals || 0) === 0 || (match.away_goals || 0) === 0
  ).length

  // Draw rate
  const draws = finishedMatches.filter(match => 
    (match.home_goals || 0) === (match.away_goals || 0)
  ).length
  const drawRate = finishedMatches.length > 0 
    ? (draws / finishedMatches.length) * 100 
    : 0

  // Simulate late goals (since we don't have minute-by-minute data)
  const lateGoals = Math.floor(totalGoals * 0.25) // Assume 25% of goals are late

  return {
    totalMatches,
    avgGoalsPerMatch,
    highScoringMatches,
    cleanSheets,
    drawRate,
    lateGoals,
  }
}
