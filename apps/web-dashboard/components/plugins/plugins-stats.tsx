'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Puzzle, 
  CheckCircle, 
  AlertCircle, 
  XCircle, 
  Activity,
  Clock,
  Zap
} from 'lucide-react'

export function PluginsStats() {
  // Mock plugin statistics
  const stats = {
    totalPlugins: 8,
    activePlugins: 6,
    inactivePlugins: 1,
    errorPlugins: 1,
    totalRequests: 15420,
    avgResponseTime: 245,
    uptime: 99.2
  }

  const statCards = [
    {
      title: 'Total Plugins',
      value: stats.totalPlugins,
      icon: Puzzle,
      description: 'Registered plugins',
      color: 'text-blue-600',
    },
    {
      title: 'Active Plugins',
      value: stats.activePlugins,
      icon: CheckCircle,
      description: 'Currently running',
      color: 'text-green-600',
    },
    {
      title: 'Plugin Errors',
      value: stats.errorPlugins,
      icon: XCircle,
      description: 'Need attention',
      color: 'text-red-600',
    },
    {
      title: 'Total Requests',
      value: stats.totalRequests.toLocaleString(),
      icon: Activity,
      description: 'Last 24 hours',
      color: 'text-purple-600',
    },
    {
      title: 'Avg Response Time',
      value: `${stats.avgResponseTime}ms`,
      icon: Clock,
      description: 'API performance',
      color: 'text-orange-600',
    },
    {
      title: 'System Uptime',
      value: `${stats.uptime}%`,
      icon: Zap,
      description: 'Last 30 days',
      color: 'text-cyan-600',
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {statCards.map((card) => {
        const Icon = card.icon
        return (
          <Card key={card.title} className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {card.title}
              </CardTitle>
              <Icon className={`h-4 w-4 ${card.color}`} />
            </CardHeader>
            <CardContent>
              <div className="space-y-1">
                <div className="text-2xl font-bold">
                  {card.value}
                </div>
                <p className="text-xs text-muted-foreground">
                  {card.description}
                </p>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
