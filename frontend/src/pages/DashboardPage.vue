<template>
  <div>
    <h1 class="page-title">Stock Information</h1>

    <div class="search-bar">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search stocks by symbol or name..."
      />
    </div>

    <div v-if="loading" class="info-box">Loading dashboard...</div>
    <div v-if="error" class="info-box error">{{ error }}</div>

    <div class="stock-grid" v-if="filteredStocks.length">
      <div class="stock-card" v-for="stock in filteredStocks" :key="stock.ticker">
        <div class="card-top">
          <div>
            <div class="ticker">{{ stock.ticker }}</div>
            <div class="company">{{ stock.company_name }}</div>
          </div>
          <span class="live-tag">Live</span>
        </div>

        <div class="price">\${{ stock.price.toFixed(2) }}</div>
        <div
          class="change"
          :class="stock.change >= 0 ? 'positive' : 'negative'"
        >
          {{ stock.change >= 0 ? "↗" : "↘" }}
          {{ stock.change >= 0 ? "+" : "" }}\${{ stock.change }}
          ({{ stock.change_pct >= 0 ? "+" : "" }}{{ stock.change_pct }}%)
        </div>

        <div class="section-label">AI Prediction</div>

        <div class="signal-row">
          <div class="prob-bar">
            <div
              class="prob-fill"
              :class="getActionClass(stock.action)"
              :style="{ width: stock.confidence + '%' }"
            ></div>
          </div>

          <span class="action-pill" :class="getActionClass(stock.action)">
            {{ stock.action }}
          </span>
        </div>

        <div class="prob-labels">
          <span>SELL</span>
          <span>HOLD</span>
          <span>BUY</span>
        </div>

        <div class="confidence">{{ stock.confidence.toFixed(2) }}% confidence</div>

        <div class="meta-row">
          <div><strong>Volume:</strong> {{ stock.volume_m }}M</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";

const API_BASE = "http://127.0.0.1:8000";

const stocks = ref([]);
const loading = ref(false);
const error = ref("");
const searchQuery = ref("");

const fetchDashboard = async () => {
  loading.value = true;
  error.value = "";

  try {
    const response = await fetch(`${API_BASE}/stocks-overview`);
    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || "Failed to fetch dashboard data.");
    }

    const data = await response.json();
    stocks.value = data.stocks || [];
  } catch (err) {
    error.value = err.message || "Unknown error occurred.";
  } finally {
    loading.value = false;
  }
};

const filteredStocks = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return stocks.value;

  return stocks.value.filter((stock) =>
    stock.ticker.toLowerCase().includes(q) ||
    stock.company_name.toLowerCase().includes(q)
  );
});

const getActionClass = (action) => {
  if (action === "BUY") return "buy";
  if (action === "SELL") return "sell";
  return "hold";
};

onMounted(() => {
  fetchDashboard();
});
</script>

<style scoped>
.page-title {
  font-size: 28px;
  margin-bottom: 20px;
}

.search-bar {
  margin-bottom: 20px;
}

.search-bar input {
  width: 100%;
  height: 44px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 0 14px;
  background: white;
}

.stock-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.stock-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid #ececec;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 16px;
}

.ticker {
  font-size: 28px;
  font-weight: 700;
}

.company {
  color: #6b7280;
  font-size: 14px;
}

.live-tag {
  background: #f3f4f6;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 600;
}

.price {
  font-size: 40px;
  font-weight: 700;
  margin-bottom: 8px;
}

.change {
  font-size: 14px;
  margin-bottom: 14px;
}

.positive {
  color: #16a34a;
}

.negative {
  color: #ef4444;
}

.section-label {
  font-weight: 600;
  margin-bottom: 8px;
}

.signal-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.prob-bar {
  flex: 1;
  height: 14px;
  background: #e5e7eb;
  border-radius: 999px;
  overflow: hidden;
}

.prob-fill {
  height: 100%;
  border-radius: 999px;
}

.prob-fill.buy {
  background: #22c55e;
}

.prob-fill.sell {
  background: #ef4444;
}

.prob-fill.hold {
  background: #f4b51d;
}

.action-pill {
  padding: 6px 10px;
  border-radius: 999px;
  color: white;
  font-weight: 700;
  font-size: 12px;
}

.action-pill.buy {
  background: #22c55e;
}

.action-pill.sell {
  background: #ef4444;
}

.action-pill.hold {
  background: #f4b51d;
}

.prob-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #6b7280;
  margin-top: 8px;
}

.confidence {
  margin-top: 10px;
  font-size: 14px;
  color: #6b7280;
}

.meta-row {
  margin-top: 16px;
  font-size: 14px;
}

.info-box {
  padding: 16px;
  border-radius: 10px;
  background: white;
}

.error {
  color: #ef4444;
}

@media (max-width: 1000px) {
  .stock-grid {
    grid-template-columns: 1fr;
  }
}
</style>