# VocaDine — User Documentation
**Voice-based restaurant finder for English-speaking tourists in Germany**

---

## Requirements

- Python 3.12+
- A microphone
- Internet connection (Google STT + Places API)
- A Google Places API key

---

## Installation

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

## Configuration

Create a `.env` file in the same folder as `main.py`:

```
GOOGLE_PLACES_API_KEY=your_key_here
```

---

## Run

```bash
python main.py
```

The assistant will greet you and begin asking questions. Speak naturally — you can answer multiple questions at once. Example:

> "I want Italian food for two in Munich tonight, nothing too fancy."

The assistant will skip any questions already answered and read out the top 3 restaurant recommendations.

---

## Tips

- Speak clearly and wait for the beep before answering
- You can say "stop asking" or "just find something" at any point to skip remaining questions
- City names: say the German city name naturally — the system handles common English pronunciations
- Say "any" or "no preference" to skip a question

---

## Troubleshooting

| Problem | Solution |
|---|---|
| "No results found" | Try a larger city or different cuisine |
| STT not responding | Check microphone permissions; speak after the prompt |
| API error | Check your `.env` file and API key quota |
| edge-tts silent | Check internet connection; edge-tts requires network access |
