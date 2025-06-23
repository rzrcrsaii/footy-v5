'use client'

import { Button } from '@/components/ui/button'
import { useWebSocket } from '@/lib/websocket/provider'
import { HeaderClock } from '@/components/ui/live-clock'
import { Wifi, WifiOff } from 'lucide-react'

export function Header() {
  const { isConnected, connectionStatus } = useWebSocket()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <a className="mr-6 flex items-center space-x-2" href="/dashboard">
            <span className="font-bold text-xl text-gradient">Footy-Brain</span>
          </a>
        </div>
        
        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <div className="w-full flex-1 md:w-auto md:flex-none">
            {/* Search or other header content can go here */}
          </div>
          
          <nav className="flex items-center space-x-4">
            {/* Live Clock */}
            <HeaderClock />

            {/* WebSocket Connection Status */}
            <div className="flex items-center gap-2">
              {isConnected ? (
                <Wifi className="h-4 w-4 text-green-600" />
              ) : (
                <WifiOff className="h-4 w-4 text-red-600" />
              )}
              <span className="text-xs text-muted-foreground">
                {connectionStatus}
              </span>
            </div>

            {/* User menu would go here */}
            <Button variant="ghost" size="sm">
              Admin
            </Button>
          </nav>
        </div>
      </div>
    </header>
  )
}
