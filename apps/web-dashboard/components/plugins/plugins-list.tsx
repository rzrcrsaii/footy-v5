'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Play, 
  Square, 
  Settings, 
  Code,
  Search,
  ExternalLink
} from 'lucide-react'

interface Plugin {
  id: string
  name: string
  description: string
  status: 'active' | 'inactive' | 'error'
  version: string
  endpoint: string
  lastUpdated: string
  requestCount: number
  responseTime: number
  errorRate: number
}

export function PluginsList() {
  const [searchTerm, setSearchTerm] = useState('')
  
  // Mock plugins data
  const plugins: Plugin[] = [
    {
      id: 'api-football',
      name: 'API-Football',
      description: 'Primary football data provider with fixtures, teams, and statistics',
      status: 'active',
      version: '1.2.0',
      endpoint: '/api/v1/football',
      lastUpdated: '2024-01-15T10:30:00Z',
      requestCount: 8420,
      responseTime: 180,
      errorRate: 0.2
    },
    {
      id: 'odds-api',
      name: 'Odds API',
      description: 'Real-time betting odds from multiple bookmakers',
      status: 'active',
      version: '1.1.5',
      endpoint: '/api/v1/odds',
      lastUpdated: '2024-01-15T09:15:00Z',
      requestCount: 3240,
      responseTime: 220,
      errorRate: 0.5
    },
    {
      id: 'news-api',
      name: 'Football News API',
      description: 'Latest football news and updates from various sources',
      status: 'active',
      version: '1.0.8',
      endpoint: '/api/v1/news',
      lastUpdated: '2024-01-15T08:45:00Z',
      requestCount: 1560,
      responseTime: 340,
      errorRate: 1.2
    },
    {
      id: 'weather-api',
      name: 'Weather API',
      description: 'Weather conditions for match venues',
      status: 'inactive',
      version: '1.0.3',
      endpoint: '/api/v1/weather',
      lastUpdated: '2024-01-14T16:20:00Z',
      requestCount: 420,
      responseTime: 150,
      errorRate: 0.0
    },
    {
      id: 'social-api',
      name: 'Social Media API',
      description: 'Social media sentiment and trending topics',
      status: 'error',
      version: '0.9.2',
      endpoint: '/api/v1/social',
      lastUpdated: '2024-01-15T07:30:00Z',
      requestCount: 0,
      responseTime: 0,
      errorRate: 100.0
    },
    {
      id: 'stats-api',
      name: 'Advanced Stats API',
      description: 'Detailed player and team performance statistics',
      status: 'active',
      version: '1.3.1',
      endpoint: '/api/v1/stats',
      lastUpdated: '2024-01-15T11:00:00Z',
      requestCount: 2180,
      responseTime: 280,
      errorRate: 0.8
    }
  ]

  const filteredPlugins = plugins.filter(plugin =>
    plugin.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    plugin.description.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getStatusIcon = (status: Plugin['status']) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'inactive':
        return <AlertCircle className="h-4 w-4 text-yellow-600" />
      case 'error':
        return <XCircle className="h-4 w-4 text-red-600" />
    }
  }

  const getStatusBadge = (status: Plugin['status']) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800 border-green-200">Active</Badge>
      case 'inactive':
        return <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200">Inactive</Badge>
      case 'error':
        return <Badge className="bg-red-100 text-red-800 border-red-200">Error</Badge>
    }
  }

  const handleTogglePlugin = (pluginId: string, currentStatus: Plugin['status']) => {
    // TODO: Implement plugin toggle functionality
    console.log(`Toggle plugin ${pluginId} from ${currentStatus}`)
  }

  const handleConfigurePlugin = (pluginId: string) => {
    // TODO: Implement plugin configuration
    console.log(`Configure plugin ${pluginId}`)
  }

  const handleViewCode = (pluginId: string) => {
    // TODO: Implement view code functionality
    console.log(`View code for plugin ${pluginId}`)
  }

  return (
    <div className="space-y-6">
      {/* Search */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search plugins..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="text-sm text-muted-foreground">
          {filteredPlugins.length} of {plugins.length} plugins
        </div>
      </div>

      {/* Plugins Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredPlugins.map((plugin) => (
          <PluginCard
            key={plugin.id}
            plugin={plugin}
            onToggle={handleTogglePlugin}
            onConfigure={handleConfigurePlugin}
            onViewCode={handleViewCode}
            getStatusIcon={getStatusIcon}
            getStatusBadge={getStatusBadge}
          />
        ))}
      </div>

      {filteredPlugins.length === 0 && (
        <Card>
          <CardContent className="p-6">
            <div className="text-center text-muted-foreground">
              <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No plugins found matching your search.</p>
              <p className="text-sm mt-2">Try adjusting your search terms.</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

interface PluginCardProps {
  plugin: Plugin
  onToggle: (id: string, status: Plugin['status']) => void
  onConfigure: (id: string) => void
  onViewCode: (id: string) => void
  getStatusIcon: (status: Plugin['status']) => JSX.Element
  getStatusBadge: (status: Plugin['status']) => JSX.Element
}

function PluginCard({ 
  plugin, 
  onToggle, 
  onConfigure, 
  onViewCode, 
  getStatusIcon, 
  getStatusBadge 
}: PluginCardProps) {
  return (
    <Card className="card-hover">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="text-lg flex items-center gap-2">
              {getStatusIcon(plugin.status)}
              {plugin.name}
            </CardTitle>
            <div className="flex items-center gap-2">
              {getStatusBadge(plugin.status)}
              <Badge variant="outline" className="text-xs">
                v{plugin.version}
              </Badge>
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">
          {plugin.description}
        </p>
        
        <div className="space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Endpoint:</span>
            <code className="bg-muted px-1 rounded text-xs">
              {plugin.endpoint}
            </code>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Requests (24h):</span>
            <span className="font-medium">{plugin.requestCount.toLocaleString()}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Avg Response:</span>
            <span className="font-medium">{plugin.responseTime}ms</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Error Rate:</span>
            <span className={`font-medium ${
              plugin.errorRate > 5 ? 'text-red-600' : 
              plugin.errorRate > 1 ? 'text-yellow-600' : 'text-green-600'
            }`}>
              {plugin.errorRate.toFixed(1)}%
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-2 pt-2 border-t">
          <Button
            size="sm"
            variant={plugin.status === 'active' ? 'destructive' : 'default'}
            onClick={() => onToggle(plugin.id, plugin.status)}
            className="flex-1"
          >
            {plugin.status === 'active' ? (
              <>
                <Square className="h-3 w-3 mr-1" />
                Stop
              </>
            ) : (
              <>
                <Play className="h-3 w-3 mr-1" />
                Start
              </>
            )}
          </Button>
          
          <Button
            size="sm"
            variant="outline"
            onClick={() => onConfigure(plugin.id)}
          >
            <Settings className="h-3 w-3" />
          </Button>
          
          <Button
            size="sm"
            variant="outline"
            onClick={() => onViewCode(plugin.id)}
          >
            <Code className="h-3 w-3" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
