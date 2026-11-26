# -*- coding: utf-8 -*-
"""Тесты юридических страниц — FR-SITE96 (ред. 26.11), FR-SITE150…152, NFR-SITE114.

Запуск: `python3 tests/test_legal.py` или через pytest. Строковые проверки — без зависимостей;
проверка в браузере (test_render_*) берёт Playwright и Chromium (/opt/pw-browsers/chromium или
CHROMIUM_PATH), нет их — пропускается, а не валит прогон.

FR-SITE150 — политика конфиденциальности по всем продуктам: сайт и сайт партнёров, Andre AI,
             Нейроний, партнёрская программа, бот, платежи, cookie, записи об использовании, сроки.
FR-SITE151 — условия использования по ценовой политике 26.11: бесплатное, стратегия, подписка
             Нейрония с автопродлением, пакеты, услуги консультантов, промокоды, возвраты.
FR-SITE152 — условия партнёрской программы — partners/terms/ (RU и EN); на них ведут подвал
             и форма заявки сайта партнёров.
NFR-SITE114 — три документа одного вида: оглавление, одинаковое строение RU и EN, реквизиты
             только прежние, условия партнёров работают на обоих адресах сайта партнёров.
"""
import html as _h
import os
import re
import sys
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "tools"))

from tools import build_legal as B  # noqa: E402

KINDS = ("privacy", "terms", "partner_terms")
LANGS = ("en", "ru")
FILES = {(k, l): B.PATHS[k][l].strip("/") + "/index.html" for k in KINDS for l in LANGS}


def _read(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def _page(kind, lang):
    return _read(FILES[(kind, lang)])


def _text(kind, lang):
    """Видимый текст страницы одной строкой: без тегов, неразрывные пробелы — обычные."""
    body = _page(kind, lang)
    body = body[body.index("<main>"):body.index("</main>")]
    t = _h.unescape(re.sub(r"<[^>]+>", " ", body)).replace(" ", " ")
    return re.sub(r"\s+", " ", t)


def _has(kind, lang, *phrases):
    t = _text(kind, lang)
    missing = [p for p in phrases if p not in t]
    assert not missing, "%s/%s: нет %s" % (kind, lang, missing)


def _sections(kind, lang):
    """Разделы страницы: id, заголовок и кусок разметки до следующего раздела."""
    body = _page(kind, lang)
    body = body[body.index("<main>"):body.index("</main>")]
    parts = re.split(r'(<h2 id="s\d+">.*?</h2>)', body)
    out = []
    for i in range(1, len(parts), 2):
        m = re.match(r'<h2 id="(s\d+)">(.*?)</h2>', parts[i])
        out.append((m.group(1), _h.unescape(m.group(2)), parts[i + 1]))
    return out


# ── генератор ────────────────────────────────────────────────────────────────

def test_generator_reproduces_every_page_byte_for_byte():
    """FR-SITE96: страницы собирает tools/build_legal.py, файлы в git — ровно сборка; правка текста — только там."""
    before = {rel: _read(rel) for rel in FILES.values()}
    written = B.build()
    assert sorted(written) == sorted(FILES.values()), written
    for rel, txt in before.items():
        assert _read(rel) == txt, rel + ": файл в git расходится с генератором"


def test_build_is_idempotent_and_deterministic():
    """NFR-SITE114: повторная сборка не меняет ни байта; одна и та же страница рисуется одинаково."""
    B.build()
    first = {rel: _read(rel) for rel in FILES.values()}
    B.build()
    assert {rel: _read(rel) for rel in FILES.values()} == first
    for k in KINDS:
        for l in LANGS:
            assert B.render(k, l) == B.render(k, l) == first[FILES[(k, l)]]


# ── строение страниц ─────────────────────────────────────────────────────────

def test_every_page_has_the_common_skeleton():
    """NFR-SITE114: язык, заголовок, дата редакции 26.11, canonical и hreflang, описание, оглавление по разделам,
    подвал со ссылками на два других документа и почтой, язык запоминается в ait_lang."""
    for (k, l), rel in FILES.items():
        page, doc = _page(k, l), B.LEGAL[k][l]
        title = _h.escape(doc["title"])
        assert '<html lang="%s">' % l in page, rel
        assert "<title>%s | Andre AI Technologies</title>" % title in page and "<h1>%s</h1>" % title in page, rel
        assert ("Last updated: November 26, 2026" if l == "en" else "Обновлено: 26 ноября 2026") in page, rel
        assert '<link rel="canonical" href="%s">' % B.CANON[k][l] in page, rel
        for l2 in LANGS:
            assert '<link rel="alternate" hreflang="%s" href="%s">' % (l2, B.CANON[k][l2]) in page, rel
        assert '<meta name="description" content="%s">' % _h.escape(doc["lead"]) in page, rel
        assert "localStorage.setItem('ait_lang', '%s')" % l in page, rel
        assert 'href="#"' not in page and "‑" not in page, rel + ": пустая ссылка или U+2011 (FR-SITE100)"
        secs = _sections(k, l)
        assert [s[0] for s in secs] == ["s%d" % i for i in range(1, len(secs) + 1)], rel
        toc = re.findall(r'<li><a href="#(s\d+)">(.*?)</a></li>', page[page.index('<nav class="toc"'):page.index("</nav>", page.index('<nav class="toc"'))])
        assert [(i, _h.unescape(t)) for i, t in toc] == [(s[0], s[1]) for s in secs], rel + ": оглавление не по разделам"
        assert [s[1] for s in secs] == [t for t, _ in doc["sections"]], rel
        foot = page[page.index('<footer class="foot">'):page.index("</footer>")]
        for other in KINDS:
            name = _h.escape(B.LEGAL[other][l]["title"])
            assert (">%s</a>" % name in foot) == (other != k), (rel, other)
        assert 'href="mailto:admin@andre.technology"' in foot and "2026 © Andre AI Technologies LTD" in foot, rel


def test_both_languages_have_the_same_structure():
    """NFR-SITE114: русская и английская редакции — один документ: те же разделы, подзаголовки, пункты и абзацы,
    в том же порядке; заголовки разделов — на своём языке."""
    cyr = re.compile(u"[А-Яа-яЁё]")
    for k in KINDS:
        en, ru = _sections(k, "en"), _sections(k, "ru")
        assert len(en) == len(ru) and len(en) >= 12, k
        for (i1, t1, b1), (i2, t2, b2) in zip(en, ru):
            assert i1 == i2
            # имя продукта («Andre AI») одно на обоих языках; остальные заголовки — на своём языке
            assert t1 == t2 == "Andre AI" or (cyr.search(t2) and not cyr.search(t1)), (k, t1, t2)
            for tag in ("<h3>", "<li>", "<p>", "<ul>", "<a href="):
                assert b1.count(tag) == b2.count(tag), (k, t1, tag, b1.count(tag), b2.count(tag))
            # ссылки раздела — на те же документы, каждая на своём языке
            l1 = re.findall(r'<a href="([^"]+)"', b1)
            l2 = re.findall(r'<a href="([^"]+)"', b2)
            assert [re.sub(r"/ru/$", "/", h) for h in l2] == l1, (k, t1, l1, l2)


def test_identity_and_contacts_stay_as_they_were():
    """NFR-SITE114: реквизиты — только прежние: Andre AI Technologies LTD и admin@andre.technology. Номеров
    регистрации, адресов и других почт не появляется; применимое право — прежней фразой."""
    for (k, l), rel in FILES.items():
        page = _page(k, l)
        assert set(re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", page)) == {"admin@andre.technology"}, rel
        assert "Andre AI Technologies LTD" in page, rel
        t = _text(k, l).lower()
        for bad in ("company number", "registration number", "reg. no", "registered office", "vat number", "tax id",
                    "инн", "огрн", "кпп", "регистрационный номер", "юридический адрес", "зарегистрирована по адресу"):
            assert bad not in t, (rel, bad)
    _has("terms", "en", "The terms are governed by the law of the country where Andre AI Technologies LTD is registered, "
                        "unless mandatory consumer law of your country provides otherwise.")
    _has("terms", "ru", "К условиям применяется право страны регистрации Andre AI Technologies LTD, если обязательные нормы "
                        "о защите прав потребителей вашей страны не предусматривают иного.")
    _has("partner_terms", "en", "governed by the law of the country where Andre AI Technologies LTD is registered")
    _has("partner_terms", "ru", "применяется право страны регистрации Andre AI Technologies LTD")


def test_links_work_from_the_site_and_from_the_partners_folder():
    """NFR-SITE114, NFR-SITE110: страницы сайта ссылаются на документы путём от корня; условия партнёров —
    только относительными путями внутри partners/ и полными адресами andre.technology, потому что ту же страницу
    отдаёт и partners.andre.technology/terms/ (Caddy: /x → /partners/x). Каждый относительный путь ведёт на
    существующий файл."""
    for k in ("privacy", "terms"):
        for l in LANGS:
            page = _page(k, l)
            other = "terms" if k == "privacy" else "privacy"
            assert '<a href="%s">' % B.PATHS[other][l] in page and '<a href="%s">' % B.PATHS["partner_terms"][l] in page
            assert '<a href="/?lang=%s">' % l in page and 'href="/favicon.ico"' in page
    for l in LANGS:
        rel = FILES[("partner_terms", l)]
        page, here = _page("partner_terms", l), os.path.dirname(os.path.join(_ROOT, rel))
        for url in re.findall(r'\b(?:src|href)="([^"]+)"', page):
            assert not url.startswith("/"), rel + ": путь от корня уйдёт на поддомене в чужую папку: " + url
            if url.startswith(("https://", "mailto:", "#")):
                continue
            target = os.path.normpath(os.path.join(here, url.split("?")[0]))
            assert target.startswith(os.path.join(_ROOT, "partners")), (rel, url, "выходит из partners/")
            assert os.path.exists(target if os.path.isfile(target) else os.path.join(target, "index.html")), (rel, url)
        for k in ("privacy", "terms"):
            assert '<a href="https://andre.technology%s">' % B.PATHS[k][l] in page, (rel, k)
        assert '<a href="%s?lang=%s">' % ("../" if l == "en" else "../../", l) in page
    assert 'data-lang="ru" href="ru/"' in _page("partner_terms", "en") and 'data-lang="en" href="../"' in _page("partner_terms", "ru")


def test_partners_site_links_to_the_partner_terms():
    """FR-SITE152: в подвале сайта партнёров — «Условия партнёрской программы» на языке страницы; у формы заявки
    в партнёры — строка о согласии со ссылками на условия и политику (в новой вкладке — форма не теряется)."""
    from tools import build_partners
    idx, i18n = _read("partners/index.html"), build_partners.read_i18n()
    legal = idx[idx.index('<div class="legal">'):idx.index("</div>", idx.index('<div class="legal">'))]
    assert '<a href="terms/ru/" data-href-ru="terms/ru/" data-href-en="terms/" data-i18n="legal.partner">Условия партнёрской программы</a>' in legal
    assert 'data-href-en="https://andre.technology/privacy/"' in legal and 'data-href-en="https://andre.technology/terms/"' in legal
    assert i18n["en"]["legal.partner"] == "Partner program terms"
    form = idx[idx.index('<form class="lf" id="app-form"'):idx.index("</form>", idx.index('id="app-form"'))]
    note = re.search(r'<p class="m-legal" data-i18n="app.terms">(.*?)</p>', form)
    assert note and form.index("m-legal") < form.index('id="app-btn"'), "строка об условиях — перед кнопкой заявки"
    for txt, terms, privacy in ((note.group(1), "terms/ru/", "https://andre.technology/privacy/ru/"),
                                (i18n["en"]["app.terms"], "terms/", "https://andre.technology/privacy/")):
        links = re.findall(r'<a href="([^"]+)" data-href-ru="([^"]+)" data-href-en="([^"]+)" target="_blank" rel="noopener">', txt)
        assert [l[0] for l in links] == [terms, privacy], txt
        assert links[0][1:] == ("terms/ru/", "terms/") and links[1][1:] == ("https://andre.technology/privacy/ru/", "https://andre.technology/privacy/")
    assert "условия партнёрской программы" in note.group(1) and "partner program terms" in i18n["en"]["app.terms"]
    assert ".m-legal {" in _read("partners/partners.css")
    build_partners.build(check=True)   # метки версий partners.css/js свежие — иначе SystemExit «запустите build_partners.py»


# ── содержание ───────────────────────────────────────────────────────────────

def test_privacy_covers_every_product():
    """FR-SITE150: политика — про все продукты и потоки данных, без умолчаний."""
    _has("privacy", "en",
         "andre.technology", "partners.andre.technology", "maturity.andre.technology", "strategy.andre.technology",
         "company .neuronium.ai", "Telegram bot",
         # сайт: формы, кнопки пакетов, хранилище браузера, без cookie и аналитики
         "FormSubmit", "promo code and profile name", "localStorage", "set no cookies, run no analytics",
         # Andre AI: вход по коду, голос и расшифровка, данные компании и схемы, ИИ
         "Sign-in codes", "valid for 10 minutes", "voice recording", "delete the recording once it has been recognised",
         "kept on our server for 14 days", "process schemas “as is” and “to be”", "OpenAI and Anthropic",
         "do not use it to train AI models", "calculated by fixed rules, not by an AI model",
         # платежи
         "Stripe", "We do not see or store full card numbers", "Tochka Bank",
         # Нейроний: пространство, Google Workspace по OAuth с выбранным доступом, учёт расхода, свой ключ
         "Google Workspace through Google sign-in (OAuth)", "choose which access to grant",
         "myaccount.google.com/permissions", "Limited Use", "against the model budget", "own model API key",
         # партнёры: заявка, профиль с согласия, заявки клиентов, отзывы
         "LinkedIn profile", "the rate you propose", "only after you turn on “show in catalog”",
         "name, email, company and message", "rate it from 1 to 5",
         # получатели, перенос, права
         "We do not sell personal data", "United States", "standard contractual clauses", "within 30 days",
         "data protection authority", "under 16")
    _has("privacy", "ru",
         "partners.andre.technology", "maturity.andre.technology", "strategy.andre.technology", "компания .neuronium.ai",
         "Telegram-бот", "FormSubmit", "не ставят cookie, не подключают аналитику", "Коды входа", "действует 10 минут",
         "удаляем сразу после распознавания", "14 дней хранится на нашем сервере", "схемы процессов «как есть» и «как будет»",
         "OpenAI и Anthropic", "не обучаем на них ИИ-модели", "Stripe", "Полные номера карт мы не видим и не храним",
         "Точка Банка", "Google Workspace через вход Google (OAuth)", "сама выбрать, какой доступ дать",
         "Limited Use", "в бюджете модели", "свой ключ API модели", "профиль LinkedIn", "предложенная ставка",
         "только после того, как вы включите «Показывать в каталоге»", "имя, email, компанию и сообщение",
         "оценку от 1 до 5", "Мы не продаём персональные данные", "США", "в течение 30 дней", "младше 16 лет")


def test_privacy_says_plainly_what_usage_records_hold():
    """FR-SITE150 (владелец: «скажи прямо»): продукт пишет клики, паузы между клавишами, итоговый текст полей,
    ошибки, IP и вызовы ИИ целиком; секретные поля — без текста; хранение 180 дней; cookie у продукта — одна."""
    _has("privacy", "en", "every click", "the pauses between keystrokes", "the final text of the field",
         "we record only length and timing, never the text", "browser errors and network failures", "IP address",
         "each call to an AI model in full", "no third-party analytics", "180 days, then they are deleted automatically",
         "one cookie, amx_lang", "for a year")
    _has("privacy", "ru", "каждое нажатие", "паузы между нажатиями клавиш", "итоговый текст поля",
         "записываются только длина и время, текст — никогда", "ошибки браузера и сбои сети", "IP-адрес",
         "каждый вызов ИИ-модели целиком", "сторонняя аналитика не подключена", "180 дней, затем они удаляются автоматически",
         "одну cookie — amx_lang", "на год")


def test_terms_follow_the_pricing_policy():
    """FR-SITE151: условия — по ценовой политике 26.11 и тому, что делает продукт (журнал заказов, Stripe, Нейроний)."""
    _has("terms", "en",
         "interview and schema of the first business process in Andre AI are free",
         "AI Strategy — a one-time purchase", "renews automatically for the same period", "monthly or yearly",
         "You can cancel at any time", "Cancellation takes effect at the end of the paid period",
         "budget for AI model calls", "At 80% we warn you", "connect your own model API key",
         "3 days after the end of the paid period the workspace becomes read-only",
         "10 schemas an hour", "12 weekly 60-minute sessions", "team of 10 people",
         "they are not a loan or credit, carry no interest or fees", "250 or more employees",
         "“AI Platform” — the strategy and the first month of Neuronium", "from the fourth month",
         "10% off the AI Strategy and the first paid month of Neuronium", "One code applies to an order",
         "divided by 0.70", "70% goes to the consultant",
         "Within 14 days of payment", "Refunds are made to the original payment method",
         "we refund the rest", "If the whole payment is disputed, the order is treated as unpaid",
         "keep all rights to the data you add", "produced by AI models and may be inaccurate",
         "Our total liability for any claim is limited to the amount you paid",
         "Prices are shown without VAT or other taxes", "we do not store card details")
    _has("terms", "ru",
         "интервью и схема первого бизнес-процесса в Andre AI бесплатны", "ИИ-стратегия — разовая покупка",
         "продлевается автоматически на тот же срок", "помесячно или за год", "Отменить подписку можно в любой момент",
         "Отмена вступает в силу в конце оплаченного периода", "бюджет на вызовы ИИ-моделей", "На 80 % мы предупреждаем",
         "подключить свой ключ API модели", "через 3 дня после конца оплаченного периода пространство переходит в режим чтения",
         "10 схем в час", "12 еженедельных занятий по 60 минут", "команду из 10 человек",
         "это не заём и не кредит, без процентов и комиссий", "от 250 сотрудников",
         "скидку 10 % на ИИ-стратегию и первый оплаченный месяц Нейрония", "К заказу применяется один код",
         "разделённая на 0,70", "70 % получает консультант", "В течение 14 дней после оплаты",
         "Деньги возвращаются тем же способом, которым вы платили", "мы возвращаем остальное",
         "Если оспорен весь платёж, заказ считается неоплаченным", "остаются у вас и вашей компании",
         "создают ИИ-модели, и они могут быть неточными", "Цены указаны без НДС и других налогов")


def test_partner_terms_cover_the_program():
    """FR-SITE152: ступени (экзамен проверяют вручную), ставка от $50, 70 % услуги, 10 % с цены после скидки только
    с оплаченного и не возвращённого, выплаты раз в месяц вручную по реквизитам партнёра, налоги, поведение,
    профиль — с согласия, окончание."""
    _has("partner_terms", "en",
         "Application.", "Academy.", "Certificate.", "Interview.", "Partner.", "checks it manually",
         "from $50 an hour", "A new rate applies to new orders", "You receive 70% of that price",
         "10% of what the client actually paid for these items after the discount",
         "a $500 strategy costs the client $450 with your code, and you receive $45",
         "only on amounts that have been paid and not refunded", "the first paid month of Neuronium",
         "once a month, to the payment details you provide", "Payouts are made manually",
         "You pay your own taxes", "You are responsible for the quality of your services",
         "only after you turn on “show in catalog”", "You can turn it off at any time",
         "You may leave the program at any time", "your promo code is disabled",
         "not our employee or representative", "Changes do not affect orders already paid")
    _has("partner_terms", "ru",
         "Заявка.", "Академия.", "Сертификат.", "Собеседование.", "Партнёр.", "проверяет его вручную",
         "от $50 в час", "Новая ставка действует для новых заказов", "Вы получаете 70 % этой цены",
         "10 % от суммы, которую клиент фактически заплатил за эти позиции после скидки",
         "стратегия за $500 с вашим кодом стоит клиенту $450, вы получаете $45",
         "только на оплаченные и не возвращённые суммы", "раз в месяц, по реквизитам, которые вы указали",
         "Выплаты делаются вручную", "Налоги, регистрацию и взносы в своей стране вы платите сами",
         "За качество своих услуг и поведение с клиентами отвечаете вы",
         "только после того, как вы включите «Показывать в каталоге»", "Выключить показ можно в любой момент",
         "Выйти из программы можно в любой момент", "промокод отключается", "не наш сотрудник и не представитель",
         "Изменения не затрагивают уже оплаченные заказы")


def test_spec_lists_the_requirements_and_their_tests():
    """Трассировка: у FR-SITE150…152 и NFR-SITE114 — раздел в спеке, а каждый названный там тест есть."""
    spec = _read("SPEC-SITE.md")
    sec = spec[spec.index("## Юридические страницы 26.11"):]
    for rid in ("FR-SITE150", "FR-SITE151", "FR-SITE152", "NFR-SITE114"):
        assert "### %s — " % rid in sec, rid
    named = set(re.findall(r"test_legal\.(test_\w+)", sec))
    assert len(named) >= 8
    missing = sorted(t for t in named if t not in globals())
    assert not missing, "в спеке названы тесты, которых нет: %s" % missing
    assert "tools/build_legal.py" in _read("AGENTS.md") and "partners/terms/" in _read("AGENTS.md")


# ── в браузере ───────────────────────────────────────────────────────────────

class Skip(Exception):
    pass


def _skip(msg):
    try:
        import pytest
        pytest.skip(msg)
    except ImportError:
        raise Skip(msg)


def test_render_pages_on_both_addresses_without_errors():
    """NFR-SITE114: шесть страниц на компьютере и телефоне — без прокрутки вбок и ошибок, значки отдаются,
    оглавление ведёт на разделы, переключатель языка — на ту же страницу другого языка; условия партнёров —
    и как andre.technology/partners/terms/, и как partners.andre.technology/terms/; сайт партнёров ведёт на них
    из подвала и из формы заявки (tools/legal_check.py)."""
    try:
        import playwright.sync_api  # noqa: F401
    except ImportError:
        _skip("нет Playwright")
    import legal_check as L
    import partners_check as C
    if not os.path.exists(C.CHROMIUM):
        _skip("нет Chromium: " + C.CHROMIUM)
    base, base2, _, _, stop = C.servers()
    browser = C.launch(C.playwright())
    problems = []
    try:
        L.run(browser, base, base2, problems)
    finally:
        browser.close()
        stop()
    assert not problems, "\n".join(problems)


if __name__ == "__main__":
    failed = skipped = 0
    t0 = time.time()
    for name, fn in sorted(globals().items(), key=lambda kv: (kv[0].startswith("test_render"), kv[0])):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok   %s" % name)
            except Skip as e:
                skipped += 1
                print("skip %s: %s" % (name, e))
            except Exception as e:  # AssertionError и любые сбои
                failed += 1
                print("FAIL %s: %s: %s" % (name, type(e).__name__, e))
    print("\nЮридические страницы: %s, пропущено %d, %.0f с" % ("ПРОВАЛОВ %d" % failed if failed else "все тесты пройдены", skipped, time.time() - t0))
    raise SystemExit(1 if failed else 0)
