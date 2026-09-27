# -*- coding: utf-8 -*-
"""Проверка текста панели «Текст к слайду» лекции 3.

    python3 build/l3/lint_notes.py                      # все файлы notes/
    python3 build/l3/lint_notes.py notes/slide-07.json
"""
import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
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


TYPES = ("p", "h", "ul", "ol", "note", "cards")


def check(path):
    name = os.path.basename(path)
    bad = []
    add = lambda m: bad.append("%s: %s" % (name, m))
    try:
        data = json.load(io.open(path, encoding="utf-8"))
    except Exception as e:
        return ["%s: не разбирается как JSON — %s" % (name, e)]
    if not isinstance(data, dict):
        return ["%s: на верхнем уровне должен быть объект {title, blocks}" % name]
    title = data.get("title", "")
    if not title or len(title) > 64:
        add("заголовок пустой или длиннее 64 знаков")
    blocks = data.get("blocks") or []
    if len(blocks) < 3:
        add("меньше трёх блоков — панель должна разбирать тему, а не дублировать слайд")
    kinds = set()
    for i, b in enumerate(blocks):
        t = b.get("t")
        kinds.add(t)
        if t not in TYPES:
            add("блок %d: неизвестный тип %r" % (i, t)); continue
        v = b.get("v")
        if not v:
            add("блок %d: пустой" % i); continue
        if t == "cards":
            if not isinstance(v, list) or not v:
                add("блок %d: карточки должны быть непустым списком" % i); continue
            for c in v:
                if not re.match(r"^ph-[a-z0-9-]+$", c.get("i", "")):
                    add("блок %d: плохое имя иконки %r" % (i, c.get("i")))
                elif c["i"] not in ICONS:
                    add("блок %d: несуществующая иконка %s" % (i, c["i"]))
                if not c.get("h") or not c.get("p"):
                    add("блок %d: карточка без названия или пояснения" % i)
        elif t in ("ul", "ol"):
            if not isinstance(v, list) or not v:
                add("блок %d: список должен быть непустым" % i)
        else:
            if not isinstance(v, str):
                add("блок %d: значение должно быть строкой" % i)
            elif t == "p" and len(v) > 1400:
                add("блок %d: абзац длиннее 1400 знаков" % i)
    if "p" not in kinds:
        add("нет ни одного обычного абзаца")
    if not ({"cards", "ul", "ol"} & kinds):
        add("нет ни одного перечисления (cards/ul/ol) — канон требует карточек для пунктов")

    blob = json.dumps(data, ensure_ascii=False)
    blob_b = re.sub(r"(AI|Data) Governance", "", blob)   # термины, которые владелец просил латиницей
    for w in BANNED:
        if re.search(re.escape(w), blob_b, re.I):
            add("англицизм: %s" % w)
    plain = re.sub(r"[A-Za-z-]*AI[A-Za-z-]*", lambda m: m.group(0), blob)
    if re.search(r"(?<![A-Za-z])AI(?![A-Za-z])(?! Governance)(?!-[Ff]irst)", blob):
        add("«AI» вместо «ИИ»")
    words = []
    def walk(x, key=None):
        if isinstance(x, dict):
            for k, v in x.items():
                walk(v, k)
        elif isinstance(x, list):
            for v in x:
                walk(v, key)
        elif isinstance(x, str) and key not in ("i", "t"):
            words.append(x)
    walk(data)
    extra = latin_words(re.sub(r"\*\*", "", " ".join(words)))
    if extra:
        add("латиница вне белого списка: %s" % ", ".join(extra[:10]))
    if len(blob) < 900:
        add("текста слишком мало (%d знаков): панель — второй слой лекции" % len(blob))
    return bad


def main():
    files = sys.argv[1:] or sorted(
        os.path.join(HERE, "notes", f) for f in os.listdir(os.path.join(HERE, "notes"))
        if f.endswith(".json"))
    if not files:
        print("нет файлов"); return 1
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
