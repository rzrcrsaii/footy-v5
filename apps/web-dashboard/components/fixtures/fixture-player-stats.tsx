"use client"

import React, { useState } from 'react'
import { 
  Trophy, 
  Target, 
  Users, 
  Star,
  Award,
  TrendingUp,
  Activity,
  Zap,
  Shield,
  Timer,
  User,
  Crown,
  Shirt
} from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'

interface PlayerStats {
  player: {
    id: number
    name: string
    photo?: string
  }
  team: {
    id: number
    name: string
    logo?: string
  }
  rating?: number
  statistics: {
    games: {
      minutes: number
      rating?: string
      substitute: boolean
    }
    goals: {
      total: number
      assists: number
    }
    shots: {
      total: number
      on: number
    }
    passes: {
      total: number
      accuracy: number
    }
    tackles: {
      total: number
    }
    cards: {
      yellow: number
      red: number
    }
    fouls: {
      drawn: number
      committed: number
    }
  }
}

interface TeamPlayerStats {
  team: {
    id: number
    name: string
    logo?: string
  }
  players: PlayerStats[]
}

interface FixturePlayerStatsProps {
  data: {
    teams: TeamPlayerStats[]
    highlights: {
      top_rated: PlayerStats[]
      goal_scorers: PlayerStats[]
      assist_providers: PlayerStats[]
      yellow_cards: PlayerStats[]
      red_cards: PlayerStats[]
    }
  }
}

export function FixturePlayerStats({ data }: FixturePlayerStatsProps) {
  const [selectedTeam, setSelectedTeam] = useState<number | null>(null)

  if (!data || !data.teams) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Oyuncu İstatistikleri</CardTitle>
          <CardDescription>Bu maç için henüz oyuncu verisi bulunmuyor.</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  const { teams, highlights } = data

  const PlayerCard = ({ player, showTeam = false }: { player: PlayerStats, showTeam?: boolean }) => {
    const rating = player.rating || (player.statistics.games.rating ? parseFloat(player.statistics.games.rating) : 0)
    
    const getRatingColor = (rating: number) => {
      if (rating >= 8) return 'text-green-600 bg-green-100 dark:bg-green-900'
      if (rating >= 7) return 'text-blue-600 bg-blue-100 dark:bg-blue-900'
      if (rating >= 6) return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900'
      return 'text-red-600 bg-red-100 dark:bg-red-900'
    }

    return (
      <Card className="hover:shadow-md transition-shadow">
        <CardContent className="p-4">
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <h4 className="font-semibold text-sm">{player.player.name}</h4>
              {showTeam && (
                <p className="text-xs text-muted-foreground">{player.team.name}</p>
              )}
            </div>
            {rating > 0 && (
              <Badge className={`text-xs ${getRatingColor(rating)}`}>
                {rating.toFixed(1)}
              </Badge>
            )}
          </div>
          
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Dakika:</span>
              <span className="font-medium">{player.statistics.games.minutes}'</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Gol:</span>
              <span className="font-medium">{player.statistics.goals.total}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Asist:</span>
              <span className="font-medium">{player.statistics.goals.assists}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Şut:</span>
              <span className="font-medium">{player.statistics.shots.total}</span>
            </div>
          </div>
          
          {(player.statistics.cards.yellow > 0 || player.statistics.cards.red > 0) && (
            <div className="flex gap-1 mt-2">
              {Array.from({ length: player.statistics.cards.yellow }).map((_, i) => (
                <div key={i} className="w-3 h-4 bg-yellow-400 rounded-sm" />
              ))}
              {Array.from({ length: player.statistics.cards.red }).map((_, i) => (
                <div key={i} className="w-3 h-4 bg-red-500 rounded-sm" />
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  const HighlightSection = ({ 
    title, 
    icon: Icon, 
    players, 
    color 
  }: { 
    title: string
    icon: any
    players: PlayerStats[]
    color: string 
  }) => {
    if (players.length === 0) return null

    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className={`flex items-center gap-2 text-sm ${color}`}>
            <Icon className="h-4 w-4" />
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {players.slice(0, 3).map((player, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <div>
                  <span className="font-medium">{player.player.name}</span>
                  <span className="text-muted-foreground ml-2">({player.team.name})</span>
                </div>
                <div className="flex items-center gap-2">
                  {title.includes('Gol') && (
                    <Badge variant="outline">{player.statistics.goals.total}</Badge>
                  )}
                  {title.includes('Asist') && (
                    <Badge variant="outline">{player.statistics.goals.assists}</Badge>
                  )}
                  {title.includes('Rating') && player.rating && (
                    <Badge variant="outline">{player.rating.toFixed(1)}</Badge>
                  )}
                </div>
              </div>
            ))}
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
          <h2 className="text-2xl font-bold">Oyuncu İstatistikleri</h2>
          <p className="text-muted-foreground">Detaylı performans analizi</p>
        </div>
        <Badge variant="outline" className="flex items-center gap-1">
          <Users className="h-3 w-3" />
          {teams.reduce((total, team) => total + team.players.length, 0)} oyuncu
        </Badge>
      </div>

      {/* Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <HighlightSection
          title="En Yüksek Rating"
          icon={Star}
          players={highlights.top_rated}
          color="text-yellow-600"
        />
        
        <HighlightSection
          title="Gol Kralları"
          icon={Target}
          players={highlights.goal_scorers}
          color="text-green-600"
        />
        
        <HighlightSection
          title="Asist Liderleri"
          icon={TrendingUp}
          players={highlights.assist_providers}
          color="text-blue-600"
        />
      </div>

      {/* Team Tabs */}
      <Tabs defaultValue={teams[0]?.team.id.toString()} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          {teams.map((team) => (
            <TabsTrigger key={team.team.id} value={team.team.id.toString()}>
              {team.team.name}
            </TabsTrigger>
          ))}
        </TabsList>

        {teams.map((team) => (
          <TabsContent key={team.team.id} value={team.team.id.toString()} className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shirt className="h-5 w-5" />
                  {team.team.name} Oyuncuları
                </CardTitle>
                <CardDescription>
                  {team.players.length} oyuncu performansı
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {team.players
                    .sort((a, b) => {
                      const ratingA = a.rating || (a.statistics.games.rating ? parseFloat(a.statistics.games.rating) : 0)
                      const ratingB = b.rating || (b.statistics.games.rating ? parseFloat(b.statistics.games.rating) : 0)
                      return ratingB - ratingA
                    })
                    .map((player, index) => (
                      <PlayerCard key={index} player={player} />
                    ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>

      {/* Performance Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Performans Özeti
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-muted rounded-lg">
              <Target className="h-6 w-6 mx-auto mb-2 text-green-600" />
              <div className="text-2xl font-bold">
                {highlights.goal_scorers.reduce((total, player) => total + player.statistics.goals.total, 0)}
              </div>
              <div className="text-xs text-muted-foreground">Toplam Gol</div>
            </div>
            
            <div className="text-center p-4 bg-muted rounded-lg">
              <TrendingUp className="h-6 w-6 mx-auto mb-2 text-blue-600" />
              <div className="text-2xl font-bold">
                {highlights.assist_providers.reduce((total, player) => total + player.statistics.goals.assists, 0)}
              </div>
              <div className="text-xs text-muted-foreground">Toplam Asist</div>
            </div>
            
            <div className="text-center p-4 bg-muted rounded-lg">
              <Timer className="h-6 w-6 mx-auto mb-2 text-yellow-600" />
              <div className="text-2xl font-bold">
                {highlights.yellow_cards.length}
              </div>
              <div className="text-xs text-muted-foreground">Sarı Kart</div>
            </div>
            
            <div className="text-center p-4 bg-muted rounded-lg">
              <Shield className="h-6 w-6 mx-auto mb-2 text-red-600" />
              <div className="text-2xl font-bold">
                {highlights.red_cards.length}
              </div>
              <div className="text-xs text-muted-foreground">Kırmızı Kart</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
