"""Генерирует SVG-ассеты профиля (тёмная и светлая темы) в папку assets/.

Запуск: python scripts/build_assets.py
Чтобы поменять текст карточек или стек — правьте PROJECTS / STACK ниже.
"""

from pathlib import Path
from xml.sax.saxutils import escape

ASSETS = Path(__file__).resolve().parent.parent / "assets"

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


def svg(width: int, height: int, body: str, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">'
        f"<title>{escape(title)}</title>{body}</svg>\n"
    )


def text(x, y, s, size, fill, font=SANS, weight=400, anchor="start", spacing=0) -> str:
    extra = f' letter-spacing="{spacing}"' if spacing else ""
    return (
        f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'
    )


def chips(x, y, items, t, size=15, gap=10, max_x=None) -> tuple[str, float]:
    """Рисует ряд «чипов» и переносит их на новую строку при выходе за max_x."""
    out, cx, cy, h = [], x, y, size + 16
    for item in items:
        w = len(item) * size * MONO_CHAR + 24
        if max_x and cx + w > max_x:
            cx, cy = x, cy + h + gap
        out.append(
            f'<rect x="{cx}" y="{cy}" width="{w:.0f}" height="{h}" rx="6" '
            f'fill="{t["chip"]}" stroke="{t["border"]}"/>'
        )
        out.append(text(cx + 12, cy + h / 2 + size * 0.35, item, size, t["text"], MONO))
        cx += w + gap
    return "".join(out), cy + h


def header(t) -> str:
    w, h = 1200, 320
    b = [f'<rect width="{w}" height="{h}" rx="16" fill="{t["card"]}" stroke="{t["border"]}"/>']
    b.append(text(56, 76, "~/treyzar", 20, t["muted"], MONO))
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
    mq, mq_r = node(api_r + 56, 70, "RabbitMQ")
    pg, pg_r = node(700, 196, "PostgreSQL")
    worker, worker_r = node(pg_r + 36, 196, "worker")
    ch, _ = node(worker_r + 40, 196, "ClickHouse")
    b += [api, mq, worker, pg, ch]
    line = f'stroke="{arrow}" stroke-width="1.5" fill="none" marker-end="url(#a)"'
    b.append(f'<path d="M{api_r + 4} 92H{api_r + 52}" {line}/>')
    b.append(f'<path d="M740 118V192" {line}/>')
    b.append(f'<path d="M{mq_r - 40} 118V156H{(pg_r + 36 + worker_r) / 2:.0f}V192" {line}/>')
    b.append(f'<path d="M{worker_r + 4} 218H{worker_r + 36}" {line}/>')
    b.append(text(1144, 290, "Чебоксары · BRESLER", 17, t["muted"], MONO, anchor="end"))
    return svg(w, h, "".join(b), "Ivan · treyzar — Python Backend Developer")


def card(p, t) -> str:
    w, h = 600, 300
    b = [f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="{t["card"]}" stroke="{t["border"]}" stroke-width="1.5"/>']
    b.append(f'<rect x="1" y="1" width="6" height="{h - 2}" rx="3" fill="{t["accent"]}"/>')
    b.append(text(36, 50, p["label"], 15, t["accent"], MONO, weight=600, spacing=1))
    b.append(text(36, 98, p["title"], 34, t["text"], weight=700))
    for i, line in enumerate(p["lines"]):
        b.append(text(36, 140 + i * 28, line, 19, t["muted"]))
    row, _ = chips(36, 236, p["chips"], t, size=14, gap=8, max_x=w - 24)
    b.append(row)
    return svg(w, h, "".join(b), f'{p["title"]}: {" ".join(p["lines"])}')


def stack(t) -> str:
    w = 1200
    row_h, top = 58, 40
    h = top * 2 + row_h * len(STACK) - 14
    b = [f'<rect width="{w}" height="{h}" rx="16" fill="{t["card"]}" stroke="{t["border"]}"/>']
    for i, (group, items) in enumerate(STACK):
        y = top + i * row_h
        b.append(text(56, y + 28, group, 18, t["muted"], MONO))
        row, _ = chips(240, y, items, t, size=17, gap=12)
        b.append(row)
    return svg(w, h, "".join(b), "Стек: " + "; ".join(f"{g}: {', '.join(i)}" for g, i in STACK))


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        (ASSETS / f"header-{name}.svg").write_text(header(t), encoding="utf-8")
        (ASSETS / f"stack-{name}.svg").write_text(stack(t), encoding="utf-8")
        for p in PROJECTS:
            (ASSETS / f'project-{p["slug"]}-{name}.svg').write_text(card(p, t), encoding="utf-8")
    print("assets written to", ASSETS)


if __name__ == "__main__":
    main()
