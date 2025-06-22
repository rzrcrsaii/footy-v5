import { Metadata } from 'next'
import { FixturesHeader } from '@/components/fixtures/fixtures-header'
import { FixturesFilters } from '@/components/fixtures/fixtures-filters'
import { FixturesList } from '@/components/fixtures/fixtures-list'

export const metadata: Metadata = {
  title: 'Fixtures',
  description: 'Football fixtures and match schedules',
}

export default function FixturesPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <FixturesHeader />
      
      {/* Filters */}
      <FixturesFilters />
      
      {/* Fixtures List */}
      <FixturesList />
    </div>
  )
}
