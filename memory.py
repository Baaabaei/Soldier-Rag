from anthropic import Anthropic
import config


class ConversationMemory:
    def __init__(self, max_turns=config.MEMORY_MAX_TURNS):
        self.sessions = {}
        self.max_turns = max_turns
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    def add_turn(self, session_id, role, content):
        history = self.sessions.setdefault(session_id, [])
        history.append({"role": role, "content": content})
        self.sessions[session_id] = history[-self.max_turns:]

    def get_history(self, session_id):
        return self.sessions.get(session_id, [])

    def contextualize_query(self, session_id, query):
        history = self.get_history(session_id)
        if not history:
            return query

        history_text = "\n".join(f"{h['role']}: {h['content']}" for h in history)

        prompt = (
            "با توجه به تاریخچه گفتگوی زیر، سوال جدید کاربر را طوری بازنویسی کن که مستقل و کامل باشد "
            "و بدون نیاز به تاریخچه قابل فهم باشد. فقط سوال بازنویسی‌شده را برگردان، بدون هیچ توضیح اضافه.\n\n"
            f"تاریخچه:\n{history_text}\n\nسوال جدید: {query}\n\nسوال بازنویسی‌شده:"
        )

        response = self.client.messages.create(
            model=config.GENERATION_MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text.strip()
