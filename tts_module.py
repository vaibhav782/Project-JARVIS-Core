import requests

def generate_speech(text: str, filename: str = "response.mp3"):
    """Generates an MP3 audio file from text using Google Translate TTS."""
    formatted_text = text.replace(" ", "+")
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={formatted_text}&tl=en&client=tw-ob"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Project-JARVIS"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        with open(filename, "wb") as file:
            file.write(response.content)
        return True
    except Exception as e:
        print(f"[TTS Error] {e}")
        return False