'use client'

import { useState, useEffect } from 'react'
import { Clock, Calendar } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { dateNowISO, formatToTurkeyTime, debugCurrentTime } from '@/lib/utils/dateNow'

interface LiveClockProps {
  timezone?: string
  showDate?: boolean
  showSeconds?: boolean
  compact?: boolean
  className?: string
}

export function LiveClock({
  timezone = 'Europe/Istanbul',
  showDate = true,
  showSeconds = true,
  compact = false,
  className = ''
}: LiveClockProps) {
  const [currentTime, setCurrentTime] = useState<Date>(new Date())

  useEffect(() => {
    const timer = setInterval(() => {
      try {
        setCurrentTime(new Date())
      } catch (error) {
        console.error('Error updating time:', error)
      }
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  const formatTime = (date: Date) => {
    try {
      return date.toLocaleTimeString('tr-TR', {
        timeZone: timezone,
        hour: '2-digit',
        minute: '2-digit',
        ...(showSeconds && { second: '2-digit' }),
        hour12: false
      })
    } catch (error) {
      console.error('Error formatting time:', error)
      return '--:--'
    }
  }

  const formatDate = (date: Date) => {
    try {
      return date.toLocaleDateString('tr-TR', {
        timeZone: timezone,
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    } catch (error) {
      console.error('Error formatting date:', error)
      return 'Tarih bilinmiyor'
    }
  }

  const formatShortDate = (date: Date) => {
    try {
      return date.toLocaleDateString('tr-TR', {
        timeZone: timezone,
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      })
    } catch (error) {
      console.error('Error formatting short date:', error)
      return '--/--/----'
    }
  }

  const getUTCTime = (date: Date) => {
    try {
      return date.toISOString().split('T')[1].split('.')[0]
    } catch (error) {
      console.error('Error getting UTC time:', error)
      return '--:--:--'
    }
  }

  if (compact) {
    return (
      <div className={`flex items-center gap-2 text-sm text-muted-foreground ${className}`}>
        <Clock className="h-4 w-4" />
        <span className="font-mono">{formatTime(currentTime)}</span>
        {showDate && (
          <>
            <Calendar className="h-4 w-4 ml-2" />
            <span>{formatShortDate(currentTime)}</span>
          </>
        )}
      </div>
    )
  }

  return (
    <Card className={`${className}`}>
      <CardContent className="p-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-primary" />
            <div className="flex flex-col">
              <div className="text-2xl font-mono font-bold text-primary">
                {formatTime(currentTime)}
              </div>
              <div className="text-xs text-muted-foreground">
                Turkey Time (GMT+3) • UTC: {getUTCTime(currentTime)}
              </div>
            </div>
          </div>

          {showDate && (
            <div className="flex items-center gap-2 ml-4">
              <Calendar className="h-5 w-5 text-muted-foreground" />
              <div className="flex flex-col">
                <div className="text-sm font-medium">
                  {formatDate(currentTime)}
                </div>
                <div className="text-xs text-muted-foreground">
                  {formatShortDate(currentTime)}
                </div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

// Safe header clock with date - no layout impact, no hydration issues
export function HeaderClock({ className = '' }: { className?: string }) {
  const [currentTime, setCurrentTime] = useState<Date | null>(null)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    setCurrentTime(new Date())

    const timer = setInterval(() => {
      try {
        setCurrentTime(new Date())
      } catch (error) {
        console.error('Header clock error:', error)
      }
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  const formatTime = () => {
    if (!currentTime) return '--:--'
    try {
      return currentTime.toLocaleTimeString('tr-TR', {
        timeZone: 'Europe/Istanbul',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      })
    } catch {
      return '--:--'
    }
  }

  const formatDate = () => {
    if (!currentTime) return '--/--'
    try {
      return currentTime.toLocaleDateString('tr-TR', {
        timeZone: 'Europe/Istanbul',
        day: '2-digit',
        month: '2-digit'
      })
    } catch {
      return '--/--'
    }
  }

  // Prevent hydration mismatch by not rendering until mounted
  if (!mounted) {
    return (
      <div className={`flex items-center gap-2 text-sm text-muted-foreground ${className}`}>
        <Clock className="h-4 w-4" />
        <span className="font-mono">--:--</span>
        <Calendar className="h-4 w-4" />
        <span className="font-mono">--/--</span>
      </div>
    )
  }

  return (
    <div className={`flex items-center gap-2 text-sm text-muted-foreground ${className}`}>
      <Clock className="h-4 w-4" />
      <span className="font-mono">{formatTime()}</span>
      <Calendar className="h-4 w-4" />
      <span className="font-mono">{formatDate()}</span>
    </div>
  )
}

// Full version for dashboard
export function DashboardClock({ className = '' }: { className?: string }) {
  return (
    <LiveClock 
      showDate 
      showSeconds 
      className={className}
    />
  )
}
