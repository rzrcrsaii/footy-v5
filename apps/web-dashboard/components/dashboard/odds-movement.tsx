'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { apiClient, queryKeys } from '@/lib/api/client'

interface OddsMovement {
  id: number
  fixture: string
  market: string
  value: string
  oldOdd: number
  newOdd: number
  change: number
}

export function OddsMovement() {
  // Get recent fixtures to simulate odds movements
  const { data: fixtures, isLoading } = useQuery({
    queryKey: queryKeys.fixtures.list({ league_id: 39, season_year: 2024, per_page: 5 }),
    queryFn: () => apiClient.getFixtures({ league_id: 39, season_year: 2024, per_page: 5 }),
    refetchInterval: 300000, // Refetch every 5 minutes
  })

  // Transform fixtures into odds movements (simulated for now)
  const movements: OddsMovement[] = fixtures?.fixtures?.slice(0, 3).map((fixture: any, index: number) => ({
    id: fixture.id || index + 1,
    fixture: `${fixture.home_team_name || 'Home'} vs ${fixture.away_team_name || 'Away'}`,
    market: index === 0 ? 'Match Winner' : index === 1 ? 'Over 2.5 Goals' : 'Both Teams to Score',
    value: index === 0 ? fixture.home_team_name || 'Home' : index === 1 ? 'Over' : 'Yes',
    oldOdd: 2.10 - (index * 0.15),
    newOdd: 1.95 - (index * 0.10),
    change: -0.15 + (index * 0.25),
  })) || []

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Odds Movement</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center justify-between p-2 rounded-lg">
                <div className="flex-1">
                  <div className="h-4 bg-muted rounded w-3/4 mb-1"></div>
                  <div className="h-3 bg-muted rounded w-1/2"></div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-4 bg-muted rounded w-12"></div>
                  <div className="h-4 bg-muted rounded w-8"></div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Odds Movement</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {movements.length > 0 ? movements.map((movement) => (
            <div key={movement.id} className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/50">
              <div className="flex-1">
                <p className="text-sm font-medium">{movement.fixture}</p>
                <p className="text-xs text-muted-foreground">
                  {movement.market} - {movement.value}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm">{movement.newOdd.toFixed(2)}</span>
                <div className={`flex items-center gap-1 ${
                  movement.change > 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {movement.change > 0 ? (
                    <TrendingUp className="h-3 w-3" />
                  ) : (
                    <TrendingDown className="h-3 w-3" />
                  )}
                  <span className="text-xs">
                    {movement.change > 0 ? '+' : ''}{movement.change.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          )) : (
            <div className="text-center py-4 text-muted-foreground">
              <p className="text-sm">No odds movements available</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
