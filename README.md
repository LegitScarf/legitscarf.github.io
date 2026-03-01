<div align="center">

<!-- HEADER BANNER -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:020507,50:00ff88,100:ffb800&height=200&section=header&text=NEXALPHA&fontSize=72&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Intelligent%20Market%20Systems%20%E2%80%94%20India&descAlignY=58&descSize=16" width="100%"/>

<br/>

<!-- STATUS BADGES -->
![Status](https://img.shields.io/badge/STATUS-LIVE_BETA-00ff88?style=for-the-badge&labelColor=020507&color=00ff88)
![Products](https://img.shields.io/badge/PRODUCTS-2_ACTIVE-ffb800?style=for-the-badge&labelColor=020507&color=ffb800)
![Market](https://img.shields.io/badge/MARKET-NIFTY50%20%7C%20BSE%20%7C%20NSE-00d4ff?style=for-the-badge&labelColor=020507&color=00d4ff)
![Tech](https://img.shields.io/badge/POWERED_BY-MULTI--AGENT_AI-ff3b5c?style=for-the-badge&labelColor=020507&color=ff3b5c)

<br/><br/>

<!-- TECH STACK BADGES -->
![HTML](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=flat-square&logo=amazonaws&logoColor=white)
![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-222222?style=flat-square&logo=github&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)

</div>

---

<div align="center">

### *Transforming how India trades and invests — through AI systems that perceive, reason, and act on financial markets in real time.*

</div>

---

## ⚡ Overview

**NexAlpha** is the product brand for a suite of multi-agent AI systems built for the Indian financial markets. This repository contains the static website (`index.html`) — the public-facing landing page that communicates the company vision, presents both products, and directs users to the live beta applications.

> Both products are currently in **Beta v0.1**. Next-generation versions are actively in development.

---

## 🛰️ Live Products

<table>
<tr>
<td width="50%" valign="top">

### ⚙️ OptiTrade
**Multi-Agent Options Trading Assistant**

![OptiTrade](https://img.shields.io/badge/BETA-v0.1-ff3b5c?style=flat-square&labelColor=020507)
![Market](https://img.shields.io/badge/Nifty50-F%26O-00ff88?style=flat-square&labelColor=020507)

A sophisticated multi-agent system purpose-built for **Nifty50 Futures & Options** trading. Specialized agents collaborate in real time to scan the market, analyze options chains, and surface actionable signals.

**Capabilities:**
- Real-time Nifty50 options chain monitoring
- Multi-agent signal synthesis & validation
- Open interest & implied volatility analysis
- Risk-calibrated trade recommendations
- Live P&L tracking and Greeks dashboard

</td>
<td width="50%" valign="top">

### 📊 BharatAlpha
**AI Equity Research & Intelligence Platform**

![BharatAlpha](https://img.shields.io/badge/BETA-v0.1-ff3b5c?style=flat-square&labelColor=020507)
![Market](https://img.shields.io/badge/BSE%20%7C%20NSE-EQUITY-ffb800?style=flat-square&labelColor=020507)

A deep equity research platform built specifically for the **Indian market** — giving retail investors access to institutional-grade intelligence across BSE and NSE.

**Capabilities:**
- BSE & NSE comprehensive stock coverage
- AI-driven fundamental & technical analysis
- Sector rotation and macro intelligence
- Company-specific research report generation
- Portfolio screening and risk assessment

</td>
</tr>
</table>

> [!WARNING]
> Both OptiTrade and BharatAlpha are currently in **beta**. Features and interfaces are actively evolving. Next-generation versions with expanded capabilities and deeper agent collaboration are in development.

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript — zero dependencies, zero build step |
| **Typography** | Orbitron · Share Tech Mono · Syne — via Google Fonts |
| **Animations** | CSS keyframes, SVG stroke-dashoffset draw-on, IntersectionObserver API |
| **Visual FX** | CRT scanlines, animated grid background, canvas particles, custom cursor |
| **Hosting** | GitHub Pages — branch: `main`, root: `/` |
| **Product Backend** | AWS Application Load Balancer — region: `ap-south-1` |

---

## 📁 Repository Structure

```
nexalpha/
├── index.html        ← static website (all CSS & JS inline, zero dependencies)
└── README.md         ← this file
```

The entire site lives in a single `index.html`. No build step, no package manager, no framework required.

---

## 🚀 Local Development

```bash
# Clone the repository
git clone https://github.com/your-username/your-username.github.io.git
cd your-username.github.io

# Option 1 — open directly
open index.html

# Option 2 — Python server (recommended)
python -m http.server 5500
# → http://localhost:5500

# Option 3 — Node.js
npx serve .
# → http://localhost:3000
```

---

## 🌐 Deployment (GitHub Pages)

```bash
# Push your changes
git add .
git commit -m "deploy: update site"
git push origin main

# GitHub Pages will auto-redeploy within ~60 seconds
# Site live at: https://your-username.github.io
```

**Setup (first time):**
1. Go to **Settings → Pages** in your repository
2. Source: **Deploy from a branch** → `main` → `/ (root)`
3. Save — your site will be live at `https://your-username.github.io`

> [!NOTE]
> The product backends currently run on **HTTP** (AWS ALB). Since GitHub Pages enforces HTTPS, some browsers may block navigation as mixed content. The fix is to front both ALBs with a custom domain and ACM SSL certificate — expected during beta.

---

## 🗺️ Roadmap

| Status | Item |
|---|---|
| ✅ Done | Static site deployed on GitHub Pages |
| ✅ Done | OptiTrade Beta v0.1 — live on AWS ap-south-1 |
| ✅ Done | BharatAlpha Beta v0.1 — live on AWS ap-south-1 |
| 🔄 Next | HTTPS via custom domain & AWS Certificate Manager |
| ⬜ Planned | Live market data ticker via NSE/BSE API |
| ⬜ Planned | OptiTrade V2 — expanded instruments, predictive agents |
| ⬜ Planned | BharatAlpha V2 — deeper agent collaboration, portfolio intelligence |
| ⬜ Planned | Early-access waitlist form for V2 sign-ups |

---

## 🔧 Updating Product Links

The product URLs appear in **4 places** in `index.html`. Search for these strings to locate them:

```
href="http://optitrade-alb-...      ← OptiTrade card + CTA button
href="http://bharatalpha-alb-...    ← BharatAlpha card + CTA button
```

Replace with updated URLs whenever the backends are migrated or redeployed.

---

## ⚠️ Disclaimer

The content on this website is for **informational purposes only** and does not constitute financial advice. Trading in Futures and Options involves significant risk of loss. Users should conduct their own research and consult a SEBI-registered financial advisor before making investment decisions.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:ffb800,50:00ff88,100:020507&height=120&section=footer" width="100%"/>

**© 2025 NexAlpha — All Rights Reserved**

*Proprietary software. Unauthorized reproduction or distribution is not permitted.*

![Visitor Badge](https://visitor-badge.laobi.icu/badge?page_id=nexalpha.readme&left_color=020507&right_color=00ff88)

</div>
