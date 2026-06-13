import { Link } from 'react-router-dom'

const features = [
  { icon: '🔍', title: 'SMS Analysis', desc: 'Detect spam/ham with confidence scores and suspicious word identification.' },
  { icon: '🧠', title: 'Explainable AI', desc: 'Word-level explanations showing why a message was flagged.' },
  { icon: '🔗', title: 'Phishing Detection', desc: 'Analyze URLs for domain spoofing, suspicious TLDs, and fake login pages.' },
  { icon: '⚠️', title: 'Fraud Detection', desc: 'Identify banking fraud, lottery scams, fake jobs, and investment fraud.' },
  { icon: '🌐', title: 'Multilingual', desc: 'Support for English, Hindi, and Marathi with automatic language detection.' },
  { icon: '📊', title: 'Real-Time Analytics', desc: 'Comprehensive dashboard with spam trends, fraud categories, and reports.' },
  { icon: '🎯', title: 'Campaign Detection', desc: 'Cluster similar spam messages to detect coordinated scam campaigns.' },
  { icon: '🤖', title: 'AI Assistant', desc: 'Gemini-powered chatbot explains dangers and provides security advice.' },
]

const pipelineSteps = [
  'SMS Received', 'Language Detection', 'URL Analysis', 'Fraud Pattern Analysis',
  'ML Prediction', 'Explainable AI Layer', 'Security Score', 'Campaign Detection', 'Feedback Learning',
]

const heroStats = [
  { num: '98%+', label: 'ACCURACY' },
  { num: '<2s', label: 'RESPONSE TIME' },
  { num: '5', label: 'FRAUD CATEGORIES' },
  { num: '3', label: 'LANGUAGES' },
]

export default function Home() {
  return (
    <>
      <section className="hero-section">
        <div className="container">
          <div className="hero-badge">
            🛡️ AI-POWERED SECURITY
          </div>

          <h1 className="hero-title">
            Protect yourself from<br />
            <span className="gradient-text">SMS fraud &amp; phishing</span>
          </h1>

          <p className="hero-subtitle mb-4">
            Paste any SMS message and get an instant AI-powered risk assessment,
            fraud detection, and actionable security advice — powered by
            TextGuard.
          </p>

          <div className="d-flex gap-3 justify-content-center flex-wrap mb-2">
            <Link to="/detect" className="btn btn-hsds btn-lg px-4">
              Analyze SMS Now
            </Link>
          </div>

          <div className="hero-stats">
            {heroStats.map((s, i) => (
              <div key={i} className="hero-stat text-center">
                <div className="stat-num">{s.num}</div>
                <div className="stat-label">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="page-container pt-0">
        <div className="container">
          <h2 className="section-title">Platform Modules</h2>
          <div className="row g-4">
            {features.map((f, i) => (
              <div key={i} className="col-md-6 col-lg-3">
                <div className="card card-hsds h-100 p-4">
                  <div className="feature-icon">{f.icon}</div>
                  <h5 className="fw-bold">{f.title}</h5>
                  <p className="text-muted small mb-0">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="pb-5">
        <div className="container">
          <div className="row g-4 align-items-stretch">
            <div className="col-lg-5">
              <div className="card card-hsds p-4 h-100">
                <h5 className="fw-bold mb-3" style={{ color: 'var(--hsds-primary)' }}>
                  TextGuard Pipeline
                </h5>
                {pipelineSteps.map((step, i) => (
                  <div key={i} className="pipeline-step">
                    <span className="step-num">{i + 1}</span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="col-lg-7">
              <div className="card card-hsds p-4 h-100 text-center d-flex flex-column justify-content-center">
                <h4 className="fw-bold mb-4">Target Performance Metrics</h4>
                <div className="row">
                  {[
                    { val: '>98%', label: 'Accuracy' },
                    { val: '>97%', label: 'Precision' },
                    { val: '>97%', label: 'Recall' },
                    { val: '>97%', label: 'F1 Score' },
                  ].map((m, i) => (
                    <div key={i} className="col-6 col-md-3">
                      <div className="stat-card">
                        <div className="stat-value">{m.val}</div>
                        <div className="stat-label">{m.label}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
