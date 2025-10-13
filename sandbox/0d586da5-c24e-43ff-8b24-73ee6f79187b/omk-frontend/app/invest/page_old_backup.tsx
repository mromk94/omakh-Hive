'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, SlidersHorizontal, MapPin, TrendingUp, Home, Calculator } from 'lucide-react';
import { useAccount } from 'wagmi';
import { useRouter } from 'next/navigation';
import { formatCurrency } from '@/lib/utils';

interface Property {
  id: string;
  name: string;
  location: string;
  country: string;
  image: string;
  totalValue: number;
  blockPrice: number;
  totalBlocks: number;
  availableBlocks: number;
  apy: number;
  type: 'residential' | 'commercial';
  featured: boolean;
}

export default function InvestPage() {
  const { address, isConnected } = useAccount();
  const router = useRouter();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedType, setSelectedType] = useState<'all' | 'residential' | 'commercial'>('all');
  const [sortBy, setSortBy] = useState<'apy' | 'price' | 'newest'>('apy');

  // Mock properties data
  const [properties] = useState<Property[]>([
    {
      id: '1',
      name: 'Luxury Apartment Complex',
      location: 'Dubai Marina',
      country: 'UAE',
      image: '🏙️',
      totalValue: 100000,
      blockPrice: 100,
      totalBlocks: 1000,
      availableBlocks: 450,
      apy: 12,
      type: 'residential',
      featured: true,
    },
    {
      id: '2',
      name: 'Commercial Office Building',
      location: 'Canary Wharf',
      country: 'UK',
      image: '🏢',
      totalValue: 250000,
      blockPrice: 250,
      totalBlocks: 1000,
      availableBlocks: 320,
      apy: 10.5,
      type: 'commercial',
      featured: true,
    },
    {
      id: '3',
      name: 'Beach Resort Villa',
      location: 'Bali',
      country: 'Indonesia',
      image: '🏖️',
      totalValue: 75000,
      blockPrice: 75,
      totalBlocks: 1000,
      availableBlocks: 580,
      apy: 14,
      type: 'residential',
      featured: false,
    },
    {
      id: '4',
      name: 'Downtown Shopping Mall',
      location: 'Singapore',
      country: 'Singapore',
      image: '🏬',
      totalValue: 500000,
      blockPrice: 500,
      totalBlocks: 1000,
      availableBlocks: 250,
      apy: 9.5,
      type: 'commercial',
      featured: false,
    },
  ]);

  useEffect(() => {
    if (!isConnected) {
      router.push('/connect');
    }
  }, [isConnected, router]);

  const filteredProperties = properties
    .filter(p => {
      if (selectedType !== 'all' && p.type !== selectedType) return false;
      if (searchQuery && !p.name.toLowerCase().includes(searchQuery.toLowerCase()) && 
          !p.location.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      return true;
    })
    .sort((a, b) => {
      if (sortBy === 'apy') return b.apy - a.apy;
      if (sortBy === 'price') return a.blockPrice - b.blockPrice;
      return 0; // newest
    });

  return (
    <div className="min-h-screen bg-black text-stone-100">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl md:text-4xl font-black mb-2">
            <span className="bg-gradient-to-r from-yellow-500 to-yellow-600 bg-clip-text text-transparent">
              Investment Properties
            </span>
          </h1>
          <p className="text-stone-400">
            Invest in fractional real estate and earn passive income
          </p>
        </motion.div>

        {/* Stats Bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
        >
          <div className="bg-gradient-to-br from-stone-900 to-black p-4 rounded-xl border border-yellow-500/30">
            <div className="text-2xl font-bold text-yellow-500">{properties.length}</div>
            <div className="text-sm text-stone-400">Properties Available</div>
          </div>
          <div className="bg-gradient-to-br from-stone-900 to-black p-4 rounded-xl border border-yellow-500/30">
            <div className="text-2xl font-bold text-yellow-500">
              {formatCurrency(properties.reduce((sum, p) => sum + p.totalValue, 0))}
            </div>
            <div className="text-sm text-stone-400">Total Value</div>
          </div>
          <div className="bg-gradient-to-br from-stone-900 to-black p-4 rounded-xl border border-yellow-500/30">
            <div className="text-2xl font-bold text-yellow-500">$100</div>
            <div className="text-sm text-stone-400">Min Investment</div>
          </div>
          <div className="bg-gradient-to-br from-stone-900 to-black p-4 rounded-xl border border-yellow-500/30">
            <div className="text-2xl font-bold text-yellow-500">12%</div>
            <div className="text-sm text-stone-400">Avg APY</div>
          </div>
        </motion.div>

        {/* Search and Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-6"
        >
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-stone-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by name or location..."
                className="w-full pl-12 pr-4 py-3 bg-stone-900 border border-yellow-500/30 rounded-xl text-stone-100 placeholder-stone-500 focus:outline-none focus:border-yellow-500/50 transition-colors"
              />
            </div>

            {/* Filter Button */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="px-6 py-3 bg-stone-900 border border-yellow-500/30 hover:border-yellow-500/50 rounded-xl flex items-center gap-2 transition-colors"
            >
              <SlidersHorizontal className="w-5 h-5 text-yellow-500" />
              <span>Filters</span>
            </button>
          </div>

          {/* Filters Panel */}
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-4 p-4 bg-stone-900 border border-yellow-500/30 rounded-xl"
            >
              <div className="grid md:grid-cols-2 gap-4">
                {/* Property Type */}
                <div>
                  <label className="text-sm text-stone-400 mb-2 block">Property Type</label>
                  <div className="flex gap-2">
                    {['all', 'residential', 'commercial'].map((type) => (
                      <button
                        key={type}
                        onClick={() => setSelectedType(type as any)}
                        className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-colors ${
                          selectedType === type
                            ? 'bg-yellow-500 text-black'
                            : 'bg-stone-800 text-stone-300 hover:bg-stone-700'
                        }`}
                      >
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Sort By */}
                <div>
                  <label className="text-sm text-stone-400 mb-2 block">Sort By</label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as any)}
                    className="w-full px-4 py-2 bg-stone-800 border border-yellow-500/30 rounded-lg text-stone-100 focus:outline-none focus:border-yellow-500/50"
                  >
                    <option value="apy">Highest APY</option>
                    <option value="price">Lowest Price</option>
                    <option value="newest">Newest</option>
                  </select>
                </div>
              </div>
            </motion.div>
          )}
        </motion.div>

        {/* Properties Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProperties.map((property, index) => (
            <motion.div
              key={property.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + index * 0.05 }}
              className="group bg-gradient-to-br from-stone-900 to-black border border-yellow-500/30 hover:border-yellow-500/50 rounded-2xl overflow-hidden transition-all cursor-pointer"
              onClick={() => router.push(`/invest/${property.id}`)}
            >
              {/* Image */}
              <div className="aspect-video bg-gradient-to-br from-yellow-500/20 to-yellow-600/20 flex items-center justify-center text-8xl relative">
                {property.image}
                {property.featured && (
                  <div className="absolute top-4 right-4 px-3 py-1 bg-yellow-500 text-black text-xs font-bold rounded-full">
                    FEATURED
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-xl font-bold text-stone-100 mb-1 group-hover:text-yellow-500 transition-colors">
                      {property.name}
                    </h3>
                    <div className="flex items-center gap-1 text-sm text-stone-400">
                      <MapPin className="w-3 h-3" />
                      {property.location}, {property.country}
                    </div>
                  </div>
                  <div className="px-2 py-1 bg-yellow-500/20 text-yellow-500 text-xs font-semibold rounded">
                    {property.type === 'residential' ? <Home className="w-4 h-4" /> : '🏢'}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4 py-4 border-y border-stone-800">
                  <div>
                    <div className="text-xs text-stone-400 mb-1">Block Price</div>
                    <div className="text-lg font-bold text-stone-100">
                      {formatCurrency(property.blockPrice)}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-stone-400 mb-1">APY</div>
                    <div className="text-lg font-bold text-green-500 flex items-center gap-1">
                      <TrendingUp className="w-4 h-4" />
                      {property.apy}%
                    </div>
                  </div>
                </div>

                {/* Progress */}
                <div className="mb-4">
                  <div className="flex items-center justify-between text-xs text-stone-400 mb-2">
                    <span>Available</span>
                    <span>{property.availableBlocks}/{property.totalBlocks} blocks</span>
                  </div>
                  <div className="h-2 bg-stone-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-yellow-500 to-yellow-600"
                      style={{ width: `${(property.availableBlocks / property.totalBlocks) * 100}%` }}
                    />
                  </div>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    router.push(`/invest/${property.id}`);
                  }}
                  className="w-full py-3 bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 text-black font-semibold rounded-xl transition-all flex items-center justify-center gap-2"
                >
                  <Calculator className="w-4 h-4" />
                  View Details
                </button>
              </div>
            </motion.div>
          ))}
        </div>

        {/* No Results */}
        {filteredProperties.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-16"
          >
            <div className="text-6xl mb-4">🏠</div>
            <h3 className="text-xl font-bold text-stone-100 mb-2">No Properties Found</h3>
            <p className="text-stone-400 mb-6">Try adjusting your filters or search query</p>
            <button
              onClick={() => {
                setSearchQuery('');
                setSelectedType('all');
                setShowFilters(false);
              }}
              className="px-6 py-3 bg-yellow-500 hover:bg-yellow-600 text-black font-semibold rounded-xl transition-colors"
            >
              Reset Filters
            </button>
          </motion.div>
        )}
      </div>
    </div>
  );
}
