import { Metadata } from 'next'
import { LiveMatchesGrid } from '@/components/live/live-matches-grid'
import { LiveDataHeader } from '@/components/live/live-data-header'

export const metadata: Metadata = {
  title: 'Live Data',
  description: 'Real-time football match data, odds, and statistics',
}

export default function LiveDataPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <LiveDataHeader />
      
      {/* Live Matches Grid */}
      <LiveMatchesGrid />
    </div>
  )
}
