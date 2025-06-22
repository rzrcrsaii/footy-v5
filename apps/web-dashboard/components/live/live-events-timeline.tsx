'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { apiClient, queryKeys, type LiveEvent } from '@/lib/api/client'
import { useWebSocket } from '@/lib/websocket/provider'
import { useEffect, useState } from 'react'
import { 
  Clock, 
  Goal, 
  AlertTriangle, 
  ArrowUpDown, 
  Square, 
  Play, 
  StopCircle,
  Users
} from 'lucide-react'

interface LiveEventsTimelineProps {
  fixtureId: number
}

export function LiveEventsTimeline({ fixtureId }: LiveEventsTimelineProps) {
  const [realtimeEvents, setRealtimeEvents] = useState<LiveEvent[]>([])
  const { lastMessage } = useWebSocket()

  const { data: events, isLoading } = useQuery({
    queryKey: queryKeys.live.events(fixtureId),
    queryFn: () => apiClient.getLiveEvents(fixtureId, { limit: 50 }),
    refetchInterval: 30000,
  })

  // Handle real-time event updates
  useEffect(() => {
    if (lastMessage && lastMessage.type === 'event_update' && lastMessage.fixture_id === fixtureId) {
      setRealtimeEvents(prev => {
        const newEvents = [...prev, lastMessage.data]
        return newEvents.slice(0, 50) // Keep only latest 50 events
      })
    }
  }, [lastMessage, fixtureId])

  // Combine API data with real-time updates
  const allEvents = [...(events || []), ...realtimeEvents]
    .sort((a, b) => {
      // Sort by match minute (descending - latest first)
      const aMinute = a.match_minute || 0
      const bMinute = b.match_minute || 0
      return bMinute - aMinute
    })

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Live Events</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex items-center gap-3">
                <Skeleton className="h-8 w-8 rounded-full" />
                <div className="space-y-1 flex-1">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
                </div>
                <Skeleton className="h-6 w-12" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (allEvents.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Live Events</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-8">
            <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No events recorded yet.</p>
            <p className="text-sm mt-2">Match events will appear here as they happen.</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Live Events
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {allEvents.map((event, index) => (
            <EventItem key={`${event.id}-${index}`} event={event} />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

interface EventItemProps {
  event: LiveEvent
}

function EventItem({ event }: EventItemProps) {
  const getEventIcon = (eventType: string) => {
    switch (eventType.toLowerCase()) {
      case 'goal':
        return <Goal className="h-5 w-5 text-green-600" />
      case 'card':
      case 'yellow card':
        return <Square className="h-5 w-5 text-yellow-500" />
      case 'red card':
        return <Square className="h-5 w-5 text-red-600" />
      case 'substitution':
        return <ArrowUpDown className="h-5 w-5 text-blue-600" />
      case 'match_start':
        return <Play className="h-5 w-5 text-green-600" />
      case 'match_end':
        return <StopCircle className="h-5 w-5 text-gray-600" />
      case 'var':
        return <AlertTriangle className="h-5 w-5 text-orange-600" />
      default:
        return <Clock className="h-5 w-5 text-muted-foreground" />
    }
  }

  const getEventColor = (eventType: string) => {
    switch (eventType.toLowerCase()) {
      case 'goal':
        return 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/10'
      case 'card':
      case 'yellow card':
        return 'border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-900/10'
      case 'red card':
        return 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/10'
      case 'substitution':
        return 'border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-900/10'
      default:
        return 'border-border bg-background'
    }
  }

  const formatEventText = (event: LiveEvent) => {
    let text = event.event_detail || event.event_type

    if (event.player_name) {
      text += ` - ${event.player_name}`
    }

    if (event.assist_player_name) {
      text += ` (Assist: ${event.assist_player_name})`
    }

    if (event.event_comments) {
      text += ` - ${event.event_comments}`
    }

    return text
  }

  return (
    <div className={`flex items-start gap-3 p-3 rounded-lg border ${getEventColor(event.event_type)}`}>
      {/* Event Icon */}
      <div className="flex-shrink-0 mt-1">
        {getEventIcon(event.event_type)}
      </div>

      {/* Event Details */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div className="space-y-1">
            <p className="font-medium text-sm">
              {formatEventText(event)}
            </p>
            
            {event.team_name && (
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Users className="h-3 w-3" />
                {event.team_name}
              </div>
            )}
            
            <p className="text-xs text-muted-foreground">
              {new Date(event.timestamp).toLocaleTimeString()}
            </p>
          </div>

          {/* Match Minute */}
          <Badge variant="outline" className="flex-shrink-0">
            {event.match_minute || 0}'
            {event.match_minute_extra && `+${event.match_minute_extra}`}
          </Badge>
        </div>
      </div>
    </div>
  )
}
