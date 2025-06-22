'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { apiClient, queryKeys, type Fixture } from '@/lib/api/client'
import { getMatchStatusColor, getMatchStatusText, formatDate } from '@/lib/utils'
import { FixturesFilters, type FixturesFilters as FiltersType } from './fixtures-filters'
import { Calendar, Clock, MapPin, Users } from 'lucide-react'

export function FixturesList() {
  const [filters, setFilters] = useState<FiltersType>({})
  const [page, setPage] = useState(1)
  const perPage = 20

  // Build query parameters from filters
  const queryParams = {
    page,
    per_page: perPage,
    ...(filters.leagueId && { league_id: filters.leagueId }),
    ...(filters.status && { status: filters.status }),
    ...(filters.dateRange?.from && { 
      date_from: filters.dateRange.from.toISOString().split('T')[0] 
    }),
    ...(filters.dateRange?.to && { 
      date_to: filters.dateRange.to.toISOString().split('T')[0] 
    }),
    sort_by: 'date',
    sort_order: 'asc' as const,
  }

  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.fixtures.list(queryParams),
    queryFn: () => apiClient.getFixtures(queryParams),
    refetchInterval: 60000, // Refetch every minute
  })

  // Filter by search term on client side
  const filteredFixtures = data?.fixtures?.filter(fixture => {
    if (!filters.search) return true
    const searchTerm = filters.search.toLowerCase()
    return (
      fixture.home_team_name?.toLowerCase().includes(searchTerm) ||
      fixture.away_team_name?.toLowerCase().includes(searchTerm)
    )
  }) || []

  const handleFiltersChange = (newFilters: FiltersType) => {
    setFilters(newFilters)
    setPage(1) // Reset to first page when filters change
  }

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
      {/* Filters */}
      <FixturesFilters onFiltersChange={handleFiltersChange} />

      {/* Results Summary */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          {isLoading ? (
            <Skeleton className="h-4 w-32" />
          ) : (
            `Showing ${filteredFixtures.length} of ${data?.total || 0} fixtures`
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
        {isLoading ? (
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

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          {/* Match Info */}
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="outline" className="text-xs">
                {fixture.league_name || `League ${fixture.league_id}`}
              </Badge>
              <Badge 
                variant={isLive ? "destructive" : "secondary"}
                className={getMatchStatusColor(fixture.status_short)}
              >
                {getMatchStatusText(fixture.status_short)}
                {fixture.status_elapsed && ` ${fixture.status_elapsed}'`}
              </Badge>
            </div>

            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-medium">
                  {fixture.home_team_name || 'Home Team'}
                </span>
                {isFinished && (
                  <span className="font-bold text-lg">
                    {fixture.home_goals}
                  </span>
                )}
              </div>
              <div className="flex items-center justify-between">
                <span className="font-medium">
                  {fixture.away_team_name || 'Away Team'}
                </span>
                {isFinished && (
                  <span className="font-bold text-lg">
                    {fixture.away_goals}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Match Details */}
          <div className="text-right space-y-2 ml-4">
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              <Clock className="h-3 w-3" />
              {formatDate(fixture.date)}
            </div>
            {fixture.venue_name && (
              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                <MapPin className="h-3 w-3" />
                {fixture.venue_name}
              </div>
            )}
            {fixture.referee && (
              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                <Users className="h-3 w-3" />
                {fixture.referee}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
