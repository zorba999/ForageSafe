import { makeReadClient, makeWalletClient, chain } from "../services/genlayer";

// Thin wrapper around the ForageSafe Intelligent Contract on GenLayer Bradbury.
export default class ForageSafe {
  constructor(contractAddress) {
    this.contractAddress = contractAddress;
    this.readClient = makeReadClient();
    this.walletAddress = null;
  }

  setWallet(address) {
    this.walletAddress = address || null;
  }

  // ---- reads (free, no wallet needed) --------------------------------
  async getReports() {
    const raw = await this.readClient.readContract({
      address: this.contractAddress,
      functionName: "get_reports",
      args: [],
    });

    return entriesOf(raw)
      .map(([id, report]) => {
        const obj = mapToObject(report);
        let verdict = {};
        try {
          verdict = JSON.parse(obj.verdict_json || "{}");
        } catch (_) {
          verdict = {};
        }
        return { key: id, ...obj, verdict };
      })
      .sort((a, b) => Number(b.id) - Number(a.id));
  }

  async getCount() {
    const c = await this.readClient.readContract({
      address: this.contractAddress,
      functionName: "get_count",
      args: [],
    });
    return Number(c);
  }

  // ---- write (needs a connected, funded wallet) ----------------------
  async identify({ kind, speciesGuess, features, habitat, location, photoRef }) {
    if (!this.walletAddress) throw new Error("NO_WALLET");
    const client = makeWalletClient(this.walletAddress);

    const txHash = await client.writeContract({
      address: this.contractAddress,
      functionName: "identify",
      args: [
        kind,
        speciesGuess || "",
        features,
        habitat || "",
        location || "",
        photoRef || "",
      ],
    });

    const receipt = await client.waitForTransactionReceipt({
      hash: txHash,
      status: "ACCEPTED",
      interval: 8000,
      retries: 90,
    });
    return receipt;
  }
}

// genlayer-js decodes GenVM dicts/structs as Map when non-empty but as a
// plain object when empty — normalise both to [key, value] pairs.
function entriesOf(x) {
  if (x instanceof Map) return Array.from(x.entries());
  if (x && typeof x === "object") return Object.entries(x);
  return [];
}

function mapToObject(maybeMap) {
  if (maybeMap instanceof Map || (maybeMap && typeof maybeMap === "object")) {
    return entriesOf(maybeMap).reduce((acc, [k, v]) => {
      acc[k] = v instanceof Map ? mapToObject(v) : v;
      return acc;
    }, {});
  }
  return maybeMap;
}

export const faucetUrl = "https://testnet-faucet.genlayer.foundation/";
export const explorerBase =
  chain?.blockExplorers?.default?.url || "https://explorer-bradbury.genlayer.com/";
