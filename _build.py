#!/usr/bin/env python3
# kakol.pro static generator. Re-runnable: `python3 _build.py`.
# Reads content/meta.json + content/*.html, emits pages + feed.xml + sitemap.xml + robots.txt
# + manifest.webmanifest + assets/index.json + 404.html. Retro surface, modern head/meta underneath.
import json, os, html, datetime
from email.utils import format_datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DOMAIN = "https://kakol.pro"
GH = "https://github.com/k4k0l/k4k0l.github.io"
EMAIL = "michal@kakol.pro"
BUILD_DATE = "2026-06-19"
meta = json.load(open(os.path.join(HERE, "content/meta.json")))
by_slug = {m["slug"]: m for m in meta}
notes = sorted([m for m in meta if m["kind"] == "note"], key=lambda m: m["date"], reverse=True)

NAV = [("Home", "/"), ("Projects", "/projects.html"), ("Field Notes", "/notes.html"),
       ("Research", "/research.html"), ("CV", "/cv.html"), ("Contact", "/contact.html")]

HEAD_ART = """<!--
   _              _           _
  | | ____ _  ___| | ___ _ __( )___   ___ ___  _ __ _ __   ___ _ __
  | |/ / _` |/ __| |/ / | '__|/ __|  / __/ _ \\| '__| '_ \\ / _ \\ '__|
  |   < (_| | (__|   <| | |   \\__ \\ | (_| (_) | |  | | | |  __/ |
  |_|\\_\\__,_|\\___|_|\\_\\_|_|   |___/  \\___\\___/|_|  |_| |_|\\___|_|

  Hello, view-source friend. Yes, the page looks like 1996 on purpose.
  Underneath: semantic HTML5, responsive, dark mode, RSS, sitemap, JSON-LD,
  a service worker, and a command palette (press "/"). The retro is the joke;
  the engineering is the punchline.   kto ma znaleźć, ten znajdzie.
-->"""

def esc(s): return html.escape(s, quote=True)

def jsonld(page_kind, title, desc, url, date=None):
    site = {"@context": "https://schema.org", "@type": "WebSite", "name": "Michał Kąkol", "url": DOMAIN,
            "inLanguage": "en", "author": {"@type": "Person", "name": "Michał Kąkol"}}
    graph = [site]
    if page_kind == "home":
        graph.append({"@type": "Person", "name": "Michał Kąkol", "url": DOMAIN,
                      "jobTitle": "Data Science Manager & AI systems builder",
                      "description": desc, "sameAs": ["https://github.com/k4k0l"]})
    elif page_kind == "note":
        graph.append({"@type": "Article", "headline": title, "description": desc,
                      "datePublished": date, "url": url,
                      "author": {"@type": "Person", "name": "Michał Kąkol"},
                      "publisher": {"@type": "Person", "name": "Michał Kąkol"}})
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + "</script>"

def render(title, desc, body_main, url_path, page_kind="page", date=None, og_type="website"):
    full_title = "Michał Kąkol · kakol.pro" if page_kind == "home" else esc(title) + " · kakol.pro"
    canon = DOMAIN + url_path
    nav = "\n      ".join(
        '<a href="{u}"{cur}>{t}</a>'.format(u=u, t=esc(t), cur=' aria-current="page"' if u == url_path or (url_path == "/index.html" and u == "/") else "")
        for t, u in NAV)
    head = """<!doctype html>
<html lang="{lang}">
<head>
{art}
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{ftitle}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta name="author" content="Michał Kąkol">
<meta name="theme-color" content="#fbfbf4" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0c0e11" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="kakol.pro">
<meta property="og:title" content="{otitle}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta name="twitter:card" content="summary">
<link rel="alternate" type="application/rss+xml" title="kakol.pro — field notes" href="/feed.xml">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="stylesheet" href="/assets/style.css">
{ld}
</head>
<body>
<a class="skip" href="#main">skip to content</a>
<div class="wrap">
  <header class="masthead">
    <h1><a href="/" style="text-decoration:none;color:inherit">Michał Kąkol</a></h1>
    <p class="tagline">building systems for when things get too complex to hold in your head</p>
    <p class="sub">a home page · est. MMXXVI · best viewed with curiosity (and, allegedly, Netscape at 800&times;600)</p>
  </header>
  <nav class="main" aria-label="Sections">
      {nav}
  </nav>
  <div class="toolbar">
    <span>visitors: <span id="hitcounter" class="counter" aria-label="hit counter">000000</span></span>
    <button id="lights" class="btn" type="button" title="toggle the lights">💡 lights</button>
    <button id="sound" class="btn" type="button" title="play the site theme">♪ theme</button>
    <button id="palbtn" class="btn" type="button" title="press / anywhere">⌘ jump</button>
    <button id="askbtn" class="btn" type="button" title="ask the page (AI)" hidden>✦ ask</button>
    <label class="small">find: <input id="site-search" type="search" placeholder="search the site" aria-label="Search the site"></label>
  </div>
  <ul id="search-results" aria-live="polite"></ul>
  <hr class="fancy">
  <main id="main">
{body}
  </main>
""".format(lang=("pl" if page_kind == "note" and date and by_slug.get(title_to_slug(title), {}).get("lang") == "pl" else "en"),
           art=HEAD_ART, ftitle=esc(full_title), desc=esc(desc), canon=esc(canon), ogtype=og_type,
           otitle=esc(full_title), ld=jsonld(page_kind, title, desc, canon, date), nav=nav, body=body_main)
    foot = """  <hr class="fancy">
  <footer>
    <p class="uc"><span class="bar"></span> this corner of the web is under eternal construction <span class="bar"></span></p>
    <div class="cssmarquee" aria-hidden="true"><span>&#9733; welcome to my home page &#9733; thanks for stopping by &#9733; the prompt is a sentence, the workspace is a memory &#9733; kto ma znalez&#769;c&#769;, ten znajdzie &#9733;</span></div>
    <p class="webring">&#9668; <a href="/notes.html">a random field note</a> &middot; you are on <strong>kakol.pro</strong> &middot; <a href="/feed.xml">subscribe</a> &#9658;</p>
    <p class="guestbook"><a href="{gh}/issues/new?title=hello%20from%20a%20visitor&amp;body=(this%20is%20the%20guestbook.%20a%2090s%20guestbook%2C%20backed%20by%20GitHub%20Issues.)">&#9998; sign the guestbook</a></p>
    <div class="badges">
      <a class="badge b-html" href="https://validator.w3.org/nu/?doc={canon}">VALID&nbsp;HTML5</a><a class="badge b-notepad" href="#">HAND-WRITTEN</a><a class="badge b-lynx" href="#">LYNX&nbsp;FRIENDLY</a><a class="badge b-noai" href="#">NO&nbsp;AI&nbsp;SLOP*</a><a class="badge b-rss" href="/feed.xml">RSS&nbsp;2.0</a>
    </div>
    <p class="small" id="konami-note" hidden>&#9650;&#9650;&#9660;&#9660;&#9664;&#9658;&#9664;&#9658;BA — 1996 mode engaged.</p>
    <p class="nav-foot small"><a href="/">home</a> · <a href="/projects.html">projects</a> · <a href="/notes.html">notes</a> · <a href="/research.html">research</a> · <a href="/cv.html">cv</a> · <a href="/contact.html">contact</a> · <a href="https://github.com/k4k0l">github</a></p>
    <p class="small">&copy; MMXXV–MMXXVI Michał Kąkol · last updated {built} · *no-AI-slop is a joke; this site was written with AI as the executor and a human as the architect. that is rather the point.</p>
  </footer>
</div>
<script src="/assets/main.js" defer></script>
</body>
</html>
""".format(gh=GH, canon=esc(canon), built=BUILD_DATE)
    return head + foot

# small helper: map a title back to slug (for lang in <html>) — best-effort
_slug_by_title = {m["title"]: m["slug"] for m in meta}
def title_to_slug(t): return _slug_by_title.get(t, "")

def write(path, content):
    full = os.path.join(HERE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(content)

def read_content(slug): return open(os.path.join(HERE, "content", slug + ".html")).read()

# ---------- pages ----------
# HOME
home = by_slug["home"]
recent = "".join('<li><span class="date">{d}</span> &nbsp; <a href="/notes/{s}.html">{t}</a></li>'.format(
    d=n["date"], s=n["slug"], t=esc(n["title"])) for n in notes[:4])
home_body = ('<h1>What I have been thinking about</h1>\n' + read_content("home") +
             '\n<h2>Recent field notes</h2>\n<ul class="notes">\n' + recent + '\n</ul>\n'
             '<p class="small"><a href="/notes.html">all field notes &rarr;</a> &middot; <a href="/feed.xml">rss</a></p>')
write("index.html", render(home["title"], home["description"], home_body, "/index.html", "home", og_type="website"))

# NOTES individual + index
for n in notes:
    body = ('<h1>' + esc(n["title"]) + '</h1>\n'
            '<p class="byline">' + n["date"] + ' &middot; field note &middot; ' +
            " ".join('<span class="tag">#' + esc(t) + '</span>' for t in n["tags"]) + '</p>\n' +
            read_content(n["slug"]) +
            '\n<hr>\n<p class="small">&#9664; <a href="/notes.html">back to all field notes</a></p>')
    write("notes/{}.html".format(n["slug"]), render(n["title"], n["description"], body, "/notes/{}.html".format(n["slug"]), "note", date=n["date"], og_type="article"))

notes_list = "".join(
    '<li><span class="date">{d}</span> &nbsp; <a href="/notes/{s}.html">{t}</a><br><span class="small">{desc}</span> {tags}</li>'.format(
        d=n["date"], s=n["slug"], t=esc(n["title"]), desc=esc(n["description"]),
        tags=" ".join('<span class="tag">#' + esc(t) + '</span>' for t in n["tags"][:3])) for n in notes)
notes_body = ('<h1>Field Notes</h1>\n<p>Short essays — the kind a researcher used to leave on a home page. '
              'Some technical, some not. <a href="/feed.xml">RSS</a> if you are the subscribing type.</p>\n'
              '<ul class="notes">\n' + notes_list + '\n</ul>')
write("notes.html", render("Field Notes", "Field notes by Michał Kąkol — workspaces over prompts, experimentation as error-surfacing, and the return of the home page.", notes_body, "/notes.html"))

# PROJECTS
p = by_slug["projects"]
write("projects.html", render(p["title"], p["description"], '<h1>Projects</h1>\n' + read_content("projects"), "/projects.html"))

# RESEARCH (fix Scholar placeholder href injected by content agent)
r = by_slug["research"]
research_html = read_content("research").replace('href="#"', 'href="' + SCHOLAR_URL + '"') if (SCHOLAR_URL := os.environ.get("SCHOLAR_URL", "https://scholar.google.com/scholar?q=Micha%C5%82+K%C4%85kol+credibility")) else read_content("research")
write("research.html", render(r["title"], r["description"], '<h1>Research Roots</h1>\n' + research_html, "/research.html"))

# CV (hand-authored; links to the public Field Guide; ATS on request)
cv_body = """<h1>Curriculum Vitae</h1>
<p>I keep my CV in the shape of a <em>field guide</em> &mdash; ordered by what is most defensible, not most flattering. A machine sees a resume; a human sees field notes.</p>
<ul>
  <li><strong><a href="/cv/Michal_Kakol_Field_Guide_CV.pdf">Field Guide CV (PDF)</a></strong> &mdash; the readable, human version.</li>
  <li>A plain, single-column <strong>ATS / classic resume</strong> is available on request (it carries a phone number, so it does not live in public). <a href="/contact.html">Ask</a>.</li>
</ul>
<p>The short version: hands-on Data Science manager and AI systems builder. Strongest signal &mdash; experimentation integrity and error-surfacing systems. I lead through technical judgment and work-origination, not headcount. Honest about the ceilings: mid scale, a fair amount of single-operator infrastructure, reactive-strong rather than platform-grade.</p>
<blockquote>Why hire me lives in the CV. Who I am and what I have been thinking about lives on the rest of this site.</blockquote>"""
write("cv.html", render("Curriculum Vitae", "Michał Kąkol — CV (Field Guide edition, PDF). Hands-on Data Science manager and AI systems builder.", cv_body, "/cv.html"))

# CONTACT
contact_body = """<h1>Contact</h1>
<p>The old-fashioned way, which is to say: email.</p>
<ul>
  <li>Email: <a href="mailto:{email}">{email}</a></li>
  <li>Code: <a href="https://github.com/k4k0l">github.com/k4k0l</a></li>
  <li>This site: <a href="/feed.xml">RSS</a> &middot; <a href="{gh}/issues/new?title=hello">guestbook (GitHub issues)</a></li>
</ul>
<p>No contact form, no chat widget, no &ldquo;let&rsquo;s hop on a quick call.&rdquo; If something here was useful or wrong, tell me; both are welcome.</p>
<blockquote>kto ma znalez&#769;c&#769;, ten znajdzie.</blockquote>""".format(email=EMAIL, gh=GH)
write("contact.html", render("Contact", "Contact Michał Kąkol — email, GitHub, RSS.", contact_body, "/contact.html"))

# 404
nf_body = """<h1>404 &mdash; not found</h1>
<p>This page does not exist, or has rotted, or was never written. The web does that.</p>
<p>Try the <a href="/">home page</a>, the <a href="/notes.html">field notes</a>, or press <code>/</code> to jump somewhere.</p>
<p class="small">HTTP 404. The most honest status code there is.</p>"""
write("404.html", render("404", "Page not found.", nf_body, "/404.html"))

# ---------- feed / sitemap / robots / manifest / index.json / favicon ----------
def rfc822(d):
    return format_datetime(datetime.datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc, hour=12))
items = "".join("""    <item>
      <title>{t}</title>
      <link>{u}</link>
      <guid isPermaLink="true">{u}</guid>
      <pubDate>{d}</pubDate>
      <description>{desc}</description>
    </item>
""".format(t=esc(n["title"]), u=DOMAIN + "/notes/" + n["slug"] + ".html", d=rfc822(n["date"]), desc=esc(n["description"])) for n in notes)
feed = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <title>kakol.pro — field notes</title>
  <link>{dom}</link>
  <description>Field notes by Michał Kąkol — systems, experiments, AI, and the return of the home page.</description>
  <language>en</language>
  <lastBuildDate>{lb}</lastBuildDate>
  <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="{dom}/feed.xml" rel="self" type="application/rss+xml"/>
{items}</channel></rss>
""".format(dom=DOMAIN, lb=rfc822(BUILD_DATE), items=items)
write("feed.xml", feed)

urls = ["/", "/projects.html", "/notes.html", "/research.html", "/cv.html", "/contact.html"] + ["/notes/{}.html".format(n["slug"]) for n in notes]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
sm += "".join("  <url><loc>{}{}</loc><lastmod>{}</lastmod></url>\n".format(DOMAIN, u, BUILD_DATE) for u in urls)
sm += "</urlset>\n"
write("sitemap.xml", sm)

write("robots.txt", "User-agent: *\nAllow: /\nSitemap: {}/sitemap.xml\n".format(DOMAIN))

manifest = {"name": "Michał Kąkol — kakol.pro", "short_name": "kakol.pro", "start_url": "/",
            "display": "minimal-ui", "background_color": "#fbfbf4", "theme_color": "#fbfbf4",
            "description": "Home page of Michał Kąkol.", "icons": [{"src": "/favicon.svg", "sizes": "any", "type": "image/svg+xml"}]}
write("manifest.webmanifest", json.dumps(manifest, ensure_ascii=False, indent=2))

# site index for palette + search
idx = [{"title": "Home", "url": "/", "kind": "page"},
       {"title": "Projects", "url": "/projects.html", "kind": "page"},
       {"title": "Field Notes", "url": "/notes.html", "kind": "page"},
       {"title": "Research Roots", "url": "/research.html", "kind": "page"},
       {"title": "Curriculum Vitae", "url": "/cv.html", "kind": "page"},
       {"title": "Contact", "url": "/contact.html", "kind": "page"}]
idx += [{"title": n["title"], "url": "/notes/" + n["slug"] + ".html", "kind": "note"} for n in notes]
write("assets/index.json", json.dumps(idx, ensure_ascii=False))

# favicon — tiny retro terminal "k" cursor
fav = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="4" fill="#0a0a0a"/><text x="6" y="23" font-family="Courier New,monospace" font-size="18" font-weight="bold" fill="#39ff14">k</text><rect x="19" y="9" width="7" height="15" fill="#39ff14"><animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/></rect></svg>'''
write("favicon.svg", fav)

write(".nojekyll", "")
print("built:", len(urls), "urls,", len(notes), "notes; feed/sitemap/robots/manifest/index/favicon ok")
