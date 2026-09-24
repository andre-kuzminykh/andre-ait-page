# -*- coding: utf-8 -*-
"""Механическая проверка разметки слайда лекции 3 (до браузерных сканеров).

    python3 build/l3/lint.py                 # все файлы out/
    python3 build/l3/lint.py out/slide-07.html
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ICONS = set(io.open(os.path.join(HERE, "icons.txt"), encoding="utf-8").read().split())

BANNED = ("workflow", "reasoning", "retrieval", "fallback", "polling", "guardrail",
          "governance", "throughput", "human review", "backlog", "adoption",
          "baseline", "продакшен", "чекпоинт", "снапшот", "промпт",
          "fine-tuning", "human-in-the-loop", "circuit breaker", "data lineage",
          "data steward", "change management", "summarization", "forecast",
          "headcount", "follow-up", "payback", "hard savings", "infrastructure cost",
          "production", "rollout", "rollback", "canary", "shadow", "kill switch",
          "feature flag", "handoff", "routing", "prompt", "tool call", "trace",
          "dashboard", "dataset", "benchmark", "eval", "grader", "drift",
          "latency", "backoff", "retry", "retries", "timeout", "idempotency",
          "checkpoint", "dead-letter", "graceful", "chaos", "observability",
          "logging", "alert", "runbook", "postmortem", "severity", "owner",
          "blast radius", "allowlist", "sandbox", "approval", "audit trail",
          "red teaming", "jailbreak", "provenance", "namespace", "retention",
          "compliance", "fairness", "explainability", "accountability",
          "sign-off", "self-service", "marketplace", "data contract",
          "control plane", "gateway", "orchestrator", "stateful", "stateless",
          "session-only", "edge case", "holdout", "overfitting", "pairwise",
          "bias", "confidence", "escalation", "override", "copilot", "deterministic",
          "toolset", "few-shot", "reasoning-модел", "use case", "throttl",
          "workload", "quota", "budget", "caching", "cache", "jitter", "backpressure",
          "concurrency", "failure mode", "cascading", "arbiter", "registry",
          "capability", "playbook", "incident", "on-call")
# Латиница разрешена ТОЛЬКО из этого списка (правка владельца: «меньше англицизмов,
# только там, где реально нужно»). Всё остальное — по-русски.
ALLOWED_LATIN = set("""
API CRM ERP JSON RAG LLM SLI SLO SLA RTO RPO MTTR ROI NPS CSI KPI IAM ID TTL
A B MLOps DataOps AIOps AgentOps OpenTelemetry GDPR CI CD MCP SQL IT
Streamlit Power BI DataLens
Governance Data
AS IS TO BE GET POST PATCH DELETE OAuth HTTP URL customer email First HR
""".split())
LATIN_WORD = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-/][A-Za-z0-9]+)*")


def latin_words(text):
    """Латинские слова видимого текста, не попавшие в белый список."""
    bad = set()
    for w in LATIN_WORD.findall(text):
        parts = re.split(r"[-/]", w)
        if w == "AI" or w in ("AI-First", "AI-first"):
            continue          # «AI» проверяется отдельно: можно только в «AI Governance»
        if not all(p in ALLOWED_LATIN or p.isdigit() for p in parts):
            bad.add(w)
    return sorted(bad)


def _font_ranges():
    """Диапазоны Unicode, которые покрывает вендорный Montserrat (css2.css)."""
    path = os.path.join(ROOT, "vendor", "fonts", "css2.css")
    if not os.path.isfile(path):
        return None
    out = []
    for block in re.findall(r"@font-face\s*{[^}]*}", io.open(path, encoding="utf-8").read()):
        if "Montserrat" not in block:
            continue
        m = re.search(r"unicode-range:\s*([^;]+);", block)
        for part in (m.group(1).split(",") if m else []):
            part = part.strip().replace("U+", "")
            if "-" in part:
                a, b = part.split("-")
                out.append((int(a, 16), int(b, 16)))
            elif "?" in part:
                out.append((int(part.replace("?", "0"), 16), int(part.replace("?", "F"), 16)))
            else:
                out.append((int(part, 16), int(part, 16)))
    return out


FONT = _font_ranges()

ALLOWED_STYLE = 'style="color:#111;-webkit-text-fill-color:#111"'
SIZE = re.compile(r"^(?:(sm|md|lg|xl|2xl):)?text-(\[[^\]]+\]|xs|sm|base|lg|xl|[2-9]xl)$")


def check(path):
    name = os.path.basename(path)
    html = io.open(path, encoding="utf-8").read()
    bad = []
    add = lambda m: bad.append("%s: %s" % (name, m))

    sid = re.search(r'id="slide-(\d+)"', html)
    if not sid:
        add("нет id слайда"); return bad
    if not html.lstrip().startswith('<div class="slide-container'):
        add("файл не начинается с <div class=\"slide-container\"")
    if html.count('class="slide-container') != 1:
        add("в файле должен быть ровно один слайд")
    if '<div class="content-z' not in html:
        add("нет обёртки content-z")

    # структура заголовка
    if sid.group(1) == "0":
        if html.count("<h1") != 1:
            add("на обложке должен быть ровно один <h1>")
    else:
        if html.count("<h2") != 1:
            add("должен быть ровно один <h2> (сейчас %d)" % html.count("<h2"))
        if html.count("<h1"):
            add("<h1> бывает только на обложке")

    # запреты
    for tag in ("<style", "<script", "<svg", ":has(", "hidden md:", "md:hidden",
                "sr-only", "shadow-", "h-screen", "overflow-auto", "overflow-y-auto"):
        if tag in html:
            add("запрещено: %s" % tag)
    for m in re.finditer(r'style="[^"]*"', html):
        if m.group(0) != ALLOWED_STYLE:
            add("посторонний style=: %s" % m.group(0)[:60])
    if re.search(r"\b\d+vw\b|\b\d+vh\b", html):
        add("размеры в vw/vh запрещены")

    # пробел перед <br>
    for m in re.finditer(r"(.)<br\s*/?>", html):
        if m.group(1) not in " >\n":
            add("нет пробела перед <br>: ...%s" % html[max(0, m.start() - 34):m.end()].strip()[-46:])

    # парность кеглей
    for m in re.finditer(r'class="([^"]*)"', html):
        toks = m.group(1).split()
        base = [t for t in toks if SIZE.match(t) and ":" not in t]
        wide = [t for t in toks if SIZE.match(t) and ":" in t]
        if base and not wide:
            add("кегль без пары для компьютера: %s" % " ".join(base))
        if wide and not base:
            add("кегль без пары для телефона: %s" % " ".join(wide))

    # иконки
    for n in set(re.findall(r"\bph-[a-z0-9-]+", html)):
        if n in ("ph-fill", "ph-bold", "ph-duotone", "ph-light", "ph-thin"):
            continue
        if n not in ICONS:
            add("несуществующая иконка %s" % n)

    # язык
    low = re.sub(r"(ai|data)\s*(<[^>]+>\s*)*governance", "", html.lower())   # термины, которые владелец просил латиницей
    for w in BANNED:
        if w.lower() in low:
            add("англицизм/запрещённое слово: %s" % w)
    text = re.sub(r"<[^>]+>", " ", re.sub(r"<!--.*?-->", " ", html, flags=re.S))
    text = text.replace("&shy;", "").replace("&nbsp;", " ")
    extra = latin_words(text)
    if extra:
        add("латиница вне белого списка: %s" % ", ".join(extra[:8]))
    # символы, которых нет в Montserrat: браузер дорисует их чужим шрифтом (≠, →, ✓)
    if FONT:
        alien = sorted(set(c for c in text if ord(c) > 127 and c not in "\u00ad\u00a0"
                           and not any(a <= ord(c) <= b for a, b in FONT)))
        if alien:
            add("символы вне шрифта Montserrat (заменить иконкой или словом): %s" % " ".join(alien))
    if re.search(r"(?<![A-Za-z])AI(?![A-Za-z])(?! Governance)(?!-[Ff]irst)", text):
        add("в тексте «AI» — должно быть «ИИ»")

    # плотность
    cards = len(re.findall(r'class="[^"]*(?:bg-white|bg-black|bg-grayBase|bg-white/10)[^"]*rounded', html))
    if cards > 18:
        add("слишком много карточек: %d" % cards)
    for m in re.finditer(r">([^<>]{120,})<", text):
        pass
    for m in re.finditer(r"<p[^>]*>([^<]{140,})", html):
        add("слишком длинный текст в абзаце (%d знаков)" % len(m.group(1)))

    # канон владельца: порядковые цифры, жирное в плашках, рубрики-пересказы
    for m in re.finditer(r">\s*(0[1-9]|[1-9]\.)\s*<", html):
        add("порядковая цифра в элементе («%s») — владелец просит убирать" % m.group(1))
    for m in re.finditer(r'<span class="([^"]*)"', html):
        cl = m.group(1)
        if re.search(r"\b(bg-|border\b)", cl) and re.search(r"\bfont-(bold|black|extrabold)\b", cl):
            add("жирный текст в плашке: %s" % cl[:70])
    for m in re.finditer(r'<(p|span)[^>]*class="[^"]*\buppercase\b[^"]*"[^>]*>(.*?)</\1>', html, re.S):
        words = re.sub(r"<[^>]+>", " ", m.group(2)).replace("&shy;", "").split()
        if sid.group(1) != "0" and len(words) > 3:
            add("рубрика-пересказ из %d слов: «%s»" % (len(words), " ".join(words)[:50]))

    # баланс div
    if html.count("<div") != html.count("</div>"):
        add("не сходится число <div>/</div>: %d и %d" % (html.count("<div"), html.count("</div>")))
    return bad


def main():
    files = sys.argv[1:] or sorted(
        os.path.join(HERE, "out", f) for f in os.listdir(os.path.join(HERE, "out"))
        if f.endswith(".html"))
    bad = []
    for f in files:
        bad += check(f)
    if bad:
        print("НАРУШЕНИЯ (%d):" % len(bad))
        for b in bad:
            print("  " + b)
        return 1
    print("чисто: %d файлов" % len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
