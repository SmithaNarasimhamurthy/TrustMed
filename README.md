# TrustMed
AI-Powered Fake Health News Detector is a chatbot that identifies fake health news using AI &amp; NLP. It analyzes news articles, provides a text summary, and offers trusted sources from WHO, CDC, and PubMed. The chatbot works on Telegram and websites for real-time fact-checking. 
Here's a **README.md** for your GitHub repository:   

## 📌 Overview  
The **Fake Health News Detector** is an AI-powered chatbot designed to identify **misinformation in health-related news**. Using **Natural Language Processing (NLP)** and **machine learning**, it analyzes news articles, generates a **text summary**, and provides **trusted sources** from organizations like WHO, CDC, and PubMed.  

## 🚀 Features  
- ✅ **Fake News Detection**: Classifies news as **real or fake** using AI.  
- 📝 **Text Summarization**: Provides a concise summary of the analyzed news.  
- 🔍 **Trusted Sources**: Offers verified references from WHO, CDC, and PubMed.  
- 🌐 **Cross-Platform API**: Easily integrates with websites and applications.  

## 🛠️ Technologies Used  
- **Python**, **FastAPI**, **Flask** (for backend services)  
- **BERT**, **XGBoost**, **TF-IDF** (for NLP & classification)  
- **Twilio API** (for chatbot integration)  

## ⚡ Installation & Setup  
1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/fake-health-news-detector.git  
   cd fake-health-news-detector  
   ```  
2. **Install dependencies**  
   ```bash
   pip install -r requirements.txt  
   ```  
3. **Run the FastAPI server**  
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 5000 --reload  
   ```  
4. **Expose local server using ngrok**  
   ```bash
   ngrok http 5000  
   ```  

## 📡 API Usage  
- **Endpoint:** `POST /predict`  
- **Request Body:**  
   ```json
   {
     "text": "Drinking lemon juice cures cancer completely!"
   }
   ```  
- **Response:**  
   ```json
   {
     "prediction": "🛑 Fake News",
     "summary": "Lemon juice does not cure cancer. No scientific evidence supports this claim.",
     "trusted_sources": [
       "https://www.who.int",
       "https://www.cdc.gov",
       "https://pubmed.ncbi.nlm.nih.gov"
     ]
   }
   ```  

## 📌 Future Enhancements  
- Expand dataset for better accuracy  
- Improve **explainability** of AI predictions  
- Add support for analyzing **videos & images**  

🚀 **Contributions are welcome!** Feel free to open issues and submit pull requests.  

---

Let me know if you need any modifications! 😊
