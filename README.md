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

## 🛡️ Invisible Device Binding
Beyond behavioral rhythm, the engine captures a **Hardware Fingerprint** to verify the environment:
* **CPU Core Count:** Detects hardware-level shifts.
* **Screen Resolution:** Identifies display environment anomalies.
* **Timezone Consistency:** Cross-references network IP location with device system time.
* **Platform/OS Signature:** Ensures the session originates from authorized operating systems.

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
## 📂 Audit Trail Architecture
Each authentication event generates a self-contained **ISO 8601** compliant CSV package in the `logs/` folder.
* **Format:** `LOG_YYYYMMDD_HHMMSS_ffffff.csv`
* **PII Protection:** User identities are stored *inside* the encrypted/secure files, while filenames remain strictly chronological to prevent metadata leaks.

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

## ⚙️ Data Storage Configuration

OpenBehavior-Auth is designed to be infrastructure-agnostic. You can deploy this project locally, on serverless platforms, or on enterprise hardware without modifying the core API logic.

Data routing is controlled entirely via the `storage_mode` parameter in `config.json`.

| `storage_mode` Value | Infrastructure | Description |
| :--- | :--- | :--- |
| `"local_csv"` | **Local Machine (Default)** | Perfect for testing and student projects. Generates a local `biometrics_db.csv` file that can be opened directly in Microsoft Excel. |
| `"sql_db"` | **VPS / Enterprise** | Routes data to the SQL adapter. Designed for deployment on DigitalOcean, AWS EC2, or internal bank servers using SQLite, PostgreSQL, or Oracle. |
| `"cloud_api"` | **Netlify / Vercel / Cloudflare** | Routes data to the Webhook adapter. Ideal for serverless deployments where you want to POST data to a third-party service like Google Sheets API, Supabase, or Firebase. |



**To change your environment:**
1. Open `config.json`.
2. Update the `"storage_mode"` string.
3. Restart the FastAPI server. The router will automatically attach the correct database adapter.


Parameter,Default,Description
enrollment_sessions,3,Number of attempts required to build the initial user profile.
threshold,50.0,The similarity score (0-100) required to achieve CERTIFIED status.
storage_mode,local_csv,Defines the storage backend (currently supports daily ISO-rotated CSVs).

## 🚀 Quick Start (Local Testing)

1. **Clone & Install:**
   ```bash
   git clone [https://github.com/your-username/OpenBehavior-Auth.git](https://github.com/your-username/OpenBehavior-Auth.git)
   cd OpenBehavior-Auth
   pip install fastapi uvicorn

2. **Launch the Engine:**

Bash
python -m uvicorn api.main:app --reload

3. **Access the Lab:**
Open http://127.0.0.1:8000/test.html in your browser.
Note: No internet connection is required as the lab uses zero-dependency Vanilla JS.


## 🔒 Privacy & Data Policy
This engine follows a **Logic-Only** synchronization policy. 
- **Tracked Files:** All `.py` and `.html` files containing core logic.
- **Ignored Files:** All files in the `logs/` directory and `.csv` files are excluded via `.gitignore`. 
This ensures that your local biometric audit trails remain private and are never uploaded to the public repository.

