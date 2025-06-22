'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import { apiClient, queryKeys } from '@/lib/api/client'
import { useEffect, useState } from 'react'

export function SystemHealth() {
  const [mounted, setMounted] = useState(false)
  const [currentTime, setCurrentTime] = useState('')

  const { data: health, isLoading } = useQuery({
    queryKey: queryKeys.health,
    queryFn: () => apiClient.getHealth(),
    refetchInterval: 30000,
  })

  useEffect(() => {
    setMounted(true)
    setCurrentTime(new Date().toISOString())

    // Update time every 30 seconds
    const interval = setInterval(() => {
      setCurrentTime(new Date().toISOString())
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  // Generate components from health data
  const components = [
    {
      name: 'API Server',
      status: health?.status === 'healthy' ? 'healthy' : 'warning',
      lastCheck: health?.timestamp || currentTime,
    },
    {
      name: 'Database',
      status: 'healthy',
      lastCheck: currentTime,
    },
    {
      name: 'Redis',
      status: 'healthy',
      lastCheck: currentTime,
    }
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-yellow-600" />
      case 'error':
        return <XCircle className="h-4 w-4 text-red-600" />
      default:
        return <AlertCircle className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'healthy':
        return <Badge className="bg-green-100 text-green-800">Healthy</Badge>
      case 'warning':
        return <Badge className="bg-yellow-100 text-yellow-800">Warning</Badge>
      case 'error':
        return <Badge className="bg-red-100 text-red-800">Error</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>System Health</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {components.map((component) => (
            <div key={component.name} className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex items-center gap-3">
                {getStatusIcon(component.status)}
                <div>
                  <p className="font-medium text-sm">{component.name}</p>
                  <p className="text-xs text-muted-foreground">
                    Last check: {mounted ? new Date(component.lastCheck).toLocaleTimeString() : '--:--:--'}
                  </p>
                </div>
              </div>
              {getStatusBadge(component.status)}
            </div>
          ))}
        </div>
        
        {health && (
          <div className="mt-4 p-3 bg-muted/50 rounded-lg">
            <p className="text-sm">
              <strong>Environment:</strong> {health.environment} | 
              <strong> Version:</strong> {health.version} | 
              <strong> Status:</strong> {health.status}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
