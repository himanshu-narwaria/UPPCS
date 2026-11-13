"""Shared learner-facing study components for full, quick and 72-hour views."""
import html
import json
from pathlib import Path
from source_model import clean, plain

HERE = Path(__file__).resolve().parent
PDF = "Preview_Indian_Polity_and_Governance_Part_4_2026_26118_C_E_Book.pdf"
INTROS = json.loads((HERE / "source_intros.json").read_text(encoding="utf-8"))
SOURCE = json.loads((HERE / "all_source_questions.json").read_text(encoding="utf-8"))
REVIEW = json.loads((HERE / "review_questions.json").read_text(encoding="utf-8"))
E = html.escape

STUDY_CSS = """
.study-path{padding:14px 16px;border:1px solid var(--line);border-left:4px solid var(--acc);border-radius:10px;margin:0 0 22px;background:var(--soft)}
.study-path p{margin:4px 0}.study-path a{color:var(--acc);text-decoration:underline}
.study-table{margin:16px 0;overflow-wrap:anywhere}.study-table caption{text-align:left;font-weight:650;margin:0 0 8px}.study-table th{width:36%}
.study-trap,.study-hook{padding:12px 14px;border-radius:9px;margin:14px 0;line-height:1.55}.study-trap{background:var(--warnbg);border-left:3px solid var(--warn)}.study-hook{background:var(--soft);border-left:3px solid var(--acc)}
.study-recall{border:1px solid var(--line);border-radius:10px;padding:14px;margin:20px 0}.study-recall h4{margin:0 0 6px}.study-recall details{border-top:1px solid var(--line);padding:10px 0}.study-recall summary{cursor:pointer;font-weight:550}.study-recall .a{padding:8px 0 0;line-height:1.55}.study-recall .src{display:block;color:var(--mute);font-size:12px;margin-top:6px}
.source-layer{border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:18px 0}.source-layer>summary{cursor:pointer;font-weight:650}.source-layer .source-card{border-top:1px solid var(--line);padding:12px 0}.source-card summary{cursor:pointer;line-height:1.45}.source-card .pt{padding:6px 0}.source-card .pt:before{content:none}.source-card ol{padding-left:24px}.source-card .source-answer{padding:12px;background:var(--soft);line-height:1.55}.source-note{font-size:13px;color:var(--mute);line-height:1.5}.source-point{line-height:1.55!important}.source-link{font-size:12px;color:var(--acc);white-space:normal}.review-label{display:inline-block;font-size:12px;padding:2px 7px;background:var(--warnbg);color:var(--warn);border-radius:5px}
.chapter-map{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 20px}.chapter-map a{font-size:13px;padding:6px 10px;border:1px solid var(--line);border-radius:18px;color:var(--acc)}
body.imp .pt.keep{display:revert}body.imp .study-table{display:table}body.imp .topic:has(.pt.keep){display:block}
@media(max-width:500px){.topic h3{flex-wrap:wrap}.toc a{flex-wrap:wrap}.toc .q{margin-left:30px}.study-table{font-size:13px}.study-table th,.study-table td{padding:8px}.pn a{overflow-wrap:anywhere}.study-recall{padding:10px}.plan-grid{grid-template-columns:1fr!important}}
@media print{.source-layer{break-inside:auto}.source-layer:not([open])>*:not(summary){display:none}.study-recall details>.a{display:block}.study-recall{break-inside:avoid}}
"""


def page_label(pages):
    return f"PDF p. {pages[0]}" if len(pages) == 1 else f"PDF pp. {pages[0]}-{pages[-1]}"


def source_link(pages):
    return f'<a class="source-link" href="{PDF}#page={pages[0]}" target="_blank" rel="noopener noreferrer">{page_label(pages)} · supplied book</a>'


def learning_support(chapter, quick=False):
    n = chapter["num"]
    out = [f'<table class="study-table" id="c{n}-compare"><caption>Keep these apart</caption><tbody>']
    for left, right in chapter["comparison"]:
        out.append(f'<tr><th scope="row">{E(left)}</th><td>{E(right)}</td></tr>')
    out.append('</tbody></table>')
    out.append(f'<div class="study-trap" id="c{n}-trap"><b>Common confusion.</b> {E(chapter["confusion"])}</div>')
    if chapter.get("memory_hook"):
        out.append(f'<div class="study-hook"><b>Learning aid - not from source.</b> {E(chapter["memory_hook"])}</div>')
    if n == 41:
        out.append('<p class="source-note"><b>Book correction checked 13 November 2026.</b> The official text identifies <a href="https://www.legislative.gov.in/static/uploads/2025/08/cb1b190ea633a1746368ed1fac35fb30.pdf" target="_blank" rel="noopener noreferrer">Article 330A as women\'s representation in Lok Sabha</a>; <a href="https://www.legislative.gov.in/static/uploads/2025/07/359f70a69695affb9d72f8393102bd2e.pdf" target="_blank" rel="noopener noreferrer">Article 300A concerns property</a>. This corrects the source\'s label; it is not a complete update of current law.</p>')
    out.append(f'<section class="study-recall" id="c{n}-recall" aria-label="Active recall"><h4>Close the notes. Try these.</h4><p class="source-note">Say an answer first, then open it to check the reasoning.</p>')
    for question, answer in chapter["recall"]:
        out.append(f'<details class="recall"><summary>{E(question)}</summary><div class="a">{E(answer)}<span class="src">{page_label(chapter["pages"])} · chapter source range</span></div></details>')
    out.append('</section>')
    return "\n".join(out)


def source_card(record, review=False):
    pages = record["pages"]
    tag = ' <span class="review-label">Unscored source check</span>' if record["review"] else ''
    title = f'Book Q{record["source_no"]} · {page_label(pages)}'
    opts = '<ol type="a">' + ''.join(f'<li>{E(o)}</li>' for o in record["o"]) + '</ol>' if record["o"] else '<p>' + E(record["body"]) + '</p>'
    reasons = ' '.join(record["review"])
    return (f'<details class="source-card" id="{record["id"]}{"-review" if review else ""}" data-pages="{",".join(map(str, pages))}"><summary>{E(title)}{tag}</summary>'
            f'<p class="pt source-stem">{E(record["s"])}</p>{opts}<p class="source-note">{E("; ".join(record["exams"]))}</p>'
            f'<div class="source-answer"><b>Book key: ({E(record["source_key"])}).</b> {E(reasons)}'
            + (f'<p class="source-note">Printed reference: {E(record["cross_reference"])} Resolved to the earlier explanation on {page_label(record["explanation_pages"])}.</p>' if record.get("cross_reference") and record["explanation_pages"] else '')
            + f'<p>{E(record["f"])}</p>'
            f'<p class="source-note">Source explanation, including its original time context; not an independently verified official key.</p>{source_link(pages)}</div></details>')


def source_layer(chapter):
    n = chapter["num"]
    intro = INTROS[str(n)]
    text = clean(intro["text"])
    points = [plain(x) for x in text.split('*') if plain(x)]
    records = [x for x in SOURCE if x["chapter"] == n]
    out = [f'<details class="source-layer" id="c{n}-source"><summary>Read more from the supplied PDF</summary>',
           '<p class="source-note">The short guide above is selective. This layer retains the chapter opening and the question-bank explanations, including other exams. Source-era office-holders, statistics and legal claims may be dated. Only UPPSC-labelled scorable items enter Practice; other exams do not enter repeat counts.</p>',
           f'<h4>Chapter opening · {source_link(intro["pages"])}</h4><ul>']
    out.extend(f'<li class="pt source-point">{E(point)}</li>' for point in points)
    out.append('</ul><h4>Source question explanations</h4><p class="source-note">These are evidence cards, not a second scored quiz. Open a card to read its original question, key and full explanation. Printed asterisks and label defects remain visible.</p>')
    out.extend(source_card(x) for x in records)
    out.append('</details>')
    return "\n".join(out)


def review_layer():
    return (f'<details class="source-layer" id="source-review"><summary>{len(REVIEW)} UPPSC source questions need review · excluded from scoring</summary>'
            '<p class="source-note">The book prints an asterisk key or malformed option labels for these items. They remain available for reading. No guessed option is marked correct.</p>'
            + ''.join(source_card(x, review=True) for x in REVIEW) + '</details>')
