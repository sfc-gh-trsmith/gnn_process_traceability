import { useState } from 'react'
import { motion } from 'framer-motion'
import { Database, Cpu, BarChart3, Shield, Zap, Code } from 'lucide-react'

const tabs = ['Executive Overview', 'Technical Deep-Dive']

export default function About() {
  const [activeTab, setActiveTab] = useState(0)

  return (
    <div className="space-y-6">
      <div className="rounded-xl bg-gradient-to-br from-primary/20 to-secondary/20 border border-primary/30 p-8">
        <h1 className="text-2xl font-bold text-text-primary mb-2">
          GNN Process Traceability
        </h1>
        <p className="text-text-secondary max-w-3xl">
          An AI-powered manufacturing analytics solution that uses Graph Neural Networks 
          to trace defects through the supply chain and identify hidden root cause patterns.
        </p>
      </div>

      <div className="flex gap-2 border-b border-border pb-1">
        {tabs.map((tab, i) => (
          <button
            key={tab}
            onClick={() => setActiveTab(i)}
            className={`px-4 py-2 rounded-t-lg font-medium transition-colors ${
              activeTab === i
                ? 'bg-card text-primary border border-border border-b-0'
                : 'text-text-secondary hover:text-text-primary'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {activeTab === 0 && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="rounded-xl bg-card border border-border p-6">
                <h3 className="text-lg font-semibold text-critical mb-3">The Problem</h3>
                <ul className="space-y-2 text-text-secondary">
                  <li>• Manufacturing defects cost billions annually</li>
                  <li>• Traditional analysis misses complex patterns</li>
                  <li>• Root causes span multiple supply chain stages</li>
                  <li>• Manual investigation is slow and incomplete</li>
                </ul>
              </div>
              <div className="rounded-xl bg-card border border-border p-6">
                <h3 className="text-lg font-semibold text-success mb-3">The Solution</h3>
                <ul className="space-y-2 text-text-secondary">
                  <li>• GNN models capture supply chain structure</li>
                  <li>• Automated pattern discovery across entities</li>
                  <li>• Real-time risk scoring and alerts</li>
                  <li>• AI-generated actionable insights</li>
                </ul>
              </div>
            </div>

            <div className="rounded-xl bg-card border border-border p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">Key Discoveries</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-critical/10 border border-critical/30">
                  <h4 className="font-medium text-critical">Pattern 1: Vulcan Steel Batch 2847</h4>
                  <p className="text-sm text-text-secondary mt-1">
                    92% correlation with Surface Defects - specific batch from Vulcan Steel 
                    shows significantly elevated defect rates
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-warning/10 border border-warning/30">
                  <h4 className="font-medium text-warning">Pattern 2: Heat Treatment + HD-Series</h4>
                  <p className="text-sm text-text-secondary mt-1">
                    85% correlation with Dimensional Errors - combination of Line 3 heat 
                    treatment and HD-Series products
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-xl bg-card border border-border p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">Business Impact</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-3 px-4 text-text-secondary">Metric</th>
                      <th className="text-left py-3 px-4 text-text-secondary">Before</th>
                      <th className="text-left py-3 px-4 text-text-secondary">After</th>
                      <th className="text-left py-3 px-4 text-text-secondary">Impact</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-border">
                      <td className="py-3 px-4">Defect Rate</td>
                      <td className="py-3 px-4">4.2%</td>
                      <td className="py-3 px-4 text-success">2.1%</td>
                      <td className="py-3 px-4 text-success">-50%</td>
                    </tr>
                    <tr className="border-b border-border">
                      <td className="py-3 px-4">Root Cause Time</td>
                      <td className="py-3 px-4">5 days</td>
                      <td className="py-3 px-4 text-success">4 hours</td>
                      <td className="py-3 px-4 text-success">-97%</td>
                    </tr>
                    <tr className="border-b border-border">
                      <td className="py-3 px-4">Supplier Audits</td>
                      <td className="py-3 px-4">Random</td>
                      <td className="py-3 px-4 text-success">Risk-based</td>
                      <td className="py-3 px-4 text-success">3x efficiency</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 1 && (
          <div className="space-y-6">
            <div className="rounded-xl bg-card border border-border p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">Data Architecture</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-lg bg-accent/10 border border-accent/30">
                  <Database className="w-6 h-6 text-accent mb-2" />
                  <h4 className="font-medium text-accent">Bronze Layer</h4>
                  <p className="text-sm text-text-secondary mt-1">
                    Raw data: Suppliers, Materials, Work Orders, Process Steps, Parameters, Defects, Stations
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-purple/10 border border-purple/30">
                  <Cpu className="w-6 h-6 text-purple mb-2" />
                  <h4 className="font-medium text-purple">Silver Layer</h4>
                  <p className="text-sm text-text-secondary mt-1">
                    GNN embeddings, feature engineering, relationship mapping, temporal aggregations
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-primary/10 border border-primary/30">
                  <BarChart3 className="w-6 h-6 text-primary mb-2" />
                  <h4 className="font-medium text-primary">Gold Layer</h4>
                  <p className="text-sm text-text-secondary mt-1">
                    Root cause analysis, risk scores, defect correlations, path analysis
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-xl bg-card border border-border p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">Technology Stack</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { icon: Database, label: 'Snowflake', desc: 'Data Platform' },
                  { icon: Cpu, label: 'PyTorch Geometric', desc: 'GNN Framework' },
                  { icon: Shield, label: 'Cortex AI', desc: 'LLM Insights' },
                  { icon: Zap, label: 'React + FastAPI', desc: 'Full-Stack' },
                ].map((tech, i) => (
                  <div key={i} className="p-4 rounded-lg bg-background text-center">
                    <tech.icon className="w-8 h-8 text-primary mx-auto mb-2" />
                    <p className="font-medium text-text-primary">{tech.label}</p>
                    <p className="text-xs text-text-secondary">{tech.desc}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-xl bg-card border border-border p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">GNN Architecture</h3>
              <div className="space-y-3">
                {[
                  { step: 1, title: 'Graph Construction', desc: 'Build heterogeneous graph from supply chain entities (suppliers, materials, work orders, stations)' },
                  { step: 2, title: 'Feature Encoding', desc: 'Encode node features including process parameters, temporal patterns, and categorical embeddings' },
                  { step: 3, title: 'Message Passing', desc: 'GraphSAGE layers aggregate neighborhood information through supply chain connections' },
                  { step: 4, title: 'Risk Prediction', desc: 'Final MLP layers predict defect probability and risk scores for each entity' },
                ].map((item) => (
                  <div key={item.step} className="flex items-start gap-4 p-4 rounded-lg bg-background">
                    <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-semibold flex-shrink-0">
                      {item.step}
                    </div>
                    <div>
                      <h4 className="font-medium text-text-primary">{item.title}</h4>
                      <p className="text-sm text-text-secondary mt-0.5">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-xl bg-card border border-border p-6">
              <div className="flex items-center gap-2 mb-4">
                <Code className="w-5 h-5 text-primary" />
                <h3 className="text-lg font-semibold text-text-primary">API Endpoints</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm font-mono">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-2 px-3 text-text-secondary">Method</th>
                      <th className="text-left py-2 px-3 text-text-secondary">Endpoint</th>
                      <th className="text-left py-2 px-3 text-text-secondary">Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      ['GET', '/api/health', 'Snowflake connection status'],
                      ['GET', '/api/summary/metrics', 'Dashboard KPIs'],
                      ['GET', '/api/network/flow', 'Sankey diagram data'],
                      ['GET', '/api/risk/root-causes', 'Root cause patterns'],
                      ['GET', '/api/risk/scores', 'Entity risk scores'],
                    ].map(([method, endpoint, desc], i) => (
                      <tr key={i} className="border-b border-border">
                        <td className="py-2 px-3 text-success">{method}</td>
                        <td className="py-2 px-3 text-primary">{endpoint}</td>
                        <td className="py-2 px-3 text-text-secondary">{desc}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  )
}
