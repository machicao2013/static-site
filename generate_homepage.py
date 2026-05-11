#!/usr/bin/env python3
"""Generate a single terminal-style homepage for this static site."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import Path


SKIPPED_DIR_NAMES = {
    ".git",
    ".github",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
    "node_modules",
}


@dataclass(frozen=True)
class Page:
    title: str
    path: Path
    updated_at: datetime


@dataclass(frozen=True)
class Section:
    name: str
    path: Path
    pages: tuple[Page, ...]


def extract_title(html_path: Path) -> str:
    content = html_path.read_text(encoding="utf-8", errors="ignore")
    for pattern in (
        r"<title[^>]*>(.*?)</title>",
        r"<h1[^>]*>(.*?)</h1>",
    ):
        match = re.search(pattern, content, flags=re.IGNORECASE | re.DOTALL)
        if match:
            title = re.sub(r"<[^>]+>", "", match.group(1))
            title = re.sub(r"\s+", " ", title).strip()
            if title:
                return title
    return html_path.stem.replace("-", " ").replace("_", " ").strip() or html_path.name


def url_for(path: Path) -> str:
    return path.as_posix()


def collect_sections(root: Path) -> tuple[Section, ...]:
    sections: list[Section] = []
    for directory in sorted((path for path in root.iterdir() if path.is_dir()), key=lambda path: path.name):
        if directory.name.startswith(".") or directory.name in SKIPPED_DIR_NAMES:
            continue

        pages: list[Page] = []
        for html_path in sorted(directory.rglob("*.html"), key=lambda path: path.relative_to(directory).as_posix()):
            relative_parts = html_path.relative_to(root).parts
            if any(part in SKIPPED_DIR_NAMES or part.startswith(".") for part in relative_parts):
                continue
            if html_path.name == "index.html":
                continue

            pages.append(
                Page(
                    title=extract_title(html_path),
                    path=html_path.relative_to(root),
                    updated_at=datetime.fromtimestamp(html_path.stat().st_mtime),
                )
            )

        if pages:
            sections.append(
                Section(
                    name=directory.name,
                    path=directory.relative_to(root),
                    pages=tuple(sorted(pages, key=lambda page: page.title.lower())),
                )
            )

    return tuple(sections)


def render_category_buttons(sections: tuple[Section, ...]) -> str:
    total_pages = sum(len(section.pages) for section in sections)
    buttons = [
        f"""        <button class="cat" type="button" aria-pressed="true" data-section="ALL">
          <span>全部页面</span>
          <span>{total_pages}</span>
        </button>"""
    ]
    for section in sections:
        buttons.append(
            f"""        <button class="cat" type="button" aria-pressed="false" data-section="{escape(section.name)}">
          <span>{escape(section.name)}</span>
          <span>{len(section.pages)}</span>
        </button>"""
        )
    return "\n".join(buttons)


def render_results(sections: tuple[Section, ...]) -> str:
    items: list[str] = []
    index = 1
    for section in sections:
        for page in section.pages:
            date = page.updated_at.strftime("%Y-%m-%d")
            search_text = f"{page.title} {page.path.as_posix()} {section.name}".lower()
            items.append(
                f"""        <a class="result" href="{escape(url_for(page.path), quote=True)}" data-section="{escape(section.name)}" data-text="{escape(search_text)}">
          <span>
            <strong>{index:02d} {escape(page.title)}</strong>
            <small>{escape(page.path.as_posix())}</small>
          </span>
          <span class="tag">{escape(section.name)}</span>
          <time datetime="{date}">{date}</time>
        </a>"""
            )
            index += 1
    return "\n".join(items)


def render_root_index(sections: tuple[Section, ...]) -> str:
    total_pages = sum(len(section.pages) for section in sections)
    categories = render_category_buttons(sections)
    results = render_results(sections)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>网站首页</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #0d1117;
      --panel: #11161d;
      --panel-2: #171d25;
      --line: #303843;
      --line-2: #3a4554;
      --ink: #e8edf2;
      --muted: #9aa5b1;
      --gold: #f1c75b;
      --gold-soft: rgba(241, 199, 91, 0.12);
      --green: #94c973;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background:
        linear-gradient(rgba(255,255,255,0.025) 50%, transparent 50%),
        var(--bg);
      background-size: 100% 4px;
      font-family: "SF Mono", Menlo, Consolas, "Noto Sans SC", monospace;
      line-height: 1.5;
    }}
    button,
    input {{
      font: inherit;
    }}
    a {{
      color: inherit;
      text-decoration: none;
    }}
    .shell {{
      width: min(1360px, calc(100% - 28px));
      margin: 0 auto;
      padding: 24px 0 40px;
    }}
    .topbar {{
      min-height: 42px;
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: center;
      color: var(--muted);
      border: 1px solid var(--line);
      background: #0a0e13;
      padding: 10px 14px;
    }}
    .prompt {{
      color: var(--green);
    }}
    .layout {{
      min-height: calc(100vh - 110px);
      display: grid;
      grid-template-columns: 310px minmax(0, 1fr);
      border: 1px solid var(--line);
      border-top: 0;
      background: var(--panel);
      box-shadow: 0 26px 90px rgba(0, 0, 0, 0.38);
    }}
    aside {{
      padding: 20px;
      border-right: 1px solid var(--line);
      background: #0d1117;
    }}
    main {{
      min-width: 0;
      padding: 22px;
    }}
    .label {{
      text-transform: uppercase;
      letter-spacing: 0.14em;
      font-size: 0.72rem;
      color: var(--muted);
    }}
    h1,
    h2 {{
      margin: 8px 0 16px;
      letter-spacing: 0;
      line-height: 1;
    }}
    h1 {{
      font-size: 1.4rem;
    }}
    h2 {{
      max-width: 900px;
      font-size: clamp(2rem, 4vw, 4.8rem);
      color: #f7f4e8;
    }}
    .cat-list {{
      display: grid;
      gap: 8px;
      margin-top: 18px;
    }}
    .cat {{
      min-height: 46px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      border: 1px solid transparent;
      border-bottom-color: #2c3440;
      background: transparent;
      color: #dce4ec;
      padding: 9px 10px;
      text-align: left;
      cursor: pointer;
    }}
    .cat:hover {{
      color: var(--gold);
      background: rgba(255,255,255,0.035);
    }}
    .cat[aria-pressed="true"] {{
      border-color: var(--gold);
      background: #202832;
      color: var(--gold);
      box-shadow: inset 3px 0 0 var(--gold);
    }}
    .summary {{
      margin-top: 24px;
      display: grid;
      gap: 8px;
      color: var(--muted);
      font-size: 0.88rem;
    }}
    .summary b {{
      color: var(--ink);
    }}
    .toolbar {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 14px;
      align-items: center;
      margin: 22px 0;
    }}
    .search {{
      width: 100%;
      min-height: 50px;
      border: 1px solid var(--line-2);
      background: #0d1117;
      color: var(--ink);
      padding: 0 14px;
      outline: 0;
    }}
    .search:focus {{
      border-color: var(--gold);
      box-shadow: 0 0 0 3px var(--gold-soft);
    }}
    .count {{
      color: var(--muted);
      white-space: nowrap;
    }}
    .results {{
      display: grid;
      gap: 9px;
    }}
    .result {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto auto;
      gap: 18px;
      align-items: center;
      min-height: 64px;
      padding: 12px 14px;
      border: 1px solid #2f3946;
      background: var(--panel-2);
      transition: border-color 160ms ease, background 160ms ease, transform 160ms ease;
    }}
    .result.is-hidden {{
      display: none;
    }}
    .result:hover {{
      border-color: var(--gold);
      background: #202832;
      transform: translateX(3px);
    }}
    .result strong {{
      display: block;
      color: var(--gold);
      font-weight: 700;
      letter-spacing: 0;
    }}
    .result small {{
      display: block;
      margin-top: 2px;
      color: var(--muted);
      word-break: break-word;
    }}
    .tag,
    time {{
      color: var(--muted);
      white-space: nowrap;
      font-size: 0.88rem;
    }}
    .empty {{
      display: none;
      border: 1px dashed var(--line-2);
      color: var(--muted);
      padding: 22px;
      background: rgba(255,255,255,0.025);
    }}
    .empty.show {{
      display: block;
    }}
    @media (max-width: 860px) {{
      .shell {{
        width: min(100% - 20px, 1360px);
        padding-top: 10px;
      }}
      .topbar,
      .layout,
      .toolbar,
      .result {{
        grid-template-columns: 1fr;
      }}
      .topbar {{
        display: grid;
      }}
      aside {{
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }}
      main {{
        padding: 16px;
      }}
      .tag,
      time {{
        white-space: normal;
      }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <header class="topbar">
      <span><span class="prompt">~/static-site-2</span> generate_homepage.py</span>
      <span>{len(sections)} dirs / {total_pages} pages</span>
    </header>
    <div class="layout" data-active="ALL">
      <aside>
        <div class="label">directories</div>
        <h1>site index</h1>
        <div class="cat-list">
{categories}
        </div>
        <div class="summary">
          <span><b>{len(sections)}</b> 个目录</span>
          <span><b>{total_pages}</b> 个页面</span>
          <span>左侧筛选，右侧直接打开页面。</span>
        </div>
      </aside>
      <main>
        <div class="label">terminal mode</div>
        <h2>Open a report, guide, or tool.</h2>
        <div class="toolbar">
          <input class="search" type="search" placeholder="搜索标题、路径或分类" aria-label="搜索标题、路径或分类">
          <span class="count"></span>
        </div>
        <div class="results">
{results}
        </div>
        <p class="empty">没有匹配的页面。</p>
      </main>
    </div>
  </div>
  <script>
    const layout = document.querySelector(".layout");
    const search = document.querySelector(".search");
    const count = document.querySelector(".count");
    const empty = document.querySelector(".empty");
    const cats = Array.from(document.querySelectorAll(".cat"));
    const items = Array.from(document.querySelectorAll(".result"));
    const total = items.length;

    function applyFilters() {{
      const active = layout.dataset.active;
      const query = search.value.trim().toLowerCase();
      let visible = 0;

      for (const item of items) {{
        const sectionMatch = active === "ALL" || item.dataset.section === active;
        const queryMatch = !query || item.dataset.text.includes(query);
        const show = sectionMatch && queryMatch;
        item.classList.toggle("is-hidden", !show);
        if (show) visible += 1;
      }}

      count.textContent = `${{visible}} / ${{total}} pages`;
      empty.classList.toggle("show", visible === 0);
    }}

    for (const cat of cats) {{
      cat.addEventListener("click", () => {{
        layout.dataset.active = cat.dataset.section;
        for (const item of cats) item.setAttribute("aria-pressed", "false");
        cat.setAttribute("aria-pressed", "true");
        applyFilters();
      }});
    }}

    search.addEventListener("input", applyFilters);
    applyFilters();
  </script>
</body>
</html>
"""


def generate_homepages(root: Path | str = ".") -> list[Path]:
    root = Path(root)
    sections = collect_sections(root)
    root_index = root / "index.html"
    root_index.write_text(render_root_index(sections), encoding="utf-8")
    return [root_index]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the site homepage.")
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Project root to scan. Defaults to the current directory.",
    )
    args = parser.parse_args()

    for path in generate_homepages(args.root):
        print(f"generated {path}")


if __name__ == "__main__":
    main()
