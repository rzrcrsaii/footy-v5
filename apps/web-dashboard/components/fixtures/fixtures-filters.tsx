'use client'

import { useState } from 'react'
import { CalendarDays, Trophy, Users, Search } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { DatePickerWithRange } from '@/components/ui/date-range-picker'
import { Badge } from '@/components/ui/badge'

interface FixturesFiltersProps {
  onFiltersChange?: (filters: FixturesFilters) => void
}

export interface FixturesFilters {
  dateRange?: {
    from: Date
    to: Date
  }
  leagueId?: number
  teamId?: number
  status?: string
  search?: string
}

export function FixturesFilters({ onFiltersChange }: FixturesFiltersProps) {
  const [filters, setFilters] = useState<FixturesFilters>({})
  const [isExpanded, setIsExpanded] = useState(false)

  const handleFilterChange = (key: keyof FixturesFilters, value: any) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
    onFiltersChange?.(newFilters)
  }

  const clearFilters = () => {
    setFilters({})
    onFiltersChange?.({})
  }

  const activeFiltersCount = Object.values(filters).filter(Boolean).length

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <h3 className="font-medium">Filters</h3>
            {activeFiltersCount > 0 && (
              <Badge variant="secondary">{activeFiltersCount} active</Badge>
            )}
          </div>
          <div className="flex items-center gap-2">
            {activeFiltersCount > 0 && (
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

        {isExpanded && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {/* Date Range */}
            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                <CalendarDays className="h-4 w-4" />
                Date Range
              </Label>
              <DatePickerWithRange
                value={filters.dateRange}
                onChange={(dateRange) => handleFilterChange('dateRange', dateRange)}
              />
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
                  <SelectValue placeholder="Select league" />
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

            {/* Status */}
            <div className="space-y-2">
              <Label>Status</Label>
              <Select
                value={filters.status}
                onValueChange={(value) => handleFilterChange('status', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="NS">Not Started</SelectItem>
                  <SelectItem value="1H">First Half</SelectItem>
                  <SelectItem value="2H">Second Half</SelectItem>
                  <SelectItem value="HT">Half Time</SelectItem>
                  <SelectItem value="FT">Full Time</SelectItem>
                  <SelectItem value="PST">Postponed</SelectItem>
                  <SelectItem value="CANC">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Search */}
            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                <Search className="h-4 w-4" />
                Search Teams
              </Label>
              <Input
                placeholder="Team name..."
                value={filters.search || ''}
                onChange={(e) => handleFilterChange('search', e.target.value)}
              />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
