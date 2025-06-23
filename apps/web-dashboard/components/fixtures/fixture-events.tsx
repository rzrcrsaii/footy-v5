"use client"

import React from 'react'
import { 
  Goal, 
  AlertTriangle, 
  ArrowUpDown, 
  Video,
  Clock,
  User,
  UserCheck,
  UserX,
  Zap,
  Target
} from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'

interface MatchEvent {
  time: {
    elapsed: number
    extra?: number
  }
  team: {
    id: number
    name: string
    logo?: string
  }
  player: {
    id: number
    name: string
  }
  assist?: {
    id: number
    name: string
  }
  type: string
  detail: string
  comments?: string
}

interface FixtureEventsProps {
  data: MatchEvent[]
}

export function FixtureEvents({ data }: FixtureEventsProps) {
  if (!data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Maç Olayları</CardTitle>
          <CardDescription>Bu maç için henüz olay verisi bulunmuyor.</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  // Sort events by time
  const sortedEvents = [...data].sort((a, b) => {
    const timeA = a.time.elapsed + (a.time.extra || 0)
    const timeB = b.time.elapsed + (b.time.extra || 0)
    return timeA - timeB
  })

  const getEventIcon = (type: string, detail: string) => {
    switch (type) {
      case 'Goal':
        return <Target className="h-4 w-4 text-green-600" />
      case 'Card':
        if (detail === 'Yellow Card') {
          return <AlertTriangle className="h-4 w-4 text-yellow-500" />
        } else if (detail === 'Red Card') {
          return <AlertTriangle className="h-4 w-4 text-red-600" />
        }
        return <AlertTriangle className="h-4 w-4 text-gray-500" />
      case 'subst':
        return <ArrowUpDown className="h-4 w-4 text-blue-600" />
      case 'Var':
        return <Video className="h-4 w-4 text-purple-600" />
      default:
        return <Zap className="h-4 w-4 text-gray-500" />
    }
  }

  const getEventColor = (type: string, detail: string) => {
    switch (type) {
      case 'Goal':
        return 'bg-green-100 border-green-200 dark:bg-green-950 dark:border-green-800'
      case 'Card':
        if (detail === 'Yellow Card') {
          return 'bg-yellow-100 border-yellow-200 dark:bg-yellow-950 dark:border-yellow-800'
        } else if (detail === 'Red Card') {
          return 'bg-red-100 border-red-200 dark:bg-red-950 dark:border-red-800'
        }
        return 'bg-gray-100 border-gray-200 dark:bg-gray-950 dark:border-gray-800'
      case 'subst':
        return 'bg-blue-100 border-blue-200 dark:bg-blue-950 dark:border-blue-800'
      case 'Var':
        return 'bg-purple-100 border-purple-200 dark:bg-purple-950 dark:border-purple-800'
      default:
        return 'bg-gray-100 border-gray-200 dark:bg-gray-950 dark:border-gray-800'
    }
  }

  const getEventBadgeVariant = (type: string, detail: string) => {
    switch (type) {
      case 'Goal':
        return 'default'
      case 'Card':
        if (detail === 'Yellow Card') return 'secondary'
        if (detail === 'Red Card') return 'destructive'
        return 'outline'
      case 'subst':
        return 'outline'
      case 'Var':
        return 'secondary'
      default:
        return 'outline'
    }
  }

  const formatEventTime = (elapsed: number, extra?: number) => {
    if (extra) {
      return `${elapsed}+${extra}'`
    }
    return `${elapsed}'`
  }

  const getEventDescription = (event: MatchEvent) => {
    switch (event.type) {
      case 'Goal':
        if (event.assist) {
          return `${event.player.name} (Asist: ${event.assist.name})`
        }
        return event.player.name
      case 'Card':
        return `${event.player.name} - ${event.detail}`
      case 'subst':
        return `${event.player.name} → ${event.assist?.name || 'Bilinmiyor'}`
      case 'Var':
        return `VAR - ${event.detail || 'İnceleme'}`
      default:
        return event.player.name
    }
  }

  // Group events by half
  const firstHalfEvents = sortedEvents.filter(event => event.time.elapsed <= 45)
  const secondHalfEvents = sortedEvents.filter(event => event.time.elapsed > 45 && event.time.elapsed <= 90)
  const extraTimeEvents = sortedEvents.filter(event => event.time.elapsed > 90)

  const EventGroup = ({ title, events, icon }: { 
    title: string
    events: MatchEvent[]
    icon: React.ReactNode 
  }) => {
    if (events.length === 0) return null

    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          {icon}
          <h3 className="font-semibold text-lg">{title}</h3>
          <Badge variant="outline">{events.length} olay</Badge>
        </div>
        
        <div className="space-y-3">
          {events.map((event, index) => (
            <div key={index} className={`p-4 rounded-lg border ${getEventColor(event.type, event.detail)}`}>
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className="flex items-center gap-2 mt-1">
                    {getEventIcon(event.type, event.detail)}
                    <Badge variant={getEventBadgeVariant(event.type, event.detail)} className="text-xs">
                      {formatEventTime(event.time.elapsed, event.time.extra)}
                    </Badge>
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-sm">{event.team.name}</span>
                      <Badge variant="outline" className="text-xs">
                        {event.type === 'Goal' ? '⚽' : 
                         event.type === 'Card' ? (event.detail === 'Yellow Card' ? '🟨' : '🟥') :
                         event.type === 'subst' ? '🔄' :
                         event.type === 'Var' ? '📺' : '⚡'}
                      </Badge>
                    </div>
                    
                    <p className="text-sm text-muted-foreground">
                      {getEventDescription(event)}
                    </p>
                    
                    {event.comments && (
                      <p className="text-xs text-muted-foreground mt-1 italic">
                        {event.comments}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Maç Olayları</h2>
          <p className="text-muted-foreground">Kronolojik olay zaman çizelgesi</p>
        </div>
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4" />
          <span className="text-sm font-medium">{sortedEvents.length} toplam olay</span>
        </div>
      </div>

      {/* Event Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <Target className="h-6 w-6 mx-auto mb-2 text-green-600" />
            <div className="text-2xl font-bold">
              {sortedEvents.filter(e => e.type === 'Goal').length}
            </div>
            <div className="text-xs text-muted-foreground">Gol</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <AlertTriangle className="h-6 w-6 mx-auto mb-2 text-yellow-500" />
            <div className="text-2xl font-bold">
              {sortedEvents.filter(e => e.type === 'Card').length}
            </div>
            <div className="text-xs text-muted-foreground">Kart</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <ArrowUpDown className="h-6 w-6 mx-auto mb-2 text-blue-600" />
            <div className="text-2xl font-bold">
              {sortedEvents.filter(e => e.type === 'subst').length}
            </div>
            <div className="text-xs text-muted-foreground">Değişiklik</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <Video className="h-6 w-6 mx-auto mb-2 text-purple-600" />
            <div className="text-2xl font-bold">
              {sortedEvents.filter(e => e.type === 'Var').length}
            </div>
            <div className="text-xs text-muted-foreground">VAR</div>
          </CardContent>
        </Card>
      </div>

      {/* Timeline */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Olay Zaman Çizelgesi
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-8">
          <EventGroup 
            title="İlk Yarı" 
            events={firstHalfEvents}
            icon={<div className="w-6 h-6 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center text-xs font-bold">1</div>}
          />
          
          {secondHalfEvents.length > 0 && (
            <>
              <Separator />
              <EventGroup 
                title="İkinci Yarı" 
                events={secondHalfEvents}
                icon={<div className="w-6 h-6 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center text-xs font-bold">2</div>}
              />
            </>
          )}
          
          {extraTimeEvents.length > 0 && (
            <>
              <Separator />
              <EventGroup 
                title="Uzatma Dakikaları" 
                events={extraTimeEvents}
                icon={<div className="w-6 h-6 bg-orange-100 dark:bg-orange-900 rounded-full flex items-center justify-center text-xs font-bold">+</div>}
              />
            </>
          )}
          
          {sortedEvents.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Henüz hiç olay kaydedilmemiş.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
