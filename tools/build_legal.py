# -*- coding: utf-8 -*-
"""Собирает юридические страницы сайта на двух языках (FR-SITE96).

    python3 tools/build_legal.py   # пишет privacy/, privacy/ru/, terms/, terms/ru/

Ссылки «Политика конфиденциальности» и «Условия использования» в подвале
главной вели в никуда (#). Теперь у каждой своя страница: короткая, читаемая,
в фирменных цветах и шрифте главной. Язык страницы запоминается в ait_lang —
тот же ключ, что у главной, биографии и курса.

Тексты — здесь же, в LEGAL. Правишь текст — пересобираешь страницы этим
скриптом и прогоняешь tests/test_site.py.
"""
import html
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://andre.technology"
UPDATED = {"en": "November 2, 2026", "ru": "2 ноября 2026"}
EMAIL = "admin@andre.technology"
LOGO = ("https://i.ibb.co/gn7SmgY/"
        "866f2500-dd81-4d09-8c0f-2b55c25a3464-removalai-preview.png")

PATHS = {
    "privacy": {"en": "/privacy/", "ru": "/privacy/ru/"},
    "terms": {"en": "/terms/", "ru": "/terms/ru/"},
}

UI = {
    "en": {"home": "Home", "updated": "Last updated", "contact": "Contact", "other": "Terms of Use",
           "other_p": "Privacy Policy", "copy": "2026 © Andre AI Technologies LTD"},
    "ru": {"home": "На главную", "updated": "Обновлено", "contact": "Связаться", "other": "Условия использования",
           "other_p": "Политика конфиденциальности", "copy": "2026 © Andre AI Technologies LTD"},
}

MAIL = '<a href="mailto:%s">%s</a>' % (EMAIL, EMAIL)

# Тексты. Каждый раздел — заголовок и абзацы/списки (строки, начинающиеся с «- », — пункты списка).
LEGAL = {
    "privacy": {
        "en": {
            "title": "Privacy Policy",
            "lead": "This policy explains what personal data Andre AI Technologies LTD (“we”, “us”) collects on andre.technology, "
                    "why we collect it and what rights you have.",
            "sections": [
                ("Who we are", [
                    "Andre AI Technologies LTD operates the website andre.technology and is the controller of the personal data described here. "
                    "Questions about this policy or your data: " + MAIL + ".",
                ]),
                ("What we collect", [
                    "- Data you send us through forms on the site: your name, email, Telegram handle or other contact, your message, "
                    "the package and company size you picked, and the email you leave to subscribe to news.",
                    "- Technical data that is processed automatically when the page loads: IP address, browser and device type, "
                    "requested pages and time. It is handled by our hosting and content delivery providers (see below).",
                    "- Settings stored only in your browser (localStorage): the chosen language and, if the network failed, "
                    "a form you sent that is waiting to be delivered. These never leave your device unless you send the form.",
                ]),
                ("What we do not collect", [
                    "The site sets no cookies, runs no analytics or advertising trackers and does not build profiles of visitors.",
                ]),
                ("Why we use it", [
                    "- To answer your request and arrange an AI diagnostic, strategy session, consultation or other service you asked about "
                    "(steps taken at your request before a contract).",
                    "- To send our newsletter if you subscribed (your consent; you can unsubscribe at any time).",
                    "- To keep the site secure and working (our legitimate interest).",
                ]),
                ("Who processes it for us", [
                    "- FormSubmit (formsubmit.co) delivers form submissions to our mailbox.",
                    "- GitHub Pages hosts the site; Google Fonts and Cloudflare cdnjs deliver fonts and icons.",
                    "- Our email provider stores the messages we receive.",
                    "We do not sell personal data and share it only with these providers, or when the law requires it. "
                    "Some providers are located outside your country; they protect data with standard contractual safeguards.",
                ]),
                ("Our other services", [
                    "The AI diagnostic (maturity.andre.technology), AI strategy workspace (strategy.andre.technology), Neuronium (neuronium.ai) "
                    "and our Telegram bot are separate services with their own terms. Links to social networks lead to sites "
                    "governed by their own policies.",
                ]),
                ("How long we keep it", [
                    "Requests and correspondence — as long as needed to handle them and for up to 3 years afterwards for our records. "
                    "Newsletter email — until you unsubscribe. Server logs of our providers — according to their retention rules.",
                ]),
                ("Your rights", [
                    "You may request access to your data, its correction or deletion, restriction of or objection to processing, "
                    "and a copy in a portable format; you may withdraw consent at any time. Write to " + MAIL + " — we answer within 30 days. "
                    "You also have the right to complain to your data protection authority.",
                ]),
                ("Children", [
                    "The site is intended for businesses and is not directed at children under 16. We do not knowingly collect their data.",
                ]),
                ("Changes", [
                    "We may update this policy; the date of the latest version is shown at the top of the page.",
                ]),
            ],
        },
        "ru": {
            "title": "Политика конфиденциальности",
            "lead": "Здесь написано, какие персональные данные Andre AI Technologies LTD («мы») собирает на сайте andre.technology, "
                    "зачем и какие у вас есть права.",
            "sections": [
                ("Кто мы", [
                    "Andre AI Technologies LTD — владелец сайта andre.technology и оператор описанных здесь персональных данных. "
                    "Вопросы о политике и ваших данных: " + MAIL + ".",
                ]),
                ("Что мы собираем", [
                    "- Данные, которые вы отправляете через формы на сайте: имя, email, ник в Telegram или другой контакт, текст сообщения, "
                    "выбранный пакет и размер компании, а также email для подписки на новости.",
                    "- Технические данные, которые обрабатываются автоматически при загрузке страницы: IP-адрес, тип браузера и устройства, "
                    "открытые страницы и время. Их обрабатывают наши хостинг и сети доставки контента (см. ниже).",
                    "- Настройки, которые хранятся только в вашем браузере (localStorage): выбранный язык и — если пропала сеть — "
                    "отправленная форма, которая ждёт доставки. Они не покидают ваше устройство, пока вы сами не отправите форму.",
                ]),
                ("Чего мы не собираем", [
                    "Сайт не ставит cookie, не подключает аналитику и рекламные трекеры и не составляет профили посетителей.",
                ]),
                ("Зачем мы их используем", [
                    "- Чтобы ответить на ваш запрос и организовать ИИ-диагностику, стратегию, консультацию или другую услугу, о которой вы спросили "
                    "(действия по вашему запросу до заключения договора).",
                    "- Чтобы присылать новости, если вы подписались (ваше согласие; отписаться можно в любой момент).",
                    "- Чтобы сайт работал и был защищён (наш законный интерес).",
                ]),
                ("Кто обрабатывает данные по нашему поручению", [
                    "- FormSubmit (formsubmit.co) доставляет отправленные формы на нашу почту.",
                    "- GitHub Pages размещает сайт; Google Fonts и Cloudflare cdnjs отдают шрифты и значки.",
                    "- Наш почтовый сервис хранит полученные письма.",
                    "Мы не продаём персональные данные и передаём их только этим сервисам или по требованию закона. "
                    "Часть сервисов находится за пределами вашей страны; данные у них защищены стандартными договорными гарантиями.",
                ]),
                ("Наши другие сервисы", [
                    "ИИ-диагностика (maturity.andre.technology), кабинет ИИ-стратегии (strategy.andre.technology), Нейроний (neuronium.ai) "
                    "и наш Telegram-бот — отдельные сервисы со своими условиями. Ссылки на соцсети ведут на сайты с их собственными политиками.",
                ]),
                ("Сколько мы храним данные", [
                    "Запросы и переписку — сколько нужно для ответа и до 3 лет после него для нашего учёта. "
                    "Email для новостей — пока вы не отпишетесь. Журналы серверов наших подрядчиков — по их правилам хранения.",
                ]),
                ("Ваши права", [
                    "Вы можете запросить доступ к своим данным, их исправление или удаление, ограничение обработки или возразить против неё, "
                    "получить копию в переносимом формате и в любой момент отозвать согласие. Напишите на " + MAIL + " — ответим в течение 30 дней. "
                    "Вы также вправе пожаловаться в орган по защите персональных данных.",
                ]),
                ("Дети", [
                    "Сайт предназначен для бизнеса и не рассчитан на детей младше 16 лет. Мы сознательно не собираем их данные.",
                ]),
                ("Изменения", [
                    "Мы можем обновлять эту политику; дата последней редакции указана в начале страницы.",
                ]),
            ],
        },
    },
    "terms": {
        "en": {
            "title": "Terms of Use",
            "lead": "These terms govern your use of andre.technology, operated by Andre AI Technologies LTD. "
                    "By using the site you agree to them.",
            "sections": [
                ("About the site", [
                    "The site describes our AI transformation services: AI maturity diagnostic, AI strategy, the Neuronium AI platform, "
                    "team training and consulting. It is provided for information and to let you contact us.",
                ]),
                ("Prices and services", [
                    "Prices on the site are indicative and may change. A service is provided only under a separate agreement, offer "
                    "or invoice, which sets its exact scope, price and terms; it prevails over the site. The free AI diagnostic is offered "
                    "as long as it is available and may be changed or discontinued.",
                ]),
                ("No professional advice", [
                    "Materials on the site, including case examples, are general information and not legal, financial or investment advice. "
                    "Results described in cases depend on each company and are not guaranteed.",
                ]),
                ("Intellectual property", [
                    "Texts, videos, images, logos, designs and code of the site belong to Andre AI Technologies LTD or its licensors. "
                    "You may view and share links to the site; any other copying or use requires our written permission.",
                ]),
                ("Acceptable use", [
                    "Do not attempt to break or overload the site, send spam or malicious content through its forms, "
                    "or use it in breach of the law.",
                ]),
                ("Third-party services and links", [
                    "The site links to our separate services and to third-party websites and social networks. They have their own terms, "
                    "and we are not responsible for third-party content.",
                ]),
                ("Liability", [
                    "The site is provided “as is”. To the extent permitted by law, we are not liable for indirect losses or for losses "
                    "caused by interruptions, errors or the use of information from the site.",
                ]),
                ("Personal data", [
                    "How we handle personal data is described in the <a href=\"/privacy/\">Privacy Policy</a>.",
                ]),
                ("Changes and governing law", [
                    "We may update these terms; the date of the latest version is shown at the top of the page. The terms are governed by "
                    "the law of the country where Andre AI Technologies LTD is registered, unless mandatory consumer law of your country "
                    "provides otherwise.",
                ]),
            ],
        },
        "ru": {
            "title": "Условия использования",
            "lead": "Эти условия регулируют использование сайта andre.technology, которым управляет Andre AI Technologies LTD. "
                    "Пользуясь сайтом, вы с ними соглашаетесь.",
            "sections": [
                ("О сайте", [
                    "Сайт рассказывает о наших услугах ИИ-трансформации: ИИ-диагностике, ИИ-стратегии, ИИ-платформе Нейроний, "
                    "обучении команды и консалтинге. Он носит информационный характер и помогает связаться с нами.",
                ]),
                ("Цены и услуги", [
                    "Цены на сайте ориентировочные и могут меняться. Услуга оказывается только по отдельному договору, оферте или счёту — "
                    "в них указаны точный объём, цена и условия, и они имеют приоритет над сайтом. Бесплатная ИИ-диагностика доступна, "
                    "пока мы её предлагаем, и может быть изменена или прекращена.",
                ]),
                ("Не профессиональная консультация", [
                    "Материалы сайта, включая примеры кейсов, — общая информация, а не юридическая, финансовая или инвестиционная консультация. "
                    "Результаты из кейсов зависят от конкретной компании и не гарантируются.",
                ]),
                ("Интеллектуальная собственность", [
                    "Тексты, видео, изображения, логотипы, дизайн и код сайта принадлежат Andre AI Technologies LTD или её лицензиарам. "
                    "Сайт можно смотреть и делиться ссылками на него; иное копирование и использование — только с нашего письменного согласия.",
                ]),
                ("Допустимое использование", [
                    "Нельзя пытаться взломать или перегрузить сайт, отправлять через формы спам или вредоносное содержимое "
                    "и использовать сайт с нарушением закона.",
                ]),
                ("Сторонние сервисы и ссылки", [
                    "Сайт ведёт на наши отдельные сервисы, на сторонние сайты и в соцсети. У них свои условия, "
                    "и мы не отвечаем за содержимое сторонних ресурсов.",
                ]),
                ("Ответственность", [
                    "Сайт предоставляется «как есть». В пределах, допустимых законом, мы не отвечаем за косвенные убытки и за убытки "
                    "из-за перебоев, ошибок или использования информации с сайта.",
                ]),
                ("Персональные данные", [
                    "Как мы обращаемся с персональными данными, описано в <a href=\"/privacy/ru/\">Политике конфиденциальности</a>.",
                ]),
                ("Изменения и применимое право", [
                    "Мы можем обновлять эти условия; дата последней редакции указана в начале страницы. К условиям применяется право страны "
                    "регистрации Andre AI Technologies LTD, если обязательные нормы о защите прав потребителей вашей страны не предусматривают иного.",
                ]),
            ],
        },
    },
}

CSS = """
  :root { --bg: #050505; --tx: #E5E7EB; --tx2: #cbd5e1; --tx3: #94a3b8; --line: rgba(255,255,255,0.12); --p: #8854F3; --p2: #a071ff; --o: #F97316; --o2: #ff8a33; }
  *, *::before, *::after { box-sizing: border-box; }
  html { background: var(--bg); color-scheme: dark; -webkit-text-size-adjust: 100%; text-size-adjust: 100%; }
  body { margin: 0; background: var(--bg); color: var(--tx); font: 15px/1.7 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; -webkit-font-smoothing: antialiased; }
  a { color: var(--p2); text-decoration: none; } a:hover { color: #fff; }
  ::selection { background: var(--p); color: #fff; }
  .hdr { position: sticky; top: 0; z-index: 5; display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 0.9rem clamp(16px, 4vw, 48px);
    background: rgba(5,5,5,0.82); -webkit-backdrop-filter: blur(14px); backdrop-filter: blur(14px); border-bottom: 1px solid var(--line); }
  .logo img { display: block; width: 2.6rem; height: 2.6rem; object-fit: contain; }
  .hdr-r { display: flex; align-items: center; gap: 1.2rem; font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; }
  .hdr-r a { color: var(--tx3); } .hdr-r a:hover, .hdr-r a.on { color: #fff; }
  .lang-switch { display: flex; gap: 0.35rem; align-items: center; } .lang-switch span { color: rgba(255,255,255,0.25); }
  main { max-width: 46rem; margin: 0 auto; padding: clamp(2rem, 7vw, 4.5rem) clamp(16px, 4vw, 24px) 3rem; }
  h1 { margin: 0 0 0.6rem; font-size: clamp(26px, 5vw, 40px); line-height: 1.15; font-weight: 800; text-transform: uppercase; letter-spacing: -0.01em;
    background: linear-gradient(100deg, #ff8a33 0%, #a071ff 80%); -webkit-background-clip: text; background-clip: text; color: transparent; }
  .upd { margin: 0 0 1.8rem; font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--tx3); }
  .lead { margin: 0 0 2.2rem; font-size: 16px; color: var(--tx2); }
  h2 { margin: 2.2rem 0 0.7rem; font-size: 15px; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; color: #fff; }
  h2::before { content: ''; display: inline-block; width: 0.55rem; height: 0.55rem; margin-right: 0.7rem; border-radius: 50%; background: linear-gradient(135deg, var(--p), var(--o)); vertical-align: 0.08em; }
  p, li { color: var(--tx2); } p { margin: 0 0 0.8rem; }
  ul { margin: 0 0 0.8rem; padding-left: 1.2rem; } li { margin: 0 0 0.45rem; } li::marker { color: var(--o2); }
  .foot { max-width: 46rem; margin: 0 auto; padding: 1.6rem clamp(16px, 4vw, 24px) 2.6rem; border-top: 1px solid var(--line); display: flex; flex-wrap: wrap; gap: 0.6rem 1.6rem;
    font-size: 11.5px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--tx3); }
  .foot a { color: var(--tx3); } .foot a:hover { color: #fff; }
"""

PAGE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#050505">
<meta name="color-scheme" content="dark">
<title>{title} | Andre AI Technologies</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{site}{path}">
<link rel="alternate" hreflang="en" href="{site}{path_en}">
<link rel="alternate" hreflang="ru" href="{site}{path_ru}">
<meta name="robots" content="index, follow">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png">
<link rel="icon" type="image/png" sizes="48x48" href="/favicon-48x48.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&display=swap" rel="stylesheet">
<!-- FR-SITE96: юридическая страница; собрана tools/build_legal.py — правки текста там, не здесь -->
<style>{css}</style>
</head>
<body>
<header class="hdr">
  <a class="logo" href="{home}" aria-label="Andre AI Technologies"><img src="{logo}" alt="AIT" width="42" height="42"></a>
  <nav class="hdr-r">
    <a href="{home}">{ui_home}</a>
    <span class="lang-switch"><a class="lang-opt{en_on}" data-lang="en" href="{path_en}">EN</a><span>|</span><a class="lang-opt{ru_on}" data-lang="ru" href="{path_ru}">RU</a></span>
  </nav>
</header>
<main>
  <h1>{title}</h1>
  <p class="upd">{ui_updated}: {updated}</p>
  <p class="lead">{lead}</p>
{body}
</main>
<footer class="foot">
  <span>{copy}</span>
  <a href="{other_href}">{other}</a>
  <a href="mailto:{email}">{email}</a>
</footer>
<script>
  /* язык страницы запоминается для главной, биографии и курса — общий ключ ait_lang */
  try {{ localStorage.setItem('ait_lang', '{lang}'); }} catch (e) {{}}
</script>
</body>
</html>
"""


def _section(title, items):
    out = ["  <h2>%s</h2>" % html.escape(title)]
    ul = []
    for it in items:
        if it.startswith("- "):
            ul.append("    <li>%s</li>" % it[2:])
            continue
        if ul:
            out.append("  <ul>\n" + "\n".join(ul) + "\n  </ul>"); ul = []
        out.append("  <p>%s</p>" % it)
    if ul:
        out.append("  <ul>\n" + "\n".join(ul) + "\n  </ul>")
    return "\n".join(out)


def build():
    written = []
    for kind, langs in LEGAL.items():
        other = "terms" if kind == "privacy" else "privacy"
        for lang, doc in langs.items():
            ui = UI[lang]
            page = PAGE.format(
                lang=lang, title=html.escape(doc["title"]), desc=html.escape(doc["lead"]), site=SITE,
                path=PATHS[kind][lang], path_en=PATHS[kind]["en"], path_ru=PATHS[kind]["ru"],
                css=CSS, home="/?lang=%s" % lang, logo=LOGO, ui_home=ui["home"],
                en_on=" active" if lang == "en" else "", ru_on=" active" if lang == "ru" else "",
                ui_updated=ui["updated"], updated=UPDATED[lang], lead=doc["lead"],
                body="\n".join(_section(t, items) for t, items in doc["sections"]),
                copy=ui["copy"], other_href=PATHS[other][lang], other=ui["other"] if kind == "privacy" else ui["other_p"],
                email=EMAIL)
            rel = PATHS[kind][lang].strip("/") + "/index.html"
            path = os.path.join(ROOT, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(page)
            written.append(rel)
    return written


if __name__ == "__main__":
    for rel in build():
        print("written", rel)
