### 1. The Enrollment Threshold
* **Metric:** 5 Successful Logins.
* **Reasoning:** A single session is an outlier. Five sessions allow the system to calculate a **Standard Deviation** and a **Mean**, creating a stable "Golden Baseline." During this phase, the system operates in "Passive Learning" mode.

### 2. The Matching Algorithm (Euclidean Distance)
* **Formula:** $d = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$
* **Logic:** We treat Dwell Time and Flight Time as coordinates on a 2D plane. If the "Distance" between today's login and the baseline is greater than **20.0**, the session is flagged.

### 3. Anti-Automation (Bot) Policy
* **Metric:** Timing Variance (Jitter).
* **Rule:** If Variance $< 2.0$, reject immediately.
* **Reasoning:** Human biology is noisy. Legitimate users cannot press keys with microsecond precision. A variance of near-zero is a mathematical signature of **Selenium** or **Puppeteer** scripts.

### 4. Risk-Based Actions (The RBA Matrix)
| Score | Status | Action Required |
| :--- | :--- | :--- |
| **0 - 20** | **Certified** | Allow access; update baseline (10% learning rate). |
| **21 - 50** | **Suspicious** | Step-up Authentication (Require SMS/Email OTP). |
| **50+ / Bot** | **Rejected** | Block session; flag for manual review. |
