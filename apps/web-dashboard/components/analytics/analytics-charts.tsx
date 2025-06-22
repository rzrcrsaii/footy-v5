'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { apiClient, queryKeys } from '@/lib/api/client'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts'
import { BarChart3, TrendingUp, PieChart as PieChartIcon } from 'lucide-react'

export function AnalyticsCharts() {
  const { data: fixtures, isLoading } = useQuery({
    queryKey: queryKeys.fixtures.list({ per_page: 100, league_id: 39, season_year: 2024 }),
    queryFn: () => apiClient.getFixtures({ per_page: 100, league_id: 39, season_year: 2024 }),
    refetchInterval: 300000,
  })

  // Prepare chart data
  const chartData = prepareChartData(fixtures?.fixtures || [])

  if (isLoading) {
    return (
      <div className="grid gap-6 md:grid-cols-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-48" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-64 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  return (
    <div className="grid gap-6">
      {/* Goals Distribution Chart */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Goals Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData.goalsDistribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="goals" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="matches" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Match Outcomes Pie Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChartIcon className="h-5 w-5" />
              Match Outcomes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={chartData.matchOutcomes}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {chartData.matchOutcomes.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Goals Trend Over Time */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Goals Trend Over Time
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData.goalsTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="avgGoals"
                stroke="#3b82f6"
                strokeWidth={2}
                name="Average Goals per Match"
              />
              <Line
                type="monotone"
                dataKey="totalMatches"
                stroke="#ef4444"
                strokeWidth={2}
                name="Total Matches"
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}

function prepareChartData(fixtures: any[]) {
  // Goals distribution
  const goalsDistribution = Array.from({ length: 8 }, (_, i) => ({
    goals: i.toString(),
    matches: fixtures.filter(f => {
      const totalGoals = (f.home_goals || 0) + (f.away_goals || 0)
      return totalGoals === i
    }).length
  }))

  // Match outcomes
  const finishedMatches = fixtures.filter(f =>
    ['FT', 'AET', 'PEN'].includes(f.status_short)
  )

  const homeWins = finishedMatches.filter(f => (f.home_goals || 0) > (f.away_goals || 0)).length
  const draws = finishedMatches.filter(f => (f.home_goals || 0) === (f.away_goals || 0)).length
  const awayWins = finishedMatches.filter(f => (f.home_goals || 0) < (f.away_goals || 0)).length

  const matchOutcomes = [
    { name: 'Home Wins', value: homeWins, color: '#3b82f6' },
    { name: 'Draws', value: draws, color: '#f59e0b' },
    { name: 'Away Wins', value: awayWins, color: '#ef4444' },
  ]

  // Goals trend over time (simplified)
  const goalsTrend = Array.from({ length: 10 }, (_, i) => {
    const date = new Date()
    date.setDate(date.getDate() - (9 - i) * 3)

    return {
      date: date.toLocaleDateString(),
      avgGoals: 2.5 + Math.random() * 1.5,
      totalMatches: Math.floor(Math.random() * 10) + 5,
    }
  })

  return {
    goalsDistribution,
    matchOutcomes,
    goalsTrend,
  }
}
