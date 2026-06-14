from llm import generate_message
from fastapi import FastAPI

app = FastAPI()

categories = {}
merchants = {}
customers = {}
triggers = {}

@app.get("/v1/healthz")
def healthz():
    return {
        "status": "ok",
        "contexts_loaded": {
            "category": len(categories),
            "merchant": len(merchants),
            "customer": len(customers),
            "trigger": len(triggers)
        }
    }

@app.post("/v1/context")
def receive_context(data: dict):

    scope = data["scope"]
    context_id = data["context_id"]
    payload = data["payload"]

    if scope == "category":
        categories[context_id] = payload

    elif scope == "merchant":
        merchants[context_id] = payload

    elif scope == "customer":
        customers[context_id] = payload

    elif scope == "trigger":
        triggers[context_id] = payload

    return {
        "accepted": True
    }

@app.post("/v1/tick")
def tick(data: dict):

    merchant = merchants.get("m_001")

    if not merchant:
        return {"actions": []}

    trigger = next(iter(triggers.values()), None)

    if not trigger:
        trigger_kind = "general"
    else:
        trigger_kind = trigger.get("kind", "general")

    prompt = f"""
You are Vera, an AI growth assistant for local merchants.

Merchant:
{merchant}

Trigger Type:
{trigger_kind}

Write ONE WhatsApp message.

Requirements:
- Address the merchant by name.
- Use merchant facts.
- Adapt to the trigger type.
- Be specific.
- Ask exactly one follow-up question.
- Keep under 60 words.
- Do not invent facts.

Return only the message.
"""

    message = generate_message(prompt)

    return {
        "actions": [
            {
                "conversation_id": "conv_001",
                "merchant_id": "m_001",
                "trigger_kind": trigger_kind,
                "body": message
            }
        ]
    }
@app.post("/v1/reply")
def reply(data: dict):

    user_message = data.get("message", "")

    response = generate_message(
        f"""
        You are Vera.

        Merchant said:
        {user_message}

        Reply naturally in under 40 words.
        """
    )

    return {
        "action": "send",
        "body": response
    }
@app.get("/v1/metadata")
def metadata():
    return {
        "team_name": "Vidhi Vera Bot",
        "model": "gemini-2.5-flash",
        "version": "1.0"
    }