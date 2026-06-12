import { Doughnut } from 'react-chartjs-2'
import { Chart as ChartJS, ArcElement, Tooltip } from 'chart.js'

ChartJS.register(ArcElement, Tooltip)

export default function SecurityGauge({ score = 50 }) {
  const getColor = (s) => {
    if (s >= 70) return '#10b981'
    if (s >= 40) return '#f59e0b'
    return '#ef4444'
  }

  const getClass = (s) => {
    if (s >= 70) return 'score-safe'
    if (s >= 40) return 'score-moderate'
    return 'score-danger'
  }

  const data = {
    datasets: [{
      data: [score, 100 - score],
      backgroundColor: [getColor(score), '#e2e8f0'],
      borderWidth: 0,
      circumference: 180,
      rotation: 270,
    }],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '75%',
    plugins: { tooltip: { enabled: false } },
  }

  return (
    <div className="text-center">
      <div className="gauge-container">
        <Doughnut data={data} options={options} />
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -20%)' }}>
          <div className={`security-score-value ${getClass(score)}`}>{score}</div>
          <small className="text-muted">/ 100</small>
        </div>
      </div>
      <p className="mt-2 text-muted small">SMS Security Score</p>
    </div>
  )
}
