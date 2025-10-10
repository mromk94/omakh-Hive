'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import InteractiveCard from '../cards/InteractiveCard';

interface ROICalculatorProps {
  theme?: 'light' | 'dark';
  onCalculate?: (amount: number, period: string, result: number) => void;
}

export default function ROICalculator({ theme = 'light', onCalculate }: ROICalculatorProps) {
  const [amount, setAmount] = useState<string>('1000');
  const [period, setPeriod] = useState<string>('1 year');
  const [results, setResults] = useState<any>(null);
  const [showResults, setShowResults] = useState(false);

  const APY = 15; // 15% annual percentage yield

  const calculateROI = () => {
    const principal = parseFloat(amount) || 0;
    
    if (principal < 100) {
      alert('Minimum investment is $100');
      return;
    }

    const periods: { [key: string]: number } = {
      '3 months': 0.25,
      '6 months': 0.5,
      '1 year': 1,
      '2 years': 2,
      '5 years': 5,
    };

    const years = periods[period] || 1;
    const finalAmount = principal * Math.pow(1 + APY / 100, years);
    const profit = finalAmount - principal;
    const roi = ((profit / principal) * 100).toFixed(2);

    const result = {
      initial: principal,
      final: finalAmount.toFixed(2),
      profit: profit.toFixed(2),
      roi: roi,
      period: period,
      omk_tokens: (principal / 0.1).toFixed(0), // 1 OMK = 0.1 USDT
    };

    setResults(result);
    setShowResults(true);

    // Callback to parent
    if (onCalculate) {
      onCalculate(principal, period, finalAmount);
    }
  };

  return (
    <InteractiveCard title="💰 ROI Calculator" theme={theme}>
      <div className="space-y-6">
        {/* Investment Amount */}
        <div>
          <label className={`block text-sm font-semibold mb-2 ${
            theme === 'dark' ? 'text-gray-300' : 'text-gray-700'
          }`}>
            Investment Amount (USD)
          </label>
          <div className="relative">
            <span className={`absolute left-4 top-1/2 -translate-y-1/2 text-xl font-bold ${
              theme === 'dark' ? 'text-gray-400' : 'text-gray-600'
            }`}>
              $
            </span>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="1000"
              min="100"
              max="1000000"
              className={`w-full pl-10 pr-4 py-4 text-xl font-bold rounded-xl border-2 focus:outline-none transition-all ${
                theme === 'dark'
                  ? 'bg-gray-800 border-gray-700 focus:border-purple-500 text-white'
                  : 'bg-white border-purple-300 focus:border-purple-500 text-gray-900'
              }`}
            />
          </div>
          <p className={`text-xs mt-1 ${theme === 'dark' ? 'text-gray-500' : 'text-gray-500'}`}>
            Minimum: $100 | Maximum: $1,000,000
          </p>
        </div>

        {/* Time Period */}
        <div>
          <label className={`block text-sm font-semibold mb-2 ${
            theme === 'dark' ? 'text-gray-300' : 'text-gray-700'
          }`}>
            Time Period
          </label>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
            {['3 months', '6 months', '1 year', '2 years', '5 years'].map((p) => (
              <motion.button
                key={p}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setPeriod(p)}
                className={`py-3 px-4 rounded-xl font-semibold transition-all ${
                  period === p
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
                    : theme === 'dark'
                      ? 'bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700'
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                }`}
              >
                {p}
              </motion.button>
            ))}
          </div>
        </div>

        {/* Calculate Button */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={calculateROI}
          className="w-full py-5 bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 text-white rounded-xl text-xl font-bold shadow-2xl hover:shadow-purple-500/50 transition-all"
        >
          ✨ Calculate My Returns
        </motion.button>

        {/* Results */}
        <AnimatePresence>
          {showResults && results && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className={`rounded-2xl p-6 mt-6 ${
                theme === 'dark'
                  ? 'bg-gradient-to-br from-purple-900/50 to-pink-900/50 border border-purple-500/30'
                  : 'bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200'
              }`}
            >
              <h4 className={`text-xl font-bold mb-4 ${
                theme === 'dark' ? 'text-white' : 'text-gray-900'
              }`}>
                📈 Your Projected Returns
              </h4>

              <div className="space-y-4">
                {/* Initial Investment */}
                <div className="flex justify-between items-center">
                  <span className={theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}>
                    Initial Investment:
                  </span>
                  <span className={`text-2xl font-black ${
                    theme === 'dark' ? 'text-white' : 'text-gray-900'
                  }`}>
                    ${parseFloat(results.initial).toLocaleString()}
                  </span>
                </div>

                {/* OMK Tokens */}
                <div className="flex justify-between items-center">
                  <span className={theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}>
                    OMK Tokens:
                  </span>
                  <span className={`text-xl font-bold ${
                    theme === 'dark' ? 'text-purple-300' : 'text-purple-600'
                  }`}>
                    {parseFloat(results.omk_tokens).toLocaleString()} OMK
                  </span>
                </div>

                <div className="border-t border-gray-400/30 my-2" />

                {/* Final Value */}
                <div className="flex justify-between items-center">
                  <span className={`font-semibold ${theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}`}>
                    After {results.period}:
                  </span>
                  <span className="text-3xl font-black text-green-500">
                    ${parseFloat(results.final).toLocaleString()}
                  </span>
                </div>

                {/* Profit */}
                <div className="flex justify-between items-center">
                  <span className={`font-semibold ${theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}`}>
                    Your Profit:
                  </span>
                  <span className="text-2xl font-black text-green-400">
                    +${parseFloat(results.profit).toLocaleString()}
                  </span>
                </div>

                {/* ROI Percentage */}
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className={`mt-4 p-4 rounded-xl text-center ${
                    theme === 'dark'
                      ? 'bg-green-900/30 border border-green-500/50'
                      : 'bg-green-100 border border-green-300'
                  }`}
                >
                  <div className="text-sm font-semibold text-green-600 dark:text-green-400">
                    Return on Investment
                  </div>
                  <div className="text-4xl font-black text-green-500 mt-1">
                    +{results.roi}%
                  </div>
                </motion.div>

                {/* Comparison with Banks */}
                <div className={`mt-4 p-4 rounded-xl text-sm ${
                  theme === 'dark' ? 'bg-gray-800' : 'bg-white'
                }`}>
                  <p className={`font-semibold mb-2 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
                    💡 Compare with traditional banks:
                  </p>
                  <p className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>
                    A regular savings account at 2% APY would only give you <strong>${
                      (parseFloat(results.initial) * Math.pow(1.02, parseFloat(results.period.split(' ')[0]))).toFixed(2)
                    }</strong> - that's <strong className="text-red-500">${
                      (parseFloat(results.final) - (parseFloat(results.initial) * Math.pow(1.02, parseFloat(results.period.split(' ')[0])))).toFixed(2)
                    } less</strong> than OMK Hive! 🚀
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </InteractiveCard>
  );
}
