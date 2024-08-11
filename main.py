from fasthtml import FastHTML, picolink
from fasthtml.common import *
import arxiv
from collections import defaultdict
from datetime import datetime
import re

app, rt = fast_app(
    pico=True,
    hdrs=(
        Link(rel="stylesheet", href="index.css"),
        Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"),
    )
)
client = arxiv.Client()
cache = defaultdict(lambda: None)
bookmarked_categories = defaultdict(lambda: []) # each of these keys will be a category (e..g cs.LG), and 

# tables = database('data/interests.db').t
# interests = tables.interests
# if not interests in tables:
#     interests.create(name=str, papers=str, pk='name')
# Interest = interests.dataclass()

@app.get("/bookmark/{paper_id}")
def upsert_bookmark(paper):
    bookmarked_categories[paper.primary_category].append(paper)

def create_paper_card(paper, expanded=False):
    icon = "fa fa-bookmark-o" if paper not in bookmarked_categories[paper.primary_category] else "fa fa-bookmark"
    bookmark_title = Div(
                A(
                    I(
                        cls=icon,
                        style="font-size: 1.5em;", # when this is clicked, add to bookmarks
                        hx_post=f"/bookmark/{paper.get_short_id()}",
                    ),
                    style="margin-right: 0.7em;", # mark the icon bigger: font-size: 1.5em;
                ),
                H2(
                    clean_title(paper.title),
                    hx_get=f"/{'collapse' if expanded else 'expand'}/{paper.get_short_id()}",
                    hx_target="closest article",
                    hx_swap="outerHTML",
                    style="user-select: none; cursor: pointer; font-size: 1.2rem; width: 61.8vw;",
                ),
                style="display: flex; align-items: start;",
            )
    
    title_components = Div(
        get_git_link(paper.summary, paper.comment),
        A(
            "🔗", href=paper.pdf_url, target="_blank",
            style="font-size: 1em; margin-right: 0.5em; text-decoration: none;"
        ),
        Span(published_when(paper), style="font-size: 1em; margin-right: 0.5em;"),
        Span(f"[{paper.primary_category}]", style="font-size: 1em; margin-right: 0.5em;"),
        style="display: flex; align-items: baseline; margin-top: 0.5em; font-size: 1em;",
    )

    content = [bookmark_title, title_components]
    
    if expanded:
        content.extend([
            Div(P(truncate(paper.summary), style="font-size: 1.0em; margin-top: 1em; width: 61.8vw;"),
            Footer(f"✍️ {', '.join(author.name for author in paper.authors)}", style="width: 61.8vw;"),)
        ])
    return Article(
        *content,
        id=f"paper-{paper.get_short_id()}",
        cls="card box",
        style="margin-left: 1rem; width: 63.5vw;",
    )

def clean_title(title):
    return title.replace(' and ', ' & ')

def published_when(paper):
    delta = datetime.now(paper.published.tzinfo) - paper.published
    if 365*2 > delta.days > 365:
        return f"{delta.days//365} year old"
    elif delta.days > 365:
        return f"{delta.days//365} years old"
    elif 30*2 > delta.days > 30:
        return f"{delta.days//30} month old"
    elif delta.days > 30:
        return f"{delta.days//30} months old"
    elif delta.days > 0:
        return f"{delta.days} days old"
    elif delta.seconds > 3600:
        return f"{delta.seconds//3600} hours old"
    else:
        return f"{delta.seconds//60} minutes old"

def truncate(s):
    return s[:s.find('.', s.find('.', s.find('.')+1)+1)+1] + '..'

def get_git_link(summary, comment):
    link = None
    summary = summary or ''
    comment = comment or ''
    mask = r'(https?://github.com/[^ ]+)'
    if (found_link := re.findall(mask, summary)):
        link = found_link[0]
    elif (found_link := re.findall(mask, comment)):
        link = found_link[0]
    if link and '%' in link:
        link = link[:link.find('%')]
    if link:
        return A(
            I(cls="fa fa-github"),
            href=link.rstrip('.'), target="_blank",
            style="margin-right: 0.5em; text-decoration: none;"
        )
    return None
    
@app.get("/")
def home():
    search = arxiv.Search(
        query="chatgpt",
        max_results=50,
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
            style="display: flex; align-items: center; margin-left: 1.4vw; margin-bottom: 2.6%;"
        ),
        Div(
            *[create_paper_card(r) for r in results],
            id="content"
        ),
        
        *get_sidebar(),

        cls="container",
        style="max-width: 64vw; margin: 0; padding: 0;",
    )

def get_sidebar():
    # return [
    #     Div(
    #         H2("Interests", style="font-size: 1.5em; margin-bottom: 1rem;"),
    #             Ul(
    #                 Li("Conformal Prediction", draggable='true'),
    #                 Li("KANs"),
    #                 Li("Federated Learning"),
    #                 style="list-style-type: none; padding: 0; margin: 0;"
    #             ),
    #         Input(
    #             type="text",
    #             placeholder="Add Interest",
    #             style="width: 10vw; height: 2.5em; margin-top: 2%;",
    #             hx_post="/add-interest",
    #             hx_swap="outerHTML",
    #         ),
    #     cls="card box",
    #     style="position: fixed; right: 0; top: 0; margin-right: 1.5rem; margin-top: 1.3%; padding: 1rem;"
    #     ),
    # ]
    return [
        Div(
            H2("Bookmarks", style="font-size: 1.5em; margin-bottom: 1rem;"),  # create a bookmark card for each category, and a subcard for each paper in each category
            *[Div(
                H3(f"{category} ({len(papers)})"),
                *[create_paper_card(paper) for paper in papers],
                style="margin-bottom: 1rem;"
            ) for category, papers in bookmarked_categories.items()],
            cls="card box",
            style="position: fixed; right: 0; top: 0; margin-right: 1.5rem; margin-top: 1.3%; padding: 1rem;"
        ),
    ]

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