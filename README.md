# Afyniq 🥑

A smart nutrition tracking PWA for Kenya, powered by Gemini AI.

## 🚀 How to Run Locally

1.  **Open Terminal**: Go to the project folder.
2.  **Activate Virtual Environment** (Optional but recommended):
    ```bash
    # Windows
    venv\Scripts\activate
    ```
3.  **Install Dependencies** (If you haven't yet):
    ```bash
    pip install -r requirements.txt
    ```
4.  **Start the Server**:
    ```bash
    python main.py
    ```
5.  **Open in Browser**:
    Visit `http://localhost:5000`

## 📸 Rate Limits (Fair Usage)

To prevent abuse and manage AI costs, the following limits apply per user (by IP address):

*   **Camera/AI Analysis**: **5 pictures per minute**.
    *   *Why?* AI analysis is expensive and computationally heavy. This prevents rapid-fire spamming.
*   **Login/Register**: **10 attempts per minute**.
    *   *Why?* To stop hackers from guessing passwords (brute-force attacks).
*   **Global Limit**: **200 requests per day**.
    *   *Why?* General protection for the server.

## 📱 How to Verify It's an App (PWA)

**On Desktop (Chrome/Edge):**
1.  Open `http://localhost:5000`.
2.  Look at the right side of the URL address bar.
3.  You should see a small **"Install Afyniq"** icon (monitor with a down arrow).
4.  Click it to install. It will open in its own standalone window, removing the browser interface.

**On Mobile (Android - Chrome):**
1.  (Requires HTTPS or Port Forwarding to test on phone, or deploy to Vercel).
2.  Once deployed, visit the site.
3.  You should see an **"Install App"** button (or "Add to Home Screen" prompt).
4.  Once installed, it appears as a native app icon on your home screen and launches without the browser bar.

## 🛠️ Features
*   **AI Food Detection**: Identifies Kenyan foods (Sukuma Wiki, Ugali, Chapati, etc.).
*   **Multi-Tenancy**: Private data for each user.
*   **Offline Support**: Caches basic assets (PWA).
*   **Security**: Rate limiting and encrypted passwords.
