# 🍄 ForageSafe

**Cautious AI safety checks for wild mushrooms & plants — verified on GenLayer.**

ForageSafe is a decentralized app on the **GenLayer Bradbury testnet**. A user
describes a specimen (features, habitat, an optional species guess); an
**Intelligent Contract** grounds the guess with a live web lookup, asks an LLM
for a **safety-first risk assessment**, and multiple validators reach
**consensus** on the verdict via GenLayer's comparative equivalence principle.
Every check is stored immutably on-chain.

> ⚠️ **Safety first.** This is an educational tool. It never tells you something
> is safe to eat, and it always warns about toxic look-alikes. AI can be wrong —
> never eat a wild mushroom or plant based on this app. Confirm with a qualified
> local expert.

## Why GenLayer (and not a plain web app)?

- **Web access without oracles** — the contract reads reference data straight
  from the internet (`gl.get_webpage`).
- **Natural-language judgment** — the LLM interprets unstructured field notes.
- **Consensus on a subjective verdict** — several validators must agree on the
  same risk category, so no single hallucinating model decides. That is exactly
  GenLayer's adjudication niche, and the reason this belongs on-chain.

## Project layout

```
forage-safe/
├─ contracts/forage_safe.py   # the Intelligent Contract
├─ deploy/deployScript.ts     # optional script-based deploy
├─ app/                       # Vue 3 + Vite frontend (deploys to Vercel)
│  ├─ src/services/genlayer.js  # client + account (testnetBradbury)
│  ├─ src/logic/ForageSafe.js   # contract read/write wrapper
│  └─ src/components/ForageScreen.vue
└─ README.md
```

## Deployed contract

- Network: **GenLayer Bradbury** (chainId `4221`, RPC `https://rpc-bradbury.genlayer.com`)
- Address: `0x4bc28A9330F6F9929D151Cc0683B5799D3495687`
- Explorer: https://explorer-bradbury.genlayer.com/

## Develop / deploy the contract

```bash
# from forage-safe/
npx genlayer network set testnet-bradbury
npx genlayer account import --private-key 0x... --name my-burner
npx genlayer account unlock --account my-burner
npx genlayer deploy --contract contracts/forage_safe.py
```

## Run the frontend

```bash
cd app
cp .env.example .env        # set VITE_CONTRACT_ADDRESS
npm install
npm run dev                 # http://localhost:5173
```

To submit a check, click **Connect wallet** (MetaMask or any injected EVM
wallet). The app adds/switches the wallet to the Bradbury network automatically;
fund it from the [faucet](https://testnet-faucet.genlayer.foundation/). Browsing
past checks is free and needs no wallet.

## Deploy to Vercel

The frontend is a static Vite build.

```bash
cd app
npm i -g vercel
vercel            # link + deploy (set VITE_CONTRACT_ADDRESS in project env)
vercel --prod
```

`app/vercel.json` already sets the Vite framework preset and SPA rewrites. Set
`VITE_CONTRACT_ADDRESS` in the Vercel project's Environment Variables.

## Security

- The deployer key lives only in the OS keychain (`genlayer account`) and in a
  git-ignored `.env` — never committed and never shipped to Vercel.
- The frontend needs **no** private key baked in; each user connects their own
  EVM wallet (MetaMask, Rabby, …) and signs transactions there.

## License

MIT
