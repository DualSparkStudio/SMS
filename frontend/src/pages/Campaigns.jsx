import { useEffect, useState } from 'react'
import { campaignAPI } from '../api/client'

const riskColors = { critical: 'danger', high: 'warning', medium: 'info', low: 'success' }

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    loadCampaigns()
  }, [])

  const loadCampaigns = (refresh = false) => {
    if (refresh) setRefreshing(true)
    const request = refresh ? campaignAPI.detect().then(() => campaignAPI.list()) : campaignAPI.list()
    request
      .then(({ data }) => {
        setCampaigns(data.results || data)
      })
      .catch(() => {})
      .finally(() => {
        setLoading(false)
        setRefreshing(false)
      })
  }

  if (loading) return <div className="loading-spinner"><div className="spinner-border text-success" /></div>

  return (
    <div className="page-container">
      <div className="container">
        <div className="d-flex justify-content-between align-items-start flex-wrap gap-2 mb-2">
          <div>
            <h2 className="page-title mb-1">Spam Campaign Monitor</h2>
            <p className="page-subtitle mb-0">
              Detected spam, scam, and bulk marketing campaigns from similar messages.
            </p>
          </div>
          <button
            type="button"
            className="btn btn-outline-hsds btn-sm"
            onClick={() => loadCampaigns(true)}
            disabled={refreshing}
          >
            {refreshing ? 'Scanning...' : 'Refresh Campaigns'}
          </button>
        </div>

        {campaigns.length === 0 ? (
          <div className="card card-hsds p-5 text-center">
            <h5>No campaigns detected yet</h5>
            <p className="text-muted">
              Analyze promotional or spam messages (especially bulk templates with {'{{placeholders}}'}) to detect campaigns.
            </p>
          </div>
        ) : (
          <div className="row g-4">
            {campaigns.map((c) => (
              <div key={c.id} className="col-md-6">
                <div className="card card-hsds p-4 h-100">
                  <div className="d-flex justify-content-between align-items-start mb-3">
                    <h5 className="mb-0">{c.campaign_name}</h5>
                    <span className={`badge bg-${riskColors[c.risk_level] || 'secondary'}`}>
                      {c.risk_level?.toUpperCase()}
                    </span>
                  </div>

                  <div className="row g-2 mb-3">
                    <div className="col-4">
                      <small className="text-muted d-block">Messages</small>
                      <strong>{c.message_count}</strong>
                    </div>
                    <div className="col-4">
                      <small className="text-muted d-block">Affected Users</small>
                      <strong>{c.affected_users}</strong>
                    </div>
                    <div className="col-4">
                      <small className="text-muted d-block">Risk Score</small>
                      <strong>{c.risk_score}%</strong>
                    </div>
                  </div>

                  <div className="mb-3">
                    <small className="text-muted">Keywords:</small>
                    <div className="d-flex flex-wrap gap-1 mt-1">
                      {(c.cluster_keywords || []).map((k, i) => (
                        <span key={i} className="badge bg-secondary">{k}</span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <small className="text-muted">Sample Messages:</small>
                    {[...new Set(c.sample_messages || [])].slice(0, 2).map((m, i) => (
                      <p key={i} className="small mb-1 mt-1 p-2 rounded sample-box">
                        "{m}{m.length >= 150 ? '...' : ''}"
                      </p>
                    ))}
                  </div>

                  <div className="mt-3">
                    <span className={`badge ${
                      c.campaign_type === 'scam' ? 'badge-spam'
                        : c.campaign_type === 'marketing' ? 'bg-info text-dark'
                          : 'bg-warning text-dark'
                    }`}>
                      {c.campaign_type?.toUpperCase()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
