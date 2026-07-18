<template>
  <div class="app">
    <!-- Safety banner -->
    <div class="safety-banner">
      ⚠️ <strong>Educational tool only.</strong> Never eat a wild mushroom or plant based on this app.
      AI can be wrong — always confirm with a qualified local expert.
    </div>

    <header class="header">
      <div class="brand">
        <span class="logo">🍄</span>
        <div>
          <h1>ForageSafe</h1>
          <p class="tagline">AI foraging safety checks, verified on GenLayer</p>
        </div>
      </div>

      <div class="account">
        <template v-if="address">
          <span class="addr" :title="address">{{ short(address) }}</span>
          <a class="link" :href="faucetUrl" target="_blank" rel="noopener">Faucet</a>
          <button class="btn ghost" @click="disconnect">Disconnect</button>
        </template>
        <template v-else>
          <button class="btn primary" @click="connect">Connect wallet</button>
        </template>
      </div>
    </header>

    <main class="grid">
      <!-- Submit form -->
      <section class="card">
        <h2>Check a specimen</h2>

        <label>Type</label>
        <div class="segmented">
          <button :class="{ active: form.kind === 'mushroom' }" @click="form.kind = 'mushroom'">🍄 Mushroom</button>
          <button :class="{ active: form.kind === 'plant' }" @click="form.kind = 'plant'">🌿 Plant</button>
        </div>

        <label>Species guess <span class="muted">(optional — grounds the web lookup)</span></label>
        <input v-model="form.speciesGuess" placeholder="e.g. Amanita muscaria" />

        <label>Observed features <span class="req">*</span></label>
        <textarea
          v-model="form.features"
          rows="4"
          placeholder="Cap colour & shape, gills/pores, stem, ring, volva, spore print colour, smell, bruising..."
        ></textarea>

        <div class="row">
          <div>
            <label>Habitat</label>
            <input v-model="form.habitat" placeholder="Oak woodland, on dead wood..." />
          </div>
          <div>
            <label>Location</label>
            <input v-model="form.location" placeholder="Region / country" />
          </div>
        </div>

        <label>Photo URL / IPFS <span class="muted">(optional, kept on record)</span></label>
        <input v-model="form.photoRef" placeholder="ipfs://... or https://..." />

        <p v-if="error" class="error">{{ error }}</p>

        <button
          v-if="address"
          class="btn primary full"
          :disabled="submitting || !canSubmit"
          @click="submit"
        >
          {{ submitting ? progress : "Analyze specimen" }}
        </button>
        <button v-else class="btn primary full" @click="connect">
          Connect wallet to analyze
        </button>
        <p v-if="submitting" class="muted small">
          Validators are running the LLM, reading the web and reaching consensus.
          This can take a few minutes on testnet — you can leave this tab open.
        </p>
        <p v-if="!hasWalletExt" class="muted small">
          No EVM wallet detected. Install <a class="link" href="https://metamask.io" target="_blank" rel="noopener">MetaMask</a> to submit checks.
        </p>
        <p v-else-if="address" class="muted small">
          Submitting costs a little testnet GEN — get free tokens from the
          <a class="link" :href="faucetUrl" target="_blank" rel="noopener">faucet</a>.
        </p>
      </section>

      <!-- Results feed -->
      <section class="card">
        <div class="feed-head">
          <h2>Recent checks <span class="muted">({{ reports.length }})</span></h2>
          <button class="btn ghost small" @click="refresh" :disabled="loading">
            {{ loading ? "…" : "Refresh" }}
          </button>
        </div>

        <p v-if="!reports.length && !loading" class="muted">No checks yet. Be the first!</p>

        <div v-for="r in reports" :key="r.key" class="report">
          <div class="report-top">
            <span class="kind">{{ r.kind === 'mushroom' ? '🍄' : '🌿' }}</span>
            <strong>{{ r.verdict.identified_species || r.species_guess || 'Unknown' }}</strong>
            <span class="badge" :class="riskClass(r.verdict.risk)">{{ riskLabel(r.verdict.risk) }}</span>
          </div>

          <p class="reason">{{ r.verdict.reason }}</p>

          <div v-if="r.verdict.toxic_lookalikes && r.verdict.toxic_lookalikes.length" class="lookalikes">
            ☠️ <strong>Toxic look-alikes:</strong> {{ r.verdict.toxic_lookalikes.join(', ') }}
          </div>

          <div v-if="r.verdict.key_features_to_check && r.verdict.key_features_to_check.length" class="checks">
            🔍 <strong>Check:</strong> {{ r.verdict.key_features_to_check.join(' · ') }}
          </div>

          <div class="report-meta">
            <span>confidence: {{ r.verdict.confidence || '—' }}</span>
            <span>by {{ short(r.submitter) }}</span>
          </div>
          <p class="disclaimer">{{ r.verdict.disclaimer }}</p>
        </div>
      </section>
    </main>

    <footer class="footer">
      Contract:
      <a class="link" :href="explorerBase + 'contracts/' + contractAddress" target="_blank" rel="noopener">
        {{ short(contractAddress) }}
      </a>
      · GenLayer Bradbury testnet
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from "vue";
import ForageSafe, { faucetUrl, explorerBase } from "../logic/ForageSafe";
import {
  hasWallet,
  connectWallet,
  getConnectedAddress,
  onWalletChange,
} from "../services/genlayer";

const contractAddress = import.meta.env.VITE_CONTRACT_ADDRESS;
const forage = new ForageSafe(contractAddress);

const address = ref("");
const hasWalletExt = ref(hasWallet());
const reports = ref([]);
const loading = ref(false);
const submitting = ref(false);
const progress = ref("Analyzing…");
const error = ref("");

const form = reactive({
  kind: "mushroom",
  speciesGuess: "",
  features: "",
  habitat: "",
  location: "",
  photoRef: "",
});

const canSubmit = computed(() => form.features.trim().length > 0 && !!address.value);
const short = (a) => (a ? `${a.slice(0, 6)}…${a.slice(-4)}` : "");

const setAddress = (a) => {
  address.value = a || "";
  forage.setWallet(address.value);
};

const riskLabel = (risk) =>
  ({
    DEADLY_LOOKALIKE: "☠️ Deadly look-alike",
    TOXIC: "⛔ Toxic",
    SAFE_LOOKALIKE_EXISTS: "⚠️ Risky look-alike",
    LIKELY_HARMLESS: "🟢 Likely harmless*",
    UNKNOWN: "❓ Unknown",
  })[risk] || "❓ Unknown";

const riskClass = (risk) =>
  ({
    DEADLY_LOOKALIKE: "r-deadly",
    TOXIC: "r-toxic",
    SAFE_LOOKALIKE_EXISTS: "r-warn",
    LIKELY_HARMLESS: "r-ok",
    UNKNOWN: "r-unknown",
  })[risk] || "r-unknown";

const connect = async () => {
  error.value = "";
  try {
    const a = await connectWallet();
    setAddress(a);
  } catch (e) {
    error.value =
      e?.message === "NO_WALLET"
        ? "No EVM wallet found. Install MetaMask to continue."
        : "Wallet connection was rejected.";
  }
};

const disconnect = () => setAddress("");

const refresh = async () => {
  loading.value = true;
  try {
    reports.value = await forage.getReports();
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const submit = async () => {
  error.value = "";
  if (!canSubmit.value) return;
  submitting.value = true;
  progress.value = "Waiting for wallet signature…";
  try {
    await forage.identify({ ...form }, (status) => {
      if (status === "signing") progress.value = "Waiting for wallet signature…";
      else if (status === "pending") progress.value = "Submitted — awaiting consensus…";
    });
    form.features = "";
    form.speciesGuess = "";
    form.photoRef = "";
    await refresh();
  } catch (e) {
    console.error(e);
    const msg = e?.message || "";
    error.value =
      /insufficient|balance|funds/i.test(msg)
        ? "Not enough testnet GEN. Use the Faucet link to fund your wallet."
        : /rejected|denied|User rejected/i.test(msg)
        ? "Transaction rejected in wallet."
        : /TIMEOUT/.test(msg)
        ? "Still processing on-chain. It may appear shortly — hit Refresh in a minute."
        : "Something went wrong submitting the transaction.";
  } finally {
    submitting.value = false;
  }
};

let stopWatch = () => {};
onMounted(async () => {
  setAddress(await getConnectedAddress());
  stopWatch = onWalletChange((acc, chainChanged) => {
    if (chainChanged) return; // keep session; user may switch back
    setAddress(acc);
  });
  await refresh();
});
onUnmounted(() => stopWatch());
</script>
