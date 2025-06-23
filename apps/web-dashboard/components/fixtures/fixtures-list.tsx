'use client'

import React, { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { apiClient, queryKeys, type Fixture } from '@/lib/api/client'
import { getMatchStatusColor, getMatchStatusText, formatDate } from '@/lib/utils'
import { type FixturesFilters as FiltersType } from './fixtures-filters'
import { Calendar, Clock, MapPin, Users, Eye } from 'lucide-react'

interface FixturesListProps {
  filters?: FiltersType
}

export function FixturesList({ filters = {} }: FixturesListProps) {
  const [page, setPage] = useState(1)
  const perPage = 20

  // Use today's live fixtures endpoint for better data
  const { data: todayLiveData, isLoading: isLoadingLive } = useQuery({
    queryKey: queryKeys.fixtures.todayLive(),
    queryFn: () => apiClient.getTodayLiveFixtures(),
    refetchInterval: 30000, // Refetch every 30 seconds for live data
  })

  // Get current date for O3's date-based approach
  const getCurrentDate = () => {
    const now = new Date()
    const dateStr = now.toISOString().split('T')[0] // YYYY-MM-DD format

    console.log('🗓️ Real Current Date:', now.toISOString())
    console.log('📅 Today Date String:', dateStr)

    return dateStr
  }

  const todayDate = getCurrentDate()
  console.log('📅 Using today date for API:', todayDate)

  // Build query parameters using O3's approach
  const queryParams = (() => {
    const params: any = {
      page,
      per_page: perPage,
      sort_by: 'date',
      sort_order: 'asc' as const,
    }

    // O3 Pattern 1: If user selected specific date range, use from/to
    if (filters.dateRange?.from && filters.dateRange?.to) {
      const fromDate = filters.dateRange.from.toISOString().split('T')[0]
      const toDate = filters.dateRange.to.toISOString().split('T')[0]

      // If same day, use single date parameter
      if (fromDate === toDate) {
        params.date = fromDate
        console.log('📅 Using single date:', fromDate)
      } else {
        params.from_date = fromDate
        params.to_date = toDate
        console.log('📅 Using date range:', fromDate, 'to', toDate)
      }
    } else {
      // Default: show today's matches
      params.date = todayDate
      console.log('📅 Using default today date:', todayDate)
    }

    // Add optional filters
    if (filters.leagueId) params.league_id = filters.leagueId
    if (filters.seasonYear) params.season_year = filters.seasonYear
    if (filters.status) params.status = filters.status

    return params
  })()

  const { data, isLoading, error } = useQuery({
    queryKey: ['fixtures-2025', queryParams], // Force new cache key for 2025
    queryFn: () => {
      console.log('🔍 API Query Params:', queryParams)
      console.log('🌐 API Base URL:', process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001')
      console.log('🏆 FRONTEND Season Year:', queryParams.season_year)
      return apiClient.getFixtures(queryParams)
    },
    refetchInterval: 60000, // Refetch every minute
    staleTime: 0, // Force fresh data
    cacheTime: 0, // Don't cache
    refetchOnMount: true, // Always refetch on mount
    refetchOnWindowFocus: true, // Refetch on window focus
  })

  // Combine today's live fixtures with regular fixtures
  const allFixtures = [
    ...(todayLiveData?.fixtures || []),
    ...(data?.fixtures || [])
  ]

  // Remove duplicates based on fixture ID
  const uniqueFixtures = allFixtures.filter((fixture, index, self) =>
    index === self.findIndex(f => f.id === fixture.id)
  )

  // Debug: Log the received data
  console.log('📊 Fixtures Data:', {
    today_live_count: todayLiveData?.fixtures?.length || 0,
    regular_fixtures_count: data?.fixtures?.length || 0,
    unique_fixtures_count: uniqueFixtures.length,
    first_live_fixture: todayLiveData?.fixtures?.[0] ? {
      id: todayLiveData.fixtures[0].id,
      date: todayLiveData.fixtures[0].date,
      home_team: todayLiveData.fixtures[0].home_team_name,
      away_team: todayLiveData.fixtures[0].away_team_name,
      status: todayLiveData.fixtures[0].status_short
    } : null
  })

  // Filter by search term on client side and sort intelligently
  const filteredFixtures = uniqueFixtures.filter(fixture => {
    if (!filters.search) return true
    const searchTerm = filters.search.toLowerCase()
    return (
      fixture.home_team_name?.toLowerCase().includes(searchTerm) ||
      fixture.away_team_name?.toLowerCase().includes(searchTerm)
    )
  }).sort((a, b) => {
    const dateA = new Date(a.date)
    const dateB = new Date(b.date)
    const today = new Date()

    // Check if matches are today (Turkey timezone)
    const isATodayTR = dateA.toLocaleDateString('tr-TR', { timeZone: 'Europe/Istanbul' }) ===
                      today.toLocaleDateString('tr-TR', { timeZone: 'Europe/Istanbul' })
    const isBTodayTR = dateB.toLocaleDateString('tr-TR', { timeZone: 'Europe/Istanbul' }) ===
                      today.toLocaleDateString('tr-TR', { timeZone: 'Europe/Istanbul' })

    // Today's matches first, then future matches
    if (isATodayTR && !isBTodayTR) return -1
    if (!isATodayTR && isBTodayTR) return 1

    // Within same day category, sort by time (oldest to newest)
    return dateA.getTime() - dateB.getTime()
  })

  // Reset page when filters change
  useEffect(() => {
    setPage(1)
  }, [filters])

  const isLoadingAny = isLoading || isLoadingLive

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-muted-foreground">
            <p>Error loading fixtures. Please try again later.</p>
            <Button 
              variant="outline" 
              className="mt-4"
              onClick={() => window.location.reload()}
            >
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Results Summary */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          {isLoadingAny ? (
            <Skeleton className="h-4 w-32" />
          ) : (
            <>
              <span>Showing {filteredFixtures.length} fixtures</span>
              {todayLiveData?.fixtures?.length > 0 && (
                <span className="ml-2 text-red-600 font-medium">
                  • {todayLiveData.fixtures.filter(f => ['1H', '2H', 'HT', 'ET', 'BT', 'P'].includes(f.status_short)).length} live now
                </span>
              )}
            </>
          )}
        </div>
        {data?.total_pages && data.total_pages > 1 && (
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
            >
              Previous
            </Button>
            <span className="text-sm text-muted-foreground">
              Page {page} of {data.total_pages}
            </span>
            <Button
              variant="outline"
              size="sm"
              disabled={page === data.total_pages}
              onClick={() => setPage(page + 1)}
            >
              Next
            </Button>
          </div>
        )}
      </div>

      {/* Fixtures Grid */}
      <div className="grid gap-4">
        {isLoadingAny ? (
          // Loading skeletons
          Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-6 w-48" />
                  </div>
                  <div className="text-right space-y-2">
                    <Skeleton className="h-4 w-16" />
                    <Skeleton className="h-6 w-12" />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : filteredFixtures.length === 0 ? (
          <Card>
            <CardContent className="p-6">
              <div className="text-center text-muted-foreground">
                <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No fixtures found matching your criteria.</p>
                <p className="text-sm mt-2">Try adjusting your filters or search terms.</p>
              </div>
            </CardContent>
          </Card>
        ) : (
          filteredFixtures.map((fixture) => (
            <FixtureCard key={fixture.id} fixture={fixture} />
          ))
        )}
      </div>
    </div>
  )
}

interface FixtureCardProps {
  fixture: Fixture
}

function FixtureCard({ fixture }: FixtureCardProps) {
  const isLive = ['1H', '2H', 'HT', 'ET', 'BT', 'P'].includes(fixture.status_short)
  const isFinished = ['FT', 'AET', 'PEN'].includes(fixture.status_short)
  const isUpcoming = ['NS', 'TBD'].includes(fixture.status_short)

  // Format time from date string (Turkey timezone)
  const formatMatchTime = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleTimeString('tr-TR', {
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'Europe/Istanbul'
      })
    } catch {
      return '--:--'
    }
  }

  // Format date for Turkey timezone
  const formatMatchDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('tr-TR', {
        day: '2-digit',
        month: '2-digit',
        timeZone: 'Europe/Istanbul'
      })
    } catch {
      return '--/--'
    }
  }

  // Format venue name (truncate if too long)
  const formatVenue = (venue: string | undefined) => {
    if (!venue) return ''
    return venue.length > 15 ? `${venue.substring(0, 15)}...` : venue
  }

  // Check if match is today (Turkey timezone)
  const isToday = (() => {
    try {
      const matchDate = new Date(fixture.date)
      const today = new Date()

      // Convert both dates to Turkey timezone for comparison
      const matchDateTR = matchDate.toLocaleDateString('tr-TR', { timeZone: 'Europe/Istanbul' })
      const todayTR = today.toLocaleDateString('tr-TR', { timeZone: 'Europe/Istanbul' })

      return matchDateTR === todayTR
    } catch {
      return false
    }
  })()

  return (
    <Card className={`hover:shadow-md transition-shadow ${isToday ? 'ring-2 ring-primary/20 bg-primary/5' : ''}`}>
      <CardContent className="p-3">
        <div className="flex items-center gap-2 sm:gap-4">
          {/* Time & Date */}
          <div className="flex flex-col items-center min-w-[60px] sm:min-w-[70px]">
            <div className="text-xs sm:text-sm font-medium">
              {formatMatchTime(fixture.date)}
            </div>
            <div className="text-xs text-muted-foreground">
              {formatMatchDate(fixture.date)}
            </div>
            {isToday && (
              <div className="text-xs font-medium text-primary">
                Bugün
              </div>
            )}
          </div>

          {/* Home Team */}
          <div className="flex items-center gap-1 sm:gap-2 flex-1 min-w-0">
            <div className="w-6 h-6 sm:w-7 sm:h-7 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-xs font-bold text-white shadow-sm">
              {fixture.home_team_name?.charAt(0) || 'H'}
            </div>
            <span className="font-medium truncate text-sm sm:text-base">
              {fixture.home_team_name || 'Home Team'}
            </span>
          </div>

          {/* Score */}
          <div className="flex items-center gap-1 sm:gap-2 min-w-[60px] sm:min-w-[80px] justify-center">
            {isFinished ? (
              <div className="flex items-center gap-1 font-bold text-base sm:text-lg">
                <span>{fixture.home_goals}</span>
                <span className="text-muted-foreground">-</span>
                <span>{fixture.away_goals}</span>
              </div>
            ) : isLive ? (
              <div className="flex flex-col items-center">
                <div className="flex items-center gap-1 font-bold text-sm sm:text-base">
                  <span>{fixture.home_goals}</span>
                  <span className="text-muted-foreground">-</span>
                  <span>{fixture.away_goals}</span>
                </div>
                <div className="text-xs text-red-600 font-medium">
                  {fixture.status_elapsed}'
                </div>
              </div>
            ) : (
              <div className="text-xs sm:text-sm text-muted-foreground">
                vs
              </div>
            )}
          </div>

          {/* Away Team */}
          <div className="flex items-center gap-1 sm:gap-2 flex-1 min-w-0">
            <div className="w-6 h-6 sm:w-7 sm:h-7 bg-gradient-to-br from-red-500 to-red-600 rounded-full flex items-center justify-center text-xs font-bold text-white shadow-sm">
              {fixture.away_team_name?.charAt(0) || 'A'}
            </div>
            <span className="font-medium truncate text-sm sm:text-base">
              {fixture.away_team_name || 'Away Team'}
            </span>
          </div>

          {/* Venue & Status */}
          <div className="flex flex-col items-end gap-1 min-w-[80px] sm:min-w-[120px]">
            <div className="flex items-center gap-2">
              <Badge
                variant={isLive ? "destructive" : isFinished ? "secondary" : "outline"}
                className={`text-xs ${isLive ? 'animate-pulse' : ''}`}
              >
                {isLive && '🔴 '}
                {getMatchStatusText(fixture.status_short)}
              </Badge>
            </div>
            {fixture.venue_name && (
              <div className="hidden sm:flex items-center gap-1 text-xs text-muted-foreground">
                <MapPin className="h-3 w-3" />
                <span>{formatVenue(fixture.venue_name)}</span>
              </div>
            )}
          </div>

          {/* View Details Button */}
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 sm:h-8 sm:w-8 p-0 shrink-0 hover:bg-primary/10 hover:text-primary"
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              // Navigate to fixture detail page
              window.open(`/fixtures/${fixture.id}`, '_blank')
            }}
          >
            <Eye className="h-3 w-3 sm:h-4 sm:w-4" />
          </Button>
        </div>

        {/* League info - shown on mobile/small screens */}
        <div className="mt-2 sm:hidden">
          <Badge variant="outline" className="text-xs">
            {fixture.league_name || `League ${fixture.league_id}`}
          </Badge>
        </div>
      </CardContent>
    </Card>
  )
}
