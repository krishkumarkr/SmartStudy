# app/deepseek.py
import os, requests, json, re

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_URL = "https://openrouter.ai/api/v1/chat/completions"

def deepseek_process_text(text, max_items=10):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    You are SmartStudy AI.
    Based on the following note text, generate:
    1. Up to {max_items} flashcards (question + answer).
    2. Up to {max_items} quiz questions (with options + correct answer).
    3. A list of weak topics.

    Note:
    {text}

    Return strictly JSON (no explanations, no markdown).
    {{
      "flashcards": [{{"question": "...", "answer": "..."}}],
      "quizzes": [{{"question": "...", "options": ["..",".."], "answer": "..."}}],
      "weak_topics": ["topic1", "topic2"]
    }}
    """

    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful AI tutor."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(DEEPSEEK_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        raw_output = data["choices"][0]["message"]["content"]

        print("=== RAW DEEPSEEK OUTPUT ===")
        print(raw_output)

        #  Strip markdown fences if present
        cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", raw_output).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

        try:
            return json.loads(cleaned)
        except Exception as parse_err:
            print("JSON parse error:", parse_err)
            print("Cleaned output:", cleaned)
            return None

    except Exception as e:
        print("DeepSeek API error:", e)
        print("Response text:", getattr(e.response, "text", "No response"))
        return None
