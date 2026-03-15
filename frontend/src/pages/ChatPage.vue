<template>
  <div class="chat-layout">
    <aside class="sidebar">
      <h2>AI Chat</h2>

      <button class="new-chat-btn" @click="resetChat">+ New Chat</button>

      <div class="history">
        <h3>Recent Chat</h3>
        <div class="history-item" v-for="item in history" :key="item">
          {{ item }}
        </div>
      </div>
    </aside>

    <section class="chat-main">
      <div class="chat-header">
        <h2>Chat Box</h2>
      </div>

      <div class="chat-body">
        <div class="message assistant">
          <div class="bubble">
            Hello! I'm your AI assistant. Enter a stock ticker below and I will compare two LLM explanations for the same model signal.
          </div>
        </div>

        <div v-for="(msg, index) in messages" :key="index">
          <div v-if="msg.role === 'user'" class="message user">
            <div class="bubble">{{ msg.content }}</div>
          </div>

          <div v-else class="message assistant">
            <div class="bubble compare-bubble">
              <div class="result-block">
                <h3>Model Signal</h3>
                <p><strong>Ticker:</strong> {{ msg.data.model_signal.ticker }}</p>
                <p><strong>Action:</strong> {{ msg.data.model_signal.action }}</p>
                <p>
                  <strong>Probabilities:</strong>
                  SELL {{ toPercent(msg.data.model_signal.probabilities.SELL) }},
                  HOLD {{ toPercent(msg.data.model_signal.probabilities.HOLD) }},
                  BUY {{ toPercent(msg.data.model_signal.probabilities.BUY) }}
                </p>
              </div>

              <div class="result-block">
                <h3>{{ msg.data.deepseek_explanation.model_name }}</h3>
                <p><strong>Suggestion:</strong> {{ msg.data.deepseek_explanation.suggestion }}</p>
                <p><strong>Summary:</strong> {{ msg.data.deepseek_explanation.summary }}</p>
              </div>

              <div class="result-block">
                <h3>{{ msg.data.other_llm_explanation.model_name }}</h3>
                <p><strong>Suggestion:</strong> {{ msg.data.other_llm_explanation.suggestion }}</p>
                <p><strong>Summary:</strong> {{ msg.data.other_llm_explanation.summary }}</p>
              </div>
            </div>
          </div>
        </div>

        <div v-if="loading" class="message assistant">
          <div class="bubble">Generating comparison...</div>
        </div>

        <div v-if="error" class="message assistant">
          <div class="bubble error">{{ error }}</div>
        </div>
      </div>

      <div class="chat-input">
        <input
          v-model="tickerInput"
          placeholder="Type a ticker, e.g. NVDA"
          @keyup.enter="sendMessage"
        />
        <button @click="sendMessage">Send</button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from "vue";

const API_BASE = "http://127.0.0.1:8000";

const tickerInput = ref("");
const loading = ref(false);
const error = ref("");
const messages = ref([]);
const history = ref([]);

const toPercent = (value) => `${(value * 100).toFixed(2)}%`;

const sendMessage = async () => {
  const ticker = tickerInput.value.trim().toUpperCase();
  if (!ticker) return;

  messages.value.push({
    role: "user",
    content: `Can you analyze ${ticker} stock for me?`
  });

  loading.value = true;
  error.value = "";

  try {
    const response = await fetch(`${API_BASE}/compare?ticker=${ticker}`);
    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || "Failed to fetch comparison.");
    }

    const data = await response.json();

    messages.value.push({
      role: "assistant",
      data
    });

    history.value.unshift(`Prediction about ${ticker}`);
    if (history.value.length > 5) {
      history.value.pop();
    }

    tickerInput.value = "";
  } catch (err) {
    error.value = err.message || "Unknown error occurred.";
  } finally {
    loading.value = false;
  }
};

const resetChat = () => {
  messages.value = [];
  error.value = "";
  tickerInput.value = "";
};
</script>

<style scoped>
.chat-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 24px;
  min-height: calc(100vh - 120px);
}

.sidebar {
  background: white;
  border-radius: 20px;
  padding: 20px;
  border: 1px solid #ececec;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
}

.new-chat-btn {
  width: 100%;
  height: 44px;
  border: none;
  border-radius: 12px;
  background: #f4b51d;
  color: white;
  font-weight: 700;
  cursor: pointer;
  margin: 12px 0 24px;
}

.history h3 {
  margin-bottom: 12px;
}

.history-item {
  padding: 12px;
  background: #faf5e8;
  border-radius: 10px;
  margin-bottom: 10px;
  font-size: 14px;
}

.chat-main {
  background: white;
  border-radius: 20px;
  border: 1px solid #ececec;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  min-height: 700px;
}

.chat-header {
  padding: 20px 24px;
  border-bottom: 1px solid #ececec;
}

.chat-body {
  flex: 1;
  padding: 20px 24px;
  overflow-y: auto;
}

.message {
  display: flex;
  margin-bottom: 18px;
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.bubble {
  max-width: 78%;
  background: #f8f0df;
  padding: 14px 16px;
  border-radius: 16px;
  line-height: 1.6;
}

.message.user .bubble {
  background: #f3eef3;
}

.compare-bubble {
  width: 100%;
  max-width: 100%;
}

.result-block {
  background: #fffaf0;
  border: 1px solid #f1e4b7;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 14px;
}

.chat-input {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #ececec;
}

.chat-input input {
  flex: 1;
  height: 44px;
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 0 14px;
}

.chat-input button {
  width: 100px;
  border: none;
  border-radius: 10px;
  background: #f4b51d;
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.error {
  color: #ef4444;
}

@media (max-width: 900px) {
  .chat-layout {
    grid-template-columns: 1fr;
  }
}
</style>