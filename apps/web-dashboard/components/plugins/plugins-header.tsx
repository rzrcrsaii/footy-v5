'use client'

import { Puzzle, Plus, RefreshCw, Code } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

export function PluginsHeader() {
  const handleAddPlugin = () => {
    // TODO: Implement add plugin functionality
    console.log('Add new plugin')
  }

  const handleRefresh = () => {
    // TODO: Implement refresh functionality
    window.location.reload()
  }

  const handleViewTemplate = () => {
    // TODO: Implement view template functionality
    console.log('View template wrapper')
  }

  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <Puzzle className="h-8 w-8 text-purple-500" />
          Plugins
        </h1>
        <p className="text-muted-foreground">
          Manage API wrapper plugins and external integrations
        </p>
      </div>
      
      <div className="flex items-center gap-4">
        {/* Status Badge */}
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-green-600 border-green-600">
            System Active
          </Badge>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleViewTemplate}>
            <Code className="h-4 w-4 mr-2" />
            Template
          </Button>
          <Button variant="outline" size="sm" onClick={handleRefresh}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button size="sm" onClick={handleAddPlugin}>
            <Plus className="h-4 w-4 mr-2" />
            Add Plugin
          </Button>
        </div>
      </div>
    </div>
  )
}
