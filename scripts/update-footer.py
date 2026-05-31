#!/usr/bin/env python3
"""Standardize site footer to mirror main navigation (About / Compete / Certify / Collab / Connect)."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent

_spec = importlib.util.spec_from_file_location("update_nav", SCRIPTS / "update-nav.py")
_nav = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_nav)
nav_link_paths = _nav.link_paths

FOOTER_RE = re.compile(
    r"(?:\s*<!--\s*(?:═+\s*)?FOOTER(?:\s*═+)?\s*-->\s*)*<footer\b[^>]*>.*?</footer>",
    re.DOTALL | re.IGNORECASE,
)

LINKEDIN_SVG = (
    '<path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/>'
)
INSTAGRAM_SVG = (
    '<path d="M7.8 2h8.4C19.4 2 22 4.6 22 7.8v8.4a5.8 5.8 0 0 1-5.8 5.8H7.8C4.6 22 2 19.4 2 16.2V7.8A5.8 5.8 0 0 1 7.8 2m-.2 2A3.6 3.6 0 0 0 4 7.6v8.8C4 18.39 5.61 20 7.6 20h8.8a3.6 3.6 0 0 0 3.6-3.6V7.6C20 5.61 18.39 4 16.4 4H7.6m9.65 1.5a1.25 1.25 0 0 1 1.25 1.25A1.25 1.25 0 0 1 17.25 8 1.25 1.25 0 0 1 16 6.75a1.25 1.25 0 0 1 1.25-1.25M12 7a5 5 0 0 1 5 5 5 5 0 0 1-5 5 5 5 0 0 1-5-5 5 5 0 0 1 5-5m0 2a3 3 0 0 0-3 3 3 3 0 0 0 3 3 3 3 0 0 0 3-3 3 3 0 0 0-3-3z"/>'
)


def footer_paths(file_path: Path) -> dict[str, str]:
    rel = file_path.parent.relative_to(ROOT)
    depth = len(rel.parts)
    base = "../" * depth if depth else ""
    u = dict(nav_link_paths(file_path))

    about = "" if rel.parts == ("about",) else f"{base}about/"
    events = "events.html" if rel.parts == ("upcoming events",) else f"{base}upcoming events/events.html"
    news = "news.html" if rel.parts == ("news",) else f"{base}news/news.html"
    contact = "contact.html" if not base else f"{base}contact.html"
    media = "media.html" if not base else f"{base}media.html"
    faq = "faq.html" if not base else f"{base}faq.html"

    home = "index.html" if not base else f"{base}index.html"

    u.update(
        {
            "home": home,
            "logo_nav": f"{base}assets/brand/logo-icon.png",
            "logo_footer": f"{base}assets/brand/logo-stacked-white-on-black.png",
            "who": f"{about}about-who-we-are.html",
            "history": f"{about}about-history.html",
            "impact": f"{about}about-impact.html",
            "team": f"{about}about-team.html",
            "media": media,
            "events": events,
            "news": news,
            "contact": contact,
            "faq": faq,
        }
    )
    return u


def build_footer(file_path: Path) -> str:
    u = footer_paths(file_path)
    return f'''
  <!-- ═══ FOOTER ═══ -->
  <footer class="site-footer" role="contentinfo">
    <div class="footer-inner">
      <div class="footer-brand">
        <a href="{u["home"]}" class="footer-logo" aria-label="KBI Hong Kong — home">
          <div class="footer-logo-mark"><img src="{u["logo_footer"]}" alt="" class="brand-mark-img" width="40" height="40"></div>
          <div class="footer-wordmark">
            <span class="footer-wordmark-name">KBI Hong Kong</span>
            <span class="footer-wordmark-sub">Königsberger Bridges Institute</span>
          </div>
        </a>
        <p class="footer-tagline">Building Hong Kong's pipeline of emerging technology talent through competitions, research, and community.</p>
        <p class="footer-copyright">&copy; 2026 Kingsbridge Institute Limited. All rights reserved.<br>A chapter of the Königsberger Bridges Institute.</p>
        <div class="footer-social" aria-label="Social media links">
          <a href="#" class="footer-social-link" aria-label="LinkedIn">
            <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">{LINKEDIN_SVG}</svg>
          </a>
          <a href="https://www.instagram.com/kbi_hongkong/" class="footer-social-link" aria-label="Instagram">
            <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">{INSTAGRAM_SVG}</svg>
          </a>
        </div>
      </div>
      <div class="footer-cols">
        <div class="footer-col">
          <h3 class="footer-col-heading">About</h3>
          <ul role="list">
            <li><a href="{u["who"]}">Who We Are</a></li>
            <li><a href="{u["history"]}">Our History</a></li>
            <li><a href="{u["impact"]}">Our Impact</a></li>
            <li><a href="{u["team"]}">Our Team</a></li>
            <li><a href="{u["media"]}">Media &amp; Brand Kit</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h3 class="footer-col-heading">Compete</h3>
          <ul role="list">
            <li><a href="{u["eto"]}">Emerging Technologies Olympiad (ETO)</a></li>
            <li><a href="{u["i2ol"]}">I&sup2;OL Scheme</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h3 class="footer-col-heading">Certify</h3>
          <ul role="list">
            <li><a href="{u["etti"]}">ETTI Program</a></li>
            <li><a href="{u["skillsprint"]}">SkillSprint</a></li>
            <li><a href="{u["abc5"]}">ABC5 Program</a></li>
            <li><a href="{u["isfretic"]}">ISFRETIC</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h3 class="footer-col-heading">Collab</h3>
          <ul role="list">
            <li><a href="{u["projects"]}">Project Support</a></li>
            <li><a href="{u["working"]}">Working &amp; Research Groups</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h3 class="footer-col-heading">Connect</h3>
          <ul role="list">
            <li><a href="{u["socratic"]}">Socratic Circles</a></li>
            <li><a href="{u["gatherings"]}">KBI Community Gatherings</a></li>
            <li><a href="{u["events"]}">Events</a></li>
            <li><a href="{u["news"]}">News &amp; Insights</a></li>
            <li><a href="{u["contact"]}">Contact</a></li>
            <li><a href="{u["sponsors"]}">Partner With Us</a></li>
            <li><a href="{u["membership"]}">Join Us</a></li>
          </ul>
        </div>
      </div>
    </div>
  </footer>'''


def main() -> None:
    skip_names = {"good-ones.html"}
    updated: list[Path] = []
    for html in sorted(ROOT.rglob("*.html")):
        if "scripts" in html.parts or html.name in skip_names:
            continue
        text = html.read_text(encoding="utf-8")
        if not FOOTER_RE.search(text):
            continue
        new_footer = build_footer(html)
        new_text = FOOTER_RE.sub(new_footer, text, count=1)
        if new_text != text:
            html.write_text(new_text, encoding="utf-8")
            updated.append(html.relative_to(ROOT))
    for path in updated:
        print(path)
    print(f"Updated {len(updated)} file(s).")


if __name__ == "__main__":
    main()
