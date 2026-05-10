# ============================================================
# TatvaAI v6 - Multi-AI Consensus Research System
# Gemini 2.5 + Groq + Wikipedia + Web Search + PDF Reports
# All Issues Fixed - International Professional Level
# ============================================================

import os
import sys
import io
import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
from rich import box

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from google import genai
from groq import Groq
import wikipedia
from ddgs import DDGS
from fpdf import FPDF, XPos, YPos

load_dotenv()
console = Console()

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

BLOCKED_TOPICS = ["bomb","weapon","kill","hack","virus","drug","poison","terror","suicide","explosive"]
CURRENT_YEAR = datetime.datetime.now().year
VERSION = "6.0"

def clean_text(text):
    if not text:
        return ""
    replacements = {
        "\u2022": "-", "\u2019": "'", "\u2018": "'",
        "\u201c": '"', "\u201d": '"', "\u2013": "-",
        "\u2014": "-", "\u2026": "...", "\u00e9": "e",
        "\u00e8": "e", "\u00ea": "e", "\u00b7": "-",
        "\u2012": "-", "\u2015": "-", "\u00a0": " ",
        "\u00b0": " degrees", "\u00ae": "(R)",
        "\u2122": "(TM)", "\u00a9": "(C)",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode('latin-1', errors='replace').decode('latin-1')

def safety_check(query):
    for topic in BLOCKED_TOPICS:
        if topic in query.lower():
            return False, topic
    return True, None

def ask_gemini(query):
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash", contents=query)
        return response.text.strip()
    except Exception as e:
        return f"Gemini Error: {str(e)}"

def ask_groq(query):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": query}])
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Groq Error: {str(e)}"

def get_wikipedia_facts(query):
    try:
        wikipedia.set_lang("en")
        keywords = query.replace("?","").replace("should","").replace("will","").strip()
        try:
            page = wikipedia.page(keywords, auto_suggest=True)
            return page.summary[:800], page.url
        except:
            pass
        for word in keywords.split():
            if len(word) > 4:
                try:
                    results = wikipedia.search(word, results=1)
                    if results:
                        page = wikipedia.page(results[0])
                        return page.summary[:800], page.url
                except:
                    continue
        return "Wikipedia article nahi mila.", ""
    except Exception as e:
        return f"Wikipedia error: {str(e)}", ""

def get_web_search(query):
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=3):
                results.append(f"- {r['title']}: {r['body'][:200]}")
        return "\n".join(results) if results else "Web results nahi mile."
    except Exception as e:
        return f"Web search error: {str(e)}"

def check_consensus(ans1, ans2, query):
    try:
        prompt = f"""Two AIs answered: "{query}"
AI-1: {ans1[:300]}
AI-2: {ans2[:300]}
Do both agree on main point? Reply ONLY: YES or NO"""
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt)
        return "YES" in response.text.upper()
    except:
        return False

def get_best_answer(query, gemini_ans, groq_ans, wiki_facts, web_results):
    try:
        prompt = f"""You are TatvaAI v{VERSION}. Create a comprehensive fact-checked answer.
Question: {query}
Gemini: {gemini_ans[:400]}
Groq: {groq_ans[:400]}
Wikipedia: {wiki_facts[:300]}
Web: {web_results[:300]}
Write a balanced complete answer with:
1. Key Facts
2. Main Arguments
3. Clear Conclusion
Use simple English. Use numbered lists."""
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt)
        return response.text.strip()
    except:
        return gemini_ans

def get_cross_questions(query, best_answer):
    try:
        prompt = f"""You are a debate coach and psychologist.
Topic: "{query}"
Answer given: {best_answer[:500]}
Generate 15 cross-questions a skeptic, journalist, scientist might ask.
Include: assumption challenges, evidence questions, alternatives, ethical questions.
Format EXACTLY:
Q1: [Question]
A1: [Best possible answer]
Q2: [Question]
A2: [Best possible answer]
Continue till Q15. Make questions progressively harder."""
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt)
        return response.text.strip()
    except Exception as e:
        return f"Cross questions error: {str(e)}"

def save_pdf(query, gemini_ans, groq_ans, wiki_facts, web_results, best_answer, related_q, cross_qa):
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_fill_color(15, 15, 80)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 24)
        pdf.cell(0, 18, "TatvaAI Research Report",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_fill_color(30, 30, 120)
        pdf.cell(0, 10, f"Multi-AI Consensus  |  Gemini + Groq + Wikipedia + Web  |  v{VERSION}",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_fill_color(50, 50, 150)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.cell(0, 8, f"Generated: {timestamp}   |   (C) {CURRENT_YEAR} TatvaAI",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(6)

        def section_header(title, r, g, b):
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_fill_color(r, g, b)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 9, f"  {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 10)
            pdf.ln(2)

        def add_text(text, limit=2000):
            pdf.multi_cell(0, 6, clean_text(str(text))[:limit])
            pdf.ln(3)

        section_header("QUESTION", 15, 15, 80)
        add_text(query)
        section_header("GEMINI 2.5 FLASH ANSWER", 0, 100, 160)
        add_text(gemini_ans, 1500)
        section_header("GROQ LLAMA 3.3 ANSWER", 0, 140, 80)
        add_text(groq_ans, 1500)
        section_header("WIKIPEDIA FACTS", 160, 100, 0)
        add_text(wiki_facts, 800)
        section_header("LIVE WEB SEARCH RESULTS", 100, 0, 120)
        add_text(web_results, 800)
        pdf.add_page()
        section_header("VERIFIED BEST ANSWER (TatvaAI Consensus)", 0, 120, 0)
        add_text(best_answer, 3000)
        section_header("RELATED FOLLOW-UP QUESTIONS", 0, 100, 160)
        add_text(related_q, 1000)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_fill_color(120, 0, 0)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 14, "  CROSS QUESTIONS & ANSWERS (15 Psychology-Based)",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "I", 9)
        pdf.ln(3)
        pdf.multi_cell(0, 6, clean_text(
            "Prepared by TatvaAI - psychology-based questions to help prepare for tough critics."))
        pdf.ln(3)
        add_text(cross_qa, 5000)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 6, f"TatvaAI v{VERSION}  |  (C) {CURRENT_YEAR}  |  For research purposes only.",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

        filename = f"TatvaAI_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        pdf.output(filepath)
        return filepath
    except Exception as e:
        return f"PDF ERROR: {str(e)}"

def show_welcome():
    console.print(Rule(style="bold cyan"))
    logo = (
        "\n"
        "[bold cyan]  ████████╗ █████╗ ████████╗██╗   ██╗ █████╗     █████╗ ██╗  [/bold cyan]\n"
        "[bold cyan]     ██║   ██╔══██╗   ██║   ██║   ██║██╔══██╗   ██╔══██╗██║  [/bold cyan]\n"
        "[bold cyan]     ██║   ███████║   ██║   ██║   ██║███████║   ███████║██║  [/bold cyan]\n"
        "[bold cyan]     ██║   ██╔══██║   ██║   ╚██╗ ██╔╝██╔══██║   ██╔══██║██║  [/bold cyan]\n"
        "[bold cyan]     ██║   ██║  ██║   ██║    ╚████╔╝ ██║  ██║   ██║  ██║██║  [/bold cyan]\n"
        "[bold cyan]     ╚═╝   ╚═╝  ╚═╝   ╚═╝     ╚═══╝  ╚═╝  ╚═╝   ╚═╝  ╚═╝╚═╝  [/bold cyan]\n"
        f"\n[white]       Multi-AI Consensus Research System  v{VERSION}[/white]\n"
        f"[dim]    Powered by Gemini 2.5 Flash + Groq Llama 3.3 + Wikipedia[/dim]\n"
    )
    console.print(Panel(Align.center(logo), border_style="cyan", padding=(0, 2)))
    about = (
        f"[bold yellow]About TatvaAI v{VERSION}[/bold yellow]\n\n"
        "[white]TatvaAI verifies every answer using 2 powerful AIs,[/white]\n"
        "[white]Wikipedia, and live web search for maximum accuracy.[/white]\n\n"
        "[bold cyan]How it works:[/bold cyan]\n\n"
        "  [cyan]Step 1[/cyan]  Gemini 2.5 Flash se jawab\n"
        "  [cyan]Step 2[/cyan]  Groq Llama 3.3 se jawab\n"
        "  [cyan]Step 3[/cyan]  Wikipedia facts check\n"
        "  [cyan]Step 4[/cyan]  Live web search\n"
        "  [cyan]Step 5[/cyan]  AI Consensus verify\n"
        "  [cyan]Step 6[/cyan]  Best verified answer\n"
        "  [cyan]Step 7[/cyan]  15 cross questions\n"
        "  [cyan]Step 8[/cyan]  Professional PDF report\n\n"
        "[bold yellow]Commands:[/bold yellow]\n"
        "  Koi bhi sawaal type karein → Enter\n"
        "  [bold red]exit[/bold red] → Band karo\n\n"
        f"[dim]  TatvaAI (C) {CURRENT_YEAR}  |  v{VERSION}  |  Research & Education[/dim]"
    )
    console.print(Panel(about, border_style="cyan", padding=(1, 4)))
    console.print(Rule(style="bold cyan"))
    console.print()

def tatva_ai():
    show_welcome()
    while True:
        try:
            query = console.input("\n[bold green]You:[/bold green] ").strip()
        except KeyboardInterrupt:
            console.print("\n[dim]Type 'exit' to quit.[/dim]")
            continue

        if query.lower() == "exit":
            console.print(Panel(
                Align.center(
                    f"\n[bold cyan]TatvaAI band ho raha hai.[/bold cyan]\n"
                    f"[white]Shukriya! Namaskar![/white]\n\n"
                    f"[dim](C) {CURRENT_YEAR} TatvaAI v{VERSION}[/dim]\n"
                ),
                border_style="cyan", padding=(1, 4)))
            break

        if not query:
            continue

        is_safe, blocked = safety_check(query)
        if not is_safe:
            console.print(Panel(
                f"[bold red]Blocked:[/bold red] '{blocked}'\n"
                "[white]TatvaAI harmful topics par kaam nahi karta.[/white]",
                border_style="red"))
            continue

        console.print()
        console.print(Rule(f"[bold cyan]Processing:[/bold cyan] [white]{query[:60]}[/white]", style="cyan"))

        with Progress(SpinnerColumn(), TextColumn("[cyan]Step 1: Dono AIs se jawab le raha hoon..."), transient=True) as p:
            p.add_task("", total=None)
            gemini_ans = ask_gemini(query)
            groq_ans = ask_groq(query)

        table = Table(show_header=True, header_style="bold magenta", expand=True, box=box.ROUNDED, border_style="magenta")
        table.add_column("AI Model", style="cyan bold", width=16)
        table.add_column("Answer", style="white")
        table.add_row("Gemini 2.5", gemini_ans[:300] + "..." if len(gemini_ans) > 300 else gemini_ans)
        table.add_row("", "")
        table.add_row("Groq Llama 3.3", groq_ans[:300] + "..." if len(groq_ans) > 300 else groq_ans)
        console.print(table)

        with Progress(SpinnerColumn(), TextColumn("[yellow]Step 2: Wikipedia facts..."), transient=True) as p:
            p.add_task("", total=None)
            wiki_facts, wiki_url = get_wikipedia_facts(query)

        console.print(Panel(
            f"{wiki_facts[:400]}\n\n[dim blue]{wiki_url}[/dim blue]",
            title="[bold yellow]Wikipedia Facts[/bold yellow]",
            border_style="yellow", padding=(0, 2)))

        with Progress(SpinnerColumn(), TextColumn("[blue]Step 3: Live web search..."), transient=True) as p:
            p.add_task("", total=None)
            web_results = get_web_search(query)

        console.print(Panel(web_results[:400], title="[bold blue]Live Web Results[/bold blue]",
                            border_style="blue", padding=(0, 2)))

        with Progress(SpinnerColumn(), TextColumn("[green]Step 4: Best answer generate ho raha hai..."), transient=True) as p:
            p.add_task("", total=None)
            best_answer = get_best_answer(query, gemini_ans, groq_ans, wiki_facts, web_results)
            agreed = check_consensus(gemini_ans, groq_ans, query)

        status = "[bold green]Dono AIs Agree[/bold green]" if agreed else "[bold yellow]Mixed Views[/bold yellow]"
        console.print(Panel(best_answer[:1000],
                            title=f"[bold]VERIFIED ANSWER[/bold]  {status}",
                            border_style="green" if agreed else "yellow", padding=(0, 2)))

        with Progress(SpinnerColumn(), TextColumn("[cyan]Step 5: Related questions..."), transient=True) as p:
            p.add_task("", total=None)
            related_q = ask_gemini(f"Give 5 related follow-up questions for: {query}")

        console.print(Panel(related_q[:500], title="[bold cyan]Related Questions[/bold cyan]",
                            border_style="cyan", padding=(0, 2)))

        with Progress(SpinnerColumn(), TextColumn("[red]Step 6: 15 Cross questions ban rahe hain..."), transient=True) as p:
            p.add_task("", total=None)
            cross_qa = get_cross_questions(query, best_answer)

        console.print(Panel(
            cross_qa[:800] + "\n\n[dim]...PDF mein poore 15 cross questions hain![/dim]",
            title="[bold red]Cross Questions Preview[/bold red]",
            border_style="red", padding=(0, 2)))

        console.print()
        save = console.input("[bold]PDF report save karein?[/bold] [dim](y/n):[/dim] ").strip().lower()
        if save == 'y':
            with Progress(SpinnerColumn(), TextColumn("[dim]PDF ban rahi hai..."), transient=True) as p:
                p.add_task("", total=None)
                result = save_pdf(query, gemini_ans, groq_ans, wiki_facts, web_results, best_answer, related_q, cross_qa)
            if result.startswith("PDF ERROR"):
                console.print(Panel(f"[bold red]{result}[/bold red]", border_style="red"))
            else:
                console.print(Panel(
                    f"[bold green]PDF saved![/bold green]\n\n"
                    f"[white]Location:[/white] [cyan]{result}[/cyan]\n\n"
                    f"[dim]Print: Ctrl+P[/dim]",
                    border_style="green", padding=(1, 2)))

        console.print()
        console.print(Rule(style="dim cyan"))

if __name__ == "__main__":
    tatva_ai()