import { Metadata } from 'next'
import { AnalyticsHeader } from '@/components/analytics/analytics-header'
import { AnalyticsOverview } from '@/components/analytics/analytics-overview'
import { AnalyticsCharts } from '@/components/analytics/analytics-charts'
import { AnalyticsFilters } from '@/components/analytics/analytics-filters'

export const metadata: Metadata = {
  title: 'Analytics',
  description: 'Football data analytics, trends, and insights',
}

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <AnalyticsHeader />
      
      {/* Filters */}
      <AnalyticsFilters />
      
      {/* Overview Cards */}
      <AnalyticsOverview />
      
      {/* Charts and Visualizations */}
      <AnalyticsCharts />
    </div>
  )
}
