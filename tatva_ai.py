# ============================================================
# TatvaAI v5 - Multi-AI Consensus System
# Gemini 2.5 + Groq + Wikipedia + Web + PDF + Cross Questions
# Fixes: Encoding, Logo, Description, About, Year, Font
# ============================================================

import os
import sys
import io
import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
import google.generativeai as genai
from groq import Groq
import wikipediaapi
from ddgs import DDGS
from fpdf import FPDF, XPos, YPos

# Fix encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

load_dotenv()
console = Console()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

BLOCKED_TOPICS = ["bomb","weapon","kill","hack","virus","drug","poison","terror","suicide"]

CURRENT_YEAR = datetime.datetime.now().year


def clean_text(text):
    replacements = {
        "\u2022": "-", "\u2019": "'", "\u2018": "'",
        "\u201c": '"', "\u201d": '"', "\u2013": "-",
        "\u2014": "-", "\u2026": "...", "\u00e9": "e",
        "\u00e8": "e", "\u00ea": "e", "\u00b7": "-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    result = ""
    for char in text:
        if ord(char) < 128:
            result += char
        else:
            result += "?"
    return result


def safety_check(query):
    for topic in BLOCKED_TOPICS:
        if topic in query.lower():
            return False, topic
    return True, None


def ask_gemini(query):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(query)
        return response.text.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"


def ask_groq(query):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": query}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"


def get_wikipedia_facts(query):
    try:
        wiki = wikipediaapi.Wikipedia(language='en', user_agent='TatvaAI/5.0')
        keywords = query.replace("?","").replace("should","").replace("will","").replace("is","").strip()
        for word in keywords.split():
            if len(word) > 3:
                page = wiki.page(word)
                if page.exists():
                    return page.summary[:800], page.fullurl
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
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""Two AIs answered: "{query}"
AI-1: {ans1[:300]}
AI-2: {ans2[:300]}
Do both agree on main point? Reply ONLY: YES or NO"""
        response = model.generate_content(prompt)
        return "YES" in response.text.upper()
    except:
        return False


def get_best_answer(query, gemini_ans, groq_ans, wiki_facts, web_results):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""You are TatvaAI. Create a comprehensive, fact-checked answer.

Question: {query}
Gemini: {gemini_ans[:400]}
Groq: {groq_ans[:400]}
Wikipedia: {wiki_facts[:300]}
Web: {web_results[:300]}

Write a balanced, complete answer with:
1. Key Facts
2. Main Arguments
3. Clear Conclusion

Use simple English. No bullet points, use numbered lists."""
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return gemini_ans


def get_cross_questions(query, best_answer):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""You are a debate coach and psychologist.

Topic: "{query}"
Answer given: {best_answer[:500]}

Generate 15 cross-questions that a skeptic, journalist, scientist, or critic might ask to challenge this answer.

Based on human psychology - include:
- Questions that challenge assumptions
- Questions about evidence and proof
- Questions about alternatives
- Emotional/ethical challenge questions
- Devil's advocate questions

Format EXACTLY like this for each question:
Q1: [Question]
A1: [Best possible answer to this question]

Q2: [Question]
A2: [Best possible answer]

Continue till Q15. Make questions progressively harder."""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Cross questions generate nahi ho sake: {str(e)}"


def save_pdf(query, gemini_ans, groq_ans, wiki_facts, web_results, best_answer, related_q, cross_qa):
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 22)
        pdf.set_fill_color(25, 25, 112)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 20, "TatvaAI Research Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)

        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(0, 0, 0)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.cell(0, 8, f"Generated: {timestamp}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.cell(0, 6, f"TatvaAI v5.0  |  Multi-AI Consensus System  |  (C) {CURRENT_YEAR}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(5)

        def section_header(title, r, g, b):
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_fill_color(r, g, b)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 10)
            pdf.ln(2)

        def add_text(text, limit=2000):
            pdf.multi_cell(0, 7, clean_text(str(text))[:limit])
            pdf.ln(3)

        section_header("QUESTION", 25, 25, 112)
        add_text(query)

        section_header("GEMINI 2.5 ANSWER", 70, 130, 180)
        add_text(gemini_ans, 1500)

        section_header("GROQ LLAMA ANSWER", 60, 179, 113)
        add_text(groq_ans, 1500)

        section_header("WIKIPEDIA FACTS", 200, 140, 0)
        add_text(wiki_facts, 800)

        section_header("WEB SEARCH RESULTS", 128, 0, 128)
        add_text(web_results, 800)

        pdf.add_page()
        section_header("VERIFIED BEST ANSWER (TatvaAI)", 0, 100, 0)
        add_text(best_answer, 3000)

        section_header("RELATED QUESTIONS", 70, 130, 180)
        add_text(related_q, 1000)

        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_fill_color(139, 0, 0)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 15, "CROSS QUESTIONS & ANSWERS", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(3)
        pdf.set_font("Helvetica", "I", 9)
        pdf.multi_cell(0, 6, "Prepared by TatvaAI based on human psychology - to help you prepare for tough questions")
        pdf.ln(3)
        add_text(cross_qa, 5000)

        filename = f"TatvaAI_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        pdf.output(filepath)
        return filepath
    except Exception as e:
        return f"ERROR: {str(e)}"


def show_welcome():
    console.print(Rule(style="cyan"))

    logo_text = (
        "[bold cyan]  TatvaAI v5.0[/bold cyan]\n"
        "[white]  Multi-AI Consensus Research System[/white]"
    )
    console.print(Panel(
        logo_text,
        border_style="cyan",
        padding=(1, 8),
        expand=True,
    ))

    about_text = (
        "[bold yellow]  What is TatvaAI?[/bold yellow]\n\n"
        "  TatvaAI aapke har sawal ko 2 powerful AIs (Gemini + Groq),\n"
        "  Wikipedia aur Live Web Search se verify karke ek single\n"
        "  fact-checked answer deta hai.\n\n"
        "[bold yellow]  Yeh tool kya karta hai:[/bold yellow]\n\n"
        "  [cyan]Step 1[/cyan]  Gemini 2.5 Flash se jawab leta hai\n"
        "  [cyan]Step 2[/cyan]  Groq Llama 3.3 se jawab leta hai\n"
        "  [cyan]Step 3[/cyan]  Wikipedia facts check karta hai\n"
        "  [cyan]Step 4[/cyan]  Live web search karta hai\n"
        "  [cyan]Step 5[/cyan]  Dono AIs ka consensus check karta hai\n"
        "  [cyan]Step 6[/cyan]  Best verified answer generate karta hai\n"
        "  [cyan]Step 7[/cyan]  15 psychology-based cross questions banata hai\n"
        "  [cyan]Step 8[/cyan]  Poori research PDF mein save karta hai\n\n"
        "[bold yellow]  Commands:[/bold yellow]\n\n"
        "  Koi bhi sawaal type karein aur Enter dabayein\n"
        "  [dim]'exit'[/dim] likhne par program band hoga\n\n"
        f"  [dim]TatvaAI (C) {CURRENT_YEAR}  |  Version 5.0  |  Powered by Gemini + Groq[/dim]"
    )
    console.print(Panel(
        about_text,
        border_style="cyan",
        padding=(0, 2),
        expand=True,
    ))

    console.print(Rule(style="cyan"))
    console.print()


def tatva_ai():
    show_welcome()

    while True:
        query = console.input("[bold green]Aap:[/bold green] ").strip()

        if query.lower() == "exit":
            console.print(Panel(
                f"[bold cyan]TatvaAI band ho raha hai.[/bold cyan]\n"
                f"[white]Shukriya! Namaskar![/white]\n\n"
                f"[dim](C) {CURRENT_YEAR} TatvaAI v5.0[/dim]",
                border_style="cyan",
                padding=(1, 4),
            ))
            break

        if not query:
            continue

        is_safe, blocked = safety_check(query)
        if not is_safe:
            console.print(Panel(f"[red]Blocked: '{blocked}'[/red]", border_style="red"))
            continue

        console.print()
        console.print(Rule("[bold]Step 1[/bold] [dim]Dono AIs se jawab le raha hoon...[/dim]", style="dim"))
        gemini_ans = ask_gemini(query)
        groq_ans = ask_groq(query)

        table = Table(show_header=True, header_style="bold magenta", expand=True)
        table.add_column("AI", style="cyan", width=14)
        table.add_column("Jawab", style="white")
        table.add_row("Gemini 2.5", gemini_ans[:250] + "..." if len(gemini_ans) > 250 else gemini_ans)
        table.add_row("Groq Llama", groq_ans[:250] + "..." if len(groq_ans) > 250 else groq_ans)
        console.print(table)

        console.print()
        console.print(Rule("[bold]Step 2[/bold] [dim]Wikipedia facts...[/dim]", style="dim"))
        wiki_facts, wiki_url = get_wikipedia_facts(query)
        console.print(Panel(
            f"{wiki_facts[:400]}\n\n[dim]{wiki_url}[/dim]",
            title="[yellow]Wikipedia[/yellow]",
            border_style="yellow",
            padding=(0, 2),
        ))

        console.print()
        console.print(Rule("[bold]Step 3[/bold] [dim]Web search...[/dim]", style="dim"))
        web_results = get_web_search(query)
        console.print(Panel(web_results[:400], title="[blue]Web Results[/blue]", border_style="blue", padding=(0, 2)))

        console.print()
        console.print(Rule("[bold]Step 4[/bold] [dim]Best answer generate ho raha hai...[/dim]", style="dim"))
        best_answer = get_best_answer(query, gemini_ans, groq_ans, wiki_facts, web_results)
        agreed = check_consensus(gemini_ans, groq_ans, query)
        status = "[green]Dono AIs Agree[/green]" if agreed else "[yellow]Mixed Views[/yellow]"
        console.print(Panel(
            best_answer[:1000],
            title=f"[bold]VERIFIED ANSWER[/bold] - {status}",
            border_style="green" if agreed else "yellow",
            padding=(0, 2),
        ))

        console.print()
        console.print(Rule("[bold]Step 5[/bold] [dim]Related questions...[/dim]", style="dim"))
        related_q = ask_gemini(f"Give 5 related follow-up questions for: {query}")
        console.print(Panel(related_q[:500], title="[cyan]Related Questions[/cyan]", border_style="cyan", padding=(0, 2)))

        console.print()
        console.print(Rule("[bold]Step 6[/bold] [dim]Cross questions generate ho rahe hain...[/dim]", style="dim"))
        cross_qa = get_cross_questions(query, best_answer)
        console.print(Panel(
            cross_qa[:800] + "\n\n[dim]...PDF mein poore 15 cross questions hain![/dim]",
            title="[red]Cross Questions Preview[/red]",
            border_style="red",
            padding=(0, 2),
        ))

        console.print()
        save = console.input("[bold]PDF report save karein?[/bold] [dim](y/n)[/dim]: ").strip().lower()
        if save == 'y':
            console.print("[dim]PDF ban rahi hai...[/dim]")
            result = save_pdf(query, gemini_ans, groq_ans, wiki_facts, web_results, best_answer, related_q, cross_qa)
            if result.startswith("ERROR"):
                console.print(Panel(f"[red]{result}[/red]", border_style="red"))
            else:
                console.print(Panel(
                    f"[bold green]PDF save ho gayi![/bold green]\n\n"
                    f"[white]Location:[/white] {result}\n\n"
                    f"[dim]Print ke liye: PDF kholo aur Ctrl+P dabao[/dim]",
                    border_style="green",
                    padding=(1, 2),
                ))

        console.print()
        console.print(Rule(style="dim"))
        console.print()


if __name__ == "__main__":
    tatva_ai()