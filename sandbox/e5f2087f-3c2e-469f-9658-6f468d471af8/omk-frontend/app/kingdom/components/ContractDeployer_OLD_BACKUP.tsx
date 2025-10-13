'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileCode, Play, CheckCircle, XCircle, Clock, AlertTriangle,
  Loader2, Network, Settings, Trash2, ExternalLink, RefreshCw,
  Zap, Shield, DollarSign, Copy, ChevronRight, Info
} from 'lucide-react';
import { toast } from 'react-hot-toast';

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

  useEffect(() => {
    loadContracts();
    loadDeployments();
  }, []);

  const loadContracts = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/v1/admin/contracts', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
      });
      const data = await response.json();
      if (data.success) {
        setContracts(data.contracts);
      }
    } catch (error) {
      toast.error('Failed to load contracts');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const loadDeployments = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/v1/admin/contracts/deployments', {
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
      const response = await fetch('http://localhost:8001/api/v1/admin/contracts/compile', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      if (data.success) {
        toast.success('✅ All contracts compiled successfully!');
        loadContracts();
      } else {
        toast.error('Compilation failed');
        console.error(data.output);
      }
    } catch (error) {
      toast.error('Compilation error');
      console.error(error);
    } finally {
      setCompiling(false);
    }
  };

  const prepareDeployment = async (contract: Contract) => {
    setSelectedContract(contract);
    setShowDeployModal(true);
  };

  const executePrepareDeployment = async () => {
    if (!selectedContract) return;

    try {
      const response = await fetch(`http://localhost:8001/api/v1/admin/contracts/${selectedContract.name}/deploy`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          contract_name: selectedContract.name,
          network: deployConfig.network,
          constructor_args: [],
          gas_limit: deployConfig.gasLimit,
          gas_price: deployConfig.gasPrice
        })
      });

      const data = await response.json();
      if (data.success) {
        toast.success(`✅ Deployment prepared for ${selectedContract.name}`);
        setShowDeployModal(false);
        loadContracts();
        loadDeployments();
      } else {
        toast.error(data.error || 'Failed to prepare deployment');
      }
    } catch (error) {
      toast.error('Deployment preparation failed');
      console.error(error);
    }
  };

  const executeDeployment = async (deploymentId: string) => {
    const confirmed = window.confirm(
      '⚠️ WARNING: This will deploy the contract to the blockchain.\n\n' +
      'This action:\n' +
      '• Costs real gas fees\n' +
      '• Cannot be undone\n' +
      '• Will be recorded on-chain\n\n' +
      'Are you sure you want to proceed?'
    );

    if (!confirmed) return;

    try {
      const response = await fetch(`http://localhost:8001/api/v1/admin/contracts/${deploymentId}/execute`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();
      if (data.success) {
        toast.success('🚀 Contract deployed successfully!');
        loadDeployments();
      } else {
        // Show the placeholder message
        toast.error(data.message || data.error || 'Deployment failed');
        if (data.command) {
          console.log('Manual deployment command:', data.command);
        }
      }
    } catch (error) {
      toast.error('Deployment execution failed');
      console.error(error);
    }
  };

  const cancelDeployment = async (deploymentId: string) => {
    try {
      const response = await fetch(`http://localhost:8001/api/v1/admin/contracts/deployments/${deploymentId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
      });

      const data = await response.json();
      if (data.success) {
        toast.success('Deployment cancelled');
        loadDeployments();
      }
    } catch (error) {
      toast.error('Failed to cancel deployment');
      console.error(error);
    }
  };

  const toggleContractSelection = (contractName: string) => {
    const newSelection = new Set(selectedContracts);
    if (newSelection.has(contractName)) {
      newSelection.delete(contractName);
    } else {
      newSelection.add(contractName);
    }
    setSelectedContracts(newSelection);
  };

  const batchPrepareDeployment = async () => {
    if (selectedContracts.size === 0) {
      toast.error('No contracts selected');
      return;
    }

    try {
      const contractsArray = Array.from(selectedContracts).map(name => ({
        contract_name: name,
        network: deployConfig.network,
        constructor_args: [],
        gas_limit: deployConfig.gasLimit,
        gas_price: deployConfig.gasPrice
      }));

      const response = await fetch('http://localhost:8001/api/v1/admin/contracts/batch-deploy', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          contracts: contractsArray,
          network: deployConfig.network
        })
      });

      const data = await response.json();
      if (data.success) {
        toast.success(`✅ ${data.message}`);
        setSelectedContracts(new Set());
        loadContracts();
        loadDeployments();
      }
    } catch (error) {
      toast.error('Batch deployment failed');
      console.error(error);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
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
      {/* Header */}
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
                  <button
                    onClick={batchPrepareDeployment}
                    className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 text-black rounded text-sm font-medium"
                  >
                    Prepare Batch Deployment
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
                      checked={selectedContracts.size === contracts.length}
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
                        onChange={() => toggleContractSelection(contract.name)}
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
                            className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 text-black rounded-lg font-medium transition-colors text-sm"
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
              <p className="text-gray-500 text-sm mt-2">Prepare a contract deployment to get started</p>
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
                          <span className="text-gray-500">Prepared:</span>
                          <span className="text-white ml-2">{new Date(deployment.created_at).toLocaleString()}</span>
                        </div>
                        {deployment.contract_address && (
                          <div className="flex items-center gap-2">
                            <span className="text-gray-500">Address:</span>
                            <code className="text-green-400 text-xs">{deployment.contract_address.slice(0, 10)}...</code>
                            <button
                              onClick={() => copyToClipboard(deployment.contract_address!)}
                              className="p-1 hover:bg-gray-700 rounded"
                            >
                              <Copy className="w-3 h-3 text-gray-400" />
                            </button>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex gap-2">
                      {deployment.status === 'prepared' && (
                        <>
                          <button
                            onClick={() => executeDeployment(deployment.id)}
                            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
                          >
                            <Play className="w-4 h-4" />
                            Execute Deploy
                          </button>
                          <button
                            onClick={() => cancelDeployment(deployment.id)}
                            className="p-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </>
                      )}
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
              <h3 className="text-xl font-bold text-white mb-4">Prepare Deployment</h3>
              
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
                    <option value="localhost">Localhost (Testing)</option>
                    <option value="sepolia">Sepolia Testnet</option>
                    <option value="mainnet">Ethereum Mainnet</option>
                  </select>
                </div>

                <div className="bg-yellow-600/10 border border-yellow-500/20 rounded-lg p-4">
                  <div className="flex items-start gap-2">
                    <Info className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-yellow-500">
                      <p className="font-medium mb-1">Review Required</p>
                      <p className="text-yellow-400/80">
                        This will prepare the deployment. You'll need to review and execute it from the Deployments tab.
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
                    onClick={executePrepareDeployment}
                    className="flex-1 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-black rounded-lg font-medium transition-colors"
                  >
                    Prepare Deployment
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
