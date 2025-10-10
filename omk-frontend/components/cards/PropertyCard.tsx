'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { MapPin, TrendingUp, Calculator } from 'lucide-react';
import InteractiveCard from './InteractiveCard';
import { formatCurrency } from '@/lib/utils';

interface Property {
  id: string;
  name: string;
  location: string;
  country: string;
  image: string;
  blockPrice: number;
  totalBlocks: number;
  availableBlocks: number;
  apy: number;
  type: 'residential' | 'commercial';
}

interface PropertyCardProps {
  theme?: 'light' | 'dark';
  properties?: Property[];
  onInvest?: (propertyId: string, blocks: number) => void;
}

export default function PropertyCard({ theme = 'dark', properties, onInvest }: PropertyCardProps) {
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [blocks, setBlocks] = useState(1);

  const defaultProperties: Property[] = properties || [
    {
      id: '1',
      name: 'Luxury Apartment Complex',
      location: 'Dubai Marina',
      country: 'UAE',
      image: '🏙️',
      blockPrice: 100,
      totalBlocks: 1000,
      availableBlocks: 450,
      apy: 12,
      type: 'residential',
    },
    {
      id: '2',
      name: 'Beach Resort Villa',
      location: 'Bali',
      country: 'Indonesia',
      image: '🏖️',
      blockPrice: 75,
      totalBlocks: 1000,
      availableBlocks: 580,
      apy: 14,
      type: 'residential',
    },
    {
      id: '3',
      name: 'Commercial Office',
      location: 'Lagos',
      country: 'Nigeria',
      image: '🏢',
      blockPrice: 150,
      totalBlocks: 1000,
      availableBlocks: 320,
      apy: 10.5,
      type: 'commercial',
    },
  ];

  const monthlyReturn = selectedProperty ? (blocks * selectedProperty.blockPrice * selectedProperty.apy) / 100 / 12 : 0;
  const yearlyReturn = selectedProperty ? (blocks * selectedProperty.blockPrice * selectedProperty.apy) / 100 : 0;

  return (
    <InteractiveCard title="🏠 Investment Properties" theme={theme}>
      <div className="space-y-4">
        {!selectedProperty ? (
          // Property List
          <div className="space-y-3">
            {defaultProperties.map((property, i) => (
              <motion.button
                key={property.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                onClick={() => setSelectedProperty(property)}
                className="w-full bg-gray-800 hover:bg-gray-700 border border-gray-600 rounded-xl p-4 text-left transition-all group"
              >
                <div className="flex items-start gap-3">
                  <div className="text-5xl">{property.image}</div>
                  <div className="flex-1">
                    <h3 className="font-bold text-lg mb-1 group-hover:text-yellow-500 transition-colors">
                      {property.name}
                    </h3>
                    <div className="flex items-center gap-1 text-sm text-gray-400 mb-2">
                      <MapPin className="w-3 h-3" />
                      {property.location}, {property.country}
                    </div>
                    <div className="flex items-center gap-4">
                      <div>
                        <div className="text-xs text-gray-400">Block Price</div>
                        <div className="font-bold">{formatCurrency(property.blockPrice)}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-400">APY</div>
                        <div className="font-bold text-green-500 flex items-center gap-1">
                          <TrendingUp className="w-3 h-3" />
                          {property.apy}%
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="text-xs text-gray-400 mb-1">Available</div>
                        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-yellow-500 to-yellow-600"
                            style={{ width: `${(property.availableBlocks / property.totalBlocks) * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.button>
            ))}
          </div>
        ) : (
          // Property Detail & Investment
          <div className="space-y-4">
            {/* Property Info */}
            <div className="flex items-start gap-3">
              <div className="text-6xl">{selectedProperty.image}</div>
              <div className="flex-1">
                <h3 className="font-bold text-xl mb-1">{selectedProperty.name}</h3>
                <div className="flex items-center gap-1 text-sm text-gray-400 mb-3">
                  <MapPin className="w-3 h-3" />
                  {selectedProperty.location}, {selectedProperty.country}
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-gray-800/50 rounded-lg p-3">
                    <div className="text-xs text-gray-400 mb-1">Block Price</div>
                    <div className="text-lg font-bold">{formatCurrency(selectedProperty.blockPrice)}</div>
                  </div>
                  <div className="bg-gray-800/50 rounded-lg p-3">
                    <div className="text-xs text-gray-400 mb-1">APY</div>
                    <div className="text-lg font-bold text-green-500">{selectedProperty.apy}%</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Investment Calculator */}
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <Calculator className="w-5 h-5 text-yellow-500" />
                <h4 className="font-bold">Calculate Returns</h4>
              </div>
              
              <div className="mb-4">
                <label className="text-sm text-gray-400 mb-2 block">Number of Blocks</label>
                <input
                  type="range"
                  min="1"
                  max="50"
                  value={blocks}
                  onChange={(e) => setBlocks(parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between items-center mt-2">
                  <span className="text-2xl font-bold">{blocks} blocks</span>
                  <span className="text-xl font-bold text-yellow-500">
                    {formatCurrency(blocks * selectedProperty.blockPrice)}
                  </span>
                </div>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Monthly Return:</span>
                  <span className="font-bold text-green-500">{formatCurrency(monthlyReturn)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Yearly Return:</span>
                  <span className="font-bold text-green-500">{formatCurrency(yearlyReturn)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">ROI:</span>
                  <span className="font-bold text-green-500">+{selectedProperty.apy}%</span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setSelectedProperty(null)}
                className="px-4 py-3 bg-gray-800 hover:bg-gray-700 font-semibold rounded-xl border border-gray-600"
              >
                ← Back
              </button>
              <button
                onClick={() => {
                  if (onInvest) {
                    onInvest(selectedProperty.id, blocks);
                  }
                  alert(`Invested ${blocks} blocks in ${selectedProperty.name}! 🎉`);
                }}
                className="px-4 py-3 bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 text-black font-bold rounded-xl"
              >
                Invest Now
              </button>
            </div>
          </div>
        )}
      </div>
    </InteractiveCard>
  );
}
