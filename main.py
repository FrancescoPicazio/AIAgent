from core.Agent import AgentInstance

if __name__ == "__main__":
    agent = AgentInstance("llama3.1")
    while True:
        try:
            question = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye.")
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            print("Bye.")
            break

        print(agent.invoke(question, show_progress=True))
