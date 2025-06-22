'use client'

import { Calendar, Filter, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function FixturesHeader() {
  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Fixtures</h1>
        <p className="text-muted-foreground">
          Browse and filter football fixtures by date, league, and teams
        </p>
      </div>
      
      <div className="flex items-center gap-2">
        <Button variant="outline" size="sm">
          <Calendar className="h-4 w-4 mr-2" />
          Today
        </Button>
        <Button variant="outline" size="sm">
          <Filter className="h-4 w-4 mr-2" />
          Filter
        </Button>
        <Button variant="outline" size="sm">
          <Search className="h-4 w-4 mr-2" />
          Search
        </Button>
      </div>
    </div>
  )
}
