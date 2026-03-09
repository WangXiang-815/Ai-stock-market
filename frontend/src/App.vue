<template>
  <div class="page">
    <div class="container">
      <h1>AI Stock Suggestion System</h1>
      <p class="subtitle">
        Enter any stock ticker to generate a model signal and AI explanation.
      </p>

      <div class="controls">
        <div class="input-group">
          <label for="ticker">Stock Ticker</label>
          <input
            id="ticker"
            v-model="selectedTicker"
            type="text"
            placeholder="e.g. NVDA, TSLA, AMD, META"
          />
        </div>

        <button @click="fetchSuggestion" :disabled="loading">
          {{ loading ? "Generating..." : "Generate Suggestion" }}
        </button>
      </div>

      <div v-if="error" class="card error">
        <h2>Error</h2>
        <p>{{ error }}</p>
      </div>

      <div v-if="result" class="results">
        <div class="card chart-card">
          <h2>Price Trend (6 Months)</h2>
          <canvas id="priceChart"></canvas>
        </div>

        <div class="card">
          <h2>Model Signal</h2>

          <div class="grid">
            <div><strong>Ticker:</strong> {{ result.model_signal.ticker }}</div>
            <div><strong>Date:</strong> {{ result.model_signal.prediction_date }}</div>
            <div><strong>Horizon:</strong> {{ result.model_signal.horizon_days }} days</div>
            <div><strong>Model:</strong> {{ result.model_signal.model_name }}</div>
          </div>

          <div class="action-row">
            <span class="label">Action:</span>
            <span class="badge" :class="getActionClass(result.model_signal.action)">
              {{ result.model_signal.action }}
            </span>
          </div>

          <h3>Probabilities</h3>
          <div class="probabilities">
            <div class="prob-item sell">
              <span>SELL</span>
              <span>{{ toPercent(result.model_signal.probabilities.SELL) }}</span>
            </div>
            <div class="prob-item hold">
              <span>HOLD</span>
              <span>{{ toPercent(result.model_signal.probabilities.HOLD) }}</span>
            </div>
            <div class="prob-item buy">
              <span>BUY</span>
              <span>{{ toPercent(result.model_signal.probabilities.BUY) }}</span>
            </div>
          </div>

          <h3>Features Used</h3>
          <div class="tags">
            <span
              v-for="feature in result.model_signal.features_used"
              :key="feature"
              class="tag"
            >
              {{ feature }}
            </span>
          </div>

          <h3>Notes</h3>
          <ul>
            <li v-for="note in result.model_signal.notes" :key="note">{{ note }}</li>
          </ul>
        </div>

        <div class="card">
          <h2>LLM Explanation</h2>

          <div class="grid">
            <div><strong>Suggestion:</strong> {{ result.llm_explanation.suggestion }}</div>
            <div><strong>Confidence:</strong> {{ result.llm_explanation.confidence_level }}</div>
          </div>

          <h3>Summary</h3>
          <p>{{ result.llm_explanation.summary }}</p>

          <h3>Reasoning</h3>
          <ul v-if="Array.isArray(result.llm_explanation.reasoning)">
            <li
              v-for="item in result.llm_explanation.reasoning"
              :key="item"
            >
              {{ item }}
            </li>
          </ul>
          <p v-else>{{ result.llm_explanation.reasoning }}</p>

          <h3>Risk Warning</h3>
          <ul v-if="Array.isArray(result.llm_explanation.risk_warning)">
            <li
              v-for="item in result.llm_explanation.risk_warning"
              :key="item"
            >
              {{ item }}
            </li>
          </ul>
          <p v-else>{{ result.llm_explanation.risk_warning }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from "vue";
import { Chart } from "chart.js/auto";

const selectedTicker = ref("NVDA");
const loading = ref(false);
const error = ref("");
const result = ref(null);

const API_BASE = "http://127.0.0.1:8000";

const toPercent = (value) => `${(value * 100).toFixed(2)}%`;

const getActionClass = (action) => {
  if (action === "BUY") return "buy";
  if (action === "SELL") return "sell";
  return "hold";
};

const renderChart = async (prices) => {
  await nextTick();

  const canvas = document.getElementById("priceChart");
  if (!canvas) return;

  if (window.stockChart) {
    window.stockChart.destroy();
  }

  const labels = prices.map((p) => p.date);
  const values = prices.map((p) => p.close);

  window.stockChart = new Chart(canvas, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Close Price",
          data: values,
          borderColor: "#2563eb",
          backgroundColor: "rgba(37, 99, 235, 0.12)",
          fill: true,
          tension: 0.25,
          pointRadius: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true
        }
      },
      scales: {
        x: {
          ticks: {
            maxTicksLimit: 8
          }
        }
      }
    }
  });
};

const fetchSuggestion = async () => {
  loading.value = true;
  error.value = "";
  result.value = null;

  try {
    const ticker = selectedTicker.value.trim().toUpperCase();

    if (!ticker) {
      throw new Error("Please enter a valid stock ticker.");
    }

    const explainResponse = await fetch(`${API_BASE}/explain?ticker=${ticker}`);
    if (!explainResponse.ok) {
      const text = await explainResponse.text();
      throw new Error(text || "Failed to fetch explanation.");
    }

    const explainData = await explainResponse.json();
    result.value = explainData;

    const priceResponse = await fetch(`${API_BASE}/price-history?ticker=${ticker}`);
    if (!priceResponse.ok) {
      const text = await priceResponse.text();
      throw new Error(text || "Failed to fetch price history.");
    }

    const priceData = await priceResponse.json();
    await renderChart(priceData.prices);

  } catch (err) {
    error.value = err.message || "Unknown error occurred.";
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f7fb;
  padding: 32px 16px;
  color: #1f2937;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  margin-bottom: 8px;
  font-size: 32px;
}

.subtitle {
  margin-bottom: 24px;
  color: #6b7280;
}

.controls {
  display: flex;
  align-items: end;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

.input-group {
  display: flex;
  flex-direction: column;
  min-width: 280px;
}

label {
  font-weight: 600;
  margin-bottom: 6px;
}

input,
button {
  height: 44px;
  padding: 0 14px;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  font-size: 14px;
}

input {
  background: white;
}

button {
  background: #111827;
  color: white;
  cursor: pointer;
  border: none;
  font-weight: 600;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.results {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.08);
}

.chart-card {
  grid-column: 1 / -1;
  height: 420px;
}

.error {
  border-left: 4px solid #ef4444;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 16px;
}

.action-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 16px 0;
}

.label {
  font-weight: 600;
}

.badge {
  padding: 6px 12px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 13px;
}

.badge.buy {
  background: #dcfce7;
  color: #166534;
}

.badge.sell {
  background: #fee2e2;
  color: #991b1b;
}

.badge.hold {
  background: #fef3c7;
  color: #92400e;
}

.probabilities {
  display: grid;
  gap: 10px;
  margin-bottom: 16px;
}

.prob-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 10px;
  font-weight: 600;
}

.prob-item.sell {
  background: #fef2f2;
}

.prob-item.hold {
  background: #fffbeb;
}

.prob-item.buy {
  background: #f0fdf4;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.tag {
  background: #eef2ff;
  color: #3730a3;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
}

ul {
  padding-left: 18px;
}

li {
  margin-bottom: 8px;
}

@media (max-width: 900px) {
  .results {
    grid-template-columns: 1fr;
  }

  .grid {
    grid-template-columns: 1fr;
  }
}
</style>