# TanvirSdqBot — Wikimedia Automation Tools

Python-based bots and scripts developed as part of **NDEC WERT** (Notre Dame College Wikimedia Editorial & Research Team) to support Wikipedia and Wikidata editing in 2024.

**Main achievements using these tools:**
- Structured the newly created Fulani Wikipedia (~10,000 articles) by adding ~25 core categories based on English Wikipedia patterns.
- Automated welcome messages for new editors.
- Processed and visualized data for Wikimedia Commons events (Wiki Loves Folklore, Wiki Loves Earth, etc.).

---

## 🏗️ Architecture

### 1. System Overview (ASCII)

```
========================================================================================
                  TANVIRSDQBOT — WIKIMEDIA AUTOMATION ARCHITECTURE
========================================================================================

   [ Bot Operator / Script Runner ]
                  │
                  ▼  Local Python execution (JupyterLab / CLI)
   ┌──────────────────────────────────────────────────────────────────────┐
   │                        BOT DISPATCHER                               │
   ├────────────────────┬────────────────────┬────────────────────────────┤
   │  Category Module   │  Welcome Module    │     Survey Module          │
   │  (Category/)       │  (Welcome/)        │     (Survey/)              │
   │  Bulk category     │  Auto-welcome      │  Event data collection,    │
   │  mapping & assign  │  new editors       │  heatmaps & stats          │
   └─────────┬──────────┴────────┬───────────┴────────────┬───────────────┘
             │                  │                         │
             ▼                  ▼                         ▼
   ┌──────────────────────────────────────────────────────────────────────┐
   │                         PYWIKIBOT FRAMEWORK                          │
   ├──────────────────────────────────────────────────────────────────────┤
   │  • MediaWiki Action API (read/write operations)                      │
   │  • OAuth / BotPassword authentication                                │
   │  • Rate limiting & edit throttle compliance                          │
   │  • Page, Category & User object abstractions                         │
   └───────────────────────────────────┬──────────────────────────────────┘
                                       │
                                       ▼
   ┌──────────────────────────────────────────────────────────────────────┐
   │                    WIKIMEDIA PRODUCTION PROJECTS                      │
   │  • Fulani Wikipedia (ff.wikipedia.org) — Category expansion          │
   │  • English Wikipedia — Welcome messages & user talk operations       │
   │  • Wikimedia Commons — Event data & survey analysis                  │
   └──────────────────────────────────────────────────────────────────────┘

========================================================================================
```

---

### 2. Bot Operation Lifecycle (Mermaid)

```mermaid
sequenceDiagram
    autonumber
    actor Operator as Bot Operator
    participant Script as Bot Script (Python)
    participant PWB as Pywikibot Framework
    participant API as MediaWiki Action API
    participant Wiki as Wikimedia Project

    Operator->>Script: Execute script (e.g. Category/categorize.py)
    Script->>PWB: Initialize site & authenticate (BotPassword / OAuth)
    PWB->>API: POST login token request
    API-->>PWB: Return login token & session
    PWB-->>Script: Authenticated site object

    loop For each target page / user
        Script->>PWB: Fetch page / category / user object
        PWB->>API: GET action=query (page content / user info)
        API-->>PWB: Return wikitext / metadata
        PWB-->>Script: Page/User object

        Script->>Script: Apply transformation\n(add category / compose welcome msg)
        Script->>PWB: page.save(summary="Bot: ...")
        PWB->>API: POST action=edit (with CSRF token)
        API-->>Wiki: Commit edit to live project
        API-->>PWB: Return edit success/failure
        PWB-->>Script: Result status
    end

    Script-->>Operator: Print edit summary & statistics
```

---

### 3. Module Taxonomy

```mermaid
flowchart LR
    subgraph Bot["TanvirSdqBot Repository"]
        direction TB
        CAT["Category/\nBulk category mapping\nfor Fulani Wikipedia\n~25 core categories\nadded to ~10k articles"]
        WEL["Welcome/\nAutomatic welcome\nmessages for new\nWikipedia editors"]
        SUR["Survey/\nWiki Loves event\ndata collection,\nheatmap generation\n& statistics"]
    end

    subgraph Core["Pywikibot Core"]
        PWB["pywikibot\nlibrary"]
        API["MediaWiki\nAction API"]
    end

    subgraph Projects["Live Wikimedia Projects"]
        FF["Fulani Wikipedia\n(ff.wikipedia.org)"]
        EN["English Wikipedia\n(en.wikipedia.org)"]
        COM["Wikimedia Commons\n(commons.wikimedia.org)"]
    end

    CAT --> PWB
    WEL --> PWB
    SUR --> PWB
    PWB --> API
    API --> FF
    API --> EN
    API --> COM

    classDef mod fill:#e8f5e9,stroke:#388e3c,stroke-width:2px;
    classDef core fill:#ede7f6,stroke:#5e35b1,stroke-width:2px;
    classDef wiki fill:#e3f2fd,stroke:#1976d2,stroke-width:2px;
    class CAT,WEL,SUR mod;
    class PWB,API core;
    class FF,EN,COM wiki;
```

---

### 4. Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Bot Framework** | Pywikibot | Official Wikimedia bot framework for Python; handles API auth, throttling, and page operations |
| **API Layer** | MediaWiki Action API | Read/write interface to all Wikimedia projects (Wikipedia, Commons, Wikidata) |
| **Data Analysis** | Pandas, Matplotlib | Event data aggregation, contributor statistics, and heatmap visualization |
| **Runtime** | Python 3.9+, JupyterLab | Development and execution environment |
| **Auth** | BotPassword / OAuth | Secure, rate-limited bot authentication on Wikimedia infrastructure |

---

## Repository Structure

- **`Category/`** → Scripts for bulk category mapping and assignment (core Fulani Wikipedia categorization project).
- **`Welcome/`** → Bot code for sending welcome messages to new users.
- **`Survey/`** → Tools related to Wiki Loves event data collection, analysis, and visualization.

## Setup & Usage

1. Install pywikibot: `pip install pywikibot pandas matplotlib`
2. Configure `user-config.py` with your BotPassword credentials.
3. Run any script from the relevant module directory.

> **Note:** These are production-tested scripts. Some require your own pywikibot setup and credentials.

## License

MIT License — feel free to reuse or adapt.
