'use client'

import { BarChart3, Download, RefreshCw, Calendar } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

export function AnalyticsHeader() {
  const handleExport = () => {
    // TODO: Implement export functionality
    console.log('Export analytics data')
  }

  const handleRefresh = () => {
    // TODO: Implement refresh functionality
    window.location.reload()
  }

  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <BarChart3 className="h-8 w-8 text-blue-500" />
          Analytics
        </h1>
        <p className="text-muted-foreground">
          Comprehensive football data analysis, trends, and performance insights
        </p>
      </div>
      
      <div className="flex items-center gap-4">
        {/* Data Period */}
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-muted-foreground" />
          <Badge variant="outline">
            Last 30 Days
          </Badge>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleRefresh}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>
    </div>
  )
}
