import { Metadata } from 'next'
import { DashboardStats } from '@/components/dashboard/dashboard-stats'
import { LiveMatches } from '@/components/dashboard/live-matches'
import { RecentActivity } from '@/components/dashboard/recent-activity'
import { OddsMovement } from '@/components/dashboard/odds-movement'
import { SystemHealth } from '@/components/dashboard/system-health'

export const metadata: Metadata = {
  title: 'Dashboard',
  description: 'Real-time football data dashboard overview',
}

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Real-time football data monitoring and analysis
          </p>
        </div>
      </div>

      {/* Dashboard Stats */}
      <DashboardStats />

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Live Matches */}
        <div className="lg:col-span-2">
          <LiveMatches />
        </div>

        {/* Recent Activity */}
        <RecentActivity />

        {/* Odds Movement */}
        <OddsMovement />

        {/* System Health */}
        <div className="lg:col-span-2">
          <SystemHealth />
        </div>
      </div>
    </div>
  )
}
