'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { formatTime } from '@/lib/utils'
import { apiClient, queryKeys } from '@/lib/api/client'
import { useWebSocket } from '@/lib/websocket/provider'
import { useEffect, useState } from 'react'

interface Activity {
  id: number
  type: 'goal' | 'card' | 'odds' | 'substitution' | 'match_start' | 'match_end'
  message: string
  fixture: string
  time: string
}

export function RecentActivity() {
  const [activities, setActivities] = useState<Activity[]>([])
  const { lastMessage } = useWebSocket()

  // Get recent fixtures to generate activities
  const { data: fixtures } = useQuery({
    queryKey: queryKeys.fixtures.list({ league_id: 39, season_year: 2024, per_page: 10 }),
    queryFn: () => apiClient.getFixtures({ league_id: 39, season_year: 2024, per_page: 10 }),
    refetchInterval: 300000,
  })

  // Generate activities from fixtures
  useEffect(() => {
    if (fixtures?.fixtures) {
      const newActivities: Activity[] = fixtures.fixtures.slice(0, 5).map((fixture: any, index: number) => {
        const activityTypes: Activity['type'][] = ['goal', 'card', 'odds', 'substitution', 'match_start']
        const type = activityTypes[index % activityTypes.length]

        let message = ''
        switch (type) {
          case 'goal':
            message = `Goal scored in ${fixture.home_team_name || 'Home'} vs ${fixture.away_team_name || 'Away'}`
            break
          case 'card':
            message = `Card issued in ${fixture.home_team_name || 'Home'} vs ${fixture.away_team_name || 'Away'}`
            break
          case 'odds':
            message = `Odds movement detected`
            break
          case 'substitution':
            message = `Substitution made`
            break
          case 'match_start':
            message = `Match started`
            break
        }

        return {
          id: fixture.id || index + 1,
          type,
          message,
          fixture: `${fixture.home_team_name || 'Home'} vs ${fixture.away_team_name || 'Away'}`,
          time: fixture.date || new Date(Date.now() - index * 300000).toISOString(),
        }
      })
      setActivities(newActivities)
    }
  }, [fixtures])

  // Handle WebSocket messages for real-time updates
  useEffect(() => {
    if (lastMessage && lastMessage.type === 'live_events' && lastMessage.data) {
      const newActivity: Activity = {
        id: Date.now(),
        type: 'goal', // Simplified for now
        message: `Live event: ${lastMessage.data.type || 'Unknown event'}`,
        fixture: `Fixture ${lastMessage.fixture_id}`,
        time: lastMessage.timestamp,
      }
      setActivities(prev => [newActivity, ...prev.slice(0, 4)])
    }
  }, [lastMessage])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {activities.length > 0 ? activities.map((activity) => (
            <div key={activity.id} className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted/50">
              <Badge variant="outline" className="text-xs">
                {activity.type}
              </Badge>
              <div className="flex-1">
                <p className="text-sm font-medium">{activity.message}</p>
                <p className="text-xs text-muted-foreground">{activity.fixture}</p>
              </div>
              <span className="text-xs text-muted-foreground">
                {formatTime(activity.time)}
              </span>
            </div>
          )) : (
            <div className="text-center py-4 text-muted-foreground">
              <p className="text-sm">No recent activity</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
