'use client'

import { useParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
// import { Separator } from '@/components/ui/separator' // Temporarily removed
import { apiClient, queryKeys, type Fixture } from '@/lib/api/client'
import { getMatchStatusColor, getMatchStatusText, formatDate } from '@/lib/utils'
import { FixtureDetailTabs } from '@/components/fixtures/fixture-detail-tabs'
import {
  ArrowLeft,
  Calendar,
  Clock,
  MapPin,
  Users,
  User, // Whistle yerine User kullanacağız
  Trophy,
  Timer,
  Target
} from 'lucide-react'
import Link from 'next/link'

export default function FixtureDetailPage() {
  const params = useParams()
  const fixtureId = parseInt(params.id as string)

  const { data: fixture, isLoading, error } = useQuery({
    queryKey: queryKeys.fixture(fixtureId),
    queryFn: () => apiClient.getFixture(fixtureId),
    enabled: !!fixtureId && !isNaN(fixtureId),
  })

  if (isLoading) {
    return <FixtureDetailSkeleton />
  }

  if (error || !fixture) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card>
          <CardContent className="p-6">
            <div className="text-center text-muted-foreground">
              <p>Maç detayları yüklenemedi. Lütfen tekrar deneyin.</p>
              <Link href="/fixtures">
                <Button variant="outline" className="mt-4">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Fixture Listesine Dön
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const isLive = ['1H', '2H', 'HT', 'ET', 'BT', 'P'].includes(fixture.status_short)
  const isFinished = ['FT', 'AET', 'PEN'].includes(fixture.status_short)
  const isUpcoming = ['NS', 'TBD'].includes(fixture.status_short)

  return (
    <div className="container mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/fixtures">
          <Button variant="outline" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Geri
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold">Maç Detayları</h1>
          <p className="text-muted-foreground">
            {fixture.league_name} - {fixture.round}
          </p>
        </div>
      </div>

      {/* Main Match Card */}
      <Card className="overflow-hidden">
        <CardHeader className="bg-gradient-to-r from-blue-50 to-red-50 dark:from-blue-950/20 dark:to-red-950/20">
          <div className="flex items-center justify-between">
            <Badge variant={isLive ? "destructive" : isFinished ? "secondary" : "outline"}>
              {isLive && '🔴 '}
              {getMatchStatusText(fixture.status_short)}
              {isLive && fixture.status_elapsed && ` - ${fixture.status_elapsed}'`}
            </Badge>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar className="h-4 w-4" />
              {formatDate(fixture.date)}
              <Clock className="h-4 w-4 ml-2" />
              {new Date(fixture.date).toLocaleTimeString('tr-TR', {
                hour: '2-digit',
                minute: '2-digit',
                timeZone: 'Europe/Istanbul'
              })}
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="p-8">
          {/* Teams and Score */}
          <div className="grid grid-cols-3 gap-8 items-center">
            {/* Home Team */}
            <div className="text-center space-y-4">
              <div className="w-20 h-20 mx-auto bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-2xl font-bold text-white shadow-lg">
                {fixture.home_team_name?.charAt(0) || 'H'}
              </div>
              <div>
                <h2 className="text-xl font-bold">{fixture.home_team_name}</h2>
                <p className="text-sm text-muted-foreground">Ev Sahibi</p>
              </div>
            </div>

            {/* Score */}
            <div className="text-center space-y-2">
              {isFinished || isLive ? (
                <div className="text-6xl font-bold">
                  {fixture.home_goals} - {fixture.away_goals}
                </div>
              ) : (
                <div className="text-4xl font-bold text-muted-foreground">
                  VS
                </div>
              )}
              
              {/* Half Time Score */}
              {(isFinished || isLive) && (fixture.home_goals_ht > 0 || fixture.away_goals_ht > 0) && (
                <div className="text-sm text-muted-foreground">
                  İlk Yarı: {fixture.home_goals_ht} - {fixture.away_goals_ht}
                </div>
              )}
              
              {/* Extra Time Score */}
              {isFinished && (fixture.home_goals_et > 0 || fixture.away_goals_et > 0) && (
                <div className="text-sm text-muted-foreground">
                  Uzatma: {fixture.home_goals_et} - {fixture.away_goals_et}
                </div>
              )}
              
              {/* Penalty Score */}
              {isFinished && (fixture.home_goals_pen > 0 || fixture.away_goals_pen > 0) && (
                <div className="text-sm text-muted-foreground">
                  Penaltı: {fixture.home_goals_pen} - {fixture.away_goals_pen}
                </div>
              )}
            </div>

            {/* Away Team */}
            <div className="text-center space-y-4">
              <div className="w-20 h-20 mx-auto bg-gradient-to-br from-red-500 to-red-600 rounded-full flex items-center justify-center text-2xl font-bold text-white shadow-lg">
                {fixture.away_team_name?.charAt(0) || 'A'}
              </div>
              <div>
                <h2 className="text-xl font-bold">{fixture.away_team_name}</h2>
                <p className="text-sm text-muted-foreground">Deplasman</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Match Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Match Details */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trophy className="h-5 w-5" />
              Maç Bilgileri
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Lig</span>
              <span className="font-medium">{fixture.league_name}</span>
            </div>
            <div className="h-px bg-border w-full" />
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Sezon</span>
              <span className="font-medium">{fixture.season_year}</span>
            </div>
            <div className="h-px bg-border w-full" />
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Hafta</span>
              <span className="font-medium">{fixture.round || 'Belirtilmemiş'}</span>
            </div>
            {fixture.referee && (
              <>
                <div className="h-px bg-border w-full" />
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground flex items-center gap-2">
                    <User className="h-4 w-4" />
                    Hakem
                  </span>
                  <span className="font-medium">{fixture.referee}</span>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Venue Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="h-5 w-5" />
              Stadyum Bilgileri
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {fixture.venue_name ? (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Stadyum</span>
                  <span className="font-medium">{fixture.venue_name}</span>
                </div>
                {fixture.venue_city && (
                  <>
                    <div className="h-px bg-border w-full" />
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">Şehir</span>
                      <span className="font-medium">{fixture.venue_city}</span>
                    </div>
                  </>
                )}
              </>
            ) : (
              <div className="text-center text-muted-foreground py-4">
                Stadyum bilgisi mevcut değil
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Live Updates */}
      {isLive && (
        <Card className="border-red-200 bg-red-50/50 dark:border-red-800 dark:bg-red-950/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600 dark:text-red-400">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
              Canlı Maç
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Timer className="h-4 w-4" />
                <span className="font-medium">{fixture.status_elapsed}'</span>
              </div>
              {fixture.status_extra && (
                <div className="flex items-center gap-2">
                  <Target className="h-4 w-4" />
                  <span className="font-medium">+{fixture.status_extra}'</span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Fixture Detail Tabs */}
      <FixtureDetailTabs fixture={fixture} />
    </div>
  )
}

function FixtureDetailSkeleton() {
  return (
    <div className="container mx-auto px-4 py-8 space-y-6">
      <div className="flex items-center gap-4">
        <Skeleton className="h-9 w-20" />
        <div className="space-y-2">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-32" />
        </div>
      </div>
      
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <Skeleton className="h-6 w-24" />
            <Skeleton className="h-4 w-32" />
          </div>
        </CardHeader>
        <CardContent className="p-8">
          <div className="grid grid-cols-3 gap-8 items-center">
            <div className="text-center space-y-4">
              <Skeleton className="w-20 h-20 rounded-full mx-auto" />
              <Skeleton className="h-6 w-32 mx-auto" />
            </div>
            <div className="text-center">
              <Skeleton className="h-16 w-32 mx-auto" />
            </div>
            <div className="text-center space-y-4">
              <Skeleton className="w-20 h-20 rounded-full mx-auto" />
              <Skeleton className="h-6 w-32 mx-auto" />
            </div>
          </div>
        </CardContent>
      </Card>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32" />
          </CardHeader>
          <CardContent className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex items-center justify-between">
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-4 w-24" />
              </div>
            ))}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32" />
          </CardHeader>
          <CardContent className="space-y-4">
            {[1, 2].map((i) => (
              <div key={i} className="flex items-center justify-between">
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-4 w-24" />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
