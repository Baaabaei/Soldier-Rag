from rag_pipeline import RAGPipeline


def main():
    pipeline = RAGPipeline()
    session_id = "cli-session"

    print("سیستم پرسش و پاسخ حقوقی سربازی آماده است. برای خروج 'exit' بنویسید.")

    while True:
        query = input("\nسوال شما: ").strip()
        if query.lower() == "exit":
            break
        if not query:
            continue

        answer_text, sources = pipeline.answer(session_id, query)

        print(f"\nپاسخ:\n{answer_text}")
        print("\nمنابع:")
        for url in sources:
            print(f"  - {url}")


if __name__ == "__main__":
    main()
