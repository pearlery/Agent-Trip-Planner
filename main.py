import os
import sys
from dotenv import load_dotenv
from rich.prompt import Prompt

load_dotenv()

from logger_utils import console, log_step
from rag.loader import load_documents_from_dir
from rag.vector_store import TravelVectorStore, CHROMA_DATA_PATH
from tools.semantic_search import init_search_tool, semantic_search
from tools.exchange_rate import get_exchange_rate
from tools.hotel_search import search_hotels
from agent import TravelAgent

DATA_DIR = "./data"
CSV_PATH = "data/tours_merged_cleaned2.csv"
CHROMA_DIR = CHROMA_DATA_PATH

# Backend: "typhoon" (default) | "ollama" | "groq"
BACKEND = os.getenv("LLM_BACKEND", "typhoon")

# Typhoon model (Thai LLM by SCB10X — needs TYPHOON_API_KEY)
TYPHOON_MODEL = os.getenv("TYPHOON_MODEL", "typhoon-v2.5-30b-a3b-instruct")

# Ollama model (local, no API key needed)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

# Groq model (cloud, open-source — needs GROQ_API_KEY)
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def setup_vector_store() -> TravelVectorStore:
    vs = TravelVectorStore(persist_dir=CHROMA_DIR)
    if vs.count() > 0:
        log_step("Setup", f"ChromaDB ready: {vs.count()} records loaded", "green")
        return vs

    log_step("Setup", "Vector store empty — indexing data...", "yellow")

    # Priority 1: CSV tour data
    if os.path.exists(CSV_PATH):
        from rag.vector_store import init_vector_db
        init_vector_db(csv_path=CSV_PATH, persist_dir=CHROMA_DIR)
        log_step("Setup", f"Indexed CSV: {vs.count()} records", "green")
        return vs

    # Priority 2: PDF/TXT files in data/
    if os.path.exists(DATA_DIR):
        chunks, metas = load_documents_from_dir(DATA_DIR)
        if chunks:
            vs.add_documents(chunks, metas)
            log_step("Setup", f"Indexed {len(chunks)} chunks from data/", "green")
            return vs

    log_step("Warning", f"No data found. Add '{CSV_PATH}' or PDF/TXT files in data/", "red")
    return vs


def main():
    console.rule("[bold blue]Travel Planning Agentic RAG[/bold blue]")

    # Determine backend + model
    if BACKEND == "typhoon":
        model_name = TYPHOON_MODEL
        if not os.getenv("TYPHOON_API_KEY"):
            console.print("[red]ERROR: TYPHOON_API_KEY not set.[/red]")
            console.print("[yellow]  สมัครฟรีได้ที่ https://opentyphoon.ai แล้วรัน:[/yellow]")
            console.print("[yellow]  set TYPHOON_API_KEY=your_key_here[/yellow]")
            return
    elif BACKEND == "groq":
        model_name = GROQ_MODEL
        if not os.getenv("GROQ_API_KEY"):
            console.print("[red]ERROR: GROQ_API_KEY not set. Run: set GROQ_API_KEY=your_key[/red]")
            return
    else:
        model_name = OLLAMA_MODEL

    console.print(f"[dim]Backend: {BACKEND}  |  Model: {model_name}  |  VectorDB: {CHROMA_DIR}[/dim]\n")

    # -- init RAG
    log_step("Init", "Setting up vector store...", "cyan")
    vs = setup_vector_store()
    init_search_tool(vs)

    # -- init agent
    agent = TravelAgent(model_name=model_name, backend=BACKEND)
    agent.register_tool("semantic_search", semantic_search)
    agent.register_tool("get_exchange_rate", get_exchange_rate)
    agent.register_tool("search_hotels", search_hotels)

    log_step("Ready", "Agent ready! Type your travel query in Thai or English.", "bold green")
    console.print()
    console.print("[dim]Example queries:[/dim]")
    console.print("  [cyan]•[/cyan] วางแผนทริป 5 วัน ไปญี่ปุ่น งบ 50,000 บาท")
    console.print("  [cyan]•[/cyan] แนะนำโรงแรมในโซล เกาหลี ราคาไม่เกิน $100 ต่อคืน")
    console.print("  [cyan]•[/cyan] ต้องเตรียมอะไรบ้างถ้าจะไปปารีส รวมถึงวีซ่าและค่าเงิน")
    console.print("  [cyan]•[/cyan] plan a 3-day trip to Singapore on a budget")
    console.print()

    while True:
        try:
            query = Prompt.ask("[bold cyan]คุณ[/bold cyan]")
        except (KeyboardInterrupt, EOFError):
            console.print("\nลาก่อน!")
            break

        query = query.strip()
        if not query:
            continue
        if query.lower() in {"exit", "quit", "q", "ออก", "ลาก่อน"}:
            console.print("ขอบคุณที่ใช้บริการ Travel Planning Agent!")
            break

        agent.run(query)
        console.print()


if __name__ == "__main__":
    main()
