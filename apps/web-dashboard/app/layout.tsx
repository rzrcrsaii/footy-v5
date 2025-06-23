import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { Toaster } from '@/components/ui/toaster'
import { Navigation } from '@/components/layout/navigation'
import { Header } from '@/components/layout/header'

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' })

export const metadata: Metadata = {
  title: {
    default: 'Footy-Brain Dashboard',
    template: '%s | Footy-Brain Dashboard',
  },
  description: 'Real-time football data ingestion and analysis platform',
  keywords: [
    'football',
    'soccer',
    'betting',
    'odds',
    'real-time',
    'dashboard',
    'analytics',
    'statistics',
  ],
  authors: [
    {
      name: 'Footy-Brain Team',
      url: 'https://github.com/footy-brain',
    },
  ],
  creator: 'Footy-Brain Team',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://footy-brain.com',
    title: 'Footy-Brain Dashboard',
    description: 'Real-time football data ingestion and analysis platform',
    siteName: 'Footy-Brain',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Footy-Brain Dashboard',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Footy-Brain Dashboard',
    description: 'Real-time football data ingestion and analysis platform',
    images: ['/og-image.png'],
    creator: '@footybrain',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  manifest: '/manifest.json',
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <Providers>
          <div className="min-h-screen bg-background">
            {/* Header */}
            <Header />
            
            <div className="flex">
              {/* Sidebar Navigation */}
              <Navigation />
              
              {/* Main Content */}
              <main className="flex-1 lg:pl-64 relative z-0">
                <div className="px-4 py-6 sm:px-6 lg:px-8">
                  {children}
                </div>
              </main>
            </div>
          </div>
          
          {/* Toast Notifications */}
          <Toaster />
        </Providers>
      </body>
    </html>
  )
}