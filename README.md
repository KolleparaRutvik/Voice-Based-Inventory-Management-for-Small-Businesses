# 🎙️ Vyapari Voice — Voice-Based Inventory Management for Small Businesses

> **"Shopkeeper speaks. Vyapari Voice understands. The business gets updated."**

A voice-first smart inventory and business assistant designed for small Indian retailers, Kirana stores, grocery shops, and wholesalers. The system understands English, Telugu (`తెలుగు`), Hindi (`हिंदी`), and mixed-language speech (Tenglish / Hinglish) to manage stock, answer questions, and track customer credit with minimal typing.

---

## 📌 Problem & Motivation

Small businesses often manage inventory using physical notebooks, memory, spreadsheets, or messaging applications. This causes:
* **Inaccurate stock information** and misplaced counts
* **Missed low-stock alerts**, causing stockouts of essential staples
* **Manual, time-consuming data entry** during busy store hours
* **Lost revenue** from untracked customer credit (*Udhar*)
* **Language barriers** with complex POS systems requiring typed English

---

## 💡 The 4 Core Pillars

### 1. 📦 Product & Stock Management
* Full product catalog with regional naming (*బియ్యం, చక్కెర, నూనె, కందిపప్పు, బెల్లం*).
* Kirana unit conversion factors (e.g. 1 bag = 25 kg, 1 can = 15 L, 1 carton = 24 packets).
* Real-time stock valuation, purchase vs selling cost analysis, and retail profit margins.
* Dedicated product detail view with instant **+ Quick Stock In** and **- Quick Stock Out** modals.

### 2. 🌐 Regional Language Support
* Dynamic trilingual UI toggle: **English (`EN`)**, **Telugu (`తెలుగు`)**, and **Hindi (`हिंदी`)**.
* Complete localization of navigation, dashboard metrics, actions, and voice prompts.
* Web Speech API integration set to regional speech recognition codes (`te-IN`, `hi-IN`, `en-IN`) with native speech synthesis feedback.

### 3. 💡 Stock Questions & Smart Alerts
* Natural language store assistant powered by **Google Gemini 2.5 Flash**.
* Shopkeepers can ask natural business questions:
  * *"రైస్ స్టాక్ ఎంత ఉంది?"* (How much rice is in stock?)
  * *"నూనె ఎంత మిగిలింది?"* (How much oil is left?)
  * *"రమేష్ ఎంత బాకీ ఉన్నాడు?"* (How much udhar does Ramesh owe?)
  * *"ఏ వస్తువులు తక్కువ స్టాక్ ఉన్నాయి?"* (Which items are low in stock?)
* Real-time answers grounded directly in live PostgreSQL database tables + Text-to-Speech playback.

### 4. 🎙️ Voice-Based Stock Entry
* Speak mixed regional commands (*"5 బస్తాల బియ్యం కొన్నాం 1450 రూపాయలు"* or *"2 litres oil ammamu"*).
* Gemini 2.5 extracts structured intents (`STOCK_IN`, `STOCK_OUT`, `BORROW_OUT`), quantities, units, and prices.
* Human confirmation review card with editable values before ledger commit.
* Instant live update to inventory and immutable transaction ledger in PostgreSQL.

---

## 🏗️ Architecture

```mermaid
graph TD
    A[Shopkeeper / Retailer] -->|Speaks Telugu, Hindi, English| B(Web Speech API / Mic)
    B -->|Audio Transcript| C[React + Vite Frontend]
    C -->|REST API Request| D[Flask Backend Server]
    D -->|Real-Time Context Query| E[(Supabase PostgreSQL)]
    D -->|Context + NLU Prompt| F[Google Gemini 2.5 Flash]
    F -->|Structured Intent / Spoken Answer| D
    D -->|Stock & Ledger Sync| E
    D -->|Spoken Response + Card| C
    C -->|Audio TTS Feedback| A
```

---

## 📂 Project Structure

```
voice-inventory/
├── backend/                  # Flask REST API
│   ├── app/
│   │   ├── routes/           # Blueprints: auth, products, inventory, voice, assistant, borrowings, etc.
│   │   ├── utils/            # Auth middleware, postgres_client, responses, supabase_client
│   │   └── config/           # Environment configuration
│   ├── run.py                # Server entry point (port 5000)
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Sample backend configuration
├── database/                 # PostgreSQL & Supabase Database
│   ├── schema.sql            # Complete relational schema (21 tables)
│   ├── seed.sql              # Seed SQL data
│   ├── seed_supabase.py      # Automated database seeder
│   └── apply_schema.py       # Schema migration runner
├── frontend/                 # React 18 + Vite + TypeScript
│   ├── src/
│   │   ├── components/       # LanguageSwitcher and shared components
│   │   ├── context/          # AuthContext, LanguageContext (te, hi, en)
│   │   ├── layouts/          # AppLayout (with multi-language drawer & navbar)
│   │   ├── pages/            # Dashboard, Products, ProductDetail, Inventory, Voice, Borrowings, Orders, Analytics
│   │   ├── services/         # Axios API service layer
│   │   └── types/            # TypeScript models
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
* **Node.js**: v18+
* **Python**: v3.11+
* **PostgreSQL / Supabase**: Free project from [supabase.com](https://supabase.com)
* **Google Gemini API Key**: Free key from [Google AI Studio](https://aistudio.google.com/)

---

### 1. Database Setup
1. Create a project in [Supabase](https://supabase.com).
2. Run `database/schema.sql` in the Supabase SQL Editor to create all 21 tables with foreign keys and indexes.
3. (Optional) Run `python database/seed_supabase.py` to seed sample Indian Kirana store products, inventory, suppliers, and customer udhar.

---

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Create `backend/.env`:
```env
FLASK_APP=run.py
FLASK_ENV=development
PORT=5000
DATABASE_URL=postgresql://postgres.your-project:your-password@aws-0-region.pooler.supabase.com:6543/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-publishable-or-service-key
GEMINI_API_KEY=your-gemini-api-key
JWT_SECRET=your-secret-key
```

Start the Flask server:
```bash
python run.py
```
Backend runs at `http://localhost:5000`.

---

### 3. Frontend Setup
```bash
cd frontend
npm install
```

Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:5000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-publishable-key
```

Start Vite dev server:
```bash
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🧪 Testing & Verification

1. **Explore Demo Store**: Click the "Explore Demo Store" button on the login screen.
2. **Multi-Language Toggle**: Switch between **English**, **తెలుగు**, and **हिंदी** via the globe selector in the header or sidebar.
3. **Voice Stock Entry**: Head to `/voice`, speak *"5 బస్తాల బియ్యం కొన్నాం"* or click a quick command chip, inspect the confirmation card, and click Confirm.
4. **Stock Queries**: Switch to the **Stock Questions & AI** tab, tap *"రైస్ స్టాక్ ఎంత ఉంది?"*, and hear Vyapari Voice reply with the real-time stock balance.
5. **Customer Udhar**: Visit `/borrowings` to view pending customer credit, record payments, and click **WhatsApp Reminder** to generate prefilled payment reminder links.

---

## 📄 License
This project is licensed under the MIT License.
