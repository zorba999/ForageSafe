# ForageSafe

A cautious AI companion for wild foragers, built on GenLayer.

Describe a wild mushroom or plant (cap, gills, stem, smell, habitat, an optional
species guess) and ForageSafe returns a safety verdict: a risk level, the toxic
look-alikes that could be confused with it, and the exact features to verify. It
is a caution engine, not a permission engine. It never tells you something is
safe to eat.

> Educational tool only. Never eat a wild mushroom or plant based on this app.
> Always confirm with a qualified local expert.

## How it works

The verdict is produced by an Intelligent Contract on the GenLayer Bradbury
testnet. On each check the contract:

1. Fetches a live web reference for the species guess.
2. Asks an LLM for a safety-first risk assessment.
3. Reaches consensus across validators using the non-comparative equivalence
   principle, so no single model decides the outcome.
4. Stores the verdict on-chain.

This is why the app lives on GenLayer rather than a plain backend: web access
without oracles, natural-language judgment, and decentralized consensus on a
subjective safety call.

## Deployed contract

| | |
|---|---|
| Network | GenLayer Bradbury testnet (chain id 4221) |
| RPC | https://rpc-bradbury.genlayer.com |
| Contract | `0xcd5B8C06C8EF7b8817118D4297d2513b2c4783d8` |
| Explorer | https://explorer-bradbury.genlayer.com |

## Tech stack

- Intelligent Contract: Python (GenLayer GenVM)
- Frontend: Vue 3, Vite, GSAP
- Chain access: genlayer-js, injected EVM wallet (MetaMask)

## Project structure

```
forage-safe/
  contracts/forage_safe.py        Intelligent Contract
  deploy/deployScript.ts          Script-based deploy
  app/                            Vue + Vite frontend
    src/services/genlayer.js      Wallet adapter and client
    src/logic/ForageSafe.js       Contract read/write wrapper
    src/components/ForageScreen.vue
```

## Run the frontend

```bash
cd app
cp .env.example .env      # sets VITE_CONTRACT_ADDRESS
npm install
npm run dev               # http://localhost:5173
```

Browsing past checks is free and needs no wallet. To submit a check, connect an
EVM wallet; the app adds the Bradbury network automatically. Fund the wallet from
the [faucet](https://testnet-faucet.genlayer.foundation/). Consensus can take a
few minutes, after which the verdict appears in the field log.

## Deploy the contract

```bash
npx genlayer network set testnet-bradbury
npx genlayer account import --private-key 0x... --name my-wallet
npx genlayer account unlock --account my-wallet
npx genlayer deploy --contract contracts/forage_safe.py
```

## Deploy to Vercel

The frontend is a static Vite build. Import the repository in Vercel, set the
root directory to `app`, and add the environment variable
`VITE_CONTRACT_ADDRESS`. The included `app/vercel.json` sets the framework preset
and SPA rewrites.

## Security

No private key is committed or shipped to the frontend. Each user connects their
own wallet and signs transactions locally. The deployer key stays in the OS
keychain and in a git-ignored `.env`.

## License

MIT
