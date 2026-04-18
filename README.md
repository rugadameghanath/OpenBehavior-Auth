# OpenBehavior-Auth
Open-Behavioral-Auth (OBA): A privacy-first, open-source engine for passive MFA. Capture user "rhythms"—keystroke dynamics and pointer velocity—via a lightweight JS SDK. Features adaptive threshold matching to handle behavioral drift across devices. Build and self-host your own RBA framework to detect anomalies without user friction.

---

# Project: Open-Behavioral-Auth (OBA)
**An Open-Source Behavioral Biometrics Engine for Risk-Based Authentication (RBA).**

OBA provides a plug-and-play SDK and a lightweight API to identify users based on their "digital rhythm"—how they type, move their mouse, and interact with touchscreens.

## 🚀 How it Works
OBA operates on a "Collect -> Extract -> Score" pipeline. It doesn't store what a user types (privacy-first), but rather the **timing and velocity** of their interactions.

1. **JS Collector:** A lightweight script hooked to DOM events.
2. **Feature Extraction:** API converts raw timestamps into deltas (Dwell, Flight, Jitter).
3. **Multi-Profile Matching:** Compare against historical averages based on Device Context.
4. **Adaptive Baseline:** Automatically updates the user's "Golden Profile" to account for natural behavior drift.

---

## 🛠 Project Structure
```text
├── sdk/                # Frontend JS (Vanilla/React/Vue support)
├── api/                # FastAPI / Go service for scoring logic
├── engine/             # The "Brain" (Euclidean & Cosine Similarity math)
├── migrations/         # SQL Schemas (MSSQL, Oracle, Postgres)
└── docs/               # Integration & Compliance (DPDPA/GDPR) guides
```

---

## 📊 Database Logic: Handling Multi-Context Drift
OBA doesn't just store one "average." It maintains a **Contextual Profile** to prevent false negatives when a user switches from a laptop to a mobile device.

| Feature | Desktop (Profile A) | Mobile (Profile B) |
| :--- | :--- | :--- |
| **Input Method** | Mechanical Keyboard | Virtual Keyboard (Thumb) |
| **Dwell Time** | ~80ms | ~115ms |
| **Velocity** | Mouse Move (High) | Touch Swipe (Medium) |
| **Precision** | Pixel-perfect | Radius-based |

The system uses a **weighted similarity score** to determine if the current session belongs to the "Same," "New," or "Impersonator" category.

---

## 🛡 Privacy & Security
* **Zero PII:** OBA does not collect keystroke characters. It only sees "Key Down" and "Key Up" intervals.
* **Hash-Based ID:** Users are identified via salted hashes of their existing UserIDs.
* **Self-Hosted:** Being open-source, the data stays in *your* database, ensuring compliance with local data residency laws.

---

## 📝 Roadmap
- [ ] Implement `performance.now()` precision handling for modern browsers.
- [ ] Add "Bot Detection" to filter out automated Selenium/Puppeteer scripts.
- [ ] Create a "Shadow Mode" for initial profile enrollment.
- [ ] Build a Dashboard to visualize "Drift" patterns over time.

---

### Tips for your GitHub Launch:
1.  **License:** Use the **MIT License** if you want maximum adoption, or **AGPL** if you want to ensure that anyone who modifies the engine must share their improvements back.
2.  **The "Hook":** In your intro, mention that this helps satisfy **Regulatory Requirements** (like the RBI 668 circular for RBA). This makes it professionally relevant to developers in the fintech space.
3.  **Visuals:** Add a "Live Demo" link where people can type a sentence twice and see their "Similarity Score" in real-time.
