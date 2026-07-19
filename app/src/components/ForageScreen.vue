<template>
  <div :data-theme="theme"
       style="min-height:100vh;background:var(--bg);color:var(--ink);font-family:'Albert Sans',sans-serif;transition:background .6s ease,color .6s ease;overflow-x:hidden;padding-bottom:46px;">

    <!-- drifting spores -->
    <div style="position:fixed;inset:0;pointer-events:none;z-index:1;overflow:hidden;">
      <div v-for="(s,i) in spores" :key="i"
           :style="`position:absolute;bottom:-4vh;left:${s.left}%;width:${s.size}px;height:${s.size}px;border-radius:50%;background:var(--glow);opacity:${s.op};filter:blur(0.5px);box-shadow:0 0 8px var(--heroGlow);animation:fsDrift ${s.dur}s linear ${s.delay}s infinite;`"></div>
    </div>

    <!-- nav -->
    <nav style="position:fixed;top:0;left:0;right:0;z-index:40;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px clamp(16px,4vw,40px);background:var(--navbg);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-bottom:1px solid var(--line);transition:background .6s ease;">
      <a href="#top" style="display:flex;align-items:center;gap:10px;color:var(--ink);">
        <span style="width:10px;height:10px;border-radius:50%;background:radial-gradient(circle at 35% 35%,var(--glow),var(--em2));box-shadow:0 0 12px var(--heroGlow),0 0 4px var(--glow);display:inline-block;"></span>
        <span style="font-family:'Instrument Serif',serif;font-size:22px;letter-spacing:.01em;">ForageSafe</span>
        <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--muted);letter-spacing:.14em;padding-top:4px;">FIELD&nbsp;OS</span>
      </a>
      <div style="display:flex;align-items:center;gap:clamp(10px,2.5vw,22px);">
        <a href="#check" class="fs-nav-link" style="font-size:13px;font-weight:600;letter-spacing:.04em;">Field check</a>
        <a href="#log" class="fs-nav-link" style="font-size:13px;font-weight:600;letter-spacing:.04em;">Field log</a>
        <button v-if="!address" @click="connect" class="fs-cta"
          style="font:inherit;font-weight:700;font-size:12px;letter-spacing:.03em;padding:9px 16px;border-radius:999px;border:none;cursor:pointer;color:#0C130D;background:linear-gradient(120deg,var(--glow),var(--em));box-shadow:0 6px 20px var(--heroGlow);">
          Connect wallet
        </button>
        <span v-else style="display:flex;align-items:center;gap:8px;">
          <span :title="address" style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--muted);border:1px solid var(--line);border-radius:999px;padding:6px 11px;">{{ short(address) }}</span>
          <a :href="faucetUrl" target="_blank" rel="noopener" style="font-family:'IBM Plex Mono',monospace;font-size:11px;">faucet</a>
        </span>
        <button @click="toggleTheme" aria-label="Toggle dark and light mode"
          style="position:relative;width:58px;height:30px;border-radius:999px;border:1px solid var(--line);background:var(--bg2);cursor:pointer;padding:0;transition:background .6s ease;">
          <span style="position:absolute;top:8px;left:12px;width:2px;height:2px;border-radius:50%;background:var(--glow);opacity:.7;animation:fsPulse 3s ease-in-out infinite;"></span>
          <span style="position:absolute;top:17px;left:20px;width:2px;height:2px;border-radius:50%;background:var(--glow);opacity:.45;animation:fsPulse 4s ease-in-out 1s infinite;"></span>
          <span style="position:absolute;top:10px;right:14px;width:2px;height:2px;border-radius:50%;background:var(--glow);opacity:.55;animation:fsPulse 5s ease-in-out .5s infinite;"></span>
          <span :style="`position:absolute;top:3px;left:3px;width:22px;height:22px;border-radius:50%;background:radial-gradient(circle at 35% 30%,var(--glow),var(--em2) 70%);box-shadow:0 0 14px var(--heroGlow),0 1px 4px rgba(0,0,0,.3);transform:translateX(${theme==='dark'?0:28}px);transition:transform .55s cubic-bezier(.34,1.56,.4,1),background .6s ease;`"></span>
        </button>
      </div>
    </nav>

    <!-- hero -->
    <header id="top" style="position:relative;min-height:100svh;display:flex;flex-direction:column;justify-content:center;padding:120px clamp(20px,6vw,80px) 80px;z-index:2;">
      <div style="position:absolute;inset:0;background:radial-gradient(900px 520px at 20% 30%,var(--heroGlow),transparent 70%);pointer-events:none;"></div>
      <svg ref="mycelium" viewBox="0 0 1440 620" preserveAspectRatio="xMidYMax slice" aria-hidden="true" style="position:absolute;left:0;right:0;bottom:0;width:100%;height:52%;pointer-events:none;opacity:.9;">
        <path d="M140,620 C200,470 90,380 210,250" fill="none" stroke="var(--myc)" stroke-width="1.3"></path>
        <path d="M310,620 C300,480 420,430 380,300 C360,230 430,190 470,150" fill="none" stroke="var(--myc)" stroke-width="1.1"></path>
        <path d="M620,620 C560,500 700,440 660,330" fill="none" stroke="var(--myc)" stroke-width="1.4"></path>
        <path d="M840,620 C880,490 790,420 900,320 C960,270 920,200 990,160" fill="none" stroke="var(--myc)" stroke-width="1.1"></path>
        <path d="M1080,620 C1040,520 1160,470 1120,370" fill="none" stroke="var(--myc)" stroke-width="1.3"></path>
        <path d="M1300,620 C1340,480 1230,420 1330,290" fill="none" stroke="var(--myc)" stroke-width="1.2"></path>
        <path d="M210,250 C260,220 240,170 300,140" fill="none" stroke="var(--myc)" stroke-width="0.9"></path>
        <path d="M660,330 C700,290 640,250 690,210" fill="none" stroke="var(--myc)" stroke-width="0.9"></path>
        <circle cx="210" cy="250" r="3" fill="var(--glow)" opacity="0.3"></circle>
        <circle cx="470" cy="150" r="2.5" fill="var(--glow)" opacity="0.3"></circle>
        <circle cx="660" cy="330" r="3" fill="var(--glow)" opacity="0.3"></circle>
        <circle cx="990" cy="160" r="2.5" fill="var(--glow)" opacity="0.3"></circle>
        <circle cx="1120" cy="370" r="3" fill="var(--glow)" opacity="0.3"></circle>
        <circle cx="1330" cy="290" r="2.5" fill="var(--glow)" opacity="0.3"></circle>
      </svg>
      <div style="position:relative;max-width:1100px;">
        <p data-hero-line style="font-family:'IBM Plex Mono',monospace;font-size:12px;letter-spacing:.28em;color:var(--em);margin:0 0 26px;text-transform:uppercase;">A cautious companion for wild foragers · on-chain</p>
        <h1 style="font-family:'Instrument Serif',serif;font-weight:400;font-size:clamp(3rem,9.5vw,7.6rem);line-height:.98;margin:0 0 30px;letter-spacing:-.01em;">
          <span data-hero-line style="display:block;">Beautiful,</span>
          <span data-hero-line style="display:block;">but <em style="color:var(--em);font-style:italic;">never</em> reckless.</span>
        </h1>
        <p data-hero-line style="max-width:52ch;font-size:clamp(1rem,1.6vw,1.2rem);line-height:1.65;color:var(--muted);margin:0 0 42px;text-wrap:pretty;">Describe what you found: cap, gills, stem, smell, habitat. ForageSafe returns a careful safety verdict, reasoned by decentralized AI validators and recorded on GenLayer: the risk, the toxic look-alikes, and exactly what to verify. It will warn you. It will never clear you.</p>
        <div data-hero-line style="display:flex;gap:16px;flex-wrap:wrap;align-items:center;">
          <button @click="scrollTo('check')" class="fs-cta" style="font:inherit;font-weight:700;font-size:15px;letter-spacing:.03em;padding:16px 32px;border-radius:999px;border:none;cursor:pointer;color:#0C130D;background:linear-gradient(120deg,var(--glow),var(--em));box-shadow:0 8px 30px var(--heroGlow);">Begin a field check</button>
          <a href="#log" class="fs-link-underline" style="font-weight:600;font-size:14px;letter-spacing:.03em;color:var(--muted);border-bottom:1px solid var(--line);padding-bottom:2px;">Browse the field log →</a>
        </div>
      </div>
      <div style="position:absolute;bottom:26px;left:50%;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;gap:8px;opacity:.6;">
        <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.3em;color:var(--muted);">SCROLL</span>
        <span style="width:1px;height:34px;background:linear-gradient(var(--em),transparent);display:block;"></span>
      </div>
    </header>

    <main style="position:relative;z-index:2;">
      <!-- field check -->
      <section id="check" style="padding:clamp(60px,10vh,120px) clamp(20px,6vw,80px);max-width:1240px;margin:0 auto;">
        <div data-reveal style="margin-bottom:38px;">
          <p style="font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.28em;color:var(--em);margin:0 0 12px;">01 · FIELD CHECK</p>
          <h2 style="font-family:'Instrument Serif',serif;font-weight:400;font-size:clamp(2rem,4.5vw,3.4rem);margin:0;line-height:1.05;">Tell it what you found.</h2>
        </div>
        <div data-reveal style="background:var(--card);border:1px solid var(--line);border-radius:24px;box-shadow:var(--shadow);padding:clamp(22px,4vw,44px);position:relative;overflow:hidden;transition:background .6s ease;">
          <div style="position:absolute;top:-80px;right:-80px;width:260px;height:260px;border-radius:50%;background:radial-gradient(circle,var(--heroGlow),transparent 70%);pointer-events:none;"></div>
          <p style="font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.2em;color:var(--muted);margin:0 0 14px;">SPECIMEN TYPE</p>
          <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:32px;">
            <button v-for="t in types" :key="t.id" @click="type=t.id" class="fs-chip"
              :style="`font:inherit;text-align:left;cursor:pointer;padding:14px 22px;border-radius:16px;transition:all .3s ease;color:var(--ink);${type===t.id?'border:1.5px solid var(--em);background:var(--inputbg);box-shadow:0 0 0 4px var(--heroGlow),0 6px 18px var(--heroGlow);':'border:1.5px solid var(--line);background:transparent;opacity:.75;'}`">
              <span style="display:block;font-weight:700;font-size:15px;">{{ t.label }}</span>
              <span style="display:block;font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.08em;opacity:.65;margin-top:4px;">{{ t.note }}</span>
            </button>
          </div>
          <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:26px;margin-bottom:26px;">
            <label style="display:block;">
              <span style="display:block;font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.2em;color:var(--muted);margin-bottom:10px;">SPECIES GUESS · OPTIONAL</span>
              <input v-model="form.species" type="text" placeholder="e.g. golden chanterelle" style="width:100%;box-sizing:border-box;font:inherit;font-size:16px;color:var(--ink);background:var(--inputbg);border:1px solid var(--line);border-radius:14px;padding:14px 16px;transition:border-color .25s ease;">
            </label>
            <label style="display:block;">
              <span style="display:block;font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.2em;color:var(--muted);margin-bottom:10px;">LOCATION · REGION</span>
              <input v-model="form.location" type="text" placeholder="e.g. Middle Atlas, Morocco" style="width:100%;box-sizing:border-box;font:inherit;font-size:16px;color:var(--ink);background:var(--inputbg);border:1px solid var(--line);border-radius:14px;padding:14px 16px;transition:border-color .25s ease;">
            </label>
          </div>
          <label style="display:block;margin-bottom:26px;">
            <span style="display:block;font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.2em;color:var(--muted);margin-bottom:10px;">FIELD NOTES: WHAT DO YOU SEE, SMELL, FEEL?</span>
            <textarea v-model="form.desc" rows="4" placeholder="Egg-yolk yellow, trumpet-shaped cap · blunt forked ridges under the cap running down the stem · smells faintly of apricot · growing scattered from soil under oaks…" style="width:100%;box-sizing:border-box;font:inherit;font-size:16px;line-height:1.6;color:var(--ink);background:var(--inputbg);border:1px solid var(--line);border-radius:14px;padding:16px;resize:vertical;transition:border-color .25s ease;"></textarea>
          </label>
          <label style="display:block;margin-bottom:34px;">
            <span style="display:block;font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.2em;color:var(--muted);margin-bottom:10px;">HABITAT &amp; SUBSTRATE</span>
            <input v-model="form.habitat" type="text" placeholder="e.g. mixed hardwood forest, growing from soil near oak roots" style="width:100%;box-sizing:border-box;font:inherit;font-size:16px;color:var(--ink);background:var(--inputbg);border:1px solid var(--line);border-radius:14px;padding:14px 16px;transition:border-color .25s ease;">
          </label>
          <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
            <button @click="analyze" :disabled="analyzing" class="fs-cta"
              :style="`font:inherit;font-weight:700;font-size:15px;letter-spacing:.03em;padding:17px 36px;border-radius:999px;border:none;cursor:pointer;color:#0C130D;background:linear-gradient(120deg,var(--glow),var(--em));box-shadow:0 8px 30px var(--heroGlow);opacity:${analyzing?.6:1};`">
              {{ analyzeLabel }}
            </button>
            <span v-if="analyzing" style="display:flex;align-items:center;gap:8px;font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--muted);">
              <span style="width:6px;height:6px;border-radius:50%;background:var(--glow);animation:fsPulse 1s ease-in-out infinite;"></span>
              {{ progress }}
            </span>
            <span v-else style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--muted);opacity:.8;">Sparse notes → verdict defaults to UNKNOWN.</span>
          </div>
          <p v-if="error" style="color:#D6493A;font-size:13px;margin:16px 0 0;">{{ error }}</p>
        </div>
      </section>

      <!-- verdict -->
      <section v-if="v" id="verdict" ref="verdictEl" style="padding:0 clamp(20px,6vw,80px) clamp(60px,10vh,120px);max-width:1240px;margin:0 auto;">
        <div style="margin-bottom:38px;">
          <p style="font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.28em;color:var(--em);margin:0 0 12px;">02 · VERDICT</p>
          <h2 style="font-family:'Instrument Serif',serif;font-weight:400;font-size:clamp(2rem,4.5vw,3.4rem);margin:0 0 6px;line-height:1.05;">{{ v.name }}</h2>
          <p style="font-family:'Instrument Serif',serif;font-style:italic;font-size:18px;color:var(--muted);margin:0;">{{ v.latin }}</p>
        </div>
        <div style="background:var(--card);border:1px solid var(--line);border-radius:24px;box-shadow:var(--shadow);padding:clamp(22px,4vw,44px);margin-bottom:26px;">
          <div style="display:flex;gap:clamp(24px,4vw,56px);flex-wrap:wrap;align-items:flex-start;">
            <div style="flex:1 1 420px;min-width:280px;">
              <span ref="badgeEl" :style="`display:inline-flex;align-items:center;gap:10px;padding:12px 22px;border-radius:999px;border:1.5px solid ${v.riskColor};color:${v.riskColor};font-family:'IBM Plex Mono',monospace;font-weight:500;font-size:clamp(14px,2vw,18px);letter-spacing:.14em;margin-bottom:30px;`">
                <span :style="`width:9px;height:9px;border-radius:50%;background:${v.riskColor};`"></span>
                {{ v.riskLabelUpper }}
              </span>
              <div :style="`position:relative;height:8px;border-radius:99px;background:linear-gradient(90deg,#56C271,#D9A441,#E07B39,#D6493A,#B01E3C);opacity:${v.barOpacity};margin:6px 8px 12px;`">
                <span v-if="v.showMarker" ref="markerEl" :style="`position:absolute;top:50%;left:${v.markerLeft};transform:translate(-50%,-50%);width:22px;height:22px;border-radius:50%;background:var(--card);border:5px solid ${v.riskColor};box-shadow:0 0 16px ${v.riskColor};box-sizing:border-box;`"></span>
              </div>
              <div style="display:flex;justify-content:space-between;font-family:'IBM Plex Mono',monospace;font-size:9.5px;letter-spacing:.06em;color:var(--muted);margin:0 0 30px;">
                <span>HARMLESS?</span><span>CAUTION</span><span>RISKY</span><span>TOXIC</span><span>DEADLY</span>
              </div>
              <p style="font-size:16.5px;line-height:1.7;color:var(--ink);margin:0;max-width:60ch;text-wrap:pretty;">{{ v.summary }}</p>
            </div>
            <div style="flex:0 0 auto;display:flex;flex-direction:column;align-items:center;gap:10px;">
              <div style="position:relative;width:132px;height:132px;">
                <svg viewBox="0 0 120 120" style="width:132px;height:132px;transform:rotate(-90deg);">
                  <circle cx="60" cy="60" r="52" fill="none" stroke="var(--line)" stroke-width="7"></circle>
                  <circle ref="ringEl" cx="60" cy="60" r="52" fill="none" :stroke="v.riskColor" stroke-width="7" stroke-linecap="round" stroke-dasharray="326.7" :stroke-dashoffset="v.ringOffset"></circle>
                </svg>
                <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;">
                  <span style="font-family:'Instrument Serif',serif;font-size:38px;line-height:1;"><span ref="confNumEl">{{ v.confidence }}</span><span style="font-size:20px;color:var(--muted);">%</span></span>
                </div>
              </div>
              <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.2em;color:var(--muted);">CONFIDENCE</span>
              <span style="font-size:11.5px;color:var(--muted);max-width:180px;text-align:center;line-height:1.5;">Reflects description completeness, never edibility.</span>
            </div>
          </div>
        </div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:26px;align-items:start;">
          <div>
            <h3 data-stagger style="font-family:'Instrument Serif',serif;font-weight:400;font-size:26px;margin:0 0 18px;">Toxic look-alikes</h3>
            <div style="display:flex;flex-direction:column;gap:16px;">
              <div v-for="(la,i) in v.lookalikes" :key="i" data-stagger class="fs-card-hover" style="background:var(--card);border:1px solid var(--line);border-radius:18px;padding:22px;">
                <div style="display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:8px;">
                  <span style="font-weight:700;font-size:17px;">{{ la.name }}</span>
                  <span v-if="la.tag" style="font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.1em;color:#D6493A;border:1px solid rgba(214,73,58,.4);border-radius:99px;padding:4px 10px;white-space:nowrap;">{{ la.tag }}</span>
                </div>
                <p v-if="la.note" style="font-size:14px;line-height:1.65;color:var(--muted);margin:0;">{{ la.note }}</p>
              </div>
              <p v-if="!v.lookalikes.length" style="font-size:14px;color:var(--muted);margin:0;">No specific toxic look-alikes were flagged. That is never a clearance. Verify every feature below.</p>
            </div>
          </div>
          <div>
            <h3 data-stagger style="font-family:'Instrument Serif',serif;font-weight:400;font-size:26px;margin:0 0 18px;">Verify before you trust</h3>
            <div style="display:flex;flex-direction:column;gap:12px;">
              <button v-for="(c,i) in v.checklist" :key="i" data-stagger @click="toggleCheck(i)" class="fs-check"
                :style="`font:inherit;display:flex;gap:14px;align-items:flex-start;width:100%;box-sizing:border-box;cursor:pointer;text-align:left;border-radius:16px;padding:16px 18px;transition:all .3s ease;color:var(--ink);border:1px solid ${checked[i]?'var(--em)':'var(--line)'};background:${checked[i]?'var(--inputbg)':'var(--card)'};`">
                <span :style="`flex:0 0 auto;width:24px;height:24px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;transition:all .3s ease;margin-top:2px;${checked[i]?'background:var(--em);color:#0C130D;border:1.5px solid var(--em);box-shadow:0 0 12px var(--heroGlow);':'background:transparent;color:transparent;border:1.5px solid var(--line);'}`">✓</span>
                <span style="text-align:left;">
                  <span style="display:block;font-weight:700;font-size:15px;">{{ c.title }}</span>
                  <span v-if="c.detail" style="display:block;font-size:13.5px;line-height:1.6;color:var(--muted);margin-top:4px;">{{ c.detail }}</span>
                </span>
              </button>
              <p data-stagger style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--muted);margin:8px 2px 0;line-height:1.7;">{{ checkedCount }} of {{ v.checklist.length }} verified in the field. A checked box is your observation, not ForageSafe's blessing.</p>
            </div>
          </div>
        </div>
        <p style="font-size:11.5px;color:var(--muted);font-style:italic;margin:22px 2px 0;">{{ v.disclaimer }}</p>
      </section>

      <!-- field log -->
      <section id="log" style="padding:clamp(60px,10vh,120px) clamp(20px,6vw,80px) clamp(80px,12vh,140px);max-width:1240px;margin:0 auto;">
        <div data-reveal style="display:flex;justify-content:space-between;align-items:flex-end;gap:20px;flex-wrap:wrap;margin-bottom:38px;">
          <div>
            <p style="font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.28em;color:var(--em);margin:0 0 12px;">03 · FIELD LOG</p>
            <h2 style="font-family:'Instrument Serif',serif;font-weight:400;font-size:clamp(2rem,4.5vw,3.4rem);margin:0;line-height:1.05;">Recent checks.</h2>
          </div>
          <button @click="refresh" :disabled="loading" style="font:inherit;font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.1em;color:var(--muted);background:transparent;border:1px solid var(--line);border-radius:999px;padding:8px 16px;cursor:pointer;">{{ loading ? 'SYNCING…' : 'REFRESH' }}</button>
        </div>
        <div v-if="feed.length" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:22px;">
          <article v-for="(f,i) in feed" :key="f.key" data-reveal class="fs-feed" style="background:var(--card);border:1px solid var(--line);border-radius:20px;overflow:hidden;transition:transform .35s ease,box-shadow .35s ease;">
            <div style="height:130px;background:repeating-linear-gradient(45deg,var(--stripe) 0 2px,transparent 2px 11px),var(--bg2);display:flex;align-items:center;justify-content:center;border-bottom:1px solid var(--line);position:relative;">
              <span style="font-size:44px;opacity:.5;">{{ f.type==='Mushroom' ? '🍄' : '🌿' }}</span>
              <span style="position:absolute;top:12px;left:12px;font-family:'IBM Plex Mono',monospace;font-size:9.5px;letter-spacing:.12em;color:var(--muted);border:1px solid var(--line);border-radius:99px;padding:3px 9px;background:var(--card);">{{ f.typeUpper }}</span>
            </div>
            <div style="padding:20px 22px 22px;">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                <span :style="`width:8px;height:8px;border-radius:50%;background:${f.color};box-shadow:0 0 8px ${f.color};`"></span>
                <span :style="`font-family:'IBM Plex Mono',monospace;font-size:10.5px;letter-spacing:.12em;color:${f.color};`">{{ f.labelUpper }}</span>
                <span style="margin-left:auto;font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--muted);">{{ f.date }}</span>
              </div>
              <h3 style="font-family:'Instrument Serif',serif;font-weight:400;font-size:23px;margin:0 0 2px;">{{ f.name }}</h3>
              <p style="font-family:'Instrument Serif',serif;font-style:italic;font-size:14px;color:var(--muted);margin:0 0 12px;">{{ f.latin }}</p>
              <p style="font-size:13.5px;line-height:1.6;color:var(--muted);margin:0 0 14px;">{{ f.note }}</p>
              <div style="display:flex;align-items:center;gap:10px;">
                <div style="flex:1;height:3px;border-radius:99px;background:var(--line);overflow:hidden;">
                  <div :style="`height:100%;width:${f.confidence}%;background:${f.color};border-radius:99px;`"></div>
                </div>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--muted);">{{ f.confidence }}% conf</span>
              </div>
            </div>
          </article>
        </div>
        <p v-else style="font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--muted);">No checks recorded yet. Run the first field check above.</p>
      </section>
    </main>

    <footer style="position:relative;z-index:2;border-top:1px solid var(--line);padding:44px clamp(20px,6vw,80px) 60px;display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap;">
      <div style="display:flex;align-items:center;gap:10px;">
        <span style="width:8px;height:8px;border-radius:50%;background:radial-gradient(circle at 35% 35%,var(--glow),var(--em2));box-shadow:0 0 10px var(--heroGlow);"></span>
        <span style="font-family:'Instrument Serif',serif;font-size:19px;">ForageSafe</span>
      </div>
      <p style="font-family:'Instrument Serif',serif;font-style:italic;font-size:16px;color:var(--muted);margin:0;">Beautiful, but never reckless.</p>
      <a :href="contractUrl" target="_blank" rel="noopener" style="font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--muted);">GENLAYER BRADBURY · {{ short(contractAddress) }}</a>
    </footer>

    <div style="position:fixed;bottom:0;left:0;right:0;z-index:50;background:var(--navbg);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-top:1px solid var(--line);padding:12px 16px;display:flex;align-items:center;justify-content:center;gap:10px;">
      <span style="width:6px;height:6px;border-radius:50%;background:#D6493A;animation:fsPulse 2.4s ease-in-out infinite;flex:0 0 auto;"></span>
      <p style="font-family:'IBM Plex Mono',monospace;font-size:10.5px;letter-spacing:.06em;color:var(--muted);margin:0;text-align:center;">ForageSafe is a caution engine, not a permission engine. It will never tell you something is safe to eat. When in doubt, throw it out.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from "vue";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import ForageSafe, { faucetUrl, explorerBase } from "../logic/ForageSafe";
import { hasWallet, connectWallet, getConnectedAddress, onWalletChange } from "../services/genlayer";

gsap.registerPlugin(ScrollTrigger);

const RISK_SCALE = [
  { label: "Likely harmless", color: "#56C271" },
  { label: "Caution", color: "#D9A441" },
  { label: "Risky look-alike", color: "#E07B39" },
  { label: "Toxic", color: "#D6493A" },
  { label: "Deadly", color: "#B01E3C" },
  { label: "Unknown", color: "#8B87A8" },
];
const RISK_TO_LEVEL = {
  LIKELY_HARMLESS: 0,
  SAFE_LOOKALIKE_EXISTS: 2,
  TOXIC: 3,
  DEADLY_LOOKALIKE: 4,
  UNKNOWN: 5,
};
const CONF_TO_NUM = { low: 34, medium: 66, high: 92 };
const defaultDisclaimer =
  "Educational estimate only. NEVER eat a wild mushroom or plant based on this result. Always confirm with a qualified local expert.";

const contractAddress = import.meta.env.VITE_CONTRACT_ADDRESS;
const contractUrl = explorerBase + "contracts/" + contractAddress;
const forage = new ForageSafe(contractAddress);

const types = [
  { id: "mushroom", label: "Mushroom", note: "cap · gills · stem" },
  { id: "plant", label: "Plant", note: "leaf · stem · root" },
  { id: "berry", label: "Berry", note: "fruit · cluster · seed" },
];

const theme = ref("dark");
const type = ref("mushroom");
const address = ref("");
const analyzing = ref(false);
const progress = ref("");
const error = ref("");
const loading = ref(false);
const verdict = ref(null);      // mapped verdict object
const checked = reactive({});
const feed = ref([]);
const form = reactive({ species: "", desc: "", habitat: "", location: "" });

const mycelium = ref(null);
const verdictEl = ref(null);
const markerEl = ref(null);
const confNumEl = ref(null);
const ringEl = ref(null);
const badgeEl = ref(null);

const reduced = typeof window !== "undefined" && window.matchMedia &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const spores = computed(() => {
  if (reduced) return [];
  return Array.from({ length: 24 }, (_, i) => ({
    left: (i * 37 + 13) % 100,
    size: 2 + ((i * 7) % 5),
    dur: 16 + ((i * 13) % 22),
    delay: -((i * 29) % 34),
    op: (25 + ((i * 11) % 40)) / 100,
  }));
});

const short = (a) => (a ? `${a.slice(0, 6)}…${a.slice(-4)}` : "");
const toggleTheme = () => (theme.value = theme.value === "dark" ? "light" : "dark");
const scrollTo = (id) => {
  const el = document.getElementById(id);
  if (el) window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - 76, behavior: reduced ? "auto" : "smooth" });
};

const analyzeLabel = computed(() =>
  analyzing.value ? "Consulting the validators…" : address.value ? "Run cautious analysis" : "Connect wallet to analyze"
);

const v = computed(() => {
  const sv = verdict.value;
  if (!sv) return null;
  const scale = RISK_SCALE[sv.level] || RISK_SCALE[5];
  return {
    name: sv.name,
    latin: sv.latin,
    summary: sv.summary,
    disclaimer: sv.disclaimer,
    riskColor: scale.color,
    riskLabelUpper: scale.label.toUpperCase(),
    showMarker: sv.level <= 4,
    markerLeft: (sv.level <= 4 ? sv.level * 25 : 0) + "%",
    ringOffset: 326.7 * (1 - sv.confidence / 100),
    barOpacity: sv.level <= 4 ? 1 : 0.25,
    confidence: sv.confidence,
    level: sv.level,
    lookalikes: sv.lookalikes,
    checklist: sv.checklist,
  };
});
const checkedCount = computed(() => Object.values(checked).filter(Boolean).length);
const toggleCheck = (i) => (checked[i] = !checked[i]);

// ---- map a raw contract report -> the design's verdict shape -------------
function parseLookalike(s) {
  const m = String(s).match(/^(.*?)\s*\((.+)\)\s*$/);
  if (m) return { name: m[1].trim(), tag: m[2].trim().toUpperCase(), note: "" };
  return { name: String(s).trim(), tag: "TOXIC LOOK-ALIKE", note: "" };
}
function mapVerdict(report) {
  const d = report.verdict || {};
  const level = RISK_TO_LEVEL[d.risk] ?? 5;
  const conf = CONF_TO_NUM[String(d.confidence).toLowerCase()] ?? 40;
  return {
    name: d.identified_species || report.species_guess || "Unidentified specimen",
    latin: d.identified_species || "unidentified",
    level,
    confidence: conf,
    summary: d.reason || "The description was too sparse for a responsible identification.",
    disclaimer: report.disclaimer || defaultDisclaimer,
    lookalikes: (d.toxic_lookalikes || []).map(parseLookalike),
    checklist: (d.key_features_to_check || []).map((t) => ({ title: t, detail: "" })),
  };
}
function mapFeed(reports) {
  return reports.map((r) => {
    const d = r.verdict || {};
    const level = RISK_TO_LEVEL[d.risk] ?? 5;
    const scale = RISK_SCALE[level] || RISK_SCALE[5];
    return {
      key: r.key ?? r.id,
      name: d.identified_species || r.species_guess || "Unidentified",
      latin: d.identified_species || "unidentified",
      type: r.kind === "mushroom" ? "Mushroom" : "Plant",
      typeUpper: (r.kind || "").toUpperCase(),
      color: scale.color,
      labelUpper: scale.label.toUpperCase(),
      confidence: CONF_TO_NUM[String(d.confidence).toLowerCase()] ?? 40,
      date: "#" + r.id,
      note: d.reason || "",
    };
  });
}

// ---- wallet + contract ---------------------------------------------------
const connect = async () => {
  error.value = "";
  try {
    const a = await connectWallet();
    address.value = a || "";
    forage.setWallet(address.value);
  } catch (e) {
    error.value = e?.message === "NO_WALLET"
      ? "No EVM wallet found. Install MetaMask to continue."
      : "Wallet connection was rejected.";
  }
};

const refresh = async () => {
  loading.value = true;
  try {
    feed.value = mapFeed(await forage.getReports());
  } catch (e) { console.error(e); }
  finally { loading.value = false; }
};

const analyze = async () => {
  error.value = "";
  if (!address.value) return connect();
  if (form.desc.trim().length < 8) { error.value = "Add a few more field notes first."; return; }

  analyzing.value = true;
  progress.value = "Waiting for wallet signature…";
  const kind = type.value === "mushroom" ? "mushroom" : "plant";
  const features = type.value === "berry" ? `Berry / fruit. ${form.desc}` : form.desc;
  const before = feed.value.length;
  try {
    await forage.identify(
      { kind, speciesGuess: form.species, features, habitat: form.habitat, location: form.location },
      (status) => { progress.value = status === "pending" ? "Submitted. Validators reaching consensus…" : "Waiting for wallet signature…"; }
    );
    const reports = await forage.getReports();
    feed.value = mapFeed(reports);
    const newest = reports[0];
    if (newest && reports.length >= before) {
      Object.keys(checked).forEach((k) => delete checked[k]);
      verdict.value = mapVerdict(newest);
      await nextTick();
      revealVerdict();
    }
  } catch (e) {
    console.error(e);
    const msg = e?.message || "";
    error.value = /insufficient|balance|funds/i.test(msg)
      ? "Not enough testnet GEN. Use the faucet link to fund your wallet."
      : /reject|denied/i.test(msg) ? "Transaction rejected in wallet."
      : /TIMEOUT/.test(msg) ? "Still processing on-chain. Hit Refresh in a minute; it will appear in the field log."
      : "Something went wrong submitting the transaction.";
  } finally {
    analyzing.value = false;
  }
};

// ---- GSAP ---------------------------------------------------------------
function initGsap() {
  if (reduced) {
    gsap.utils.toArray("[data-reveal],[data-hero-line]").forEach((el) => gsap.set(el, { autoAlpha: 1 }));
    return;
  }
  const svg = mycelium.value;
  if (svg) {
    svg.querySelectorAll("path").forEach((path, i) => {
      const L = path.getTotalLength();
      gsap.set(path, { strokeDasharray: L, strokeDashoffset: L });
      gsap.to(path, { strokeDashoffset: 0, duration: 2.6 + i * 0.3, ease: "power2.out", delay: 0.4 + i * 0.18 });
    });
    gsap.to(svg.querySelectorAll("circle"), { opacity: 0.85, duration: 1.4, stagger: 0.25, delay: 1.6, yoyo: true, repeat: -1, ease: "sine.inOut" });
  }
  gsap.fromTo("[data-hero-line]", { y: 56, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 1.1, stagger: 0.13, ease: "power3.out", delay: 0.15 });
  gsap.utils.toArray("[data-reveal]").forEach((el) => {
    gsap.fromTo(el, { y: 38, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.9, ease: "power3.out", scrollTrigger: { trigger: el, start: "top 88%" } });
  });
}

let vtl, badgeTween, counterObj;
function revealVerdict() {
  const el = verdictEl.value;
  if (!el || !v.value) return;
  scrollTo("verdict");
  const conf = v.value.confidence;
  const ringTo = 326.7 * (1 - conf / 100);
  const pct = v.value.level <= 4 ? v.value.level * 25 : null;
  const setFinal = () => {
    if (confNumEl.value) confNumEl.value.textContent = conf;
    if (ringEl.value) ringEl.value.style.strokeDashoffset = String(ringTo);
    if (markerEl.value && pct != null) markerEl.value.style.left = pct + "%";
  };
  if (reduced) { setFinal(); return; }
  if (vtl) vtl.kill();
  if (badgeTween) badgeTween.kill();
  if (counterObj) gsap.killTweensOf(counterObj);
  [markerEl.value, ringEl.value, badgeEl.value, el].forEach((n) => n && gsap.killTweensOf(n));
  gsap.set(el, { autoAlpha: 0 });
  const tl = gsap.timeline({ delay: 0.2, onComplete: setFinal });
  vtl = tl;
  tl.to(el, { autoAlpha: 1, y: 0, duration: 0.8, ease: "power3.out" });
  if (markerEl.value && pct != null)
    tl.fromTo(markerEl.value, { left: "0%" }, { left: pct + "%", duration: 1.5, ease: "power4.inOut", overwrite: "auto" }, "-=0.3");
  const o = { n: 0 };
  counterObj = o;
  tl.to(o, { n: conf, duration: 1.5, ease: "power2.out", onUpdate: () => { if (confNumEl.value) confNumEl.value.textContent = Math.round(o.n); } }, "-=1.3");
  if (ringEl.value)
    tl.fromTo(ringEl.value, { strokeDashoffset: 326.7 }, { strokeDashoffset: ringTo, duration: 1.5, ease: "power2.out", overwrite: "auto" }, "<");
  tl.fromTo(el.querySelectorAll("[data-stagger]"), { y: 26, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.6, stagger: 0.09, ease: "power2.out" }, "-=1.0");
  if (badgeEl.value) {
    const color = v.value.riskColor;
    const intensity = 14 + v.value.level * 9;
    badgeTween = gsap.to(badgeEl.value, { boxShadow: `0 0 ${intensity}px ${color}${v.value.level >= 3 ? "AA" : "55"}`, duration: Math.max(0.5, 1.1 - v.value.level * 0.12), repeat: -1, yoyo: true, ease: "sine.inOut" });
  }
  ScrollTrigger.refresh();
}

let stopWatch = () => {};
onMounted(async () => {
  address.value = (await getConnectedAddress()) || "";
  forage.setWallet(address.value);
  stopWatch = onWalletChange((acc, chainChanged) => { if (!chainChanged) { address.value = acc || ""; forage.setWallet(address.value); } });
  initGsap();
  await refresh();
});
onUnmounted(() => stopWatch());
</script>
