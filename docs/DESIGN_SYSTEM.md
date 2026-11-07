# VERITAS AI — Enterprise Design System Specification

## 1. Brand & Design Principles

* **Restrained Precision:** Developer-focused, minimalist aesthetics. High visual density with clean typographic hierarchy.
* **Truthful Representation:** No arbitrary decorations, excessive gradients, or fake telemetry. Empty states clearly instruct the user on how to populate data.
* **High-Contrast Readability:** Adheres to WCAG 2.2 Level AA contrast requirements across both dark and light color modes.

---

## 2. Color Palette & Semantic Tokens

### Neutral Palette (Slate/Zinc Foundation)
* **Background Deep (Dark):** `#090d16` / `#0f172a`
* **Card & Surface Background:** `#131c2e` / `#1e293b`
* **Border & Separators:** `#1e293b` / `#334155`
* **Text Primary:** `#f8fafc` (Dark Mode), `#0f172a` (Light Mode)
* **Text Secondary:** `#94a3b8` (Dark Mode), `#475569` (Light Mode)
* **Text Muted:** `#64748b`

### Semantic Action & Status Colors
* **Primary Accent (Indigo/Blue):** `#3b82f6` (Primary buttons, active tabs, focus rings)
* **Success / Pass / Verified (Emerald):** `#10b981` (Passing gates, healthy distributions, SHA-256 verified)
* **Warning / Alert / Drift (Amber):** `#f59e0b` (Statistical warning thresholds, minor regressions)
* **Danger / Blocked / Error (Rose):** `#ef4444` (Blocked CI deployments, critical drift, severe failures)
* **Governance / Ledger (Violet/Purple):** `#8b5cf6` (Cryptographic blocks, SR 11-7 regulatory tags)

---

## 3. Typography & Spacing Scale

* **Font Families:**
  * UI Text: `Geist Sans`, `Inter`, system `-apple-system`, `sans-serif`
  * Monospace / Hashes / Code: `Geist Mono`, `JetBrains Mono`, `monospace`
* **Type Hierarchy:**
  * Display Heading: `text-3xl font-extrabold tracking-tight`
  * Section Title: `text-xl font-bold tracking-tight`
  * Subsection Heading: `text-sm font-semibold uppercase tracking-wider text-slate-400`
  * Body Text: `text-sm text-slate-200 leading-relaxed`
  * Code / Metadata: `text-xs font-mono text-slate-400`
* **Component Elevation & Radii:**
  * Standard Radius: `rounded-lg` (8px) for buttons, inputs, and cards
  * Micro Radius: `rounded-md` (6px) for badges and tags
  * Border Width: `border border-slate-800`
