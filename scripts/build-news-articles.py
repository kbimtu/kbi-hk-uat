#!/usr/bin/env python3
"""Generate KBI HK news article pages from shared template."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("update_footer", SCRIPTS / "update-footer.py")
_mod = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_mod)
build_footer = _mod.build_footer

NEWS = ROOT / "news"
TEMPLATE = (NEWS / "news-iqcol-hk-launch.html").read_text(encoding="utf-8")

# Split template: styles+nav through article start; footer built from update-footer.py
STYLE_END = TEMPLATE.index("</style>") + len("</style>")
NAV_END = TEMPLATE.index("  <!-- ═══════════════════════════════════════════════════════════\n     HERO")

HEAD = TEMPLATE[:STYLE_END]
NAV = TEMPLATE[STYLE_END:NAV_END]
FOOTER = build_footer(NEWS / "_template.html") + "\n\n  <script src=\"../kbi-hk.js\"></script>\n</body>\n</html>\n"

IMG_ETO = "https://sspark.genspark.ai/cfimages?u1=HDGHUe4B3A6RkFMGdIoEXJ5hNqQVEFZNlOiPMEJPkHVqwXHFCBFfAmH%2F0E5gBUliBPW2mxjy6jFKHvHjR6NJo5UqNAklX7FRRGY8aSHE2%2BkE7%2BGGk53N3b3rKv1o4vkD2G8xmz1JUCWNAy82ZEpWFjCy%2FKRZKsH%2FiTEhHIJsTi3Y59yL5xoq5yA6LAbfU%3D&u2=FGnv%2FHrblGqv9WKPK2q0Ew%3D%3D&width=700&height=400"
IMG_TRAIN = "https://sspark.genspark.ai/cfimages?u1=w0eeeey9lbMpkr40EcFM9JtbOQjA6FW%2BsrF1n3JJpqvpDxvPNZm5NFEbX9bsofkPePct3RY%2FsisqOOXKIHozKYzdQ6pR2XgPtGfCFulsh0ZNLA%3D%3D&u2=%2BGA2I5GSdWp%2BPdE1&width=500&height=280"
IMG_QUANTUM = "https://sspark.genspark.ai/cfimages?u1=OvjcsomASP72lTvl6XdXJ48YP4cHuaFMCx7%2FGA%2F6uvWPobrFdYvKNIcIzC6%2FKMv6jZevjXiUKm2LU4%2Fdd8gLmNo0zhKVyCtjyoMiUgADoSZ0WmNiowcjfVCFGJhjFvD1Hi%2Bn5QP84E97j%2FtvXmk0W1CaDeVz0TvV99pbO5yYUwiwQ06pray9fpRKx5CYyOXhGklsJuuGlX6JRg3kM%2BVRixG0kX24BYPhf7ojilhG4nuU%2BimB4Bq7VXGSwht73MXyXK3cwmg%3D&u2=GPMU4kisZiNe7I4S&width=500&height=280"
IMG_IMPACT = "https://sspark.genspark.ai/cfimages?u1=beGaK5sDYPeKeydTLscTU34eZiBpbaRG3nSHwJ3d%2BGMrQcj%2B16uxzi34UhEuDkY2PA3FlWjpqjk47LYj2ja18IbHl3LmjLh2EPxSs0rynDqdpcfBb0vXXhl%2FaffYSgvyJJdyx03Z3m4oSoJNX5MXlMo%2B4%2BaCQbxX6QzZOoc%2FNUN5goRrC5KRFw%3D%3D&u2=hFFxo9ik1ZsZMgmb&width=500&height=280"
IMG_INSIGHT = "https://sspark.genspark.ai/cfimages?u1=xNi0Ntqn8fPrwZvBza5bOiboTw1Q3fHoz3f6Wyc%2BDf1mJR4122oi15Pamcf%2BDrZP6%2BWpy4iip9nhCa9XJ74HTBOvWFDfJPifDx2oQe7Bbq1zeWYTUm1LBAc%3D&u2=MVitLeBtTt6Awkg7&width=500&height=280"


def toc_links(items: list[tuple[str, str]]) -> str:
    lines = []
    for i, (aid, label) in enumerate(items):
        border = "" if i == len(items) - 1 else "border-bottom:1px solid var(--stone);"
        lines.append(
            f'              <a href="#{aid}" style="font-family:\'Inter\',sans-serif;font-size:0.8125rem;color:var(--text-muted);padding:6px 0;{border}display:block;">{label}</a>'
        )
    return "\n".join(lines)


def render_article(a: dict) -> str:
    tag_html = "".join(f'<span class="tag tag--{"sky" if t == "Announcement" else "stone" if t == "Insight" else "prussian"}">{t}</span>' for t in a["tags"][:3])
    sidebar_btns = ""
    for btn in a.get("sidebar_buttons", []):
        cls = btn.get("class", "btn btn-outline-prussian btn--sm")
        extra = ' target="_blank" rel="noopener"' if btn["href"].startswith("http") else ""
        sidebar_btns += f'<a href="{btn["href"]}" class="{cls}" style="justify-content:center;"{extra}>{btn["label"]}</a>\n              '

    related = ""
    for r in a.get("related", []):
        related += f'''            <a href="{r["href"]}" class="related-article-link">
              <div class="related-article-title">{r["title"]}</div>
              <div class="related-article-meta">{r["meta"]}</div>
            </a>
'''

    cta = a.get("cta", "")
    hero = f'''  <header class="article-hero" aria-label="Article header">
    <div class="article-hero-grid" aria-hidden="true"></div>
    <div class="article-hero-inner">
      <div class="article-hero-tags">{tag_html}</div>
      <h1>{a["hero_h1"]}</h1>
      <p style="font-family:'Inter',sans-serif;font-size:0.9375rem;color:rgba(255,255,255,0.5);margin:-12px 0 24px;max-width:640px;">{a.get("subtitle", "")}</p>
      <div class="article-hero-meta">
        <div class="article-author">
          <div>
            <div class="article-author-name">{a["byline"]}</div>
            <div class="article-author-role">KBI Hong Kong</div>
          </div>
        </div>
        <div class="article-meta-divider" aria-hidden="true"></div>
        <div class="article-meta-item"><strong>{a["date"]}</strong></div>
        <div class="article-meta-divider" aria-hidden="true"></div>
        <div class="article-meta-item">{a["read_time"]} read</div>
      </div>
    </div>
  </header>

  <main>
    <section class="section-wrap section-wrap--white" aria-label="Article content">
      <div class="article-layout">
        <article class="article-body">
{a["body"]}
{cta}
          <div class="article-share-bar">
            <span class="article-share-label">Share this article:</span>
            <a href="https://www.linkedin.com/shareArticle?mini=true" target="_blank" rel="noopener" class="share-btn">LinkedIn</a>
          </div>
        </article>
        <aside class="article-sidebar" aria-label="Article sidebar">
          <div class="sidebar-card">
            <div class="sidebar-card-title">Quick Links</div>
            <div style="display:flex;flex-direction:column;gap:10px;">
              {sidebar_btns}
            </div>
          </div>
          <div class="sidebar-card">
            <div class="sidebar-card-title">In This Article</div>
            <div style="display:flex;flex-direction:column;gap:6px;">
{toc_links(a["toc"])}
            </div>
          </div>
          <div class="sidebar-card">
            <div class="sidebar-card-title">Related Articles</div>
{related}            <a href="news.html" class="related-article-link">
              <div class="related-article-title">All News &amp; Insights →</div>
              <div class="related-article-meta">View archive</div>
            </a>
          </div>
        </aside>
      </div>
    </section>
  </main>
'''
    out = HEAD
    out = re.sub(r"<title>.*?</title>", f"<title>{a['meta_title']}</title>", out, count=1)
    out = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{a["meta_desc"]}">',
        out,
        count=1,
    )
    return out + NAV + hero + FOOTER


ARTICLES = [
    {
        "slug": "news-eto-eastern-2026.html",
        "meta_title": "ETO Eastern Conference 2026: Interest Registration Is Open — KBI Hong Kong",
        "meta_desc": "Interest registration is open for ETO Eastern Conference 2026 — 9–11 October at CDNIS, Hong Kong's global emerging-technologies conference.",
        "tags": ["Announcement", "Competitions", "ETO"],
        "byline": "KBI HK Competitions Team",
        "date": "10 May 2026",
        "read_time": "5 min",
        "hero_h1": "ETO Eastern Conference 2026:<br>Interest Registration Is <em>Open</em>",
        "subtitle": "9–11 October 2026 · Canadian International School of Hong Kong (CDNIS)",
        "toc": [
            ("intro", "Introduction"),
            ("whats-new", "What's new in 2026"),
            ("overview", "At a glance"),
            ("eto-and-i2ol", "ETO and I2OL"),
            ("registration", "Registration"),
            ("coming-2026", "Also in 2026"),
            ("cta", "Register"),
        ],
        "sidebar_buttons": [
            {"href": "https://forms.gle/7WwvpwKxkDXtRbK2A", "label": "Register Interest →", "class": "btn btn-yellow btn--sm"},
            {"href": "../upcoming events/eto2026.html", "label": "ETO 2026 Programme Page"},
            {"href": "../programme/i2ol.html", "label": "I2OL Scheme"},
        ],
        "related": [
            {"href": "news-skillsprint-2026-launch.html", "title": "Emerging-Technology SkillSprint (ETS) 2026", "meta": "Announcement · 4 min"},
            {"href": "insight-seriousness-without-hype.html", "title": "Seriousness Without Hype", "meta": "Insight · 8 min"},
        ],
        "body": '''
          <p id="intro">KBI Hong Kong is pleased to announce that <strong>ETO Eastern Conference 2026</strong> — the Emerging Technologies Olympiad Eastern Conference — is open for interest registration. The conference will be held from <strong>9–11 October 2026</strong> at the Canadian International School of Hong Kong (CDNIS).</p>
          <p>ETO is a global, cross-disciplinary emerging-technologies conference spanning three domains: Blockchain and Trust Technologies (BCTT), Data Science and Artificial Intelligence (DSAI), and Quantum Computing and Information Technologies (QCIT). It is distinct from the I2OL subject olympiads (IBCOL, IDSOL, IQCOL). Students worldwide are invited to attend in person, with a particular focus on participants across the eastern hemisphere.</p>
          <div class="article-pullquote"><p>"ETO Eastern is where Hong Kong's sharpest student minds prove themselves — not just against each other, but against the best in the world."</p></div>
          <h2 id="whats-new">What's new in 2026</h2>
          <p>The 2026 cycle brings several structural updates. Most significantly, the programme now formally adopts a two-stream model aligned with international ISCED classification, so every level of student competes in an appropriately benchmarked cohort.</p>
          <p>The two streams are:</p>
          <ul>
            <li><strong>Schoolers Stream (ISCED 1–3)</strong> – Open to primary and secondary school students. Teams in this stream are designated Schoolers Teams and produce Schoolers Projects.</li>
            <li><strong>Students Stream (ISCED 4–8)</strong> – Open to sub-degree, undergraduate, and postgraduate students. Mixed teams (Students + Schoolers) are permitted with a tertiary majority.</li>
          </ul>
          <p>This change follows sustained feedback from participating schools and universities that mixed-level competition was creating an uneven playing field. The new structure keeps the community's inclusive, cross-institution ethos while making the competition fairer and clearer for everyone.</p>
          <div class="article-fact-box" id="overview">
            <div class="article-fact-box-title">ETO Eastern Conference 2026 at a glance</div>
            <div class="article-fact-list">
              <div class="article-fact-item">Dates: 9–11 October 2026</div>
              <div class="article-fact-item">Venue: CDNIS, Hong Kong</div>
              <div class="article-fact-item">Domains: BCTT, DSAI, QCIT</div>
              <div class="article-fact-item">Streams: Schoolers (ISCED 1–3) and Students (ISCED 4–8)</div>
              <div class="article-fact-item">Scale: Approximately 36 teams and 300 participants expected</div>
            </div>
          </div>
          <h2 id="eto-and-i2ol">How ETO relates to I2OL</h2>
          <p>Students may also compete in the I2OL subject olympiads — IBCOL, IDSOL, and IQCOL — each with its own Hong Kong round and international finals. ETO is a separate conference with its own structure and adjudication.</p>
          <p>See the <a href="../programme/i2ol.html">I2OL Scheme</a> page for the subject olympiad structure. See the <a href="../upcoming events/eto2026.html">ETO Eastern Conference 2026</a> page for detailed programme, tracks, and judging.</p>
          <h2 id="registration">Registration and next steps</h2>
          <p>Interest registration is now open. Prospective participants — individually or as a team — are encouraged to register interest to receive:</p>
          <ul>
            <li>The official ETO Eastern Conference 2026 prospectus and competition handbook</li>
            <li>Invitations to pre-competition workshops and clinics</li>
            <li>Team formation support (for solo registrants who need teammates)</li>
            <li>Early announcements for official registration opening</li>
          </ul>
          <p>Official team registration and track selection will open in Q1 2026. Full details on submission deadlines, judging criteria, and presentation-day logistics will be included in the prospectus.</p>
          <div class="article-pullquote"><p>"We've consistently seen that students who engage with ETO — even if they don't win — walk away with depth of understanding that sets them apart in university applications, job interviews, and research settings."</p></div>
          <h2 id="coming-2026">Also coming in 2026</h2>
          <p>KBI HK has two flagship 2026 highlights:</p>
          <ul>
            <li><strong>ETO Eastern Conference 2026</strong> — 9–11 October at CDNIS</li>
            <li><strong>Emerging-Technology SkillSprint (ETS) 2026</strong> — The 2026 edition of our SkillSprint workshop series, following the successful 2025 FinTech series at CityU. <a href="../upcoming events/ets2026.html">ETS details</a></li>
          </ul>
          <p>All KBI members receive priority access to preparatory events. <a href="../programme/membership.html">Membership remains free for students</a>.</p>''',
        "cta": '''          <div id="cta" style="margin-top:40px;padding:28px 32px;background:var(--mist);border:1px solid var(--stone);border-radius:var(--radius-lg);">
            <div class="label-row" style="margin-bottom:12px;"><div class="u-rule"></div><span class="u-label">Call to action</span></div>
            <p style="font-family:'Inter',sans-serif;font-size:1rem;color:var(--text-muted);line-height:1.75;margin-bottom:20px;">Interest registration for ETO Eastern Conference 2026 is open now. Join us 9–11 October at CDNIS for Hong Kong's premier emerging-technologies conference.</p>
            <div style="display:flex;gap:12px;flex-wrap:wrap;">
              <a href="https://forms.gle/7WwvpwKxkDXtRbK2A" target="_blank" rel="noopener" class="btn btn-prussian">Register Interest →</a>
              <a href="../upcoming events/eto2026.html" class="btn btn-outline-prussian">Full Programme Details →</a>
            </div>
          </div>''',
        "card": {"category": "announcement", "tag": "Announcement", "date": "10 May 2026", "title": "ETO Eastern Conference 2026: Interest Registration Is Open", "excerpt": "9–11 October at CDNIS — global emerging-technologies conference. Interest registration is open.", "img": IMG_ETO},
    },
    {
        "slug": "news-skillsprint-2026-launch.html",
        "meta_title": "Emerging-Technology SkillSprint (ETS) 2026 — KBI Hong Kong",
        "meta_desc": "KBI Hong Kong launches Emerging-Technology SkillSprint (ETS) 2026 — the 2026 edition of our concentrated emerging-technology workshop series.",
        "tags": ["Announcement", "Training", "SkillSprint"],
        "byline": "KBI HK Programmes Team",
        "date": "8 May 2026",
        "read_time": "4 min",
        "hero_h1": "Launching Emerging-Technology<br>SkillSprint <em>(ETS) 2026</em>",
        "subtitle": "Intensive workshops in blockchain, data, and AI — built for serious beginners.",
        "toc": [
            ("intro", "Introduction"),
            ("what-is-skillsprint", "What SkillSprint is"),
            ("whats-new", "What's new in 2026"),
            ("connection", "Programme connections"),
            ("who-should-join", "Who should join"),
            ("next-steps", "Next steps"),
        ],
        "sidebar_buttons": [
            {"href": "../upcoming events/ets2026.html", "label": "ETS 2026 Event Page", "class": "btn btn-yellow btn--sm"},
            {"href": "../programme/skillsprint.html", "label": "SkillSprint Programme"},
            {"href": "../contact.html", "label": "Register Interest"},
        ],
        "related": [
            {"href": "news-eto-eastern-2026.html", "title": "ETO Eastern Conference 2026", "meta": "Announcement · 5 min"},
        ],
        "body": '''
          <p id="intro">After a successful 2025 edition at City University of Hong Kong, KBI Hong Kong is launching <strong>Emerging-Technology SkillSprint (ETS) 2026</strong> — the 2026 edition of our SkillSprint workshop series covering blockchain, trust technologies, data science, and AI for students who want a serious, hands-on introduction to the field.</p>
          <p>SkillSprint is not an expo or a showcase. It is a small, focused environment where participants work directly with concepts, tools, and problems that real teams face.</p>
          <h2 id="what-is-skillsprint">What SkillSprint is</h2>
          <p>The 2026 edition — ETS — is designed for:</p>
          <ul>
            <li>Students interested in emerging technologies who want to move beyond surface-level familiarity.</li>
            <li>Participants preparing for competitions (IBCOL, IDSOL, IQCOL, ETO) who need stronger foundations.</li>
            <li>Members curious about how blockchain, data, and AI actually fit together in real systems.</li>
          </ul>
          <p>Each SkillSprint edition is short and intense, technical but guided, and applied — exercises are grounded in realistic scenarios, not isolated toy problems. The 2025 series ran as <strong>FinTech SkillSprint</strong> at CityU; 2026 broadens the lens to emerging technologies across the same concentrated format.</p>
          <h2 id="whats-new">What's new in 2026</h2>
          <p>The 2026 edition builds on community feedback from 2025:</p>
          <ul>
            <li>Clearer tracks for different starting points (for example, first-time learners vs competition-ready).</li>
            <li>More structured lab components and fewer one-off demos.</li>
            <li>Integrated coverage of AI tools, including how to use them responsibly in analysis, prototyping, and documentation.</li>
          </ul>
          <h2 id="connection">How it connects to other programmes</h2>
          <p>SkillSprint is part of the broader KBI HK pathway. It helps newcomers build enough foundation to participate more confidently in olympiads and projects; gives experienced participants a way to refresh or deepen understanding; and can be a stepping stone towards more advanced training and, eventually, ISFRETIC-aligned certification pathways.</p>
          <h2 id="who-should-join">Who should consider joining</h2>
          <p>ETS is a good fit if you are a secondary or university student with genuine interest in emerging technologies; have participated in KBI programmes and want more structured learning; or are new to KBI but looking for a serious first engagement, not simply an info session.</p>
          <h2 id="next-steps">Next steps</h2>
          <p>Full dates, host venue, and registration details will be announced on the <a href="../upcoming events/events.html">Events page</a> and through KBI HK's mailing list. Members will receive early access to registration.</p>''',
        "cta": '''          <div style="margin-top:32px;display:flex;gap:12px;flex-wrap:wrap;">
            <a href="../upcoming events/events.html#ets-2026" class="btn btn-prussian">Events page</a>
            <a href="../programme/membership.html" class="btn btn-outline-prussian">Join as a member</a>
          </div>''',
        "card": {"category": "announcement", "tag": "Announcement", "date": "8 May 2026", "title": "Emerging-Technology SkillSprint (ETS) 2026", "excerpt": "The 2026 SkillSprint edition — concentrated workshops across blockchain, data, AI, and related domains.", "img": IMG_TRAIN},
    },
    {
        "slug": "news-iqcol-hk-launch.html",
        "meta_title": "Introducing IQCOL Hong Kong — KBI Hong Kong",
        "meta_desc": "KBI Hong Kong introduces IQCOL Hong Kong — the quantum computing olympiad completing the I2OL triad alongside IBCOL and IDSOL.",
        "tags": ["Announcement", "Competitions", "IQCOL"],
        "byline": "KBI HK Competitions Team",
        "date": "1 May 2026",
        "read_time": "5 min",
        "hero_h1": "Introducing IQCOL Hong Kong:<br>The Quantum Olympiad <em>Arrives</em>",
        "subtitle": "A new pathway for students serious about quantum.",
        "toc": [("intro", "Introduction"), ("why-matters", "Why IQCOL matters"), ("i2ol-fit", "I2OL fit"), ("format", "Format"), ("who-should-join", "Who should join"), ("next-steps", "Next steps")],
        "sidebar_buttons": [{"href": "https://2026.iqcol.org", "label": "IQCOL 2026", "class": "btn btn-yellow btn--sm"}, {"href": "../programme/i2ol.html", "label": "I2OL Scheme"}],
        "related": [{"href": "news-eto-eastern-2026.html", "title": "ETO Eastern Conference 2026", "meta": "5 min"}],
        "body": '''
          <p id="intro">KBI Hong Kong is proud to introduce the first <strong>IQCOL Hong Kong</strong> — the quantum computing and information olympiad that completes the I2OL triad alongside IBCOL (blockchain) and IDSOL (data science).</p>
          <p>IQCOL provides a structured way for students to engage with quantum concepts, from foundational ideas to more advanced problem-solving, in a competition format that still prioritises understanding over memorisation.</p>
          <h2 id="why-matters">Why IQCOL matters</h2>
          <p>Quantum computing is often treated as either distant or purely theoretical. IQCOL Hong Kong is designed to make serious quantum concepts accessible to motivated students; provide a clear progression from basic literacy to deeper engagement; and connect participants to a community of peers, mentors, and future opportunities.</p>
          <p>Participants may encounter topics such as qubits and measurement, quantum gates and simple circuits, quantum error and noise, and implications for cryptography and security.</p>
          <h2 id="i2ol-fit">How IQCOL fits into I2OL</h2>
          <p>IQCOL Hong Kong sits alongside IBCOL and IDSOL, covering blockchain and trust technologies, data and AI, and quantum computing and information technologies. Students may focus on IQCOL or participate across multiple olympiads.</p>
          <h2 id="format">Format and expectations</h2>
          <p>The inaugural IQCOL Hong Kong edition will run as a local qualifying round ahead of international finals, include written and problem-solving components, and emphasise clarity of reasoning. Detailed rules will be published in the IQCOL HK competition brief.</p>
          <h2 id="who-should-join">Who should consider IQCOL</h2>
          <p>IQCOL suits secondary and university students with strong interest in mathematics, physics, or computer science; past participants of quantum seminars or KBI activities; and newcomers ready to work seriously. Prior quantum programming experience is not required.</p>
          <h2 id="next-steps">Next steps</h2>
          <p>Join <a href="../programme/membership.html">KBI HK membership</a> for early updates, watch the <a href="../programme/i2ol.html">I2OL Scheme</a> page, and attend upcoming quantum-themed events to prepare.</p>''',
        "cta": "",
        "card": {"category": "announcement", "tag": "Announcement", "date": "1 May 2026", "title": "Introducing IQCOL Hong Kong", "excerpt": "The quantum computing olympiad completes the I2OL triad alongside IBCOL and IDSOL.", "img": IMG_QUANTUM},
    },
    {
        "slug": "insight-seriousness-without-hype.html",
        "meta_title": "Seriousness Without Hype — KBI Hong Kong",
        "meta_desc": "Why KBI Hong Kong is careful about how we design emerging-technology education — serious, rigorous, and context-aware.",
        "tags": ["Insight"],
        "byline": "KBI Hong Kong Editorial",
        "date": "20 April 2026",
        "read_time": "8 min",
        "hero_h1": "Seriousness Without Hype:<br>What Emerging-Tech Education <em>Should Feel Like</em>",
        "subtitle": "Why KBI HK is careful about how we design programmes.",
        "toc": [("intro", "Introduction"), ("hype-vs-serious", "Hype vs seriousness"), ("how-seriousness-looks", "In practice"), ("why-students-deserve", "Why students deserve this"), ("role-of-community", "Community"), ("accountability", "Accountability"), ("closing", "Closing")],
        "sidebar_buttons": [{"href": "../about/about-who-we-are.html", "label": "Who We Are"}, {"href": "../programme/membership.html", "label": "Join Us"}],
        "related": [{"href": "insight-beyond-one-off-events.html", "title": "Beyond One-Off Events", "meta": "7 min"}],
        "body": '''
          <p id="intro">Emerging-technology education is often presented as hype — big promises and vague language — or as dry jargon disconnected from real life. At KBI Hong Kong, we are trying to build something different: education that is serious, rigorous, and context-aware, without being shallow or inaccessible.</p>
          <h2 id="hype-vs-serious">Hype is cheap, seriousness is harder</h2>
          <p>It is easy to say that blockchain, AI, or quantum computing will change everything. It is harder to understand where they fit into existing systems, confront limitations and governance questions, and teach students to think clearly rather than repeat buzzwords.</p>
          <h2 id="how-seriousness-looks">What seriousness looks like in practice</h2>
          <p>For KBI HK, seriousness shows up in competition tasks that require genuine understanding; trainings like SkillSprint and ETTI built around real workflows; tech projects aimed at real outputs; and working groups allowed to ask uncomfortable questions.</p>
          <h2 id="why-students-deserve">Why students deserve this</h2>
          <p>Students notice when programmes are over-promised, marketing-driven, or too casual to be worth serious effort. Early experiences shape whether they stay in a field or walk away. If education is sloppy, we should not be surprised if future systems are too.</p>
          <h2 id="role-of-community">The role of community</h2>
          <p>Serious education is also about peers who challenge weak reasoning, mentors who care about growth, and institutions willing to say we do not know yet when that is the truth.</p>
          <h2 id="accountability">How we hold ourselves accountable</h2>
          <p>We check ourselves through participant feedback, alumni trajectories, and willingness to retire formats that no longer work. We are interested in whether people become more capable and responsible — not in the biggest mailing list.</p>
          <h2 id="closing">Closing</h2>
          <p>Seriousness is not about being solemn. It is about being honest about what is at stake and acting accordingly. If you share this instinct, we hope KBI Hong Kong is a place where your work can grow.</p>''',
        "cta": "",
        "card": {"category": "insight", "tag": "Insight", "date": "20 April 2026", "title": "Seriousness Without Hype", "excerpt": "What emerging-technology education should feel like — and why KBI HK designs programmes accordingly.", "img": IMG_INSIGHT},
    },
    {
        "slug": "insight-beyond-one-off-events.html",
        "meta_title": "Beyond One-Off Events — KBI Hong Kong",
        "meta_desc": "Why KBI Hong Kong cares about pathways in emerging technology — not only single competitions or workshops.",
        "tags": ["Insight", "Community"],
        "byline": "KBI Hong Kong Editorial",
        "date": "12 April 2026",
        "read_time": "7 min",
        "hero_h1": "Beyond One-Off Events:<br>Building <em>Pathways</em>",
        "subtitle": "Why KBI HK cares about what happens after the competition.",
        "toc": [("intro", "Introduction"), ("problem-one-off", "The one-off problem"), ("what-pathway-looks-like", "What a pathway looks like"), ("why-students", "For students"), ("why-partners", "For partners"), ("current-pathway", "KBI's pathway"), ("closing", "Closing")],
        "sidebar_buttons": [{"href": "../programme/programmes.html", "label": "Programmes Hub"}, {"href": "../programme/membership.html", "label": "Membership"}],
        "related": [{"href": "insight-seriousness-without-hype.html", "title": "Seriousness Without Hype", "meta": "8 min"}],
        "body": '''
          <p id="intro">Most students meet emerging technologies through one-off experiences: a competition, a workshop, a talk. These can be exciting — and frustrating if there is nowhere to go afterwards. KBI Hong Kong's work has been shaped by a simple question: what happens next?</p>
          <h2 id="problem-one-off">The problem with one-off formats</h2>
          <p>Without follow-on pathways, one-off events reward a few winners and leave others unsure what to do; create short motivation spikes that fade; and make it hard to build sustained competence.</p>
          <h2 id="what-pathway-looks-like">What a pathway looks like</h2>
          <p>A pathway means visible ways to enter through accessible introductions; deepen through SkillSprint, ETTI, tech projects, or research groups; contribute through mentorship or collaboration; and be recognised through credible certification or public work.</p>
          <h2 id="why-students">Why this matters for students</h2>
          <p>Pathways help students see where they are and what might come next, reduce pressure to peak in a single event, and allow different tempos and directions.</p>
          <h2 id="why-partners">Why this matters for partners</h2>
          <p>For schools, universities, and industry, pathways make involvement fit institutional goals, provide multiple entry points, and offer clearer ways to follow student development over time.</p>
          <h2 id="current-pathway">KBI HK's current pathway</h2>
          <p>Today the pathway broadly runs from entry through competitions and community engagement; deepening through SkillSprint, ETTI, projects, and groups; toward recognition connecting to ISFRETIC-aligned certification and longer-term roles. We expect it to keep evolving.</p>
          <h2 id="closing">Closing</h2>
          <p>One-off events are often where stories begin. If we care about what students can actually do, we must also care about what happens after the first event is over. You are invited to help shape that pathway.</p>''',
        "cta": "",
        "card": {"category": "insight", "tag": "Insight", "date": "12 April 2026", "title": "Beyond One-Off Events: Building Pathways", "excerpt": "Why KBI HK cares about what happens after the competition or workshop ends.", "img": IMG_INSIGHT},
    },
]


def card_html(c: dict, slug: str, delay: str = "") -> str:
    tag_cls = "tag--sky" if c["tag"] == "Announcement" else "tag--stone"
    return f'''      <article class="news-all-card reveal{delay}" role="listitem" data-category="{c["category"]}">
        <div class="news-all-card-visual" style="position:relative;overflow:hidden;"><img src="{c["img"]}" alt="" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;" loading="lazy"><div style="position:absolute;inset:0;background:rgba(0,49,83,0.68);" aria-hidden="true"></div></div>
        <div class="news-all-card-body">
          <div class="news-meta"><span class="tag {tag_cls}">{c["tag"]}</span><span class="news-date">{c["date"]}</span></div>
          <h4>{c["title"]}</h4>
          <p>{c["excerpt"]}</p>
          <a href="{slug}" class="link-arrow" style="margin-top:12px;display:inline-flex;">Read more <svg viewBox="0 0 12 12" fill="none" aria-hidden="true"><path d="M2 6h8M6 2l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></a>
        </div>
      </article>
'''


def scroll_card_html(c: dict, slug: str) -> str:
    tag_cls = "tag--sky" if c["tag"] == "Announcement" else "tag--stone"
    return f'''        <article class="news-scroll-card" role="listitem">
          <div class="news-scroll-card-visual"><img src="{c["img"]}" alt="" loading="lazy"><div class="news-scroll-card-overlay" aria-hidden="true"></div></div>
          <div class="news-scroll-card-body">
            <div class="news-meta"><span class="tag {tag_cls}">{c["tag"]}</span><span class="news-date">{c["date"]}</span></div>
            <h4>{c["title"]}</h4>
            <p>{c["excerpt"]}</p>
            <a href="news/{slug}" class="link-arrow">Read article <svg viewBox="0 0 12 12" fill="none" aria-hidden="true"><path d="M2 6h8M6 2l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></a>
          </div>
        </article>
'''


def main() -> None:
    for a in ARTICLES:
        path = NEWS / a["slug"]
        path.write_text(render_article(a), encoding="utf-8")
        print("Wrote", path.name)

    # news1.html redirect
    (NEWS / "news1.html").write_text(
        f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
        f'<meta http-equiv="refresh" content="0; url=news-eto-eastern-2026.html">'
        f'<link rel="canonical" href="news-eto-eastern-2026.html">'
        f'<title>Redirecting…</title></head><body><p><a href="news-eto-eastern-2026.html">Continue to article</a></p></body></html>',
        encoding="utf-8",
    )

    grid = "\n".join(
        card_html(a["card"], a["slug"], "" if i == 0 else f" reveal-delay-{min(i, 3)}")
        for i, a in enumerate(ARTICLES)
    )
    news_html = (NEWS / "news.html").read_text(encoding="utf-8")
    news_html = re.sub(
        r'<div class="news-all-grid" role="list">.*?</div>\s*</div>\s*</section>',
        f'<div class="news-all-grid" role="list">\n\n{grid}\n    </div>\n  </div>\n</section>',
        news_html,
        count=1,
        flags=re.DOTALL,
    )
    # Update featured block link
    news_html = news_html.replace('href="news1.html"', 'href="news-eto-eastern-2026.html"')
    news_html = news_html.replace(
        "ETO Eastern Conference 2026 — 9–11 October at CDNIS</h2>",
        "ETO Eastern Conference 2026: Interest Registration Is Open</h2>",
    )
    (NEWS / "news.html").write_text(news_html, encoding="utf-8")
    print("Updated news.html")

    scroll = "\n".join(scroll_card_html(a["card"], a["slug"]) for a in ARTICLES)
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    new_section = f'''  <section class="section-wrap section-wrap--mist" aria-labelledby="news-prev-heading">
    <div class="section-inner">
      <div style="display:flex;align-items:flex-end;justify-content:space-between;gap:32px;flex-wrap:wrap;margin-bottom:24px;">
        <div>
          <div class="label-row">
            <div class="u-rule" aria-hidden="true"></div><span class="u-label">News &amp; Insights</span>
          </div>
          <h2 class="section-heading reveal" id="news-prev-heading" style="margin-bottom:0;">Latest from KBI HK</h2>
        </div>
        <a href="news/news.html" class="btn btn-outline-prussian btn--sm reveal" style="flex-shrink:0;">See all
          <svg viewBox="0 0 14 14" fill="none" aria-hidden="true">
            <path d="M2 7h10M7 2l5 5-5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </a>
      </div>
      <p class="section-body reveal" style="max-width:640px;margin-bottom:28px;font-size:0.9375rem;">Scroll horizontally to browse our six most recent articles — announcements and insights from KBI Hong Kong.</p>
      <div class="news-scroll-wrap reveal">
        <div class="news-scroll-track" role="list" tabindex="0" aria-label="Latest news articles — scroll horizontally">
{scroll}
        </div>
      </div>
    </div>
  </section>'''
    index = re.sub(
        r'  <section class="section-wrap section-wrap--mist" aria-labelledby="news-prev-heading">.*?</section>\s*\n\s*<!-- ═+',
        new_section + "\n\n  <!-- ═",
        index,
        count=1,
        flags=re.DOTALL,
    )
    (ROOT / "index.html").write_text(index, encoding="utf-8")
    print("Updated index.html")


if __name__ == "__main__":
    main()
