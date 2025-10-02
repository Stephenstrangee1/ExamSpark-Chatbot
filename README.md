# ExamSpark-Chatbot
AI Chatbot for UGC NET/CSIR Prep: Instant exam tips, syllabus breakdowns, and enrollment guidance from Professor Academy.
# Professor Academy Chatbot

Flask + Gemini AI chatbot for coaching queries.
![Uploading image.png…]()

## Setup
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env`, add keys.
3. Put `service_account.json` in `credentials/`.
4. `python run.py`
5. Open http://localhost:5000

## Endpoints
- POST /chat { "message": "hi" }
- POST /save_subject { "subject": "math" }

License: MIT
