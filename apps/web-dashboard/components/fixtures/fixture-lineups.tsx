"use client"

import React from 'react'
import { 
  Users, 
  User, 
  Shield, 
  Target,
  Crown,
  UserCheck,
  Shirt
} from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'

interface Player {
  id: number
  name: string
  number: number
  pos: string
  grid?: string
}

interface TeamLineup {
  team: {
    id: number
    name: string
    logo?: string
    colors?: {
      player?: {
        primary: string
        number: string
        border: string
      }
      goalkeeper?: {
        primary: string
        number: string
        border: string
      }
    }
  }
  formation: string
  startXI: Array<{
    player: Player
  }>
  substitutes: Array<{
    player: Player
  }>
  coach: {
    id: number
    name: string
    photo?: string
  }
}

interface FixtureLineupsProps {
  data: TeamLineup[]
}

export function FixtureLineups({ data }: FixtureLineupsProps) {
  if (!data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Takım Kadroları</CardTitle>
          <CardDescription>Bu maç için henüz kadro verisi bulunmuyor.</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  const homeTeam = data[0]
  const awayTeam = data[1] || data[0] // Fallback if only one team

  const getPositionColor = (position: string) => {
    switch (position) {
      case 'G':
        return 'bg-yellow-100 border-yellow-300 text-yellow-800 dark:bg-yellow-900 dark:border-yellow-700 dark:text-yellow-200'
      case 'D':
        return 'bg-blue-100 border-blue-300 text-blue-800 dark:bg-blue-900 dark:border-blue-700 dark:text-blue-200'
      case 'M':
        return 'bg-green-100 border-green-300 text-green-800 dark:bg-green-900 dark:border-green-700 dark:text-green-200'
      case 'F':
        return 'bg-red-100 border-red-300 text-red-800 dark:bg-red-900 dark:border-red-700 dark:text-red-200'
      default:
        return 'bg-gray-100 border-gray-300 text-gray-800 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-200'
    }
  }

  const getPositionIcon = (position: string) => {
    switch (position) {
      case 'G':
        return <Shield className="h-3 w-3" />
      case 'D':
        return <Shield className="h-3 w-3" />
      case 'M':
        return <Target className="h-3 w-3" />
      case 'F':
        return <Target className="h-3 w-3" />
      default:
        return <User className="h-3 w-3" />
    }
  }

  const PlayerCard = ({ player, isSubstitute = false }: { player: Player, isSubstitute?: boolean }) => (
    <div className={`
      relative p-2 rounded-lg border-2 text-center transition-all hover:scale-105 cursor-pointer
      ${getPositionColor(player.pos)}
      ${isSubstitute ? 'opacity-75 scale-90' : ''}
    `}>
      <div className="flex items-center justify-center gap-1 mb-1">
        {getPositionIcon(player.pos)}
        <Badge variant="outline" className="text-xs px-1 py-0">
          {player.number}
        </Badge>
      </div>
      <div className="text-xs font-medium leading-tight">
        {player.name.split(' ').slice(-1)[0]} {/* Show last name only */}
      </div>
      <div className="text-xs text-muted-foreground">
        {player.pos}
      </div>
    </div>
  )

  const FormationDisplay = ({ team, isHome = true }: { team: TeamLineup, isHome?: boolean }) => {
    // Parse formation (e.g., "4-3-3" -> [4, 3, 3])
    const formationLines = team.formation.split('-').map(Number)
    
    // Group players by position lines
    const goalkeeper = team.startXI.filter(p => p.player.pos === 'G')
    const defenders = team.startXI.filter(p => p.player.pos === 'D')
    const midfielders = team.startXI.filter(p => p.player.pos === 'M')
    const forwards = team.startXI.filter(p => p.player.pos === 'F')

    const lines = [
      { players: goalkeeper, label: 'Kaleci' },
      { players: defenders, label: 'Defans' },
      { players: midfielders, label: 'Orta Saha' },
      { players: forwards, label: 'Forvet' }
    ].filter(line => line.players.length > 0)

    return (
      <div className={`space-y-4 ${isHome ? '' : 'transform rotate-180'}`}>
        {lines.map((line, lineIndex) => (
          <div key={lineIndex} className="flex justify-center">
            <div className="grid gap-2" style={{ 
              gridTemplateColumns: `repeat(${line.players.length}, minmax(0, 1fr))`,
              maxWidth: '300px'
            }}>
              {line.players.map((playerData, playerIndex) => (
                <PlayerCard 
                  key={playerIndex} 
                  player={playerData.player}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    )
  }

  const TeamCard = ({ team, isHome = true }: { team: TeamLineup, isHome?: boolean }) => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Shirt className="h-5 w-5" />
          {team.team.name}
          <Badge variant="outline">{team.formation}</Badge>
        </CardTitle>
        <CardDescription>
          İlk 11 ve yedek oyuncular
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Formation Display */}
        <div className="bg-green-50 dark:bg-green-950/20 p-4 rounded-lg border-2 border-green-200 dark:border-green-800">
          <div className="text-center mb-4">
            <Badge variant="secondary" className="mb-2">
              Formation: {team.formation}
            </Badge>
          </div>
          <FormationDisplay team={team} isHome={isHome} />
        </div>

        {/* Coach */}
        <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
          <Crown className="h-5 w-5 text-amber-600" />
          <div>
            <div className="font-medium">Antrenör</div>
            <div className="text-sm text-muted-foreground">{team.coach.name}</div>
          </div>
        </div>

        {/* Substitutes */}
        {team.substitutes.length > 0 && (
          <div>
            <h4 className="font-semibold mb-3 flex items-center gap-2">
              <UserCheck className="h-4 w-4" />
              Yedek Oyuncular ({team.substitutes.length})
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {team.substitutes.map((playerData, index) => (
                <PlayerCard 
                  key={index} 
                  player={playerData.player} 
                  isSubstitute={true}
                />
              ))}
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
          <h2 className="text-2xl font-bold">Takım Kadroları</h2>
          <p className="text-muted-foreground">Formation ve oyuncu dizilişleri</p>
        </div>
        <div className="flex items-center gap-4">
          <Badge variant="outline" className="flex items-center gap-1">
            <Users className="h-3 w-3" />
            {homeTeam.startXI.length + awayTeam.startXI.length} oyuncu
          </Badge>
        </div>
      </div>

      {/* Formation Comparison */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Formation Karşılaştırması
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold text-blue-600">{homeTeam.formation}</div>
              <div className="text-sm text-muted-foreground">{homeTeam.team.name}</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-red-600">{awayTeam.formation}</div>
              <div className="text-sm text-muted-foreground">{awayTeam.team.name}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Team Lineups */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TeamCard team={homeTeam} isHome={true} />
        <TeamCard team={awayTeam} isHome={false} />
      </div>

      {/* Position Statistics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Pozisyon Dağılımı
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {['G', 'D', 'M', 'F'].map(position => {
              const homeCount = homeTeam.startXI.filter(p => p.player.pos === position).length
              const awayCount = awayTeam.startXI.filter(p => p.player.pos === position).length
              const positionName = {
                'G': 'Kaleci',
                'D': 'Defans',
                'M': 'Orta Saha',
                'F': 'Forvet'
              }[position]

              return (
                <div key={position} className="text-center p-4 bg-muted rounded-lg">
                  <div className="flex items-center justify-center mb-2">
                    {getPositionIcon(position)}
                  </div>
                  <div className="text-lg font-bold">
                    {homeCount} - {awayCount}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {positionName}
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
