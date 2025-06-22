import { Metadata } from 'next'
import { LiveMatchHeader } from '@/components/live/live-match-header'
import { LiveOddsTable } from '@/components/live/live-odds-table'
import { LiveEventsTimeline } from '@/components/live/live-events-timeline'
import { LiveStatsChart } from '@/components/live/live-stats-chart'

interface LiveMatchPageProps {
  params: {
    fixtureId: string
  }
}

export async function generateMetadata({ params }: LiveMatchPageProps): Promise<Metadata> {
  return {
    title: `Live Match ${params.fixtureId}`,
    description: `Real-time data for match ${params.fixtureId}`,
  }
}

export default function LiveMatchPage({ params }: LiveMatchPageProps) {
  const fixtureId = parseInt(params.fixtureId)

  return (
    <div className="space-y-6">
      {/* Match Header with Score */}
      <LiveMatchHeader fixtureId={fixtureId} />
      
      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Live Odds Table */}
        <div className="lg:col-span-2">
          <LiveOddsTable fixtureId={fixtureId} />
        </div>
        
        {/* Events Timeline */}
        <LiveEventsTimeline fixtureId={fixtureId} />
        
        {/* Stats Chart */}
        <LiveStatsChart fixtureId={fixtureId} />
      </div>
    </div>
  )
}
