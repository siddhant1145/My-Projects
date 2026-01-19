from flask import Flask, request, jsonify, render_template
from groq import Groq
import datetime
from googlesearch import search

# Load environment variables

Username = "Your_Name"
Assistantname = "Assistant_name"
GroqAPIKey = "Your_Grog_API"

client = Groq(api_key=GroqAPIKey)

System = f"""
Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

def google_search(query):
    try:
        results = list(search(query, advanced=True, num_results=5))
        answer = f"Search results for '{query}':\n"
        for result in results:
            answer += f"\nTitle: {result.title}\nDescription: {result.description}\nURL: {result.url}\n"
        return answer
    except Exception as e:
        return f"Search error: {e}"

def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        f"Day : {now.strftime('%A')}\n"
        f"Date : {now.strftime('%d')}\n"
        f"Month : {now.strftime('%B')}\n"
        f"Year : {now.strftime('%Y')}\n"
        f"Time : {now.strftime('%H')}h:{now.strftime('%M')}m:{now.strftime('%S')}s\n"
    )

def AnswerModifier(answer):
    return '\n'.join([line for line in answer.split('\n') if line.strip()])

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]
messages = []
def RealTimeChatBot(query):
    try:

        messages.append({"role": "user", "content": google_search(query)})

        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True
        )

        answer = ""
        for chunk in completion:
            content_piece = getattr(chunk.choices[0].delta, "content", None)
            if content_piece:
                answer += content_piece

        messages.append({"role": "assistant", "content": answer})

        return AnswerModifier(answer)
    except Exception as e:
        return f"Error: {e}"

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    query = request.json.get("query", "")
    answer = RealTimeChatBot(query)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
