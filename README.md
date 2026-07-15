# Dadrah Sarbazi RAG

سیستم پرسش‌وپاسخ حقوقی روی داده‌های سوال/جواب سربازی dadrah.ir با Hybrid Search (Dense + Sparse از BGE-M3)، Reranking (bge-reranker-v2-m3)، Milvus به‌عنوان vector store، و Memory برای مکالمه چندمرحله‌ای.

## معماری

1. `ingest.py` — داده JSON را می‌خواند، chunk می‌کند، با BGE-M3 امبدینگ دنس و اسپارس تولید می‌کند و در Milvus درج می‌کند.
2. `vector_store.py` — schema و جست‌وجوی هیبریدی (RRF بین dense و sparse) در Milvus.
3. `reranker.py` — نتایج بازیابی‌شده را با bge-reranker-v2-m3 دوباره رتبه‌بندی می‌کند.
4. `memory.py` — تاریخچه مکالمه هر session را نگه می‌دارد و سوال جدید را با توجه به تاریخچه بازنویسی می‌کند.
5. `rag_pipeline.py` — کل جریان را به هم وصل می‌کند: بازنویسی سوال → جست‌وجوی هیبریدی → rerank → تولید پاسخ با Claude.
6. `chat.py` — رابط خط فرمان برای تست تعاملی.

## نصب

```bash
python -m venv .venv
source .venv/bin/activate   # ویندوز: .venv\Scripts\activate
pip install -r requirements.txt
```

Milvus باید در دسترس باشد (ساده‌ترین راه، Docker):

```bash
curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh
bash standalone_embed.sh start
```

فایل `.env.example` را کپی و به `.env` تغییر نام دهید و مقادیر را پر کنید (به‌خصوص `ANTHROPIC_API_KEY`)، سپس قبل از اجرا آن‌ها را load کنید (مثلاً با `python-dotenv` یا `export` دستی).

## اجرا

### ورود داده

```bash
python ingest.py data/dadrah_sarbazi_qa.json
```

### رابط خط فرمان

```bash
python chat.py
```

### API + فرانت‌اند HTML

```bash
uvicorn api:app --reload --port 8000
```

سپس مرورگر را روی `http://localhost:8000` باز کنید؛ فایل `static/index.html` به‌صورت خودکار سرو می‌شود و با endpoint داخلی `/chat` صحبت می‌کند.

Endpointها:
- `POST /chat` — بدنه: `{"query": "...", "session_id": "..." (اختیاری)}` — خروجی: `{"session_id", "answer", "sources"}`
- `DELETE /session/{session_id}` — پاک‌کردن حافظه یک مکالمه
- `GET /health`

### فرانت‌اند Streamlit (جایگزین)

```bash
streamlit run streamlit_app.py
```

این نسخه مستقیماً از `RAGPipeline` استفاده می‌کند (بدون نیاز به اجرای جدای FastAPI).

## نکات

- بار اول اجرای `ingest.py` یا `chat.py`، مدل‌های BGE-M3 و bge-reranker-v2-m3 از HuggingFace دانلود می‌شوند (چند GB حجم؛ GPU برای سرعت بهتر توصیه می‌شود، ولی CPU هم کار می‌کند).
- `config.py` تمام پارامترهای قابل تنظیم (تعداد نتایج بازیابی، اندازه chunk، نام مدل تولید پاسخ و...) را در یک‌جا نگه می‌دارد.
- `full_context` در هر رکورد شامل عنوان + سوال + همه پاسخ‌هاست تا مدل تولید پاسخ، کل زمینه را ببیند، در حالی که جست‌وجو فقط روی `chunk_text` (عنوان+سوال) انجام می‌شود.
- برای افزایش کیفیت، می‌توانید `TOP_K_RETRIEVE` و `TOP_K_RERANK` را در `config.py` تنظیم کنید.
