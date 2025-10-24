import { http, createConfig } from 'wagmi';
import { mainnet, sepolia, localhost } from 'wagmi/chains';
import { injected, walletConnect, coinbaseWallet } from 'wagmi/connectors';

// WalletConnect project ID - get from https://cloud.walletconnect.com
const projectId = process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID;

// Check if WalletConnect should be enabled
const hasValidProjectId = projectId && projectId !== 'YOUR_PROJECT_ID' && projectId.trim() !== '';

if (!hasValidProjectId) {
  console.warn('[Web3] WalletConnect disabled: No valid NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID provided');
  console.warn('[Web3] Get your project ID from: https://cloud.walletconnect.com');
  console.warn('[Web3] MetaMask and Coinbase Wallet are still available');
}

// Build connectors array - only include WalletConnect if project ID is valid
const getConnectors = () => {
  const baseConnectors = [
    // Injected wallets (MetaMask, Coinbase Wallet, etc.) - Always available
    injected({ 
      target: 'metaMask',
      shimDisconnect: true 
    }),
    
    // Coinbase Wallet - Always available
    coinbaseWallet({
      appName: 'OMK Hive',
      appLogoUrl: 'https://omakh.io/logo.png',
    }),
  ];

  // Only add WalletConnect if we have a valid project ID
  if (hasValidProjectId) {
    return [
      ...baseConnectors,
      walletConnect({
        projectId: projectId!,
        metadata: {
          name: 'OMK Hive',
          description: 'Fractional Real Estate Investment Platform',
          url: 'https://omakh.io',
          icons: ['https://omakh.io/logo.png'],
        },
        showQrModal: true,
      }),
    ];
  }

  return baseConnectors;
};

export const config = createConfig({
  chains: [mainnet, sepolia, localhost],
  connectors: getConnectors(),
  transports: {
    [mainnet.id]: http(),
    [sepolia.id]: http(),
    [localhost.id]: http(),
  },
  ssr: true,
});
