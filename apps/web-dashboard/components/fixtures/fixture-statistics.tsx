"use client"

import React from 'react'
import { 
  Target, 
  Activity, 
  Users, 
  AlertTriangle, 
  CornerDownRight,
  Timer,
  TrendingUp,
  BarChart3,
  Zap,
  Shield
} from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'

interface TeamStatistics {
  team: {
    id: number
    name: string
    logo?: string
  }
  statistics: Array<{
    type: string
    value: string | number | null
  }>
}

interface FixtureStatisticsProps {
  data: TeamStatistics[]
}

export function FixtureStatistics({ data }: FixtureStatisticsProps) {
  if (!data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Maç İstatistikleri</CardTitle>
          <CardDescription>Bu maç için henüz istatistik verisi bulunmuyor.</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  // Extract statistics for both teams
  const homeTeam = data[0]
  const awayTeam = data[1] || data[0] // Fallback if only one team

  const getStatValue = (team: TeamStatistics, statType: string): number => {
    const stat = team.statistics.find(s => s.type === statType)
    if (!stat?.value) return 0
    
    // Handle percentage values
    if (typeof stat.value === 'string' && stat.value.includes('%')) {
      return parseInt(stat.value.replace('%', ''))
    }
    
    return typeof stat.value === 'number' ? stat.value : parseInt(stat.value.toString()) || 0
  }

  const getStatDisplay = (team: TeamStatistics, statType: string): string => {
    const stat = team.statistics.find(s => s.type === statType)
    return stat?.value?.toString() || '0'
  }

  // Key statistics to display
  const keyStats = [
    {
      type: 'Ball Possession',
      icon: Activity,
      label: 'Top Hakimiyeti',
      unit: '%',
      color: 'blue'
    },
    {
      type: 'Total Shots',
      icon: Target,
      label: 'Toplam Şut',
      unit: '',
      color: 'green'
    },
    {
      type: 'Shots on Goal',
      icon: Zap,
      label: 'İsabetli Şut',
      unit: '',
      color: 'yellow'
    },
    {
      type: 'Total passes',
      icon: TrendingUp,
      label: 'Toplam Pas',
      unit: '',
      color: 'purple'
    },
    {
      type: 'Passes accurate',
      icon: BarChart3,
      label: 'İsabetli Pas',
      unit: '',
      color: 'indigo'
    },
    {
      type: 'Fouls',
      icon: AlertTriangle,
      label: 'Faul',
      unit: '',
      color: 'red'
    },
    {
      type: 'Yellow Cards',
      icon: Timer,
      label: 'Sarı Kart',
      unit: '',
      color: 'amber'
    },
    {
      type: 'Corner Kicks',
      icon: CornerDownRight,
      label: 'Korner',
      unit: '',
      color: 'teal'
    }
  ]

  const StatCard = ({ stat, homeValue, awayValue, homeDisplay, awayDisplay }: {
    stat: typeof keyStats[0]
    homeValue: number
    awayValue: number
    homeDisplay: string
    awayDisplay: string
  }) => {
    const total = homeValue + awayValue
    const homePercentage = total > 0 ? (homeValue / total) * 100 : 50
    const awayPercentage = total > 0 ? (awayValue / total) * 100 : 50

    const IconComponent = stat.icon

    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-sm font-medium">
            <IconComponent className="h-4 w-4" />
            {stat.label}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Team Values */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full" />
              <span className="text-sm font-medium">{homeTeam.team.name}</span>
            </div>
            <Badge variant="outline">
              {homeDisplay}{stat.unit}
            </Badge>
          </div>

          {/* Progress Bar */}
          <div className="relative">
            <div className="flex h-2 bg-muted rounded-full overflow-hidden">
              <div 
                className="bg-blue-500 transition-all duration-500"
                style={{ width: `${homePercentage}%` }}
              />
              <div 
                className="bg-red-500 transition-all duration-500"
                style={{ width: `${awayPercentage}%` }}
              />
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-500 rounded-full" />
              <span className="text-sm font-medium">{awayTeam.team.name}</span>
            </div>
            <Badge variant="outline">
              {awayDisplay}{stat.unit}
            </Badge>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Maç İstatistikleri</h2>
          <p className="text-muted-foreground">Detaylı performans karşılaştırması</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full" />
            <span className="text-sm font-medium">{homeTeam.team.name}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full" />
            <span className="text-sm font-medium">{awayTeam.team.name}</span>
          </div>
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {keyStats.map((stat) => {
          const homeValue = getStatValue(homeTeam, stat.type)
          const awayValue = getStatValue(awayTeam, stat.type)
          const homeDisplay = getStatDisplay(homeTeam, stat.type)
          const awayDisplay = getStatDisplay(awayTeam, stat.type)

          return (
            <StatCard
              key={stat.type}
              stat={stat}
              homeValue={homeValue}
              awayValue={awayValue}
              homeDisplay={homeDisplay}
              awayDisplay={awayDisplay}
            />
          )
        })}
      </div>

      {/* Additional Stats */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Diğer İstatistikler
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Home Team Additional Stats */}
            <div>
              <h4 className="font-semibold mb-3 flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full" />
                {homeTeam.team.name}
              </h4>
              <div className="space-y-2">
                {homeTeam.statistics
                  .filter(stat => !keyStats.some(ks => ks.type === stat.type))
                  .map((stat, index) => (
                    <div key={index} className="flex justify-between text-sm">
                      <span className="text-muted-foreground">{stat.type}</span>
                      <span className="font-medium">{stat.value || '0'}</span>
                    </div>
                  ))}
              </div>
            </div>

            {/* Away Team Additional Stats */}
            <div>
              <h4 className="font-semibold mb-3 flex items-center gap-2">
                <div className="w-3 h-3 bg-red-500 rounded-full" />
                {awayTeam.team.name}
              </h4>
              <div className="space-y-2">
                {awayTeam.statistics
                  .filter(stat => !keyStats.some(ks => ks.type === stat.type))
                  .map((stat, index) => (
                    <div key={index} className="flex justify-between text-sm">
                      <span className="text-muted-foreground">{stat.type}</span>
                      <span className="font-medium">{stat.value || '0'}</span>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
