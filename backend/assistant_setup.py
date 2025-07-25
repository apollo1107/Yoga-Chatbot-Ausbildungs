from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

PDF_FILES = [
    "files/main.pdf",
    "files/questions_direction.pdf",
    "files/200h-Yoga-Ausbildung-in-Indien-Goa.pdf",
    "files/200h-Yoga-Ausbildung-in-Kärnten.pdf",
    "files/200h-Yoga-Ausbildung-in-Mödling.pdf",
    "files/200h-Yoga-Ausbildung-in-Oberösterreich.pdf",
    "files/200h-Yoga-Ausbildung-online.pdf",
    "files/200h-Yoga-Grundausbildungen.pdf",
    "files/200h-Yogatherapie-Ausbildung.pdf",
    "files/300h-Yoga-Aufbaulehrgang.pdf",
    "files/Pranayama-Trainerin.pdf",
    "files/Sanskrit-School-für-Anfängerinnen.pdf",
    "files/Tantra-Yoga-Grundausbildung.pdf",
    "files/Trainerin-für-Meditation.pdf",
    "files/Vinyasa-Flow-Yoga-Trainerin.pdf",
    "files/Yin-Yoga-Trainerin.pdf",
    "files/Yoga-Foundation-Training.pdf",
    "files/Yoga-Gesundheitstrainer.pdf",
    "files/Yoga-Spezialisierungen.pdf",
    "files/Yoga-Vertiefungsworkshops.pdf",
]

# 1. Upload files
def upload_files():
    file_ids = []
    for path in PDF_FILES:
        with open(path, "rb") as f:
            file = client.files.create(file=f, purpose="assistants")
            file_ids.append(file.id)
    return file_ids

# 2. Create vector store
def create_vector_store(file_ids):
    vs = client.vector_stores.create(name="Yoga Course Store")
    client.vector_stores.file_batches.create_and_poll(
        vector_store_id=vs.id,
        file_ids=file_ids
    )
    return vs.id

# 3. Create assistant
def create_assistant(file_ids, vector_store_id):
    assistant = client.beta.assistants.create(
        name="Yoga Berater",
        # instructions="""
        #     Du bist Yogalehrer:in und unterstützt Kund:innen dabei, den passenden Yoga-Kurs zu finden.

        #     Dir werden 7 Fragen und die jeweiligen Antworten der Kund:innen bereitgestellt.
        #     Analysiere diese Antworten, um den passenden Yoga-Kurs zu identifizieren.
        #     Nutze file_search, um relevante Informationen aus den Kursunterlagen zu finden.
        #     Empfehle basierend auf den Antworten einen oder mehrere geeignete Kurse.

        #     Wenn du Informationen aus den Kursunterlagen gibst, füge am Ende der Antwort folgenden Satz hinzu:
        #     „Bei Fragen einfach fragen – ich helfe dir gerne weiter.“

        #     Beantworte danach alle Folgefragen der Kund:innen:
        #     – Bezieht sich die Frage auf Inhalte der Kurse, nutze file_search.  
        #     – Geht es um andere Themen, verwende dein allgemeines OpenAI-Wissen.

        #     Sei dabei stets klar, präzise und direkt auf die jeweilige Frage fokussiert.
        #     """,
        instructions = """
            Du bist Yogalehrer:in und unterstützt Kund:innen dabei, den passenden Yoga-Kurs zu finden.

            Dir werden 7 Fragen und die jeweiligen Antworten der Kund:innen bereitgestellt.
            Analysiere diese Antworten, um den passenden Yoga-Kurs zu identifizieren.
            Nutze file_search, um relevante Informationen aus den Kursunterlagen zu finden.

            Wenn du Informationen aus den Kursunterlagen verwendest, gib keine Quellverweise wie „ “ oder ähnliche an. Formuliere die Antwort natürlich und ohne solche Markierungen.

            Wenn keine passenden Informationen in den Kursunterlagen gefunden werden, beantworte die Frage mit deinem allgemeinen Wissen als Yogalehrer:in.

            Empfehle basierend auf den Antworten einen oder mehrere geeignete Kurse.
            Wenn du Informationen aus den Kursunterlagen gibst, füge am Ende der Antwort folgenden Satz hinzu:
            „Bei Fragen einfach fragen – ich helfe dir gerne weiter.“

            Beantworte danach alle Folgefragen der Kund:innen:
            – Bezieht sich die Frage auf Inhalte der Kurse, nutze file_search.  
            – Geht es um andere Themen, verwende dein allgemeines OpenAI-Wissen.

            Sei dabei stets klar, präzise und direkt auf die jeweilige Frage fokussiert.
            """,

        tools=[{"type": "file_search"}],
        model="gpt-3.5-turbo",
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
    ) 
    return assistant.id

# Run setup
if __name__ == "__main__":
    file_ids = upload_files()
    vector_store_id = create_vector_store(file_ids)
    assistant_id = create_assistant(file_ids, vector_store_id)
    print("Assistant ID:", assistant_id)