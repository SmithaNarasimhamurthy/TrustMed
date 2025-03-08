import re
import requests
import cohere
from youtube_transcript_api import YouTubeTranscriptApi
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# 🔹 Extract Video ID from YouTube URL
def extract_video_id(youtube_url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", youtube_url)
    return match.group(1) if match else None

# 🔹 Fetch Transcript from YouTube Video
def extract_youtube_transcript(video_url):
    video_id = extract_video_id(video_url)
    if not video_id:
        return None
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript])
    except Exception as e:
        print(f"⚠️ Error fetching transcript: {e}")
        return None

# 🔹 Extract Medical Claims Using Cohere
def extract_medical_claims(transcript):
    prompt = f"""Extract all **medical claims** from the given transcript.
Return only the claims, one per line.

Transcript:
{transcript}
"""

    response = co.generate(model="command", prompt=prompt, max_tokens=200)
    claims = response.generations[0].text.strip().split("\n")
    return [claim.strip() for claim in claims if claim.strip()]

# 🔹 Google Custom Search
def google_search(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={CSE_ID}&key={GOOGLE_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return [(item["title"], item["link"], item.get("snippet", "")) for item in data.get("items", [])]
    return []

# 🔹 PubMed Search
def pubmed_search(query):
    params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": 5}
    response = requests.get(PUBMED_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        if "esearchresult" in data and "idlist" in data["esearchresult"]:
            return [f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}" for pubmed_id in data["esearchresult"]["idlist"]]
    return []

# 🔹 Generate AI-Based Summary Using Cohere
def cohere_summary(query, sources):
    prompt = f"""Summarize the verification of the following medical claim based on the provided sources. 
Dont mention anything like "Is there any more information I can provide" or "I cant access that data". Give a short summary.

Claim: '{query}'
Sources:
"""
    for title, link, snippet in sources:
        prompt += f"- {title}: {snippet} (Source: {link})\n"

    response = co.generate(model="command", prompt=prompt, max_tokens=100)
    return response.generations[0].text.strip()

# 🔹 Verify Medical Claims
def verify_medical_claim(query):
    google_results = google_search(query)
    pubmed_results = pubmed_search(query)

    all_results = google_results + [(f"PubMed Article {i+1}", link, "") for i, link in enumerate(pubmed_results)]

    final_summary = cohere_summary(query, all_results) if all_results else "No relevant sources found."
    
    return all_results, final_summary

# 🔹 Analyze YouTube Video for Medical Claims
async def analyze_youtube_video(update: Update, video_url):
    transcript = extract_youtube_transcript(video_url)
    if not transcript:
        await update.message.reply_text("❌ No transcript available for this video.")
        return

    claims = extract_medical_claims(transcript)
    
    if not claims:
        await update.message.reply_text("❌ No medical claims detected in the transcript.")
        return
    
    for claim in claims:
        await update.message.reply_text(f"🔬 Claim: {claim}")

        sources, summary = verify_medical_claim(claim)

        for title, link, snippet in sources[:5]:  # Show top 5 results
            await update.message.reply_text(f"🔹 {title}\n📜 {snippet}\n🔗 {link}")

        await update.message.reply_text(f"📄 Summary: {summary}")

# 🔹 Process Medical Claim
async def process_medical_claim(update: Update, claim):
    sources, summary = verify_medical_claim(claim)

    for title, link, snippet in sources[:5]:  # Show top 5 results
        await update.message.reply_text(f"🔹 {title}\n📜 {snippet}\n🔗 {link}")

    await update.message.reply_text(f"📄 Summary: {summary}")

# 🔹 Handle User Messages
async def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text.strip()

    if "youtube.com" in user_input or "youtu.be" in user_input:
        await analyze_youtube_video(update, user_input)
    else:
        await process_medical_claim(update, user_input)

# 🔹 Handle Start Command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🤖 Welcome to the Medical Fake News Detector!\n📌 Send a YouTube link or a medical claim to verify."
    )

# 🔹 Main Function
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Bot is running...")
    app.run_polling()

# 🔹 Run the Telegram Bot
if __name__ == "__main__":
    main()
