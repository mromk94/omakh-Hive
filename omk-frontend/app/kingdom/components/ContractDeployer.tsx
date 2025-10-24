'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileCode, Play, CheckCircle, XCircle, Clock, AlertTriangle,
  Loader2, Network, Settings, Trash2, ExternalLink, RefreshCw,
  Zap, Shield, DollarSign, Copy, ChevronRight, Info, Wallet,
  Power, AlertCircle
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { 
  useAccount, 
  useConnect, 
  useDisconnect, 
  useDeployContract,
  useSwitchChain,
  useWaitForTransactionReceipt,
  usePublicClient,
  useEstimateGas
} from 'wagmi';
import { parseAbi, formatEther, type Hex } from 'viem';
import { API_ENDPOINTS } from '../../../lib/constants';
import { sepolia, mainnet } from 'viem/chains';

interface Contract {
  name: string;
  path: string;
  full_path: string;
  is_compiled: boolean;
  compiled_at: string | null;
  status: string;
  deployments: Deployment[];
  deployment_count: number;
}

interface Deployment {
  id: string;
  contract_name: string;
  network: string;
  constructor_args: any[];
  status: string;
  created_at: string;
  deployed_at: string | null;
  contract_address: string | null;
  transaction_hash: string | null;
  deployer: string;
  gas_limit?: number;
  gas_price?: number;
}

interface ContractArtifact {
  abi: any[];
  bytecode: Hex;
}

export default function ContractDeployer() {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedContracts, setSelectedContracts] = useState<Set<string>>(new Set());
  const [activeTab, setActiveTab] = useState<'contracts' | 'deployments'>('contracts');
  const [showDeployModal, setShowDeployModal] = useState(false);
  const [deployConfig, setDeployConfig] = useState({
    network: 'sepolia',
    gasLimit: null as number | null,
    gasPrice: null as number | null,
  });
  const [compiling, setCompiling] = useState(false);
  const [selectedContract, setSelectedContract] = useState<Contract | null>(null);
  const [contractArtifact, setContractArtifact] = useState<ContractArtifact | null>(null);
  const [deploymentHash, setDeploymentHash] = useState<Hex | null>(null);

  // Wagmi hooks
  const { address, isConnected, chain } = useAccount();
  const { connect, connectors } = useConnect();
  const { disconnect } = useDisconnect();
  const { switchChain } = useSwitchChain();
  const { deployContract, data: hash, isPending: isDeploying, error: deployError } = useDeployContract();
  
  // Transaction receipt
  const { data: receipt, isLoading: isConfirming } = useWaitForTransactionReceipt({
    hash: deploymentHash || undefined,
  });

  useEffect(() => {
    loadContracts();
    loadDeployments();
  }, []);

  // Handle successful deployment
  useEffect(() => {
    if (receipt && selectedContract) {
      handleDeploymentSuccess(receipt.contractAddress!);
    }
  }, [receipt]);

  const loadContracts = async () => {
    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${API_ENDPOINTS.CONTRACTS}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      if (data.success && data.contracts) {
        console.log(`✅ Loaded ${data.contracts.length} contracts`);
        setContracts(data.contracts);
      } else {
        console.error('Invalid response:', data);
        toast.error('Failed to load contracts - invalid response');
      }
    } catch (error: any) {
      console.error('Failed to load contracts:', error);
      toast.error(`Failed to load contracts: ${error?.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const loadDeployments = async () => {
    try {
      const response = await fetch(`${API_ENDPOINTS.CONTRACTS}/deployments`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
      });
      const data = await response.json();
      if (data.success) {
        setDeployments(data.deployments);
      }
    } catch (error) {
      console.error('Failed to load deployments:', error);
    }
  };

  const compileAllContracts = async () => {
    setCompiling(true);
    
    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${API_ENDPOINTS.CONTRACTS}/compile`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      if (data.success) {
        toast.success('✅ All contracts compiled successfully!');
        await loadContracts();
      } else {
        toast.error(`Compilation failed: ${data.error || 'Unknown error'}`);
        console.error('Compilation output:', data.output);
      }
    } catch (error: any) {
      console.error('Compilation error:', error);
      toast.error(`Compilation failed: ${error?.message || 'Unknown error'}`);
    } finally {
      setCompiling(false);
    }
  };

  const loadContractArtifact = async (contractName: string) => {
    try {
      const token = localStorage.getItem('auth_token') || 'dev_token';
      const response = await fetch(`${API_ENDPOINTS.CONTRACTS}/${contractName}/artifact`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      if (data.success && data.abi && data.bytecode) {
        return {
          abi: data.abi,
          bytecode: data.bytecode as Hex
        };
      }
      
      throw new Error('Invalid artifact data');
    } catch (error: any) {
      console.error('Failed to load contract artifact:', error);
      toast.error(`Failed to load artifact: ${error?.message || 'Unknown error'}`);
      throw error;
    }
  };

  const prepareDeployment = async (contract: Contract) => {
    if (!isConnected) {
      toast.error('Please connect your wallet first');
      return;
    }

    if (!contract.is_compiled) {
      toast.error('Contract not compiled. Please compile first.');
      return;
    }

    try {
      // Load contract artifact
      const artifact = await loadContractArtifact(contract.name);
      setContractArtifact(artifact);
      setSelectedContract(contract);
      setShowDeployModal(true);
    } catch (error) {
      toast.error('Failed to load contract artifact');
    }
  };

  const executeDeployment = async () => {
    if (!selectedContract || !contractArtifact || !isConnected) return;

    // Check network
    const targetChainId = deployConfig.network === 'mainnet' ? mainnet.id : sepolia.id;
    if (chain?.id !== targetChainId) {
      // Switch network
      try {
        await switchChain({ chainId: targetChainId });
      } catch (error) {
        toast.error('Please switch to the correct network in your wallet');
        return;
      }
    }

    try {
      // Deploy contract
      deployContract({
        abi: contractArtifact.abi,
        bytecode: contractArtifact.bytecode,
        args: [], // Add constructor args support later
      });

      if (hash) {
        setDeploymentHash(hash);
      }
      toast.success('🚀 Deployment transaction sent!');
      setShowDeployModal(false);
      
    } catch (error: any) {
      console.error('Deployment failed:', error);
      toast.error(error.message || 'Deployment failed');
    }
  };

  const handleDeploymentSuccess = async (contractAddress: string) => {
    if (!selectedContract) return;

    // Save deployment to backend
    try {
      const response = await fetch(`${API_ENDPOINTS.CONTRACTS}/save-deployment`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          contract_name: selectedContract.name,
          network: deployConfig.network,
          contract_address: contractAddress,
          transaction_hash: deploymentHash,
          deployer: address,
          constructor_args: []
        })
      });

      const data = await response.json();
      if (data.success) {
        toast.success(`✅ ${selectedContract.name} deployed successfully!`);
        loadContracts();
        loadDeployments();
      }
    } catch (error) {
      console.error('Failed to save deployment:', error);
    }

    // Reset state
    setSelectedContract(null);
    setContractArtifact(null);
    setDeploymentHash(null);
  };

  const handleConnectWallet = () => {
    const injected = connectors.find(c => c.id === 'injected' || c.name.includes('MetaMask'));
    if (injected) {
      connect({ connector: injected });
    } else {
      toast.error('No wallet found. Please install MetaMask.');
    }
  };

  const getNetworkName = (chainId: number) => {
    switch (chainId) {
      case 1: return 'Ethereum';
      case 11155111: return 'Sepolia';
      case 31337: return 'Localhost';
      default: return 'Unknown';
    }
  };

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { color: string; icon: any; label: string }> = {
      'not_deployed': { color: 'bg-gray-600', icon: Clock, label: 'Not Deployed' },
      'compiled': { color: 'bg-blue-600', icon: CheckCircle, label: 'Compiled' },
      'prepared': { color: 'bg-yellow-600', icon: AlertTriangle, label: 'Prepared' },
      'deploying': { color: 'bg-purple-600', icon: Loader2, label: 'Deploying' },
      'deployed': { color: 'bg-green-600', icon: CheckCircle, label: 'Deployed' },
      'failed': { color: 'bg-red-600', icon: XCircle, label: 'Failed' },
    };

    const badge = badges[status] || badges['not_deployed'];
    const Icon = badge.icon;

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium text-white ${badge.color}`}>
        <Icon className="w-3 h-3" />
        {badge.label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 text-yellow-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Wallet Connection */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <FileCode className="w-7 h-7 text-yellow-500" />
            Smart Contract Deployment
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Compile, review, and deploy contracts to testnet or mainnet
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Wallet Connection */}
          {isConnected ? (
            <div className="flex items-center gap-3 bg-gray-800/50 border border-gray-700 rounded-lg px-4 py-2">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="text-xs text-gray-400">{getNetworkName(chain?.id || 0)}</span>
              </div>
              <div className="h-4 w-px bg-gray-700" />
              <code className="text-sm text-white font-mono">
                {address?.slice(0, 6)}...{address?.slice(-4)}
              </code>
              <button
                onClick={() => disconnect()}
                className="p-1 hover:bg-gray-700 rounded transition-colors"
                title="Disconnect"
              >
                <Power className="w-4 h-4 text-gray-400" />
              </button>
            </div>
          ) : (
            <button
              onClick={handleConnectWallet}
              className="px-4 py-2 bg-gradient-to-r from-yellow-600 to-yellow-500 hover:from-yellow-700 hover:to-yellow-600 text-black rounded-lg font-medium transition-all flex items-center gap-2"
            >
              <Wallet className="w-4 h-4" />
              Connect Wallet
            </button>
          )}

          <button
            onClick={loadContracts}
            className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <RefreshCw className="w-5 h-5 text-gray-400" />
          </button>
          <button
            onClick={compileAllContracts}
            disabled={compiling}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            {compiling ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Compiling...
              </>
            ) : (
              <>
                <Zap className="w-4 h-4" />
                Compile All
              </>
            )}
          </button>
        </div>
      </div>

      {/* Wallet Connection Warning */}
      {!isConnected && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-yellow-600/10 border border-yellow-500/20 rounded-lg p-4"
        >
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-yellow-500 font-medium">Wallet Not Connected</p>
              <p className="text-yellow-400/80 text-sm mt-1">
                Connect your wallet to deploy contracts. Deployments will be signed and executed using your connected wallet.
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-800">
        <button
          onClick={() => setActiveTab('contracts')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'contracts'
              ? 'text-yellow-500 border-b-2 border-yellow-500'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <span className="flex items-center gap-2">
            <FileCode className="w-4 h-4" />
            Contracts ({contracts.length})
          </span>
        </button>
        <button
          onClick={() => setActiveTab('deployments')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'deployments'
              ? 'text-yellow-500 border-b-2 border-yellow-500'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <span className="flex items-center gap-2">
            <Network className="w-4 h-4" />
            Deployments ({deployments.length})
          </span>
        </button>
      </div>

      {/* Contracts Tab */}
      {activeTab === 'contracts' && (
        <div className="space-y-4">
          {/* Batch Actions */}
          {selectedContracts.size > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-yellow-600/10 border border-yellow-500/20 rounded-lg p-4"
            >
              <div className="flex items-center justify-between">
                <span className="text-yellow-500 font-medium">
                  {selectedContracts.size} contract(s) selected
                </span>
                <div className="flex gap-2">
                  <button
                    onClick={() => setSelectedContracts(new Set())}
                    className="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-sm"
                  >
                    Clear
                  </button>
                </div>
              </div>
            </motion.div>
          )}

          {/* Contract List */}
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-800/50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">
                    <input
                      type="checkbox"
                      checked={selectedContracts.size === contracts.length && contracts.length > 0}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedContracts(new Set(contracts.map(c => c.name)));
                        } else {
                          setSelectedContracts(new Set());
                        }
                      }}
                      className="rounded"
                    />
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Contract</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Compiled</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Deployments</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {contracts.map((contract) => (
                  <tr key={contract.name} className="hover:bg-gray-800/30 transition-colors">
                    <td className="px-4 py-3">
                      <input
                        type="checkbox"
                        checked={selectedContracts.has(contract.name)}
                        onChange={() => {
                          const newSelection = new Set(selectedContracts);
                          if (newSelection.has(contract.name)) {
                            newSelection.delete(contract.name);
                          } else {
                            newSelection.add(contract.name);
                          }
                          setSelectedContracts(newSelection);
                        }}
                        className="rounded"
                      />
                    </td>
                    <td className="px-4 py-3">
                      <div>
                        <div className="font-medium text-white">{contract.name}</div>
                        <div className="text-xs text-gray-500">{contract.path}</div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      {getStatusBadge(contract.status)}
                    </td>
                    <td className="px-4 py-3">
                      {contract.is_compiled ? (
                        <span className="text-green-400 text-sm">
                          ✓ {contract.compiled_at && new Date(contract.compiled_at).toLocaleDateString()}
                        </span>
                      ) : (
                        <span className="text-gray-500 text-sm">Not compiled</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-gray-400">{contract.deployment_count}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex justify-end gap-2">
                        {!contract.is_compiled && (
                          <button
                            onClick={compileAllContracts}
                            className="p-2 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 rounded-lg transition-colors"
                            title="Compile"
                          >
                            <Zap className="w-4 h-4" />
                          </button>
                        )}
                        {contract.is_compiled && (
                          <button
                            onClick={() => prepareDeployment(contract)}
                            disabled={!isConnected}
                            className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-black disabled:text-gray-500 rounded-lg font-medium transition-colors text-sm"
                          >
                            Deploy
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Deployments Tab */}
      {activeTab === 'deployments' && (
        <div className="space-y-4">
          {deployments.length === 0 ? (
            <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-12 text-center">
              <Network className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 text-lg">No deployments yet</p>
              <p className="text-gray-500 text-sm mt-2">Deploy a contract to get started</p>
            </div>
          ) : (
            <div className="grid gap-4">
              {deployments.map((deployment) => (
                <motion.div
                  key={deployment.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 hover:border-gray-700 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <h3 className="text-lg font-semibold text-white">{deployment.contract_name}</h3>
                        {getStatusBadge(deployment.status)}
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          deployment.network === 'mainnet' 
                            ? 'bg-green-600/20 text-green-400'
                            : 'bg-blue-600/20 text-blue-400'
                        }`}>
                          {deployment.network}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500">Deployed:</span>
                          <span className="text-white ml-2">{deployment.deployed_at && new Date(deployment.deployed_at).toLocaleString()}</span>
                        </div>
                        {deployment.contract_address && (
                          <div className="flex items-center gap-2">
                            <span className="text-gray-500">Address:</span>
                            <code className="text-green-400 text-xs">{deployment.contract_address.slice(0, 10)}...</code>
                            <button
                              onClick={() => {
                                navigator.clipboard.writeText(deployment.contract_address!);
                                toast.success('Address copied');
                              }}
                              className="p-1 hover:bg-gray-700 rounded"
                            >
                              <Copy className="w-3 h-3 text-gray-400" />
                            </button>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex gap-2">
                      {deployment.contract_address && (
                        <a
                          href={`https://${deployment.network === 'mainnet' ? '' : deployment.network + '.'}etherscan.io/address/${deployment.contract_address}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-2 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 rounded-lg transition-colors"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Deploy Modal */}
      <AnimatePresence>
        {showDeployModal && selectedContract && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
            onClick={() => setShowDeployModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-gray-900 border border-gray-800 rounded-xl p-6 max-w-lg w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-bold text-white mb-4">Deploy Contract</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Contract</label>
                  <div className="text-white font-medium">{selectedContract.name}</div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Network</label>
                  <select
                    value={deployConfig.network}
                    onChange={(e) => setDeployConfig({ ...deployConfig, network: e.target.value })}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white"
                  >
                    <option value="sepolia">Sepolia Testnet</option>
                    <option value="mainnet">Ethereum Mainnet</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Deployer</label>
                  <code className="block bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white font-mono text-sm">
                    {address}
                  </code>
                </div>

                {chain && chain.id !== (deployConfig.network === 'mainnet' ? mainnet.id : sepolia.id) && (
                  <div className="bg-yellow-600/10 border border-yellow-500/20 rounded-lg p-4">
                    <div className="flex items-start gap-2">
                      <AlertTriangle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
                      <div className="text-sm text-yellow-500">
                        <p className="font-medium mb-1">Wrong Network</p>
                        <p className="text-yellow-400/80">
                          Your wallet is on {getNetworkName(chain.id)}. You'll be prompted to switch to {deployConfig.network}.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                <div className="bg-blue-600/10 border border-blue-500/20 rounded-lg p-4">
                  <div className="flex items-start gap-2">
                    <Info className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-blue-500">
                      <p className="font-medium mb-1">Direct Wallet Deployment</p>
                      <p className="text-blue-400/80">
                        This will deploy the contract directly from your wallet. You'll sign the transaction in your wallet.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    onClick={() => setShowDeployModal(false)}
                    className="flex-1 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={executeDeployment}
                    disabled={isDeploying || isConfirming}
                    className="flex-1 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-700 text-black disabled:text-gray-500 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                  >
                    {isDeploying || isConfirming ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        {isDeploying ? 'Deploying...' : 'Confirming...'}
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4" />
                        Deploy Now
                      </>
                    )}
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
