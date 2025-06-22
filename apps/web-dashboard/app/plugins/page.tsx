import { Metadata } from 'next'
import { PluginsHeader } from '@/components/plugins/plugins-header'
import { PluginsList } from '@/components/plugins/plugins-list'
import { PluginsStats } from '@/components/plugins/plugins-stats'

export const metadata: Metadata = {
  title: 'Plugins',
  description: 'API wrapper plugins and integrations management',
}

export default function PluginsPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PluginsHeader />
      
      {/* Plugins Statistics */}
      <PluginsStats />
      
      {/* Plugins List */}
      <PluginsList />
    </div>
  )
}
