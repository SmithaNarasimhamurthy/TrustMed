import streamlit as st
import re
import requests
import cohere
from youtube_transcript_api import YouTubeTranscriptApi
PUBMED_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

COHERE_API_KEY = "fnrnqLCIFLlD3cni3EvAaR1JXTayU28xJ0jlGqpY"

TELEGRAM_BOT_TOKEN = "8136633488:AAHGdqTBQgMuXZuOhIiCuIlxA3LML6R1upA"

# Google Search API Key & Custom Search Engine ID (Replace with yours)
GOOGLE_API_KEY = "AIzaSyBtzmH64cdd2qfwHYCiEktS6NV9dqNv4VI"
CSE_ID = "077476a678641496a"

# Initialize Cohere Client
co = cohere.Client(COHERE_API_KEY)

# Extract Video ID from YouTube URL
def extract_video_id(youtube_url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", youtube_url)
    return match.group(1) if match else None

# Fetch Transcript from YouTube Video
def extract_youtube_transcript(video_url):
    video_id = extract_video_id(video_url)
    if not video_id:
        return None
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript])
    except Exception as e:
        st.error(f"⚠️ Error fetching transcript: {e}")
        return None

# Extract Medical Claims Using Cohere
def extract_medical_claims(transcript):
    prompt = f"""Extract all **medical claims** from the given transcript.
Return only the claims, one per line.

Transcript:
{transcript}
"""
    response = co.generate(model="command", prompt=prompt, max_tokens=200)
    claims = response.generations[0].text.strip().split("\n")
    return [claim.strip() for claim in claims if claim.strip()]

# Google Custom Search
def google_search(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={CSE_ID}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [(item["title"], item["link"], item.get("snippet", "")) for item in data.get("items", [])]
    return []

# PubMed Search
def pubmed_search(query):
    params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": 5}
    response = requests.get(PUBMED_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if "esearchresult" in data and "idlist" in data["esearchresult"]:
            return [f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}" for pubmed_id in data["esearchresult"]["idlist"]]
    return []

# Generate AI-Based Summary Using Cohere
def cohere_summary(query, sources):
    prompt = f"""Summarize the verification of the following medical claim based on the provided sources. 
Don't mention anything like "Is there any more information I can provide" or "I can't access that data". Give a short summary.

Claim: '{query}'
Sources:
"""
    for title, link, snippet in sources:
        prompt += f"- {title}: {snippet} (Source: {link})\n"

    response = co.generate(model="command", prompt=prompt, max_tokens=100)
    return response.generations[0].text.strip()

# Verify Medical Claims
def verify_medical_claim(query):
    google_results = google_search(query)
    pubmed_results = pubmed_search(query)

    all_results = google_results + [(f"PubMed Article {i+1}", link, "") for i, link in enumerate(pubmed_results)]
    
    summary = "❌ No relevant results found."
    if all_results:
        summary = cohere_summary(query, all_results)

    return all_results, summary

# Streamlit UI
st.set_page_config(page_title="Medical Fake News Detector", layout="wide")
st.title("🩺 Medical Fake News Detector")

st.sidebar.header("🧐 Enter a medical claim or YouTube link:")
user_input = st.sidebar.text_input("Enter here:", "")

if st.sidebar.button("Analyze"):
    if user_input:
        if "youtube.com" in user_input or "youtu.be" in user_input:
            st.subheader("🔍 Analyzing YouTube Video")
            transcript = extract_youtube_transcript(user_input)
            if transcript:
                st.write("📜 **Extracted Transcript (First 500 characters):**")
                st.text(transcript[:500] + "...")
                
                claims = extract_medical_claims(transcript)
                if claims:
                    st.subheader("🔬 Detected Medical Claims:")
                    for i, claim in enumerate(claims, 1):
                        st.write(f"**{i}.** {claim}")

                    st.subheader("🛠️ Verifying Claims...")
                    for claim in claims:
                        st.write(f"🔎 **Claim:** {claim}")
                        sources, summary = verify_medical_claim(claim)
                        
                        if sources:
                            st.write("✅ **Verified Sources:**")
                            for title, link, snippet in sources[:5]:  # Show top 5 sources
                                st.markdown(f"- [{title}]({link}) - {snippet}")
                        st.write("🤖 **AI Summary:**", summary)
                else:
                    st.warning("❌ No medical claims detected in the transcript.")
            else:
                st.error("❌ No transcript available.")
        else:
            st.subheader("🔎 Verifying Medical Claim")
            sources, summary = verify_medical_claim(user_input)
            
            if sources:
                st.write("✅ **Verified Sources:**")
                for title, link, snippet in sources[:5]:
                    st.markdown(f"- [{title}]({link}) - {snippet}")
                st.write("🤖 **AI Summary:**", summary)
            else:
                st.error("❌ No relevant sources found.")
    else:
        st.warning("⚠️ Please enter a YouTube link or medical claim.")