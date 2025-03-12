# 🚀 AI-Powered CRM Insights & Automation

## 📌 Overview  
This project is an **AI-powered agent** that automates **customer insights generation** for businesses.  
It processes **CRM data**, **geolocates customers**, **analyzes purchase trends**, and generates **actionable insights** using **LLMs (OpenAI, Gemini, OpenRouter models)**.  
The insights are **automatically sent via email**, enabling businesses to make **smarter, data-driven decisions**.  

## 🔹 Key Features  
✅ **Automated Data Processing** – Fetches customer data from Google Sheets & cleans it.  
✅ **Geolocation Analysis** – Uses **Google Maps API** to pinpoint customer locations.  
✅ **AI-Generated Insights** – Supports **OpenAI API, Gemini, and OpenRouter models**.  
✅ **Smart Report Automation** – Sends **detailed HTML reports** via **Email (Gmail API)**.  
✅ **FastAPI-Powered API** – Provides endpoints to fetch and generate insights dynamically.  

---

## 🚀 How It Works
### **1️⃣ Data Collection & Processing**
- Reads **customer purchase data** from Google Sheets.  
- Cleans and validates data (fixes missing values, ensures consistency).  
- Uses **Google Maps API** to geocode addresses into latitude/longitude.  

### **2️⃣ AI-Powered Business Insights**
- Sends processed data to **AI models (OpenAI, Gemini, OpenRouter)**, which generates:  
  - **Customer Segmentation Insights** (High-value, medium-value, low-value customers).  
  - **Geographical Sales Analysis** (Best-performing & underperforming regions).  
  - **Purchase Trends** (Seasonal trends, top-selling products, peak buying times).  
  - **Actionable Business Recommendations** (Marketing, pricing, and inventory strategies).  

### **3️⃣ Report Delivery & Automation**
- The AI-generated report is formatted into **a professional HTML document**.  
- Reports are **sent automatically** via **Email (Gmail API)**.  
- Businesses get **real-time insights** directly in their inbox.  

---

## 🛠️ Tech Stack
✔ **FastAPI** – High-performance API backend.  
✔ **Google Sheets API** – Fetches and updates CRM data.  
✔ **Google Maps API** – Geolocates customers for regional analysis.  
✔ **OpenAI, Gemini & OpenRouter API** – Generates business insights & reports.  
✔ **Gmail API** – Sends automated reports via email.  

---

# 💻 Setup Guide

### 🔹 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai_agent_crm_geo_insights.git
cd ai_agent_crm_geo_insights
```

### 🔹 2. Create & Activate a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 🔹 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔹 4. Set Up API Keys & Credentials  

### **Google Sheets API & Gmail API**
Follow this guide to enable API access:  
📌 [Google Sheets API Setup](https://developers.google.com/sheets/api/quickstart/python)  
📌 [Gmail API Setup](https://developers.google.com/gmail/api/quickstart/python)  
- Save the `credentials.json` in the `keys/` folder.  

### **Google Maps API**
- Get an API key from [Google Cloud Console](https://console.cloud.google.com/).  
- Add it to `keys/keys.py`:  
```python
MAPS_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"
```

### **OpenAI, Gemini & OpenRouter API**
- Sign up at [OpenRouter](https://openrouter.ai/) and get an API key.  
- Add it to `keys/keys.py`:  
```python
OPEN_ROUTER_KEY = "YOUR_OPENROUTER_API_KEY"
```

- If using OpenAI or Gemini separately, add the respective API keys to `keys/keys.py` as well.

### **Store Credentials & Tokens**
- Place all OAuth tokens & service account JSON files inside `keys/`.  

---

### 🔹 5. Run the FastAPI Server
```bash
uvicorn main:app --reload
```
- Visit **Swagger UI** to test the API:  
  ```
  http://127.0.0.1:8000/docs
  ```

---

# 🚀 How to Use the API
### 📌 1. Generate Customer Insights
Fetch AI-powered business insights:
```bash
curl -X POST "http://127.0.0.1:8000/insights/generate"
```
or via Python:
```python
import requests
response = requests.post("http://127.0.0.1:8000/insights/generate")
print(response.json())
```

### 📌 2. Send Report via Email
```bash
curl -X POST "http://127.0.0.1:8000/insights/send-report"
```

---

# 📈 This project is **a showcase of AI(LLM)-powered automation for business intelligence**
🚀 **In-Demand Skills** – Uses AI, automation, and API integration.  
🎯 **Real-World Use Case** – Helps businesses improve customer insights effortlessly.  
📊 **High-Value Offering** – Automates data processing, geolocation, and AI insights.  
💼 **Freelancing Ready** – Can be customized for different industries (E-commerce, SaaS, etc.).  

---

# 🌍 Deployment (Optional)
### **Deploy on Render**
1. Push code to **GitHub**.
2. Create a new web service on [Render](https://render.com).
3. Use this **Start Command**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
4. Add **environment variables** for API keys.

### **Deploy with Docker**
1. Build and run using Docker:
   ```bash
   docker build -t ai-crm-insights .
   docker run -p 8000:8000 ai-crm-insights
   ```

---

# 🛠️ Future Enhancements
🔹 Add a **dashboard** for visualizing insights.  
🔹 Implement **scheduled reports** (e.g., daily/weekly).  
🔹 Expand to **WhatsApp & Slack bots** for insights delivery.  

---

