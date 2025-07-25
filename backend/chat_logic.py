from openai import OpenAI
from openai import RateLimitError
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

QUESTIONS = [
    "Was bewegt dich momentan, tiefer ins Yoga einzutauchen?",
    "Welche dieser Aspekte faszinieren dich am meisten am Yoga?",
    "Wie lange praktizierst du bereits Yoga?",
    "Wie viel Zeit kannst du pro Woche realistisch investieren, ohne dass es stressig wird?",
    "Ist dir ein offizielles Zertifikat (z. B. Yoga Alliance) wichtig?",
    "Welche Lernform passt am besten zu deinem Alltag?",
    "Gibt es spezielle Themen oder Zielgruppen, mit denen du später arbeiten möchtest?"
]

EXAMPLE_PROMPT_TEMPLATE = """
Frage zum Thema Yoga: „{question}“
Antwort: „{answer}“
Bewerte, ob die Antwort zur Frage passt.
Die Antwort muss inhaltlich mit der Frage zusammenhängen und eine sinnvolle Reaktion darauf darstellen.
Wenn die Antwort stimmig ist, antworte ausschließlich mit: „Great!“.
Wenn die Antwort unklar, unpassend oder nicht mit der Frage verbunden ist, beginne mit:
„Die Antwort passt nicht zur Frage.“
und gib maximal drei passende Beispielantworten zur Orientierung an.
"""

user_sessions = {}

def init_thread(assistant_id):
    thread = client.beta.threads.create()
    return thread.id

def send_user_message(thread_id, message):
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )

def run_assistant(thread_id, assistant_id):
    try:
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        if run.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread_id, run_id=run.id)
            message_content = messages.data[0].content[0].text
            annotations = message_content.annotations

            # if not annotations:
            #     return "Entschuldigung, ich konnte es nicht finden. Für weitere Informationen kontaktieren Sie uns bitte über diesen Link: https://www.akshara.at/kontakt/"
            
            # Sorry, I couldn't find it. If you need more information, please contact us using this link: https://www.akshara.at/kontakt/

            return messages.data[0].content[0].text.value
        
        return "Failed to get a response from the assistant."
    
    except RateLimitError as e:
        # You could return a fallback response or a helpful message
        print("Ratenlimit der OpenAI-API überschritten:", str(e))
        return "Leider ist derzeit viel Verkehr vorhanden. Bitte versuchen Sie es in Kürze erneut."

def next_question(index):
    return QUESTIONS[index] if index < len(QUESTIONS) else None

def validate_answer(question_index, user_answer):
    prompt = EXAMPLE_PROMPT_TEMPLATE.format(
        question=QUESTIONS[question_index],
        answer=user_answer
    )
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = completion.choices[0].message.content
        if reply != "Great!":
            return False, reply
        return True, None
    except RateLimitError as e:
        # You could return a fallback response or a helpful message
        print("Ratenlimit der OpenAI-API überschritten:", str(e))
        return False, "Leider ist derzeit viel Verkehr vorhanden. Bitte versuchen Sie es in Kürze erneut.."
