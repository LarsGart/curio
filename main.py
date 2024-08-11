from fasthtml import FastHTML, picolink
from fasthtml.common import *
import arxiv
from collections import defaultdict
from datetime import datetime

app, rt = fast_app(
    pico=True,
    hdrs=( # should link to index.css
        Link(rel="stylesheet", href="index.css"),
    )
)
client = arxiv.Client()
cache = defaultdict(lambda: None)

def create_paper_card(paper, expanded=False):
    title = H2(
        paper.title,
        hx_get=f"/{'collapse' if expanded else 'expand'}/{paper.get_short_id()}",
        hx_target="closest article",
        hx_swap="outerHTML",
        style="cursor: pointer; font-size: 1.2rem; width: 61.8vw;"
    )
    
    title_components = Div(
        A(
            "🔗", href=paper.pdf_url, target="_blank",
            style="font-size: 1em; margin-right: 0.5em; text-decoration: none;"
        ),
        Span(published_when(paper), style="font-size: 1em; margin-right: 0.5em;"),
        Span(f"[{paper.primary_category}]", style="font-size: 1em; margin-right: 0.5em;"),
        style="display: flex; align-items: baseline; margin-top: 0.5em; font-size: 1em;",
    )

    content = [title, title_components]
    
    if expanded:
        content.extend([
            Div(P(truncate(paper.summary), style="font-size: 1.0em; margin-top: 1em; width: 61.8vw;"),
            Footer(f"✍️ {', '.join(author.name for author in paper.authors)}", style="width: 61.8vw;"),)
        ])
    return Article(
        *content,
        id=f"paper-{paper.get_short_id()}",
        cls="card box",
        style="margin-left: 1rem;",
    )

def published_when(paper):
    delta = datetime.now(paper.published.tzinfo) - paper.published
    if delta.days > 0:
        return f"{delta.days} days old"
    elif delta.seconds > 3600:
        return f"{delta.seconds//3600} hours old"
    else:
        return f"{delta.seconds//60} minutes old"

def truncate(s):
    return s[:s.find('.', s.find('.', s.find('.')+1)+1)+1] + '..'

@app.get("/")
def home():
    search = arxiv.Search(
        query="chatgpt",
        max_results=20,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    results = list(client.results(search))
    for paper in results:
        cache[paper.get_short_id()] = paper
    
    return Main(
        Div(
            H1("cur.io", style="font-size: 2.5em; margin-right: 1rem; margin-top: 2%;"),
            Input(
                type="search",
                placeholder="Search...",
                style="width: 16vw; height: 2.5em; margin-top: 2%;",
                hx_get="/?search={value}",
                hx_swap="outerHTML",
            ),
            style="display: flex; align-items: center; margin-left: 1.4vw;"
        ),
        Div(
            *[create_paper_card(r) for r in results],
            id="content"
        ),
        cls="container",
        style="max-width: 64vw; margin: 0; padding: 0;"
    )

@app.get("/expand/{paper_id}")
def expand_summary(paper_id: str):
    paper = cache.get(paper_id) or find_paper(paper_id)
    return create_paper_card(paper, expanded=True)

def find_paper(paper_id: str):
    if paper := cache.get(paper_id):
        return paper
    search = arxiv.Search(id_list=[paper_id])
    cache[paper_id] = next(client.results(search))
    return cache[paper_id]

@app.get("/collapse/{paper_id}")
def collapse_summary(paper_id: str):
    paper = cache.get(paper_id) or find_paper(paper_id)
    return create_paper_card(paper)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

    