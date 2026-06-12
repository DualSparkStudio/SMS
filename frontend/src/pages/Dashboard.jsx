import { useEffect, useState } from 'react'
import { Pie, Line, Bar, Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS, ArcElement, CategoryScale, LinearScale,
  PointElement, LineElement, BarElement, Tooltip, Legend, Filler,
} from 'chart.js'
import { analyticsAPI } from '../api/client'

ChartJS.register(ArcElement, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Tooltip, Legend, Filler)

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { labels: { color: '#64748b' } } },
  scales: {
    x: { ticks: { color: '#64748b' }, grid: { color: '#e2e8f0' } },
    y: { ticks: { color: '#64748b' }, grid: { color: '#e2e8f0' } },
  },
}

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    analyticsAPI.dashboard().then(({ data: d }) => {
      setData(d)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading-spinner"><div className="spinner-border text-success" /></div>

  const spamHam = data?.spam_vs_ham || { labels: [], values: [] }
  const daily = data?.daily_detection || { labels: [], spam: [], ham: [] }
  const fraud = data?.fraud_categories || { labels: [], values: [] }
  const lang = data?.language_distribution || { labels: [], values: [] }
  const reports = data?.user_reports || { labels: [], correct: [], wrong: [] }

  return (
    <div className="page-container">
      <div className="container">
        <h2 className="page-title">Analytics Dashboard</h2>
        <p className="page-subtitle">Real-time spam detection trends and fraud analytics.</p>

        <div className="row g-3 mb-4">
          {[
            { label: 'Total Analyzed', value: data?.total_analyzed || 0 },
            { label: 'Spam Detected', value: data?.spam_count || 0 },
            { label: 'Legitimate (Ham)', value: data?.ham_count || 0 },
            { label: 'Feedback Accuracy', value: `${data?.accuracy_feedback || 100}%` },
          ].map((s, i) => (
            <div key={i} className="col-6 col-md-3">
              <div className="card card-hsds stat-card">
                <div className="stat-value">{s.value}</div>
                <div className="stat-label">{s.label}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="row g-4">
          <div className="col-md-6">
            <div className="card card-hsds p-4">
              <h6 className="mb-3">Spam vs Ham</h6>
              <div style={{ height: 280 }}>
                <Pie
                  data={{
                    labels: spamHam.labels,
                    datasets: [{ data: spamHam.values, backgroundColor: ['#ef4444', '#7c5cfc'] }],
                  }}
                  options={{ ...chartOptions, plugins: { legend: { position: 'bottom', labels: { color: '#64748b' } } } }}
                />
              </div>
            </div>
          </div>

          <div className="col-md-6">
            <div className="card card-hsds p-4">
              <h6 className="mb-3">Language Distribution</h6>
              <div style={{ height: 280 }}>
                <Doughnut
                  data={{
                    labels: lang.labels,
                    datasets: [{ data: lang.values, backgroundColor: ['#7c5cfc', '#6366f1', '#a78bfa', '#c4b5fd'] }],
                  }}
                  options={{ ...chartOptions, plugins: { legend: { position: 'bottom', labels: { color: '#64748b' } } } }}
                />
              </div>
            </div>
          </div>

          <div className="col-12">
            <div className="card card-hsds p-4">
              <h6 className="mb-3">Daily Detection Trend</h6>
              <div style={{ height: 300 }}>
                <Line
                  data={{
                    labels: daily.labels,
                    datasets: [
                      { label: 'Spam', data: daily.spam, borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,0.1)', fill: true, tension: 0.3 },
                      { label: 'Ham', data: daily.ham, borderColor: '#7c5cfc', backgroundColor: 'rgba(124,92,252,0.1)', fill: true, tension: 0.3 },
                    ],
                  }}
                  options={chartOptions}
                />
              </div>
            </div>
          </div>

          <div className="col-md-6">
            <div className="card card-hsds p-4">
              <h6 className="mb-3">Fraud Categories</h6>
              <div style={{ height: 280 }}>
                <Bar
                  data={{
                    labels: fraud.labels.length ? fraud.labels : ['No data'],
                    datasets: [{ label: 'Count', data: fraud.values.length ? fraud.values : [0], backgroundColor: '#f59e0b' }],
                  }}
                  options={chartOptions}
                />
              </div>
            </div>
          </div>

          <div className="col-md-6">
            <div className="card card-hsds p-4">
              <h6 className="mb-3">User Feedback Reports</h6>
              <div style={{ height: 280 }}>
                <Line
                  data={{
                    labels: reports.labels.length ? reports.labels : ['No data'],
                    datasets: [
                      { label: 'Correct', data: reports.correct, borderColor: '#10b981', tension: 0.3 },
                      { label: 'Wrong', data: reports.wrong, borderColor: '#ef4444', tension: 0.3 },
                    ],
                  }}
                  options={chartOptions}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
