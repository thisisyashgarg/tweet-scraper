# Project Ideas (Based on Arpit Bhayani's Tweets × Your Resume)

## 1. Build a JSON Parser from Scratch (TypeScript)

Arpit explicitly recommends this for every engineer. You already built **Typu** (cURL → TS types), so a JSON parser is a natural next step in the "developer tooling" niche. Parse a raw JSON string into a native JS object without using `JSON.parse`.

**What to build:**

- A recursive descent parser that handles all JSON types (objects, arrays, strings, numbers, booleans, null)
- Proper error messages with line/column numbers
- Published as an npm package
- Validate against the [JSON test suite](https://github.com/nst/JSONTestSuite)

**Why it's great for you:** Shows depth beyond frontend, strengthens your "dev tools" brand (Typu + this), and it's a genuine talking point in interviews.

---

## 2. News Aggregator with Article De-duplication

Arpit tweeted about building a Google News-like system where the hardest problem is de-duplicating articles across millions of documents using **MinHash + LSH**.

**What to build:**

- A Next.js app that ingests RSS feeds from multiple news sources
- De-duplicates similar articles using MinHash + LSH (implement the algo yourself)
- Groups related articles together
- Shows a clean, categorized news feed

**Why it's great for you:** Combines your Next.js expertise with an actual algorithmic challenge. Most frontend devs can't touch this.

---

## 3. Interactive Database Internals Visualizer

Arpit's #1 topic is database internals — B+ trees, WAL, MVCC, buffer pools, Bloom filters.

**What to build:**

- A visual, interactive web app (Next.js + Canvas/SVG) that lets people see:
  - How B+ tree insertions/splits work step by step
  - How Bloom filters register keys and produce false positives
  - How WAL writes happen before data pages
  - How LRU cache eviction works
- Animated, step-by-step walkthroughs with play/pause controls

**Why it's great for you:** Plays to your frontend strength while showing you understand low-level concepts. This would blow up on Twitter/HN because Arpit's audience craves exactly this kind of content.

---

## 4. Build a Search Engine from Scratch

Arpit calls this "one of the most interesting projects I did in college" — building a search engine on Wikipedia data without Elasticsearch/Solr/Lucene.

**What to build:**

- An inverted index from scratch in Node.js/TypeScript
- TF-IDF ranking for relevance
- A clean Next.js search UI with instant results
- Index Wikipedia dumps or a smaller dataset like blog posts

**Why it's great for you:** You already have Elastic Search on your resume (Hiretal). Building one from scratch shows you actually understand what's under the hood.

---

## 5. Address Matching Engine

Arpit tweeted about this twice — determining if two addresses refer to the same location (e.g., "221B Baker St." vs "221-B Baker Street").

**What to build:**

- Tokenize and normalize addresses (abbreviations, punctuation, ordering)
- Fuzzy matching using Levenshtein distance and Jaro-Winkler similarity
- Confidence scoring (0-100%) for each comparison
- Optionally use geocoding APIs as a fallback
- Clean API + comparison UI in Next.js

**Why it's great for you:** Real-world problem, great for a SaaS-style project. You could even integrate it with your recruitment platform experience (matching company addresses).

---

## 6. Rate Limiter as a Service

Arpit highlighted Stripe's 4-tier rate limiting system.

**What to build:**

- Multiple algorithms: token bucket, sliding window, fixed window
- A Next.js dashboard to configure limits per API key
- Redis-backed storage for distributed rate limiting
- Deployable as middleware or standalone service
- Real-time usage graphs

**Why it's great for you:** Backend-heavy project that fills a gap in your resume. Shows you can build infrastructure, not just UIs.

---

## 7. Procedural Terrain Generator (WebGL/Canvas)

Arpit spent a week on this and called the results "out of this world." Generate terrain programmatically using layered cosine functions (Perlin noise).

**What to build:**

- Real-time 3D terrain rendering using Three.js/WebGL in a Next.js app
- Sliders to tweak frequency, amplitude, octaves, and seed
- Color mapping based on elevation (water, grass, snow)
- Export terrain as a heightmap image

**Why it's great for you:** Visually stunning portfolio piece. Demonstrates creative coding ability beyond typical CRUD apps.

---

## Top 3 Picks for You

| # | Project                       | Why                                                              |
|---|-------------------------------|------------------------------------------------------------------|
| 1 | JSON Parser in TS             | Quick win, extends your Typu brand, shows depth                  |
| 2 | DB Internals Visualizer       | Your frontend skills + Arpit's audience = viral potential        |
| 3 | Search Engine from Scratch    | Upgrades your Elastic Search experience from "used it" to "built it" |

All three are achievable in 1–3 weekends, align with your TypeScript/Next.js stack, and give you something genuinely impressive to talk about.
