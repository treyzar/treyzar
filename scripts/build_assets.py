"""Генерирует SVG-ассеты профиля (тёмная и светлая темы) в папку assets/.

Запуск: python scripts/build_assets.py
Чтобы поменять текст карточек или стек — правьте PROJECTS / STACK ниже.
"""

import re
from pathlib import Path
from xml.sax.saxutils import escape

ASSETS = Path(__file__).resolve().parent.parent / "assets"
# Иконки: icons/si — Simple Icons (CC0), icons/lu — Lucide (ISC).
ICONS = Path(__file__).resolve().parent / "icons"

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "card": "#161b22",
        "border": "#30363d",
        "text": "#e6edf3",
        "muted": "#8b949e",
        "accent": "#e3b341",
        "chip": "#21262d",
        "line": "#3d444d",
    },
    "light": {
        "bg": "#ffffff",
        "card": "#f6f8fa",
        "border": "#d0d7de",
        "text": "#1f2328",
        "muted": "#59636e",
        "accent": "#9a6700",
        "chip": "#ffffff",
        "line": "#c8d1da",
    },
}

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"
MONO_CHAR = 0.6  # ширина символа моноширинного шрифта в em

PROJECTS = [
    {
        "slug": "smip-platform",
        "label": "КОММЕРЧЕСКИЙ · BACKEND",
        "title": "SMIP Platform",
        "link": "smip.site",
        "live": True,
        "lines": [
            "SaaS-аналитика для контент-команд.",
            "REST API, JWT с ротацией refresh-сессий,",
            "парсинг соцсетей через RabbitMQ, outbox и DLQ.",
        ],
        "chips": ["FastAPI", "PostgreSQL", "ClickHouse", "RabbitMQ"],
    },
    {
        "slug": "smip-bot",
        "label": "КОММЕРЧЕСКИЙ · BOT + ADMIN",
        "title": "SMIP Bot & Admin",
        "link": "smip.site",
        "live": True,
        "lines": [
            "Telegram-бот и админка для работы с блогерами:",
            "KPI-планы, статистика, отчёты,",
            "автоматические и ручные push-уведомления.",
        ],
        "chips": ["aiogram 3", "Django", "SQLAlchemy async", "Celery"],
    },
    {
        "slug": "bresler",
        "label": "КОММЕРЧЕСКИЙ · WEB",
        "title": "bresler.ru",
        "link": "bresler.ru",
        "live": True,
        "lines": [
            "Перенос корпоративного сайта на новый стек:",
            "API каталога, новостей, поиска и форм,",
            "фоновые задачи, Docker-окружение для прода.",
        ],
        "chips": ["Django 5.2", "Django Ninja", "Celery", "PostgreSQL", "Redis"],
    },
    {
        "slug": "bank-widget",
        "label": "УЧЕБНЫЙ · PYTHON",
        "title": "Bank Widget",
        "link": "GitHub",
        "lines": [
            "Обработка банковских операций: маски карт,",
            "фильтры и поиск, чтение CSV/Excel,",
            "конвертация валют через API, логирование.",
        ],
        "chips": ["Python 3.12", "pandas", "requests", "pytest", "Poetry"],
    },
]

STACK = [
    ("Язык", ["Python 3.12", "typing", "asyncio"]),
    ("Web / API", ["FastAPI", "Django", "Django Ninja", "DRF", "Pydantic"]),
    ("Боты", ["aiogram 3"]),
    ("Данные", ["PostgreSQL", "ClickHouse", "Redis", "SQLAlchemy 2", "Alembic"]),
    ("Очереди", ["RabbitMQ", "Celery", "outbox", "DLQ"]),
    ("Качество", ["pytest", "ruff", "mypy", "CI"]),
    ("Инфра", ["Docker Compose", "Nginx", "Linux"]),
]

# Иконка для каждой группы и технологии: "si/<slug>" или "lu/<slug>".
GROUP_ICONS = {
    "Язык": "lu/code-xml", "Web / API": "lu/globe", "Боты": "lu/bot", "Данные": "lu/database",
    "Очереди": "lu/workflow", "Качество": "lu/shield-check", "Инфра": "lu/server",
}
TECH_ICONS = {
    "Python 3.12": "si/python", "typing": "lu/type", "asyncio": "lu/zap",
    "FastAPI": "si/fastapi", "Django": "si/django", "Django Ninja": "si/django", "DRF": "si/django",
    "Pydantic": "si/pydantic", "aiogram 3": "si/telegram",
    "PostgreSQL": "si/postgresql", "ClickHouse": "si/clickhouse", "Redis": "si/redis",
    "SQLAlchemy 2": "si/sqlalchemy", "Alembic": "lu/layers",
    "RabbitMQ": "si/rabbitmq", "Celery": "si/celery", "outbox": "lu/inbox", "DLQ": "lu/rotate-ccw",
    "pytest": "si/pytest", "ruff": "si/ruff", "mypy": "lu/shield-check", "CI": "si/githubactions",
    "Docker Compose": "si/docker", "Nginx": "si/nginx", "Linux": "si/linux",
}

ABOUT = {
    "title": "Бэкенд, который доходит до прода",
    "lines": [
        "Python-разработчик. Делаю бэкенд коммерческих продуктов:",
        "REST API, Telegram-боты, фоновые задачи и аналитику.",
        "Проектирую схему данных и API-контракты, пишу тесты",
        "и довожу сервисы до продакшна в Docker.",
    ],
    "facts": [
        ("lu/briefcase", "ArtInTech · SMIP"),
        ("lu/map-pin", "Чебоксары"),
        ("lu/server", "Python backend"),
        ("lu/zap", "3 коммерческих проекта"),
    ],
}

CONTACTS = [  # (файл, иконка, подпись)
    ("telegram", "si/telegram", "Telegram"),
    ("email", "lu/mail", "Email"),
    ("site", "lu/globe", "bresler.ru"),
]


# Анимации живут внутри SVG: GitHub проигрывает их и в <img>.
# При prefers-reduced-motion всё замирает.
CSS = """
.ring{transform-box:fill-box;transform-origin:center;animation:ring 2.2s ease-out infinite}
.ring.d{animation-delay:1.1s}
@keyframes ring{0%{transform:scale(1);opacity:.85}100%{transform:scale(3.2);opacity:0}}
.flow{stroke-dasharray:6 7;animation:flow 1.1s linear infinite}
@keyframes flow{to{stroke-dashoffset:-13}}
.packet{offset-rotate:0deg;opacity:0;animation:move var(--dur,2.6s) cubic-bezier(.5,0,.5,1) infinite;animation-delay:var(--delay,0s)}
@keyframes move{0%{offset-distance:0%;opacity:0}12%{opacity:1}88%{opacity:1}100%{offset-distance:100%;opacity:0}}
.halo{animation:halo 2.6s ease-in-out infinite}
@keyframes halo{0%,100%{opacity:.15}50%{opacity:.6}}
.cursor{animation:blink 1.1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
.shine{animation:shine 3.6s ease-in-out infinite}
@keyframes shine{0%{transform:translateY(-120px);opacity:0}20%{opacity:1}80%{opacity:1}100%{transform:translateY(320px);opacity:0}}
.in{opacity:0;animation:in .6s ease-out forwards;animation-delay:var(--delay,0s)}
@keyframes in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.in{opacity:1}.packet{opacity:0}}
"""


def svg(width: int, height: int, body: str, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">'
        f"<title>{escape(title)}</title><style>{CSS}</style>{body}</svg>\n"
    )


def pulse(cx, cy, color, r=6) -> str:
    """Точка «в работе» с расходящимися кольцами."""
    return (
        f'<circle class="ring" cx="{cx:.0f}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="2"/>'
        f'<circle class="ring d" cx="{cx:.0f}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="2"/>'
        f'<circle cx="{cx:.0f}" cy="{cy}" r="{r}" fill="{color}"/>'
    )


def packet(path, color, dur=2.6, delay=0.0) -> str:
    """Бегущий по стрелке «пакет данных»."""
    return (
        f'<circle class="packet" r="4.5" fill="{color}" '
        f"style=\"offset-path:path('{path}');--dur:{dur}s;--delay:{delay}s\"/>"
    )


def text(x, y, s, size, fill, font=SANS, weight=400, anchor="start", spacing=0) -> str:
    extra = f' letter-spacing="{spacing}"' if spacing else ""
    return (
        f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'
    )


def chips(x, y, items, t, size=15, gap=10, max_x=None, with_icons=True) -> tuple[str, float]:
    """Рисует ряд «чипов» и переносит их на новую строку при выходе за max_x."""
    out, cx, cy, h = [], x, y, size + 16
    for item in items:
        ic = TECH_ICONS.get(item) if with_icons else None
        isz = size + 1
        w = len(item) * size * MONO_CHAR + 24 + (isz + 8 if ic else 0)
        if max_x and cx + w > max_x:
            cx, cy = x, cy + h + gap
        out.append(
            f'<rect x="{cx:.0f}" y="{cy}" width="{w:.0f}" height="{h}" rx="6" '
            f'fill="{t["chip"]}" stroke="{t["border"]}"/>'
        )
        tx = cx + 12
        if ic:
            out.append(icon(ic, tx, cy + (h - isz) / 2, isz, t["muted"]))
            tx += isz + 8
        out.append(text(tx, cy + h / 2 + size * 0.35, item, size, t["text"], MONO))
        cx += w + gap
    return "".join(out), cy + h


def icon(name: str, x, y, size, color) -> str:
    """Встраивает иконку 24×24: Simple Icons заливкой, Lucide — обводкой."""
    src = (ICONS / f"{name}.svg").read_text(encoding="utf-8")
    inner = re.search(r"<svg[^>]*>(.*)</svg>", src, re.S).group(1)
    inner = re.sub(r"<title>.*?</title>", "", inner).strip()
    paint = (
        f'fill="{color}"'
        if name.startswith("si/")
        else f'fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    )
    return f'<svg x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}" viewBox="0 0 24 24" {paint}>{inner}</svg>'


def header(t) -> str:
    w, h = 1200, 320
    b = [f'<rect width="{w}" height="{h}" rx="16" fill="{t["card"]}" stroke="{t["border"]}"/>']
    b.append(text(56, 76, "~/treyzar", 20, t["muted"], MONO))
    b.append(f'<rect class="cursor" x="{56 + 9 * 20 * MONO_CHAR + 6:.0f}" y="60" width="11" height="21" fill="{t["accent"]}"/>')
    b.append(text(56, 150, "Ivan · treyzar", 64, t["text"], weight=700))
    b.append(f'<rect x="56" y="176" width="56" height="4" rx="2" fill="{t["accent"]}"/>')
    b.append(text(56, 222, "Python Backend Developer", 30, t["accent"], weight=600))
    b.append(text(56, 264, "API · Telegram-боты · очереди · аналитика", 22, t["muted"]))

    # Мини-схема: то, из чего обычно состоят мои сервисы.
    def node(x, y, label, accent=False):
        bw = len(label) * 17 * MONO_CHAR + 32
        stroke = t["accent"] if accent else t["border"]
        return (
            f'<rect x="{x}" y="{y}" width="{bw:.0f}" height="44" rx="8" fill="{t["bg"]}" stroke="{stroke}" stroke-width="1.5"/>'
            + text(x + bw / 2, y + 28, label, 17, t["text"], MONO, anchor="middle")
        ), x + bw

    arrow = t["line"]
    b.append(
        f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
        f'<path d="M0 0L10 5L0 10z" fill="{arrow}"/></marker></defs>'
    )
    api, api_r = node(700, 70, "FastAPI", accent=True)
    b.append(
        f'<rect class="halo" x="694" y="64" width="{api_r - 700 + 12:.0f}" height="56" rx="12" '
        f'fill="none" stroke="{t["accent"]}" stroke-width="3"/>'
    )
    mq, mq_r = node(api_r + 56, 70, "RabbitMQ")
    pg, pg_r = node(700, 196, "PostgreSQL")
    worker, worker_r = node(pg_r + 36, 196, "worker")
    ch, _ = node(worker_r + 40, 196, "ClickHouse")
    b += [api, mq, worker, pg, ch]
    line = f'class="flow" stroke="{arrow}" stroke-width="1.5" fill="none" marker-end="url(#a)"'
    paths = [  # (путь, длительность, задержка) — пакеты идут по цепочке
        (f"M{api_r + 4:.0f} 92H{api_r + 52:.0f}", 1.6, 0.0),
        ("M740 118V192", 1.8, 0.9),
        (f"M{mq_r - 40:.0f} 118V156H{(pg_r + 36 + worker_r) / 2:.0f}V192", 2.2, 1.4),
        (f"M{worker_r + 4:.0f} 218H{worker_r + 36:.0f}", 1.4, 2.6),
    ]
    for d, dur, delay in paths:
        b.append(f'<path d="{d}" {line}/>')
        b.append(packet(d, t["accent"], dur, delay))
    place = "Чебоксары · ArtInTech"
    b.append(pulse(1144 - len(place) * 17 * MONO_CHAR - 18, 284, t["accent"], r=5))
    b.append(text(1144, 290, place, 17, t["muted"], MONO, anchor="end"))
    return svg(w, h, "".join(b), "Ivan · treyzar — Python Backend Developer")


def card(p, t) -> str:
    w, h = 600, 300
    b = [f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="{t["card"]}" stroke="{t["border"]}" stroke-width="1.5"/>']
    b.append(f'<rect x="1" y="1" width="6" height="{h - 2}" rx="3" fill="{t["accent"]}"/>')
    b.append(f'<clipPath id="bar"><rect x="1" y="1" width="6" height="{h - 2}" rx="3"/></clipPath>')
    b.append(f'<g clip-path="url(#bar)"><rect class="shine" x="1" y="0" width="6" height="90" fill="{t["text"]}" opacity=".6"/></g>')
    b.append(text(36, 50, p["label"], 15, t["accent"], MONO, weight=600, spacing=1))
    if p.get("link"):
        label = p["link"] + " ↗"
        b.append(text(w - 32, 50, label, 15, t["muted"], MONO, anchor="end"))
        if p.get("live"):
            b.append(pulse(w - 32 - len(label) * 15 * MONO_CHAR - 14, 45, t["accent"], r=4.5))
    b.append(text(36, 98, p["title"], 34, t["text"], weight=700))
    for i, line in enumerate(p["lines"]):
        b.append(text(36, 140 + i * 28, line, 19, t["muted"]))
    row, _ = chips(36, 236, p["chips"], t, size=14, gap=8, max_x=w - 24, with_icons=False)
    b.append(row)
    return svg(w, h, "".join(b), f'{p["title"]}: {" ".join(p["lines"])}')


def stack(t) -> str:
    w = 1200
    row_h, top = 58, 40
    h = top * 2 + row_h * len(STACK) - 14
    b = [f'<rect width="{w}" height="{h}" rx="16" fill="{t["card"]}" stroke="{t["border"]}"/>']
    for i, (group, items) in enumerate(STACK):
        y = top + i * row_h
        row, _ = chips(260, y, items, t, size=17, gap=12)
        b.append(f'<g class="in" style="--delay:{i * 0.12:.2f}s">')
        b.append(icon(GROUP_ICONS[group], 56, y + 7, 22, t["accent"]))
        b.append(text(92, y + 28, group, 18, t["muted"], MONO))
        b.append(row + "</g>")
    return svg(w, h, "".join(b), "Стек: " + "; ".join(f"{g}: {', '.join(i)}" for g, i in STACK))


def about(t) -> str:
    w, h = 1200, 330
    b = [f'<rect width="{w}" height="{h}" rx="16" fill="{t["card"]}" stroke="{t["border"]}"/>']
    b.append(text(56, 64, "ОБО МНЕ", 16, t["accent"], MONO, weight=600, spacing=2))
    b.append(text(56, 116, ABOUT["title"], 36, t["text"], weight=700))
    for i, line in enumerate(ABOUT["lines"]):
        b.append(text(56, 170 + i * 34, line, 21, t["muted"]))
    # Правая колонка с фактами, отделённая линией.
    b.append(f'<path d="M800 48V{h - 48}" stroke="{t["border"]}" stroke-width="1.5"/>')
    for i, (ic, label) in enumerate(ABOUT["facts"]):
        y = 74 + i * 58
        b.append(f'<g class="in" style="--delay:{0.1 + i * 0.12:.2f}s">')
        b.append(f'<rect x="840" y="{y - 6}" width="44" height="44" rx="10" fill="{t["bg"]}" stroke="{t["border"]}"/>')
        b.append(icon(ic, 851, y + 5, 22, t["accent"]))
        b.append(text(904, y + 23, label, 20, t["text"]) + "</g>")
    return svg(w, h, "".join(b), "Обо мне: " + " ".join(ABOUT["lines"]))


def contact(ic, label, t) -> str:
    w, h = 40 + 26 + len(label) * 17 * MONO_CHAR + 28, 52
    b = [f'<rect x="1" y="1" width="{w - 2:.0f}" height="{h - 2}" rx="10" fill="{t["card"]}" stroke="{t["border"]}" stroke-width="1.5"/>']
    b.append(icon(ic, 20, 15, 22, t["accent"]))
    b.append(text(56, 32, label, 17, t["text"], MONO))
    return svg(round(w), h, "".join(b), label)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        (ASSETS / f"header-{name}.svg").write_text(header(t), encoding="utf-8")
        (ASSETS / f"stack-{name}.svg").write_text(stack(t), encoding="utf-8")
        (ASSETS / f"about-{name}.svg").write_text(about(t), encoding="utf-8")
        for slug, ic, label in CONTACTS:
            (ASSETS / f"contact-{slug}-{name}.svg").write_text(contact(ic, label, t), encoding="utf-8")
        for p in PROJECTS:
            (ASSETS / f'project-{p["slug"]}-{name}.svg').write_text(card(p, t), encoding="utf-8")
    print("assets written to", ASSETS)


if __name__ == "__main__":
    main()
