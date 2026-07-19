import { createClient } from "genlayer-js";
import { testnetBradbury } from "genlayer-js/chains";

// The dApp talks to the GenLayer Bradbury testnet through an injected EVM
// wallet (MetaMask, Rabby, ...). Reads are free and need no wallet.
export const chain = testnetBradbury;
const CHAIN_ID_HEX = "0x" + chain.id.toString(16); // 4221 -> 0x107d

export function hasWallet() {
  return typeof window !== "undefined" && !!window.ethereum;
}

// Make sure the wallet is pointed at Bradbury, adding it if unknown.
async function ensureChain() {
  const eth = window.ethereum;
  try {
    await eth.request({
      method: "wallet_switchEthereumChain",
      params: [{ chainId: CHAIN_ID_HEX }],
    });
  } catch (e) {
    const unknown = e?.code === 4902 || /Unrecognized|not been added/i.test(e?.message || "");
    if (!unknown) throw e;
    await eth.request({
      method: "wallet_addEthereumChain",
      params: [
        {
          chainId: CHAIN_ID_HEX,
          chainName: chain.name,
          nativeCurrency: chain.nativeCurrency,
          rpcUrls: chain.rpcUrls.default.http,
          blockExplorerUrls: [chain.blockExplorers?.default?.url].filter(Boolean),
        },
      ],
    });
  }
}

// Prompt the wallet to connect and switch to Bradbury. Returns the address.
export async function connectWallet() {
  if (!hasWallet()) {
    throw new Error("NO_WALLET");
  }
  const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
  await ensureChain();
  return accounts?.[0] || null;
}

// Silently read an already-authorised address (no popup), or null.
export async function getConnectedAddress() {
  if (!hasWallet()) return null;
  try {
    const accounts = await window.ethereum.request({ method: "eth_accounts" });
    return accounts?.[0] || null;
  } catch {
    return null;
  }
}

// React to the user changing account / network in their wallet.
export function onWalletChange(cb) {
  if (!hasWallet()) return () => {};
  const onAccounts = (accs) => cb(accs?.[0] || null);
  const onChain = () => cb(undefined, true);
  window.ethereum.on?.("accountsChanged", onAccounts);
  window.ethereum.on?.("chainChanged", onChain);
  return () => {
    window.ethereum.removeListener?.("accountsChanged", onAccounts);
    window.ethereum.removeListener?.("chainChanged", onChain);
  };
}

// Read-only client (browsing past checks, no wallet required).
export const makeReadClient = () => createClient({ chain });

// Write client bound to the connected wallet; writeContract triggers a signature.
export const makeWalletClient = (address) =>
  createClient({ chain, account: address, provider: window.ethereum });
