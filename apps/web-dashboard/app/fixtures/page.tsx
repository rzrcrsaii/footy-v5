'use client'

import { useState } from 'react'
import { Metadata } from 'next'
import { FixturesHeader } from '@/components/fixtures/fixtures-header'
import { FixturesFilters, type FixturesFilters as FiltersType } from '@/components/fixtures/fixtures-filters'
import { FixturesList } from '@/components/fixtures/fixtures-list'

export default function FixturesPage() {
  const [filters, setFilters] = useState<FiltersType>({})

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <FixturesHeader />

      {/* Filters */}
      <FixturesFilters onFiltersChange={setFilters} />

      {/* Fixtures List */}
      <FixturesList filters={filters} />
    </div>
  )
}
