"use client"

import React from 'react'
import { 
  History, 
  Trophy, 
  Target, 
  TrendingUp,
  Calendar,
  MapPin,
  Clock,
  BarChart3,
  Percent,
  Award
} from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'

interface H2HMatch {
  fixture: {
    id: number
    date: string
    status: {
      short: string
      long: string
    }
    venue?: {
      name: string
      city: string
    }
  }
  league: {
    id: number
    name: string
    country: string
    logo?: string
    season: number
  }
  teams: {
    home: {
      id: number
      name: string
      logo?: string
    }
    away: {
      id: number
      name: string
      logo?: string
    }
  }
  goals: {
    home: number
    away: number
  }
  score: {
    halftime: {
      home: number
      away: number
    }
    fulltime: {
      home: number
      away: number
    }
  }
}

interface H2HStatistics {
  total_matches: number
  team1_wins: number
  team2_wins: number
  draws: number
  team1_win_percentage: number
  team2_win_percentage: number
  draw_percentage: number
  total_goals_team1: number
  total_goals_team2: number
  average_goals_team1: number
  average_goals_team2: number
}

interface FixtureH2HProps {
  data: {
    recent_matches: H2HMatch[]
    statistics: H2HStatistics
    home_team_id: number
    away_team_id: number
  }
}

export function FixtureH2H({ data }: FixtureH2HProps) {
  if (!data || !data.recent_matches) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Karşılaşma Geçmişi</CardTitle>
          <CardDescription>Bu takımlar arasında henüz karşılaşma verisi bulunmuyor.</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  const { recent_matches, statistics, home_team_id, away_team_id } = data

  // Get team names from recent matches
  const getTeamNames = () => {
    if (recent_matches.length === 0) return { homeTeam: 'Takım 1', awayTeam: 'Takım 2' }
    
    const firstMatch = recent_matches[0]
    const homeTeam = firstMatch.teams.home.id === home_team_id 
      ? firstMatch.teams.home.name 
      : firstMatch.teams.away.name
    const awayTeam = firstMatch.teams.home.id === away_team_id 
      ? firstMatch.teams.home.name 
      : firstMatch.teams.away.name
    
    return { homeTeam, awayTeam }
  }

  const { homeTeam, awayTeam } = getTeamNames()

  const getMatchResult = (match: H2HMatch, teamId: number) => {
    const isHome = match.teams.home.id === teamId
    const teamGoals = isHome ? match.goals.home : match.goals.away
    const opponentGoals = isHome ? match.goals.away : match.goals.home
    
    if (teamGoals > opponentGoals) return 'W'
    if (teamGoals < opponentGoals) return 'L'
    return 'D'
  }

  const getResultColor = (result: string) => {
    switch (result) {
      case 'W': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'L': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      case 'D': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('tr-TR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  }

  const StatCard = ({ 
    icon: Icon, 
    title, 
    homeValue, 
    awayValue, 
    homeLabel, 
    awayLabel,
    showProgress = false,
    unit = ''
  }: {
    icon: any
    title: string
    homeValue: number
    awayValue: number
    homeLabel: string
    awayLabel: string
    showProgress?: boolean
    unit?: string
  }) => (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-sm">
          <Icon className="h-4 w-4" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{homeValue}{unit}</div>
            <div className="text-xs text-muted-foreground">{homeLabel}</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{awayValue}{unit}</div>
            <div className="text-xs text-muted-foreground">{awayLabel}</div>
          </div>
        </div>
        
        {showProgress && (
          <div className="space-y-2">
            <div className="flex h-2 bg-muted rounded-full overflow-hidden">
              <div 
                className="bg-blue-500 transition-all duration-500"
                style={{ width: `${(homeValue / (homeValue + awayValue)) * 100}%` }}
              />
              <div 
                className="bg-red-500 transition-all duration-500"
                style={{ width: `${(awayValue / (homeValue + awayValue)) * 100}%` }}
              />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Karşılaşma Geçmişi</h2>
          <p className="text-muted-foreground">Son maçlar ve istatistiksel karşılaştırma</p>
        </div>
        <Badge variant="outline" className="flex items-center gap-1">
          <History className="h-3 w-3" />
          {statistics.total_matches} maç
        </Badge>
      </div>

      {/* Overall Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard
          icon={Trophy}
          title="Galibiyet"
          homeValue={statistics.team1_wins}
          awayValue={statistics.team2_wins}
          homeLabel={homeTeam}
          awayLabel={awayTeam}
          showProgress={true}
        />
        
        <StatCard
          icon={Target}
          title="Toplam Gol"
          homeValue={statistics.total_goals_team1}
          awayValue={statistics.total_goals_team2}
          homeLabel={homeTeam}
          awayLabel={awayTeam}
          showProgress={true}
        />
        
        <StatCard
          icon={BarChart3}
          title="Ortalama Gol"
          homeValue={Math.round(statistics.average_goals_team1 * 10) / 10}
          awayValue={Math.round(statistics.average_goals_team2 * 10) / 10}
          homeLabel={homeTeam}
          awayLabel={awayTeam}
        />
      </div>

      {/* Win Percentage */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Percent className="h-5 w-5" />
            Galibiyet Yüzdeleri
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="font-medium">{homeTeam}</span>
              <div className="flex items-center gap-2">
                <Progress value={statistics.team1_win_percentage} className="w-32" />
                <span className="text-sm font-medium w-12">
                  {Math.round(statistics.team1_win_percentage)}%
                </span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="font-medium">Beraberlik</span>
              <div className="flex items-center gap-2">
                <Progress value={statistics.draw_percentage} className="w-32" />
                <span className="text-sm font-medium w-12">
                  {Math.round(statistics.draw_percentage)}%
                </span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="font-medium">{awayTeam}</span>
              <div className="flex items-center gap-2">
                <Progress value={statistics.team2_win_percentage} className="w-32" />
                <span className="text-sm font-medium w-12">
                  {Math.round(statistics.team2_win_percentage)}%
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Matches */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Son Karşılaşmalar
          </CardTitle>
          <CardDescription>
            En son {recent_matches.length} maç sonucu
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recent_matches.map((match, index) => {
              const homeResult = getMatchResult(match, home_team_id)
              const awayResult = getMatchResult(match, away_team_id)
              
              return (
                <div key={index} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">
                        {formatDate(match.fixture.date)}
                      </span>
                      <Badge variant="outline" className="text-xs">
                        {match.league.name}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={`text-xs ${getResultColor(homeResult)}`}>
                        {homeResult}
                      </Badge>
                      <Badge className={`text-xs ${getResultColor(awayResult)}`}>
                        {awayResult}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="font-medium">{match.teams.home.name}</span>
                      <div className="text-lg font-bold">
                        {match.goals.home} - {match.goals.away}
                      </div>
                      <span className="font-medium">{match.teams.away.name}</span>
                    </div>
                    
                    {match.fixture.venue && (
                      <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <MapPin className="h-3 w-3" />
                        {match.fixture.venue.name}
                      </div>
                    )}
                  </div>
                  
                  {match.score.halftime && (
                    <div className="text-xs text-muted-foreground mt-2">
                      İlk Yarı: {match.score.halftime.home} - {match.score.halftime.away}
                    </div>
                  )}
                </div>
              )
            })}
            
            {recent_matches.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                <History className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Henüz karşılaşma kaydı bulunmuyor.</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
