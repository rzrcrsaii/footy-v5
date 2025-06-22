'use client'

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { DatePickerWithRange } from '@/components/ui/date-range-picker'
import { Badge } from '@/components/ui/badge'
import { CalendarDays, Trophy, BarChart3, Filter } from 'lucide-react'

interface AnalyticsFiltersProps {
  onFiltersChange?: (filters: AnalyticsFilters) => void
}

export interface AnalyticsFilters {
  dateRange?: {
    from: Date
    to: Date
  }
  leagueId?: number
  metricType?: string
  timeframe?: string
}

export function AnalyticsFilters({ onFiltersChange }: AnalyticsFiltersProps) {
  const [filters, setFilters] = useState<AnalyticsFilters>({
    timeframe: '30d',
    metricType: 'goals'
  })
  const [isExpanded, setIsExpanded] = useState(false)

  const handleFilterChange = (key: keyof AnalyticsFilters, value: any) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
    onFiltersChange?.(newFilters)
  }

  const clearFilters = () => {
    const defaultFilters = { timeframe: '30d', metricType: 'goals' }
    setFilters(defaultFilters)
    onFiltersChange?.(defaultFilters)
  }

  const activeFiltersCount = Object.values(filters).filter(Boolean).length

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4" />
            <h3 className="font-medium">Analytics Filters</h3>
            {activeFiltersCount > 0 && (
              <Badge variant="secondary">{activeFiltersCount} active</Badge>
            )}
          </div>
          <div className="flex items-center gap-2">
            {activeFiltersCount > 2 && (
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                Clear all
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? 'Hide' : 'Show'} filters
            </Button>
          </div>
        </div>

        {/* Always visible quick filters */}
        <div className="grid gap-4 md:grid-cols-3 mb-4">
          {/* Timeframe */}
          <div className="space-y-2">
            <Label>Timeframe</Label>
            <Select
              value={filters.timeframe}
              onValueChange={(value) => handleFilterChange('timeframe', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select timeframe" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7d">Last 7 Days</SelectItem>
                <SelectItem value="30d">Last 30 Days</SelectItem>
                <SelectItem value="90d">Last 3 Months</SelectItem>
                <SelectItem value="1y">Last Year</SelectItem>
                <SelectItem value="custom">Custom Range</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Metric Type */}
          <div className="space-y-2">
            <Label className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Metric Type
            </Label>
            <Select
              value={filters.metricType}
              onValueChange={(value) => handleFilterChange('metricType', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select metric" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="goals">Goals & Scoring</SelectItem>
                <SelectItem value="possession">Ball Possession</SelectItem>
                <SelectItem value="shots">Shots & Accuracy</SelectItem>
                <SelectItem value="cards">Cards & Fouls</SelectItem>
                <SelectItem value="odds">Odds Movement</SelectItem>
                <SelectItem value="performance">Team Performance</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* League */}
          <div className="space-y-2">
            <Label className="flex items-center gap-2">
              <Trophy className="h-4 w-4" />
              League
            </Label>
            <Select
              value={filters.leagueId?.toString()}
              onValueChange={(value) => 
                handleFilterChange('leagueId', value ? parseInt(value) : undefined)
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="All leagues" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="39">Premier League</SelectItem>
                <SelectItem value="140">La Liga</SelectItem>
                <SelectItem value="78">Bundesliga</SelectItem>
                <SelectItem value="135">Serie A</SelectItem>
                <SelectItem value="61">Ligue 1</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Expanded filters */}
        {isExpanded && (
          <div className="border-t pt-4">
            <div className="grid gap-4 md:grid-cols-2">
              {/* Custom Date Range */}
              {filters.timeframe === 'custom' && (
                <div className="space-y-2 md:col-span-2">
                  <Label className="flex items-center gap-2">
                    <CalendarDays className="h-4 w-4" />
                    Custom Date Range
                  </Label>
                  <DatePickerWithRange
                    value={filters.dateRange}
                    onChange={(dateRange) => handleFilterChange('dateRange', dateRange)}
                  />
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
