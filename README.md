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
testnet, in four stages.

**1. Candidates come from the features, not from the guess.** The contract first
derives candidate species from the observed features alone. The user's species
guess is carried through as an explicitly untrusted hypothesis, so a wrong guess
cannot be used as evidence for itself.

**2. Every candidate is grounded in independent authoritative sources.** Each
candidate is resolved against the [GBIF](https://www.gbif.org) taxonomic backbone
(accepted name, rank, family, genus, and whether the name resolves at all) and
against the Wikipedia REST summary API. Both are independent of the user's input
and of each other.

**3. The verdict is formed only from that evidence,** and must cite which records
it relied on. Validators then judge it with the non-comparative equivalence
principle against factual criteria rather than tone: a verdict is rejected if the
evidence is empty while a species or a non-unknown risk is still asserted, if the
toxicity classification is wrong for the species named (a taxon with lethal
members classified as harmless), or if it implies the specimen is edible. A
verdict that is merely worded cautiously but factually wrong does not pass.

The criteria are deliberately limited to claims that are objectively checkable.
Completeness judgements, such as whether a look-alike list is exhaustive, are left
to the deterministic layer below, because they vary between validators and stall
consensus without adding safety.

**4. Deterministic guards run before anything is stored.** Independently of the
model, contract code enforces:

- An ungrounded result cannot assert a species, a low risk, or high confidence.
  It is stored as `UNKNOWN`.
- A registry of taxa with lethal or severely toxic members (Amanita, Galerina,
  Cortinarius, Lepiota, Gyromitra, Conium, Cicuta, Atropa, Nerium, Digitalis,
  Aconitum, Taxus, Convallaria and others) floors the risk at `DEADLY_LOOKALIKE`
  whenever such a taxon appears in the identification or the look-alike list.
- A verdict that lists toxic look-alikes cannot also be `LIKELY_HARMLESS`.
- Any phrasing that implies edibility is stripped.
- Malformed or unparseable model output degrades to `UNKNOWN`, never to a
  reassuring result.

Each report stores the verdict, the evidence actually consulted, and a `grounded`
flag, so the basis for any result can be inspected on-chain.

This is why the app lives on GenLayer rather than a plain backend: web access
without oracles, natural-language judgment over unstructured field notes, and
decentralized consensus on a subjective, safety-critical verdict.

## Deployed contract

| | |
|---|---|
| Network | GenLayer Bradbury testnet (chain id 4221) |
| RPC | https://rpc-bradbury.genlayer.com |
| Contract | `0x20Cb2355F8f1a417529FCE96DD9ad086Ed73B832` |
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
