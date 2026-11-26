# -*- coding: utf-8 -*-
"""Собирает юридические страницы сайта на двух языках (FR-SITE96; ред. 26.11 — FR-SITE150…152, NFR-SITE114).

    python3 tools/build_legal.py   # пишет privacy/, privacy/ru/, terms/, terms/ru/, partners/terms/, partners/terms/ru/

Три документа:
  * «Политика конфиденциальности» — все продукты: сайт и сайт партнёров, Andre AI (диагностика и кабинет
    стратегии), Нейроний, партнёрская программа, Telegram-бот, платежи, cookie и хранилище браузера,
    записи об использовании продукта (клики, паузы между клавишами, ошибки — владелец: «скажи прямо»),
    сроки хранения, получатели, права (FR-SITE150);
  * «Условия использования» — сервисы и ценовая политика 26.11: бесплатное, стратегия разово, подписка
    Нейрония с автопродлением, пакеты, проверка схем и буткемп, промокоды, возвраты, ИИ, ответственность
    (FR-SITE151);
  * «Условия партнёрской программы» — ступени, ставка, 70 %, 10 %, выплаты раз в месяц вручную, налоги,
    поведение, профиль с согласия (FR-SITE152). Лежит в partners/terms/ — эту страницу отдают и
    andre.technology/partners/terms/, и partners.andre.technology/terms/ (Caddy переписывает /x →
    /partners/x, NFR-SITE110), поэтому свои ресурсы и переходы у неё — только относительные, а ссылки на
    другие страницы andre.technology — полными адресами (NFR-SITE114).

Реквизиты компании — только те, что уже были на страницах: Andre AI Technologies LTD и admin@andre.technology;
номера регистрации и адреса не выдумываем (их нет — пункт пишется без них). Применимое право — прежней фразой.

Тексты — здесь же, в LEGAL. Правишь текст — пересобираешь страницы этим скриптом и прогоняешь
tests/test_legal.py и tests/test_site.py. Язык страницы запоминается в ait_lang — тот же ключ, что у
главной, биографии, курса и сайта партнёров.
"""
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from typo import bind_short_words  # noqa: E402 — правило переносов одно на весь сайт
SITE = "https://andre.technology"
PARTNERS_SITE = "https://partners.andre.technology"
UPDATED = {"en": "November 26, 2026", "ru": "26 ноября 2026"}
EMAIL = "admin@andre.technology"
LOGO = ("https://i.ibb.co/gn7SmgY/"
        "866f2500-dd81-4d09-8c0f-2b55c25a3464-removalai-preview.png")

ORDER = ("privacy", "terms", "partner_terms")

# Где лежит файл страницы на andre.technology (он же адрес на GitHub Pages).
PATHS = {
    "privacy": {"en": "/privacy/", "ru": "/privacy/ru/"},
    "terms": {"en": "/terms/", "ru": "/terms/ru/"},
    "partner_terms": {"en": "/partners/terms/", "ru": "/partners/terms/ru/"},
}

# Канонический адрес: условия партнёров — на поддомене, как весь сайт партнёров (NFR-SITE110).
CANON = {
    "privacy": {lang: SITE + p for lang, p in PATHS["privacy"].items()},
    "terms": {lang: SITE + p for lang, p in PATHS["terms"].items()},
    "partner_terms": {"en": PARTNERS_SITE + "/terms/", "ru": PARTNERS_SITE + "/terms/ru/"},
}

UI = {
    "en": {"home": "Home", "partners": "Partners", "updated": "Last updated", "toc": "Contents",
           "copy": "2026 © Andre AI Technologies LTD"},
    "ru": {"home": "На главную", "partners": "Партнёры", "updated": "Обновлено", "toc": "Содержание",
           "copy": "2026 © Andre AI Technologies LTD"},
}

MAIL = '<a href="mailto:%s">%s</a>' % (EMAIL, EMAIL)

# Тексты. Раздел — заголовок и пункты: строка «- …» — пункт списка, «### …» — подзаголовок, иначе абзац.
# Внутри — {MAIL} и адреса других документов {privacy}, {terms}, {partner_terms}: их подставляет _links()
# по месту страницы (с сайта — путь от корня, со страницы партнёров — полный адрес).
LEGAL = {
    "privacy": {
        "en": {
            "title": "Privacy Policy",
            "lead": "This policy explains what personal data Andre AI Technologies LTD (“we”, “us”) collects on our websites, "
                    "in Andre AI, in Neuronium and in the Andre AI partner program, why we collect it, who processes it for us "
                    "and what rights you have.",
            "sections": [
                ("Who we are", [
                    "Andre AI Technologies LTD is the controller of the personal data described in this policy. "
                    "Questions about this policy or your data: {MAIL}.",
                    "The policy covers:",
                    "- the website andre.technology and the partners site partners.andre.technology (also available at andre.technology/partners/);",
                    "- Andre AI: the AI maturity diagnostic at maturity.andre.technology and the AI strategy workspace at strategy.andre.technology;",
                    "- Neuronium: each company’s own AI workspace at <em>company</em>.neuronium.ai;",
                    "- the Andre AI partner program and the partner account;",
                    "- our Telegram bot.",
                ]),
                ("Data your company adds", [
                    "In Andre AI and Neuronium a company describes its work: processes, roles, systems and documents, and in Neuronium "
                    "also files, connected services and workflows. This content may include personal data of the company’s employees, "
                    "customers and partners. We process it to provide the service to that company, according to its settings and instructions. "
                    "The company decides what to add and is responsible for having a legal basis for it and for informing the people concerned. "
                    "Where the law treats the company as the controller of this content, we process it on the company’s behalf.",
                ]),
                ("The website and the partners site", [
                    "- Forms: the name, email, Telegram handle or other contact and the message you send, the package and company size you picked, "
                    "and the email you leave to subscribe to news. Website forms are delivered to our mailbox by FormSubmit. Forms on the partners "
                    "site go to Andre AI (strategy.andre.technology) and, if it is unavailable, to our mailbox by FormSubmit.",
                    "- A package button opens Andre AI with the package, company size, billing period and language you chose written in the page "
                    "address and, if you came by a partner’s link, the partner’s promo code and profile name.",
                    "- Technical data processed automatically when a page loads: IP address, browser and device type, requested pages and time. "
                    "It is handled by GitHub Pages, which hosts the sites, and by Google Fonts and Cloudflare cdnjs, which deliver fonts and icons. "
                    "Requests to partners.andre.technology pass through our server, which forwards them to GitHub Pages.",
                    "- Your browser’s local storage (localStorage) keeps the chosen language and, if the network failed, a form waiting to be sent. "
                    "This never leaves your device unless you send the form.",
                    "The two sites set no cookies, run no analytics or advertising trackers and do not build profiles of visitors.",
                ]),
                ("Andre AI", [
                    "### Account",
                    "- Your email and, if you sign in with Google, the name and profile picture Google shares with us. You can also set your name "
                    "and picture yourself.",
                    "- Sign-in codes we send to your email. A code is valid for 10 minutes and allows a limited number of attempts.",
                    "- Your company, your role in it (founder or invited member) and invitations.",
                    "### Diagnostic and interview",
                    "- Answers to the AI maturity diagnostic. The diagnostic result is calculated by fixed rules, not by an AI model.",
                    "- Your answers in the interview, typed or spoken. A voice recording is sent to speech recognition and turned into text, "
                    "which you can correct before sending. We keep the text with your answers and delete the recording once it has been recognised. "
                    "If recognition fails, the recording is kept on our server for 14 days so that it is not lost, and your browser keeps its own copy "
                    "until you retry or delete it.",
                    "- What you tell us about the company and what is created from it: company name, size and industry, departments, roles and people "
                    "as you describe them, processes, systems and documents, process schemas “as is” and “to be”, AI agents, the strategy and "
                    "the implementation plan.",
                    "### AI processing",
                    "To conduct the interview and build schemas, the strategy and the plan, we send the relevant parts of your answers and company data "
                    "to AI model providers (currently OpenAI and Anthropic) through their APIs, and voice recordings to OpenAI for speech recognition. "
                    "The providers process this data to return the result to us. We do not sell your data and do not use it to train AI models.",
                    "### Purchases",
                    "- Orders: the items, prices, discount, promo code and the partner it belongs to, the consultant and their rate, and the status of "
                    "payment and refunds.",
                    "- Card payments are made on Stripe’s payment page. Stripe processes your card details; we receive the payment status, the amount "
                    "and Stripe’s reference numbers. We do not see or store full card numbers.",
                    "### Usage records",
                    "We record how Andre AI is used so that we can find errors and improve the product. These records are kept in our own database; "
                    "no third-party analytics is used. We record:",
                    "- every click: what was clicked and its visible text (up to 60 characters), and how far you scrolled a screen;",
                    "- how you fill in text fields: the pauses between keystrokes, deletions, the amount of pasted text, the time it took and the final "
                    "text of the field. For fields with sign-in codes, passwords or payment details we record only length and timing, never the text;",
                    "- the screens you open and the time spent on them, browser errors and network failures, device and browser type;",
                    "- random identifiers of your browser and of the browser tab, kept in its local and session storage, which link these events "
                    "together, including before you sign in;",
                    "- each request to our server: time, address, response, IP address, browser and the page you came from;",
                    "- each call to an AI model in full: the instructions, the input and the answer, the model, the tokens used and the time it took.",
                    "### Cookies and browser storage",
                    "Andre AI sets one cookie, amx_lang, which remembers the interface language for a year. Your sign-in, company, language, theme, "
                    "drafts and unsent recordings are kept in the browser’s local storage so that you stay signed in and do not lose your work. "
                    "We do not use advertising cookies.",
                    "### Emails",
                    "We send sign-in codes and messages about your account, orders and payments through our email provider.",
                    "### Andre AI and Neuronium",
                    "If your company uses Neuronium, Andre AI passes to the company’s Neuronium workspace the processes and AI agents you choose to "
                    "launch there and the status of the subscription, and can open Neuronium for you with a signed link instead of a separate sign-in.",
                ]),
                ("Neuronium", [
                    "Each company has its own workspace at <em>company</em>.neuronium.ai. Only the email addresses allowed for the workspace can sign in: "
                    "with a code sent to the email, with Google or with a link from Andre AI.",
                    "- Workspace content: files and documents, the company’s knowledge, workflows and AI agents, chats with the assistant and the "
                    "history of runs — steps, results and errors.",
                    "- Connected services. A company can connect Google Workspace through Google sign-in (OAuth) and choose which access to grant, "
                    "for example to Gmail, Google Drive, Calendar, Sheets, Docs, Slides, Tasks or Forms. Neuronium uses this access only for the tasks "
                    "and workflows the company sets up, and only while the service stays connected. Access can be revoked at any time in your Google "
                    "Account (myaccount.google.com/permissions). Keys of other connected services are kept in the workspace’s protected secrets "
                    "storage and are never shown back.",
                    "- Our use of information received from Google APIs follows the Google API Services User Data Policy, including its Limited Use "
                    "requirements: we use it only for the features set up in the workspace, do not use it for advertising, do not sell it, do not use "
                    "it to train AI models, and people do not read it without your permission unless security or the law requires it.",
                    "- Model usage. Neuronium counts every AI model call — tokens, cost and runs — against the model budget of the company’s plan. "
                    "Calls go to AI model providers (currently Anthropic and OpenAI). A company may connect its own model API key: the key is kept "
                    "in the workspace’s secrets storage, is never shown or written to logs, and calls made with it are governed by the company’s "
                    "own agreement with that provider.",
                ]),
                ("The partner program", [
                    "### Application",
                    "- Your name, email, LinkedIn profile, the experience you describe, the rate you propose and your language.",
                    "- The stages you pass — application, Academy, certificate, interview and our decision — and our correspondence with you.",
                    "### Partner account",
                    "- You sign in with a code sent to your email. We keep your profile (name, headline, about, city and country, languages, services, "
                    "industries, skills, rate, LinkedIn), the certificates we issue, your promo code, the orders you brought or delivered, client "
                    "requests, your earnings and payouts, and the payment details you give us for payouts.",
                    "### Public profile",
                    "Your profile appears in the public catalog on the partners site and in Andre AI only after you turn on “show in catalog” in your "
                    "partner account, and you can turn it off at any time. The catalog shows your name, headline, about, city and country, languages, "
                    "services, industries, skills, rate, LinkedIn link, certificates, rating, number of completed projects and reviews.",
                    "### Client requests and reviews",
                    "- When a client writes to a consultant, we keep the client’s name, email, company and message and pass them to that consultant.",
                    "- When a client orders a schema review or a bootcamp, the consultant gets what is needed to deliver it: the client’s contact "
                    "details, company and the schemas chosen for review.",
                    "- After a service is completed, the client can rate it from 1 to 5 and write a review. A published review shows the author’s first "
                    "name, the initial of their surname and the size of the company, not its name. We may hide a review that is abusive or not "
                    "about the service.",
                ]),
                ("Telegram bot", [
                    "- Your Telegram account ID, name, username and language; the messages, voice messages, video messages and files you send to "
                    "Andre through the bot, and the replies.",
                    "- Orders for payment codes. Payments in roubles are made on Tochka Bank’s payment page: the bank processes the card details "
                    "and we receive the payment status. The code is then redeemed in Andre AI.",
                    "Messages in Telegram are also processed by Telegram under its own policy.",
                ]),
                ("Why we use data", [
                    "- To provide the services you use or order: your account, the diagnostic, the interview and the strategy, the Neuronium "
                    "workspace, orders, consultant services and the partner program (performance of a contract or steps before it).",
                    "- To take payments, keep accounts and pay partners (contract and our legal obligations).",
                    "- To answer your requests (steps taken at your request).",
                    "- To keep the services working and secure, prevent abuse, find and fix errors and improve the product — this is what usage "
                    "records and AI call logs are for (our legitimate interest).",
                    "- To publish a partner profile and to send our newsletter (your consent, which you can withdraw at any time).",
                    "We do not make decisions about you that have legal or similarly significant effects solely by automated means.",
                ]),
                ("Who receives data", [
                    "We do not sell personal data. We share it only with the following recipients and only as much as each of them needs:",
                    "- Hosting: our servers that run Andre AI, Neuronium and the partners subdomain; GitHub Pages for the websites; Google Fonts and "
                    "Cloudflare cdnjs for fonts and icons.",
                    "- AI providers: OpenAI (language models, speech recognition and text embeddings for search) and Anthropic (language models).",
                    "- Payments: Stripe; Tochka Bank for payments in roubles in the Telegram bot.",
                    "- Communication: our email provider; FormSubmit for website forms; Telegram for the bot.",
                    "- Google: for sign-in with Google and for the Google Workspace services a company connects to Neuronium.",
                    "- Consultants (partners): client requests and the order details they need to deliver a service.",
                    "- Your company: people invited to your company’s Andre AI account or Neuronium workspace see the company’s shared content.",
                    "- Authorities, when the law requires it.",
                ]),
                ("International transfers", [
                    "Some of these providers process data outside your country, including in the United States. Where the law requires it, "
                    "such transfers are protected by contractual safeguards such as standard contractual clauses.",
                ]),
                ("How long we keep data", [
                    "- Website requests and correspondence: as long as needed to handle them and up to 3 years afterwards for our records. "
                    "The same applies to partner applications that did not lead to a partnership.",
                    "- Newsletter email: until you unsubscribe.",
                    "- Andre AI account and company content: while the account exists. At your request we delete them together with the log of "
                    "requests to our server, except records we must keep by law.",
                    "- Neuronium workspace: while it exists. After a subscription ends, the workspace stays available read-only so that the company "
                    "can take its data; we delete it at the company’s request.",
                    "- Usage records and AI call logs: 180 days, then they are deleted automatically.",
                    "- Voice recordings: deleted once recognised; a recording that could not be recognised — after 14 days.",
                    "- Orders, payments, partner earnings and payouts: as long as accounting and tax law requires.",
                    "- Partner profile and reviews: while you are a partner; after that we remove the profile from the catalog and keep only what "
                    "we need for payouts and accounting.",
                    "- Server logs of our providers: according to their retention rules.",
                ]),
                ("Security", [
                    "Data travels over encrypted connections (HTTPS). Sign-in codes expire after 10 minutes and allow a limited number of attempts. "
                    "Keys of connected services and model keys are kept in protected storage and are never shown. Our team’s access to customer data "
                    "is limited to what is needed for support and fixing errors. No system is completely secure; if a breach affects your data, "
                    "we will inform you and the authorities as the law requires.",
                ]),
                ("Your rights", [
                    "You may request access to your data, its correction or deletion, restriction of or objection to processing, "
                    "and a copy in a portable format; you may withdraw consent at any time. Write to {MAIL} — we answer within 30 days. "
                    "You also have the right to complain to your data protection authority.",
                ]),
                ("Children", [
                    "Our services are intended for businesses and are not directed at children under 16. We do not knowingly collect their data.",
                ]),
                ("Changes", [
                    "We may update this policy; the date of the latest version is shown at the top of the page. If a change materially affects how "
                    "we use data you have already given us, we will tell you in the product or by email.",
                ]),
            ],
        },
        "ru": {
            "title": "Политика конфиденциальности",
            "lead": "Здесь написано, какие персональные данные Andre AI Technologies LTD («мы») собирает на наших сайтах, в Andre AI, "
                    "в Нейронии и в партнёрской программе Andre AI, зачем, кто обрабатывает их по нашему поручению и какие у вас есть права.",
            "sections": [
                ("Кто мы", [
                    "Andre AI Technologies LTD — оператор персональных данных, описанных в этой политике. "
                    "Вопросы о политике и ваших данных: {MAIL}.",
                    "Политика действует для:",
                    "- сайта andre.technology и сайта партнёров partners.andre.technology (он же — andre.technology/partners/);",
                    "- Andre AI: ИИ-диагностики зрелости на maturity.andre.technology и кабинета ИИ-стратегии на strategy.andre.technology;",
                    "- Нейрония: собственного ИИ-пространства каждой компании по адресу <em>компания</em>.neuronium.ai;",
                    "- партнёрской программы Andre AI и кабинета партнёра;",
                    "- нашего Telegram-бота.",
                ]),
                ("Данные, которые добавляет компания", [
                    "В Andre AI и Нейронии компания описывает свою работу: процессы, роли, системы и документы, а в Нейронии — ещё файлы, "
                    "подключённые сервисы и рабочие процессы. В этих материалах могут быть персональные данные сотрудников, клиентов и партнёров "
                    "компании. Мы обрабатываем их, чтобы оказать компании услугу, — по её настройкам и поручениям. Что добавлять, решает компания; "
                    "она же отвечает за законное основание и за то, чтобы люди, о которых идёт речь, были уведомлены. Если по закону оператор "
                    "этих данных — компания, мы обрабатываем их по её поручению.",
                ]),
                ("Сайт и сайт партнёров", [
                    "- Формы: имя, email, ник в Telegram или другой контакт и текст сообщения, выбранный пакет и размер компании, а также email "
                    "для подписки на новости. Формы сайта доставляет на нашу почту FormSubmit. Формы сайта партнёров уходят в Andre AI "
                    "(strategy.andre.technology), а если он недоступен — на нашу почту через FormSubmit.",
                    "- Кнопки пакетов открывают Andre AI и передают в адресе страницы выбранный пакет, размер компании, период оплаты и язык, "
                    "а если вы пришли по ссылке партнёра — его промокод и адрес его профиля.",
                    "- Технические данные, которые обрабатываются автоматически при загрузке страницы: IP-адрес, тип браузера и устройства, "
                    "открытые страницы и время. Их обрабатывают GitHub Pages, где размещены сайты, а также Google Fonts и Cloudflare cdnjs, "
                    "которые отдают шрифты и значки. Запросы к partners.andre.technology проходят через наш сервер, который передаёт их GitHub Pages.",
                    "- В хранилище браузера (localStorage) — выбранный язык и, если пропала сеть, отправленная форма, которая ждёт доставки. "
                    "Они не покидают ваше устройство, пока вы сами не отправите форму.",
                    "Оба сайта не ставят cookie, не подключают аналитику и рекламные трекеры и не составляют профили посетителей.",
                ]),
                ("Andre AI", [
                    "### Аккаунт",
                    "- Ваш email, а при входе через Google — имя и фото профиля, которые передаёт Google. Имя и фото можно задать и самому.",
                    "- Коды входа, которые мы присылаем на почту. Код действует 10 минут, число попыток ограничено.",
                    "- Ваша компания, ваша роль в ней (основатель или приглашённый участник) и приглашения.",
                    "### Диагностика и интервью",
                    "- Ответы на вопросы ИИ-диагностики. Результат диагностики считается по заданным правилам, а не ИИ-моделью.",
                    "- Ваши ответы в интервью — текстом или голосом. Голосовая запись уходит на распознавание речи и превращается в текст, "
                    "который можно поправить перед отправкой. Текст мы храним вместе с ответами, а запись удаляем сразу после распознавания. "
                    "Если распознать не удалось, запись 14 дней хранится на нашем сервере, чтобы не потерялась, а браузер держит свою копию, "
                    "пока вы не повторите распознавание или не удалите её.",
                    "- Сведения о компании и то, что из них получается: название, размер и отрасль, отделы, роли и люди — как вы их описали, "
                    "процессы, системы и документы, схемы процессов «как есть» и «как будет», ИИ-агенты, стратегия и план внедрения.",
                    "### Обработка ИИ",
                    "Чтобы вести интервью и строить схемы, стратегию и план, мы передаём нужные части ваших ответов и данных компании поставщикам "
                    "ИИ-моделей (сейчас это OpenAI и Anthropic) через их API, а голосовые записи — в OpenAI для распознавания речи. Поставщики "
                    "обрабатывают эти данные, чтобы вернуть нам результат. Мы не продаём ваши данные и не обучаем на них ИИ-модели.",
                    "### Покупки",
                    "- Заказы: позиции, цены, скидка, промокод и партнёр, которому он принадлежит, консультант и его ставка, статус оплаты "
                    "и возвратов.",
                    "- Оплата картой проходит на платёжной странице Stripe. Данные карты обрабатывает Stripe, а мы получаем статус платежа, сумму "
                    "и номера операций Stripe. Полные номера карт мы не видим и не храним.",
                    "### Записи об использовании",
                    "Мы записываем, как используется Andre AI, чтобы находить ошибки и улучшать продукт. Записи хранятся в нашей собственной базе; "
                    "сторонняя аналитика не подключена. Мы записываем:",
                    "- каждое нажатие: на что нажали и видимый текст элемента (до 60 знаков), а также насколько далеко прокручен экран;",
                    "- как заполняются текстовые поля: паузы между нажатиями клавиш, стирания, объём вставленного текста, время набора и итоговый "
                    "текст поля. В полях с кодом входа, паролем и платёжными данными записываются только длина и время, текст — никогда;",
                    "- какие экраны открывались и сколько времени на них провели, ошибки браузера и сбои сети, тип устройства и браузера;",
                    "- случайные идентификаторы браузера и вкладки — они хранятся в её локальном и сессионном хранилище и связывают эти события "
                    "между собой, в том числе до входа в аккаунт;",
                    "- каждый запрос к нашему серверу: время, адрес, ответ, IP-адрес, браузер и страницу, с которой вы пришли;",
                    "- каждый вызов ИИ-модели целиком: инструкции, входные данные и ответ, модель, расход токенов и время.",
                    "### Cookie и хранилище браузера",
                    "Andre AI ставит одну cookie — amx_lang: она на год запоминает язык интерфейса. Вход, компания, язык, тема оформления, "
                    "черновики и неотправленные записи хранятся в локальном хранилище браузера, чтобы вы оставались в аккаунте и не теряли работу. "
                    "Рекламных cookie нет.",
                    "### Письма",
                    "Коды входа и сообщения об аккаунте, заказах и платежах мы отправляем через нашего почтового провайдера.",
                    "### Andre AI и Нейроний",
                    "Если ваша компания работает в Нейронии, Andre AI передаёт в её пространство процессы и ИИ-агентов, которых вы решили там "
                    "запустить, и статус подписки, а также может открыть вам Нейроний по подписанной ссылке без отдельного входа.",
                ]),
                ("Нейроний", [
                    "У каждой компании — своё пространство по адресу <em>компания</em>.neuronium.ai. Войти в него могут только адреса почты, "
                    "которым открыт доступ к пространству, — по коду на почту, через Google или по ссылке из Andre AI.",
                    "- Содержимое пространства: файлы и документы, знания компании, рабочие процессы и ИИ-агенты, переписка с ассистентом "
                    "и история запусков — шаги, результаты и ошибки.",
                    "- Подключённые сервисы. Компания может подключить Google Workspace через вход Google (OAuth) и сама выбрать, какой доступ "
                    "дать, например к Gmail, Google Диску, Календарю, Таблицам, Документам, Презентациям, Задачам или Формам. Нейроний пользуется "
                    "этим доступом только для задач и рабочих процессов, которые настроила компания, и только пока сервис подключён. Отозвать "
                    "доступ можно в любой момент в аккаунте Google (myaccount.google.com/permissions). Ключи других подключённых сервисов "
                    "хранятся в защищённом хранилище секретов пространства и никогда не показываются обратно.",
                    "- С данными, полученными через API Google, мы обращаемся по правилам Google API Services User Data Policy, включая требования "
                    "Limited Use: используем их только для функций, настроенных в пространстве, не используем для рекламы, не продаём, не обучаем "
                    "на них ИИ-модели, и люди не читают их без вашего разрешения, если этого не требуют безопасность или закон.",
                    "- Расход ИИ-модели. Нейроний учитывает каждый вызов модели — токены, стоимость и запуски — в бюджете модели по тарифу компании. "
                    "Вызовы уходят поставщикам ИИ-моделей (сейчас это Anthropic и OpenAI). Компания может подключить свой ключ API модели: ключ "
                    "хранится в хранилище секретов пространства, нигде не показывается и не пишется в журналы, а вызовы с ним идут по собственному "
                    "договору компании с этим поставщиком.",
                ]),
                ("Партнёрская программа", [
                    "### Заявка",
                    "- Имя, email, профиль LinkedIn, опыт, который вы описали, предложенная ставка и язык.",
                    "- Ступени, которые вы прошли, — заявка, Академия, сертификат, собеседование и наше решение — и наша переписка с вами.",
                    "### Кабинет партнёра",
                    "- Вход — по коду на почту. Мы храним профиль (имя, заголовок, «о себе», город и страну, языки, услуги, отрасли, навыки, "
                    "ставку, LinkedIn), сертификаты, которые выдаём мы, ваш промокод, заказы, которые вы привели или выполнили, заявки клиентов, "
                    "начисления и выплаты, а также реквизиты, которые вы даёте для выплат.",
                    "### Публичный профиль",
                    "Профиль появляется в открытом каталоге на сайте партнёров и в Andre AI только после того, как вы включите «Показывать "
                    "в каталоге» в кабинете партнёра, и его можно выключить в любой момент. В каталоге видны имя, заголовок, «о себе», город "
                    "и страна, языки, услуги, отрасли, навыки, ставка, ссылка на LinkedIn, сертификаты, рейтинг, число выполненных проектов и отзывы.",
                    "### Заявки клиентов и отзывы",
                    "- Когда клиент пишет консультанту, мы сохраняем имя, email, компанию и сообщение клиента и передаём их этому консультанту.",
                    "- Когда клиент заказывает проверку схем или буткемп, консультант получает то, что нужно для работы: контакты клиента, "
                    "компанию и схемы, выбранные на проверку.",
                    "- После выполненной услуги клиент может поставить оценку от 1 до 5 и написать отзыв. В опубликованном отзыве видны имя "
                    "автора, первая буква фамилии и размер компании, но не её название. Отзыв с оскорблениями или не об услуге мы можем скрыть.",
                ]),
                ("Telegram-бот", [
                    "- ID аккаунта Telegram, имя, username и язык; сообщения, голосовые, кружки и файлы, которые вы отправляете Андрею через бота, "
                    "и ответы на них.",
                    "- Заказы кодов оплаты. Оплата в рублях проходит на платёжной странице Точка Банка: данные карты обрабатывает банк, "
                    "мы получаем статус платежа. Затем код вводится в Andre AI.",
                    "Сообщения в Telegram обрабатывает и сам Telegram — по своей политике.",
                ]),
                ("Зачем мы используем данные", [
                    "- Чтобы оказывать услуги, которыми вы пользуетесь или которые заказали: аккаунт, диагностика, интервью и стратегия, "
                    "пространство Нейрония, заказы, услуги консультантов и партнёрская программа (исполнение договора или действия до его "
                    "заключения).",
                    "- Чтобы принимать оплату, вести учёт и платить партнёрам (договор и наши обязанности по закону).",
                    "- Чтобы отвечать на ваши запросы (действия по вашему запросу).",
                    "- Чтобы сервисы работали и были защищены, чтобы предотвращать злоупотребления, находить и исправлять ошибки и улучшать "
                    "продукт, — для этого нужны записи об использовании и журнал вызовов ИИ (наш законный интерес).",
                    "- Чтобы публиковать профиль партнёра и присылать новости (ваше согласие; его можно отозвать в любой момент).",
                    "Мы не принимаем о вас решений, которые влекут юридические или похожие по значимости последствия, только автоматически.",
                ]),
                ("Кто получает данные", [
                    "Мы не продаём персональные данные. Мы передаём их только этим получателям и только в том объёме, который нужен каждому из них:",
                    "- Размещение: наши серверы, на которых работают Andre AI, Нейроний и поддомен сайта партнёров; GitHub Pages — для сайтов; "
                    "Google Fonts и Cloudflare cdnjs — для шрифтов и значков.",
                    "- Поставщики ИИ: OpenAI (языковые модели, распознавание речи и векторы текста для поиска) и Anthropic (языковые модели).",
                    "- Платежи: Stripe; Точка Банк — для оплаты в рублях в Telegram-боте.",
                    "- Связь: наш почтовый провайдер; FormSubmit — для форм сайта; Telegram — для бота.",
                    "- Google: для входа через Google и для сервисов Google Workspace, которые компания подключила к Нейронию.",
                    "- Консультанты (партнёры): заявки клиентов и сведения о заказе, нужные для услуги.",
                    "- Ваша компания: люди, приглашённые в аккаунт компании в Andre AI или в её пространство Нейрония, видят общие материалы компании.",
                    "- Государственные органы — когда этого требует закон.",
                ]),
                ("Передача за границу", [
                    "Часть этих сервисов обрабатывает данные за пределами вашей страны, в том числе в США. Там, где этого требует закон, "
                    "передача защищена договорными гарантиями, например стандартными договорными условиями.",
                ]),
                ("Сколько мы храним данные", [
                    "- Запросы и переписку с сайта — сколько нужно для ответа и до 3 лет после него для нашего учёта. Так же — заявки в партнёры, "
                    "которые не привели к партнёрству.",
                    "- Email для новостей — пока вы не отпишетесь.",
                    "- Аккаунт и материалы компании в Andre AI — пока существует аккаунт. По вашему запросу удаляем их вместе с журналом запросов "
                    "к нашему серверу, кроме записей, которые обязаны хранить по закону.",
                    "- Пространство Нейрония — пока оно существует. После окончания подписки пространство остаётся доступным для чтения, чтобы "
                    "компания могла забрать свои данные; удаляем его по запросу компании.",
                    "- Записи об использовании и журнал вызовов ИИ — 180 дней, затем они удаляются автоматически.",
                    "- Голосовые записи — удаляются сразу после распознавания; нераспознанная запись — через 14 дней.",
                    "- Заказы, платежи, начисления и выплаты партнёрам — столько, сколько требует закон о бухгалтерском и налоговом учёте.",
                    "- Профиль партнёра и отзывы — пока вы партнёр; после этого профиль снимаем из каталога и храним только то, что нужно "
                    "для выплат и учёта.",
                    "- Журналы серверов наших подрядчиков — по их правилам хранения.",
                ]),
                ("Защита данных", [
                    "Данные передаются по шифрованному соединению (HTTPS). Коды входа действуют 10 минут, число попыток ограничено. Ключи "
                    "подключённых сервисов и ключи моделей хранятся в защищённом хранилище и не показываются. Доступ нашей команды к данным "
                    "клиентов ограничен тем, что нужно для поддержки и исправления ошибок. Полностью защищённых систем не бывает; если утечка "
                    "затронет ваши данные, мы сообщим вам и органам по защите данных, как требует закон.",
                ]),
                ("Ваши права", [
                    "Вы можете запросить доступ к своим данным, их исправление или удаление, ограничение обработки или возразить против неё, "
                    "получить копию в переносимом формате и в любой момент отозвать согласие. Напишите на {MAIL} — ответим в течение 30 дней. "
                    "Вы также вправе пожаловаться в орган по защите персональных данных.",
                ]),
                ("Дети", [
                    "Наши сервисы предназначены для бизнеса и не рассчитаны на детей младше 16 лет. Мы сознательно не собираем их данные.",
                ]),
                ("Изменения", [
                    "Мы можем обновлять эту политику; дата последней редакции указана в начале страницы. Если изменение существенно меняет то, "
                    "как мы используем уже полученные от вас данные, мы сообщим об этом в продукте или письмом.",
                ]),
            ],
        },
    },
    "terms": {
        "en": {
            "title": "Terms of Use",
            "lead": "These terms govern the use of the website andre.technology, the partners site, Andre AI and Neuronium, operated by "
                    "Andre AI Technologies LTD (“we”, “us”), and purchases of our services. By using them or placing an order you agree "
                    "to these terms. If you accept them on behalf of a company, you confirm that you may do so.",
            "sections": [
                ("Services", [
                    "- The website andre.technology and the partners site partners.andre.technology describe our services and let you contact us "
                    "and choose a consultant.",
                    "- Andre AI: the AI maturity diagnostic (maturity.andre.technology) and the AI strategy workspace (strategy.andre.technology), "
                    "where an AI interview describes your company’s business processes and builds their schemas “as is” and “to be” and "
                    "an implementation plan.",
                    "- Neuronium: a platform where AI agents and your team run processes; each company has its own workspace at "
                    "<em>company</em>.neuronium.ai.",
                    "- Consultant services: an expert review of process schemas and a team bootcamp, delivered by certified Andre AI partners.",
                    "Partners work under the <a href=\"{partner_terms}\">Partner Program Terms</a>.",
                ]),
                ("Free services", [
                    "The AI maturity diagnostic and the interview and schema of the first business process in Andre AI are free; no payment "
                    "details are needed for them. We may change the scope of free services or stop offering them.",
                ]),
                ("Paid services", [
                    "- AI Strategy — a one-time purchase: analysis of your company’s business processes in Andre AI, their schemas and "
                    "an implementation plan, within the limits shown in the product for your order.",
                    "- Neuronium — a subscription, see “Neuronium subscription and automatic renewal”.",
                    "- Schema review — a one-time order: a consultant reviews the schemas you choose and recommends changes. The price depends on "
                    "the number of schemas at a pace of 10 schemas an hour; a complex schema or an integration beyond the basic review is priced "
                    "by a separate estimate agreed before payment.",
                    "- Bootcamp — one three-month program: 12 weekly 60-minute sessions for one team. The price is set for a team of 10 people "
                    "and does not depend on the number of participants. Before it starts, the team and the consultant agree on one or more "
                    "processes to launch in Neuronium together.",
                    "- Packages: “AI Strategy” — the strategy; “AI Platform” — the strategy and the first month of Neuronium, from the second "
                    "month the Neuronium subscription at the base price; “AI Transformation” — the strategy, three months of Neuronium and "
                    "the bootcamp, from the fourth month the Neuronium subscription at the base price. A schema review can be added to any package.",
                    "- For companies with 250 or more employees we prepare an individual estimate.",
                ]),
                ("Prices and payment", [
                    "- Prices are in US dollars and depend on the size of the company. The website shows prices “from”; before you pay, Andre AI "
                    "shows the final price and its items, any discount, the consultant’s rate and scope of work and the renewal price. The order "
                    "fixes these terms: later changes of prices or rates do not affect an order already placed.",
                    "- Prices are shown without VAT or other taxes.",
                    "- Card payments are processed by Stripe; we do not store card details. Payment codes bought in our Telegram bot are paid "
                    "in roubles through Tochka Bank and redeemed in Andre AI on the terms shown when you buy them.",
                    "- The price of a consultant service is the consultant’s hourly rate multiplied by the hours of work and divided by 0.70: "
                    "70% goes to the consultant and 30% to Andre AI.",
                ]),
                ("Neuronium subscription and automatic renewal", [
                    "- The subscription is paid monthly or yearly and renews automatically for the same period: the payment is charged to the "
                    "payment method you used until you cancel the subscription.",
                    "- From the second paid month (from the fourth in the “AI Transformation” package) the subscription is charged at the base "
                    "price for your company size. If the base price changes, the new price applies from the first renewal after we notify you.",
                    "- You can cancel at any time by writing to {MAIL} or in your account where this option is available. Cancellation takes effect "
                    "at the end of the paid period; until then the workspace works as usual. The current paid period is not refunded, except as "
                    "described in “Refunds and disputes”.",
                    "- Each month includes a budget for AI model calls made with our keys — on a yearly plan too, the budget is set per month; "
                    "the workspace shows how much has been used. At 80% we warn you; when the budget is used up, model calls with our keys stop "
                    "until the next month or a renewal. You can connect your own model API key at any time: calls made with it are not counted "
                    "against the budget and are paid to that provider under your own agreement with it.",
                    "- If a renewal is not paid, 3 days after the end of the paid period the workspace becomes read-only: you can sign in and "
                    "read everything but cannot change data or run AI until the subscription is paid. The workspace also becomes read-only when "
                    "the subscription ends.",
                ]),
                ("Consultant services", [
                    "- A schema review or a bootcamp is ordered and paid in Andre AI and delivered by a certified partner — a consultant you choose "
                    "in the catalog or one we match for you. The consultant’s rate and the scope of work are fixed in the order.",
                    "- A review is complete when the consultant has reviewed the chosen schemas and handed over the recommendations.",
                    "- The bootcamp is paid at once or, where this option is offered, in three monthly payments. Monthly payments only split "
                    "the price of the course: they are not a loan or credit, carry no interest or fees and add up exactly to the course price. "
                    "Session times are agreed with the consultant.",
                    "- If a consultant cannot deliver an ordered service, we offer another consultant or refund the part not delivered.",
                ]),
                ("Promo codes", [
                    "- A partner’s promo code gives 10% off the AI Strategy and the first paid month of Neuronium (in the “AI Transformation” "
                    "package — the first of the three months). It does not apply to schema reviews, bootcamps or later months of the subscription.",
                    "- One code applies to an order. It is entered before payment and fixed in the order. While the code is valid, it can be used "
                    "for each eligible purchase.",
                    "- The code also tells us which partner referred you: we pay that partner a commission from our share. Apart from the discount, "
                    "it does not change your price.",
                    "- Codes have no cash value. We may disable a code that is misused.",
                    "- Other codes — payment codes and campaign codes — work on the terms shown with them.",
                ]),
                ("Refunds and disputes", [
                    "- If we cannot provide a paid service or part of it, we refund the part not provided.",
                    "- Within 14 days of payment you may cancel an order that has not started — the strategy has not begun (no process beyond "
                    "the free first one has been analysed), no review has been delivered, no bootcamp session has taken place, the Neuronium "
                    "workspace has not been used in the paid period — and get a full refund. If part of the order has already been provided, "
                    "we refund the rest: bootcamp sessions not held, reviews not done, prepaid months of Neuronium that have not begun.",
                    "- Otherwise, a Neuronium period that has begun is not refunded; cancelling stops the next renewal.",
                    "- To ask for a refund, write to {MAIL} with the order details. Refunds are made to the original payment method; for card "
                    "payments your bank may take several days to show them.",
                    "- If you want to dispute a payment with your bank, please write to us first — it is usually resolved faster this way. "
                    "If the whole payment is disputed, the order is treated as unpaid: the Neuronium subscription it paid for ends and the "
                    "workspace becomes read-only.",
                    "This does not limit the rights you have under mandatory consumer protection law.",
                ]),
                ("Your account", [
                    "- You sign in with a one-time code sent to your email or with Google. Keep access to your email secure: anyone who can read "
                    "it can sign in to your account.",
                    "- The company’s account in Andre AI is managed by the person who created it: they invite colleagues, who then see the "
                    "company’s shared content.",
                    "- The services are intended for businesses and professionals. Do not use them if the law does not allow you to enter into "
                    "a contract.",
                ]),
                ("Your data and results", [
                    "- You and your company keep all rights to the data you add and to the results created for you: interview answers, process "
                    "schemas, the strategy and the plan, documents, files and Neuronium workflows.",
                    "- You allow us to store and process this content only as needed to provide, protect and support the services, including "
                    "sending it to AI model providers as described in the <a href=\"{privacy}\">Privacy Policy</a>.",
                    "- You confirm that you may share the data you add, including personal data of employees, customers and partners, and that "
                    "the people concerned have been informed where the law requires it.",
                ]),
                ("Our intellectual property", [
                    "The software of Andre AI and Neuronium, their templates, instructions for AI models, designs, texts, videos and logos belong "
                    "to Andre AI Technologies LTD or its licensors. While you use the services, you have a non-exclusive, non-transferable right "
                    "to use them for your company’s work. You may view the website and share links to it; any other copying or use requires our "
                    "written permission. If you send us suggestions, we may use them without any obligation.",
                ]),
                ("AI output", [
                    "Schemas, strategies, plans, texts and actions of AI agents are produced by AI models and may be inaccurate, incomplete or "
                    "out of date. Check them before relying on them — especially before an AI agent sends something on your company’s behalf, "
                    "makes a payment or changes data in a connected service. You decide which processes to launch and what access to give agents, "
                    "and you are responsible for the decisions and actions taken on that basis. Materials and results are not legal, financial, "
                    "tax or investment advice. Results described in case studies depend on each company and are not guaranteed.",
                ]),
                ("Acceptable use", [
                    "Do not:",
                    "- use the services in breach of the law or of other people’s rights, or to process data you have no right to process;",
                    "- send spam, malicious or misleading content, including through connected services such as email;",
                    "- try to break, overload or probe the services, get around limits or the model budget, or access other companies’ data;",
                    "- copy or resell the services, give third parties access to them without our consent, or use them to build a competing product;",
                    "- break the terms of the connected services you use through Neuronium.",
                    "We may suspend access that breaks these rules or endangers the services or other customers, and we will tell you why unless "
                    "the law prevents it.",
                ]),
                ("Third-party services", [
                    "The services rely on and link to services of other companies — Stripe, Google, Telegram, AI model providers and others. "
                    "Their own terms apply to their services, and we are not responsible for their content or availability.",
                ]),
                ("Availability and changes to the services", [
                    "We develop the services continuously and may change, add or remove features. We work to keep them available but do not "
                    "guarantee uninterrupted operation: maintenance and failures of providers may cause interruptions. If we stop a paid service, "
                    "we refund the unused part of what you paid for it.",
                ]),
                ("Ending use", [
                    "You can stop using the services at any time and ask us to delete your account and data (see the "
                    "<a href=\"{privacy}\">Privacy Policy</a>). We may end or suspend access after a serious or repeated breach of these terms "
                    "or for non-payment. Rules that by their nature should continue — on payments, refunds, intellectual property and liability — "
                    "continue to apply.",
                ]),
                ("Liability", [
                    "The services are provided “as is”. To the extent permitted by law, we are not liable for indirect losses, lost profits or "
                    "lost data, or for losses caused by interruptions, by AI output or by actions in connected services that you allowed. "
                    "Our total liability for any claim is limited to the amount you paid for the service concerned in the 12 months before the "
                    "claim. Nothing in these terms limits liability that cannot be limited by law.",
                ]),
                ("Changes and governing law", [
                    "We may update these terms; the date of the latest version is shown at the top of the page. Changes do not affect orders "
                    "already paid, and changes to the subscription apply from the next renewal. The terms are governed by the law of the country "
                    "where Andre AI Technologies LTD is registered, unless mandatory consumer law of your country provides otherwise.",
                ]),
                ("Contact", [
                    "Questions, refunds and complaints: {MAIL}. We answer within 30 days.",
                ]),
            ],
        },
        "ru": {
            "title": "Условия использования",
            "lead": "Эти условия регулируют использование сайта andre.technology, сайта партнёров, Andre AI и Нейрония, которыми управляет "
                    "Andre AI Technologies LTD («мы»), и покупку наших услуг. Пользуясь ими или оформляя заказ, вы соглашаетесь с условиями. "
                    "Если вы принимаете их от имени компании, вы подтверждаете, что вправе это сделать.",
            "sections": [
                ("Сервисы", [
                    "- Сайт andre.technology и сайт партнёров partners.andre.technology рассказывают о наших услугах и помогают связаться с нами "
                    "и выбрать консультанта.",
                    "- Andre AI: ИИ-диагностика зрелости (maturity.andre.technology) и кабинет ИИ-стратегии (strategy.andre.technology), где "
                    "ИИ-интервью описывает бизнес-процессы компании и строит их схемы «как есть» и «как будет» и план внедрения.",
                    "- Нейроний: платформа, где ИИ-агенты и ваша команда выполняют процессы; у каждой компании своё пространство по адресу "
                    "<em>компания</em>.neuronium.ai.",
                    "- Услуги консультантов: экспертная проверка схем процессов и буткемп для команды. Их оказывают сертифицированные партнёры Andre AI.",
                    "Работу партнёров регулируют <a href=\"{partner_terms}\">Условия партнёрской программы</a>.",
                ]),
                ("Бесплатные услуги", [
                    "ИИ-диагностика зрелости, а также интервью и схема первого бизнес-процесса в Andre AI бесплатны; платёжные данные для них "
                    "не нужны. Мы можем менять объём бесплатных услуг или прекратить их предоставлять.",
                ]),
                ("Платные услуги", [
                    "- ИИ-стратегия — разовая покупка: разбор бизнес-процессов компании в Andre AI, их схемы и план внедрения — в пределах, "
                    "которые продукт показывает для вашего заказа.",
                    "- Нейроний — подписка, см. «Подписка на Нейроний и автопродление».",
                    "- Проверка схем — разовый заказ: консультант проверяет выбранные вами схемы и даёт рекомендации по правкам. Цена зависит "
                    "от числа схем при темпе 10 схем в час; сложную схему или интеграцию за пределами базовой проверки оценивают отдельной "
                    "сметой, которую согласуют до оплаты.",
                    "- Буткемп — одна программа на три месяца: 12 еженедельных занятий по 60 минут для одной команды. Цена рассчитана на команду "
                    "из 10 человек и не зависит от числа участников. До начала команда и консультант согласуют один или несколько процессов, "
                    "которые запустят в Нейронии вместе.",
                    "- Пакеты: «ИИ-стратегия» — стратегия; «ИИ-платформа» — стратегия и первый месяц Нейрония, со второго месяца — подписка "
                    "на Нейроний по базовой цене; «ИИ-трансформация» — стратегия, три месяца Нейрония и буткемп, с четвёртого месяца — подписка "
                    "на Нейроний по базовой цене. К любому пакету можно добавить проверку схем.",
                    "- Для компаний от 250 сотрудников мы готовим индивидуальную смету.",
                ]),
                ("Цены и оплата", [
                    "- Цены указаны в долларах США и зависят от размера компании. На сайте — цены «от»; перед оплатой Andre AI показывает "
                    "итоговую цену и её состав, скидку, ставку и объём работы консультанта и цену продления. Заказ фиксирует эти условия: "
                    "последующие изменения цен и ставок на уже оформленный заказ не влияют.",
                    "- Цены указаны без НДС и других налогов.",
                    "- Оплата картой проходит через Stripe; данные карты мы не храним. Коды оплаты, купленные в нашем Telegram-боте, оплачиваются "
                    "в рублях через Точка Банк и вводятся в Andre AI на условиях, которые показаны при покупке.",
                    "- Цена услуги консультанта — его ставка в час, умноженная на часы работы и разделённая на 0,70: 70 % получает консультант, "
                    "30 % — Andre AI.",
                ]),
                ("Подписка на Нейроний и автопродление", [
                    "- Подписка оплачивается помесячно или за год и продлевается автоматически на тот же срок: оплата списывается со способа "
                    "оплаты, которым вы платили, пока вы не отмените подписку.",
                    "- Со второго оплаченного месяца (в пакете «ИИ-трансформация» — с четвёртого) подписка списывается по базовой цене для размера "
                    "вашей компании. Если базовая цена изменится, новая цена действует с первого продления после нашего уведомления.",
                    "- Отменить подписку можно в любой момент — письмом на {MAIL} или в аккаунте, где есть такая возможность. Отмена вступает "
                    "в силу в конце оплаченного периода; до тех пор пространство работает как обычно. Текущий оплаченный период не возвращается — "
                    "кроме случаев из раздела «Возвраты и споры».",
                    "- В каждый месяц входит бюджет на вызовы ИИ-моделей с нашими ключами — и при годовой оплате бюджет считается по месяцам; "
                    "сколько израсходовано, видно в пространстве. На 80 % мы предупреждаем, а когда бюджет исчерпан, вызовы моделей с нашими "
                    "ключами останавливаются до следующего месяца или продления. В любой момент можно подключить свой ключ API модели: вызовы "
                    "с ним не идут в бюджет и оплачиваются поставщику по вашему договору с ним.",
                    "- Если продление не оплачено, через 3 дня после конца оплаченного периода пространство переходит в режим чтения: войти "
                    "и посмотреть всё можно, а менять данные и запускать ИИ — нет, пока подписка не оплачена. В режим чтения пространство "
                    "переходит и после окончания подписки.",
                ]),
                ("Услуги консультантов", [
                    "- Проверку схем и буткемп заказывают и оплачивают в Andre AI, а оказывает их сертифицированный партнёр — консультант, "
                    "которого вы выбрали в каталоге или которого подобрали мы. Ставка и объём работы фиксируются в заказе.",
                    "- Проверка выполнена, когда консультант проверил выбранные схемы и передал рекомендации.",
                    "- Буткемп оплачивается сразу или, где такая возможность есть, тремя ежемесячными платежами. Ежемесячные платежи только "
                    "делят цену курса на части: это не заём и не кредит, без процентов и комиссий, а сумма платежей ровно равна цене курса. "
                    "Время занятий согласуется с консультантом.",
                    "- Если консультант не может оказать заказанную услугу, мы предложим другого консультанта или вернём деньги за неоказанную часть.",
                ]),
                ("Промокоды", [
                    "- Промокод партнёра даёт скидку 10 % на ИИ-стратегию и первый оплаченный месяц Нейрония (в пакете «ИИ-трансформация» — "
                    "на первый из трёх месяцев). На проверку схем, буткемп и следующие месяцы подписки он не действует.",
                    "- К заказу применяется один код. Его вводят до оплаты, и он фиксируется в заказе. Пока код действует, его можно применить "
                    "к каждой подходящей покупке.",
                    "- Код также показывает, какой партнёр вас привёл: мы платим ему комиссию из своей доли. Кроме скидки, на вашу цену это не влияет.",
                    "- Коды нельзя обменять на деньги. Код, которым злоупотребляют, мы можем отключить.",
                    "- Другие коды — коды оплаты и коды акций — действуют на условиях, которые указаны вместе с ними.",
                ]),
                ("Возвраты и споры", [
                    "- Если мы не можем оказать оплаченную услугу или её часть, мы возвращаем деньги за неоказанную часть.",
                    "- В течение 14 дней после оплаты можно отказаться от заказа, к которому ещё не приступили, — стратегия не начата (не разобран "
                    "ни один процесс сверх бесплатного первого), проверка не сдана, ни одно занятие буткемпа не прошло, пространством Нейрония "
                    "в оплаченном периоде не пользовались, — и получить полный возврат. Если часть заказа уже оказана, мы возвращаем остальное: "
                    "непроведённые занятия буткемпа, несделанные проверки, предоплаченные месяцы Нейрония, которые ещё не начались.",
                    "- В остальных случаях начавшийся период Нейрония не возвращается; отмена останавливает следующее продление.",
                    "- Чтобы запросить возврат, напишите на {MAIL} и укажите заказ. Деньги возвращаются тем же способом, которым вы платили; "
                    "при оплате картой банку может понадобиться несколько дней.",
                    "- Если вы хотите оспорить платёж через банк, сначала напишите нам — так вопрос обычно решается быстрее. Если оспорен весь "
                    "платёж, заказ считается неоплаченным: подписка на Нейроний, за которую он платил, прекращается, и пространство переходит "
                    "в режим чтения.",
                    "Это не ограничивает права, которые дают вам обязательные нормы о защите прав потребителей.",
                ]),
                ("Ваш аккаунт", [
                    "- Вход — по одноразовому коду на почту или через Google. Берегите доступ к почте: кто может её читать, может войти в ваш аккаунт.",
                    "- Аккаунтом компании в Andre AI управляет тот, кто его создал: он приглашает коллег, и они видят общие материалы компании.",
                    "- Сервисы предназначены для бизнеса и специалистов. Не пользуйтесь ими, если по закону не можете заключать договоры.",
                ]),
                ("Ваши данные и результаты", [
                    "- Все права на данные, которые вы добавляете, и на результаты, созданные для вас, — ответы интервью, схемы процессов, "
                    "стратегию и план, документы, файлы и рабочие процессы в Нейронии — остаются у вас и вашей компании.",
                    "- Вы разрешаете нам хранить и обрабатывать эти материалы только в той мере, в какой это нужно, чтобы оказывать услуги, "
                    "защищать их и поддерживать, — в том числе передавать их поставщикам ИИ-моделей, как описано в "
                    "<a href=\"{privacy}\">Политике конфиденциальности</a>.",
                    "- Вы подтверждаете, что вправе передавать добавляемые данные, в том числе персональные данные сотрудников, клиентов "
                    "и партнёров, и что люди, о которых идёт речь, уведомлены, где этого требует закон.",
                ]),
                ("Наша интеллектуальная собственность", [
                    "Программы Andre AI и Нейрония, их шаблоны, инструкции для ИИ-моделей, дизайн, тексты, видео и логотипы принадлежат "
                    "Andre AI Technologies LTD или её лицензиарам. Пока вы пользуетесь сервисами, у вас есть неисключительное право без права "
                    "передачи использовать их для работы вашей компании. Сайт можно смотреть и делиться ссылками на него; иное копирование "
                    "и использование — только с нашего письменного согласия. Если вы присылаете нам предложения, мы можем использовать их "
                    "без каких-либо обязательств.",
                ]),
                ("Результаты ИИ", [
                    "Схемы, стратегии, планы, тексты и действия ИИ-агентов создают ИИ-модели, и они могут быть неточными, неполными или "
                    "устаревшими. Проверяйте их, прежде чем на них полагаться, — особенно прежде чем ИИ-агент отправит что-то от имени компании, "
                    "проведёт платёж или изменит данные в подключённом сервисе. Вы решаете, какие процессы запускать и какой доступ давать "
                    "агентам, и отвечаете за решения и действия, принятые на этой основе. Материалы и результаты — не юридическая, финансовая, "
                    "налоговая или инвестиционная консультация. Результаты из кейсов зависят от конкретной компании и не гарантируются.",
                ]),
                ("Допустимое использование", [
                    "Нельзя:",
                    "- использовать сервисы с нарушением закона или чужих прав либо обрабатывать в них данные, на которые у вас нет права;",
                    "- рассылать спам, вредоносное или вводящее в заблуждение содержимое, в том числе через подключённые сервисы, например почту;",
                    "- пытаться взломать, перегрузить или прощупать сервисы, обходить ограничения и бюджет модели, получать доступ к данным "
                    "других компаний;",
                    "- копировать и перепродавать сервисы, давать к ним доступ третьим лицам без нашего согласия или использовать их, чтобы "
                    "сделать конкурирующий продукт;",
                    "- нарушать условия подключённых сервисов, которыми вы пользуетесь через Нейроний.",
                    "Доступ, который нарушает эти правила или угрожает сервисам и другим клиентам, мы можем приостановить и сообщим причину, "
                    "если закон этого не запрещает.",
                ]),
                ("Сторонние сервисы", [
                    "Наши сервисы опираются на сервисы других компаний — Stripe, Google, Telegram, поставщиков ИИ-моделей и других — и ведут "
                    "на них. Для их сервисов действуют их собственные условия, и мы не отвечаем за их содержимое и доступность.",
                ]),
                ("Доступность и изменения сервисов", [
                    "Мы постоянно развиваем сервисы и можем менять, добавлять и убирать функции. Мы стараемся, чтобы они были доступны, "
                    "но не гарантируем бесперебойную работу: возможны перерывы на обслуживание и сбои у поставщиков. Если мы прекратим платную "
                    "услугу, мы вернём неиспользованную часть оплаты за неё.",
                ]),
                ("Прекращение использования", [
                    "Вы можете перестать пользоваться сервисами в любой момент и попросить удалить аккаунт и данные (см. "
                    "<a href=\"{privacy}\">Политику конфиденциальности</a>). Мы можем прекратить или приостановить доступ при серьёзном или "
                    "повторном нарушении этих условий или при неоплате. Правила, которые по своей сути должны действовать и дальше, — об оплате, "
                    "возвратах, интеллектуальной собственности и ответственности — продолжают действовать.",
                ]),
                ("Ответственность", [
                    "Сервисы предоставляются «как есть». В пределах, допустимых законом, мы не отвечаем за косвенные убытки, упущенную выгоду "
                    "и потерю данных, а также за убытки из-за перебоев, результатов ИИ и действий в подключённых сервисах, которые вы разрешили. "
                    "Наша общая ответственность по любой претензии ограничена суммой, которую вы заплатили за соответствующую услугу за 12 месяцев "
                    "до претензии. Ничто в этих условиях не ограничивает ответственность, которую по закону ограничить нельзя.",
                ]),
                ("Изменения и применимое право", [
                    "Мы можем обновлять эти условия; дата последней редакции указана в начале страницы. Изменения не затрагивают уже оплаченные "
                    "заказы, а изменения подписки действуют с ближайшего продления. К условиям применяется право страны регистрации "
                    "Andre AI Technologies LTD, если обязательные нормы о защите прав потребителей вашей страны не предусматривают иного.",
                ]),
                ("Связь", [
                    "Вопросы, возвраты и жалобы: {MAIL}. Мы отвечаем в течение 30 дней.",
                ]),
            ],
        },
    },
    "partner_terms": {
        "en": {
            "title": "Partner Program Terms",
            "lead": "These terms govern the Andre AI partner program run by Andre AI Technologies LTD (“we”, “us”): how a consultant "
                    "becomes a partner, what partners earn for their services and for referred clients, and how we pay. By sending "
                    "an application you accept these terms.",
            "sections": [
                ("The program", [
                    "Partners are independent consultants certified by Andre AI. They review clients’ process schemas, run team bootcamps and help "
                    "launch processes in Neuronium, and they can bring clients with their own promo code. A partner works on their own account: "
                    "they are not our employee or representative and cannot make commitments on our behalf.",
                ]),
                ("Becoming a partner", [
                    "- Application. You send your name, email, LinkedIn profile, experience and proposed rate.",
                    "- Academy. We invite you to the Andre AI Academy course for AI consultants.",
                    "- Certificate. You take the exam on process analysis and schema review. The Andre AI team checks it manually; if you pass, "
                    "you become an Andre AI Certified Consultant.",
                    "- Interview. We go through a real case with you and agree on your rate.",
                    "- Partner. You get a partner account, a promo code and a public profile, which appears in the catalog once you turn it on.",
                    "We decide at each stage and may decline an application. Your current stage is shown in your partner account.",
                ]),
                ("Partner account", [
                    "You sign in to the partner account with a code sent to your email. There you manage your profile and rate, see your promo "
                    "code and client requests, mark a review as delivered and a bootcamp session as held, and see your earnings and payouts "
                    "by month.",
                ]),
                ("Rate and services", [
                    "- You set your own rate, from $50 an hour. A new rate applies to new orders; orders already placed keep the rate "
                    "fixed in them.",
                    "- A schema review is estimated at 10 schemas an hour. Work beyond a basic review — a complex schema or an integration — "
                    "is done under a separate estimate agreed with the client before payment.",
                    "- A bootcamp is 12 weekly 60-minute sessions over three months for one client team. Before it starts, you and the team agree "
                    "on the processes to launch.",
                    "- Other work, such as implementation or support of processes in Neuronium, is done under a separately agreed scope and estimate.",
                ]),
                ("Pay for services", [
                    "- The client pays the price of the service: your rate multiplied by the hours of work and divided by 0.70. You receive 70% "
                    "of that price, which equals your rate multiplied by the hours; Andre AI keeps 30%.",
                    "- A review is earned when you mark it delivered; a bootcamp is earned session by session as you mark sessions held, and for "
                    "all 12 sessions the sum equals the agreed pay for the course.",
                    "- You receive this pay for every service you deliver, including orders a client places directly from the catalog without "
                    "a promo code.",
                ]),
                ("Referral commission", [
                    "- Clients with your promo code get 10% off the AI Strategy and the first paid month of Neuronium (in the “AI Transformation” "
                    "package — the first of its three months).",
                    "- You receive 10% of what the client actually paid for these items after the discount, excluding VAT. Example: a $500 "
                    "strategy costs the client $450 with your code, and you receive $45.",
                    "- Commission is due only on amounts that have been paid and not refunded. If a payment is refunded or disputed, the commission "
                    "on it is reversed, also after it has been paid out.",
                    "- No commission is due on schema reviews, bootcamps or later months of the subscription, unless we agree otherwise in writing.",
                    "- Referral commission and pay for services are separate: if a client you referred orders a bootcamp from another partner, "
                    "you receive the commission and that partner receives the pay for the bootcamp. If you run it yourself, you receive both.",
                ]),
                ("Payouts", [
                    "- Your earnings are counted in US dollars and shown in your partner account by month and by order.",
                    "- After a month closes, Andre AI Technologies LTD pays the amount due for that month, once a month, to the payment details "
                    "you provide. Payouts are made manually.",
                    "- You are responsible for correct payment details. We may ask for the information we need to make the payment lawfully, "
                    "such as an invoice or tax details.",
                    "- If a client’s payment is refunded or disputed after we have paid you, the correction is deducted from your next payouts.",
                ]),
                ("Taxes", [
                    "Your rate and all amounts you receive are before your taxes. You pay your own taxes, registrations and contributions in your "
                    "country.",
                ]),
                ("Quality and conduct", [
                    "- Deliver services professionally, on time and within the agreed scope; answer client requests within a reasonable time.",
                    "- Keep clients’ data confidential and use it only to deliver the service; do not take it out of Andre AI or Neuronium beyond "
                    "what the work requires, and follow data protection law.",
                    "- Describe Andre AI, Neuronium, prices and results accurately; do not promise prices, discounts or results that we do not "
                    "offer, and do not present yourself as our employee.",
                    "- Promote your code honestly: no spam, no misleading ads, no fake reviews.",
                    "- You are responsible for the quality of your services and for your conduct towards clients.",
                ]),
                ("Public profile and reviews", [
                    "- Your profile is published in the public catalog — on the partners site and in Andre AI — only after you turn on “show in "
                    "catalog” in your partner account. You can turn it off at any time.",
                    "- The profile shows your name, headline, about, city and country, languages, services, industries, skills, rate, LinkedIn "
                    "link, certificates, rating, number of completed projects and client reviews. You confirm that what it says is true and that "
                    "you may publish it.",
                    "- Certificates are added by us. Clients rate completed services; the rating is the average of published reviews. We may hide "
                    "a review that is abusive or not about the service, but we do not edit reviews.",
                ]),
                ("Use of our name", [
                    "While you are a certified partner, you may call yourself an Andre AI Certified Consultant and link to your profile. Any other "
                    "use of our names and logos requires our permission.",
                ]),
                ("Ending the partnership", [
                    "- You may leave the program at any time by writing to {MAIL}. We may end or suspend a partnership for a breach of these terms, "
                    "client complaints we have confirmed, or misconduct.",
                    "- When the partnership ends, your profile is removed from the catalog and your promo code is disabled. Services in progress "
                    "are completed or, in agreement with the client, passed to another partner or refunded to the client.",
                    "- What you earned for services delivered and the commission on payments received before the end, minus refund corrections, "
                    "is paid with the next monthly payout.",
                ]),
                ("Changes", [
                    "We may change these terms, the commission and the program, and we tell partners about changes by email before they take "
                    "effect. Changes do not affect orders already paid: they keep the terms fixed in them.",
                ]),
                ("Liability", [
                    "To the extent permitted by law, neither side is liable to the other for indirect losses or lost profits. Our liability "
                    "to a partner is limited to the amounts due to the partner under these terms.",
                ]),
                ("Personal data and governing law", [
                    "How we handle the personal data of partners and clients is described in the <a href=\"{privacy}\">Privacy Policy</a>; "
                    "the use of our services is also governed by the <a href=\"{terms}\">Terms of Use</a>. These terms are governed by the law "
                    "of the country where Andre AI Technologies LTD is registered, unless mandatory law of your country provides otherwise.",
                ]),
                ("Contact", [
                    "Questions about the program: {MAIL}.",
                ]),
            ],
        },
        "ru": {
            "title": "Условия партнёрской программы",
            "lead": "Эти условия регулируют партнёрскую программу Andre AI, которую ведёт Andre AI Technologies LTD («мы»): как консультант "
                    "становится партнёром, сколько партнёр получает за свои услуги и за приведённых клиентов и как мы платим. Отправляя "
                    "заявку, вы принимаете эти условия.",
            "sections": [
                ("Программа", [
                    "Партнёры — независимые консультанты, сертифицированные Andre AI. Они проверяют схемы процессов клиентов, проводят буткемпы "
                    "для команд и помогают запускать процессы в Нейронии, а также могут приводить клиентов по своему промокоду. Партнёр работает "
                    "самостоятельно: он не наш сотрудник и не представитель и не может брать обязательства от нашего имени.",
                ]),
                ("Как стать партнёром", [
                    "- Заявка. Вы присылаете имя, email, профиль LinkedIn, опыт и желаемую ставку.",
                    "- Академия. Мы приглашаем вас на курс Академии Andre AI для ИИ-консультантов.",
                    "- Сертификат. Вы сдаёте экзамен по разбору процессов и проверке схем. Команда Andre AI проверяет его вручную; если экзамен "
                    "сдан, вы становитесь Andre AI Certified Consultant.",
                    "- Собеседование. Разбираем с вами реальный кейс и согласуем ставку.",
                    "- Партнёр. Вы получаете кабинет партнёра, промокод и публичный профиль, который появляется в каталоге, когда вы его включите.",
                    "Решение на каждой ступени принимаем мы и можем отказать в заявке. Текущая ступень видна в кабинете партнёра.",
                ]),
                ("Кабинет партнёра", [
                    "Вход в кабинет партнёра — по коду на почту. В кабинете вы ведёте профиль и ставку, видите свой промокод и заявки клиентов, "
                    "отмечаете «Проверка сдана» и «Занятие проведено» и видите начисления и выплаты по месяцам.",
                ]),
                ("Ставка и услуги", [
                    "- Ставку вы назначаете сами — от $50 в час. Новая ставка действует для новых заказов; оформленные заказы сохраняют "
                    "ставку, зафиксированную в них.",
                    "- Проверка схем считается по темпу 10 схем в час. Работа сверх базовой проверки — сложная схема или интеграция — делается "
                    "по отдельной смете, согласованной с клиентом до оплаты.",
                    "- Буткемп — 12 еженедельных занятий по 60 минут за три месяца для одной команды клиента. До начала вы с командой "
                    "согласуете процессы для запуска.",
                    "- Другая работа — например, внедрение или поддержка процессов в Нейронии — делается по отдельно согласованному объёму и смете.",
                ]),
                ("Оплата услуг", [
                    "- Клиент платит цену услуги: вашу ставку, умноженную на часы работы и разделённую на 0,70. Вы получаете 70 % этой цены — "
                    "то есть ставку, умноженную на часы; Andre AI оставляет себе 30 %.",
                    "- Проверка начисляется, когда вы отмечаете её сданной; буткемп — по занятиям, по мере того как вы отмечаете их проведёнными, "
                    "и за все 12 занятий сумма равна согласованной оплате за курс.",
                    "- Эту оплату вы получаете за каждую оказанную услугу, в том числе по заказам, которые клиент оформил прямо из каталога "
                    "без промокода.",
                ]),
                ("Комиссия за привлечение", [
                    "- Клиенты с вашим промокодом получают скидку 10 % на ИИ-стратегию и первый оплаченный месяц Нейрония (в пакете "
                    "«ИИ-трансформация» — на первый из трёх месяцев).",
                    "- Вы получаете 10 % от суммы, которую клиент фактически заплатил за эти позиции после скидки, без НДС. Пример: стратегия "
                    "за $500 с вашим кодом стоит клиенту $450, вы получаете $45.",
                    "- Комиссия начисляется только на оплаченные и не возвращённые суммы. При возврате или оспаривании платежа комиссия с него "
                    "списывается — и после того, как её уже выплатили.",
                    "- На проверку схем, буткемп и следующие месяцы подписки комиссия не начисляется, если мы письменно не договорились иначе.",
                    "- Комиссия за привлечение и оплата услуг — отдельные выплаты: если приведённый вами клиент заказал буткемп у другого партнёра, "
                    "вы получаете комиссию, а тот партнёр — оплату буткемпа. Если буткемп проводите вы сами, вы получаете и то и другое.",
                ]),
                ("Выплаты", [
                    "- Начисления считаются в долларах США и видны в кабинете партнёра по месяцам и по заказам.",
                    "- После закрытия месяца Andre AI Technologies LTD выплачивает сумму, причитающуюся за этот месяц, — раз в месяц, "
                    "по реквизитам, которые вы указали. Выплаты делаются вручную.",
                    "- За правильность реквизитов отвечаете вы. Мы можем попросить сведения, без которых не можем законно провести платёж, "
                    "например счёт или налоговые данные.",
                    "- Если платёж клиента вернули или оспорили после выплаты, корректировка вычитается из следующих выплат.",
                ]),
                ("Налоги", [
                    "Ваша ставка и все суммы, которые вы получаете, указаны до ваших налогов. Налоги, регистрацию и взносы в своей стране вы "
                    "платите сами.",
                ]),
                ("Качество и поведение", [
                    "- Оказывайте услуги профессионально, в срок и в согласованном объёме; отвечайте на заявки клиентов в разумный срок.",
                    "- Храните данные клиентов в тайне и используйте их только для услуги; не выносите их из Andre AI и Нейрония сверх того, "
                    "что требует работа, и соблюдайте законы о персональных данных.",
                    "- Рассказывайте об Andre AI, Нейронии, ценах и результатах точно; не обещайте цен, скидок и результатов, которых мы "
                    "не предлагаем, и не представляйтесь нашим сотрудником.",
                    "- Продвигайте промокод честно: без спама, вводящей в заблуждение рекламы и поддельных отзывов.",
                    "- За качество своих услуг и поведение с клиентами отвечаете вы.",
                ]),
                ("Публичный профиль и отзывы", [
                    "- Профиль публикуется в открытом каталоге — на сайте партнёров и в Andre AI — только после того, как вы включите «Показывать "
                    "в каталоге» в кабинете партнёра. Выключить показ можно в любой момент.",
                    "- В профиле видны имя, заголовок, «о себе», город и страна, языки, услуги, отрасли, навыки, ставка, ссылка на LinkedIn, "
                    "сертификаты, рейтинг, число выполненных проектов и отзывы клиентов. Вы подтверждаете, что сведения в нём правдивы и вы "
                    "вправе их публиковать.",
                    "- Сертификаты добавляем мы. Оценки ставят клиенты за выполненные услуги; рейтинг — среднее по опубликованным отзывам. "
                    "Отзыв с оскорблениями или не об услуге мы можем скрыть, но отзывы не редактируем.",
                ]),
                ("Наше имя", [
                    "Пока вы сертифицированный партнёр, вы можете называть себя Andre AI Certified Consultant и давать ссылку на свой профиль. "
                    "Иное использование наших названий и логотипов — только с нашего разрешения.",
                ]),
                ("Окончание партнёрства", [
                    "- Выйти из программы можно в любой момент — письмом на {MAIL}. Мы можем прекратить или приостановить партнёрство при "
                    "нарушении этих условий, подтверждённых жалобах клиентов или недобросовестном поведении.",
                    "- Когда партнёрство заканчивается, профиль снимается из каталога, а промокод отключается. Начатые услуги доводятся до конца "
                    "или, по договорённости с клиентом, передаются другому партнёру либо деньги за них возвращаются клиенту.",
                    "- Заработанное за оказанные услуги и комиссию с платежей, полученных до окончания, за вычетом корректировок по возвратам "
                    "мы выплачиваем со следующей ежемесячной выплатой.",
                ]),
                ("Изменения", [
                    "Мы можем менять эти условия, размер комиссии и устройство программы и сообщаем партнёрам об изменениях письмом до того, "
                    "как они вступят в силу. Изменения не затрагивают уже оплаченные заказы: для них действуют условия, зафиксированные в заказе.",
                ]),
                ("Ответственность", [
                    "В пределах, допустимых законом, ни одна сторона не отвечает перед другой за косвенные убытки и упущенную выгоду. Наша "
                    "ответственность перед партнёром ограничена суммами, причитающимися ему по этим условиям.",
                ]),
                ("Персональные данные и применимое право", [
                    "Как мы обращаемся с персональными данными партнёров и клиентов, описано в <a href=\"{privacy}\">Политике "
                    "конфиденциальности</a>; пользование нашими сервисами регулируют и <a href=\"{terms}\">Условия использования</a>. К этим "
                    "условиям применяется право страны регистрации Andre AI Technologies LTD, если обязательные нормы вашей страны "
                    "не предусматривают иного.",
                ]),
                ("Связь", [
                    "Вопросы о программе: {MAIL}.",
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
  .hdr-r a { color: var(--tx3); } .hdr-r a:hover, .hdr-r a.on, .hdr-r a.active { color: #fff; }
  .lang-switch { display: flex; gap: 0.35rem; align-items: center; } .lang-switch span { color: rgba(255,255,255,0.25); }
  main { max-width: 46rem; margin: 0 auto; padding: clamp(2rem, 7vw, 4.5rem) clamp(16px, 4vw, 24px) 3rem; }
  h1 { margin: 0 0 0.6rem; font-size: clamp(26px, 5vw, 40px); line-height: 1.15; font-weight: 800; text-transform: uppercase; letter-spacing: -0.01em;
    background: linear-gradient(100deg, #ff8a33 0%, #a071ff 80%); -webkit-background-clip: text; background-clip: text; color: transparent; }
  .upd { margin: 0 0 1.8rem; font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--tx3); }
  .lead { margin: 0 0 2.2rem; font-size: 16px; color: var(--tx2); }
  h2 { margin: 2.2rem 0 0.7rem; font-size: 15px; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; color: #fff; scroll-margin-top: 5.5rem; }
  h2::before { content: ''; display: inline-block; width: 0.55rem; height: 0.55rem; margin-right: 0.7rem; border-radius: 50%; background: linear-gradient(135deg, var(--p), var(--o)); vertical-align: 0.08em; }
  h3 { margin: 1.5rem 0 0.5rem; font-size: 14px; font-weight: 700; letter-spacing: 0.04em; color: #fff; }
  p, li { color: var(--tx2); overflow-wrap: break-word; } p { margin: 0 0 0.8rem; }
  ul { margin: 0 0 0.8rem; padding-left: 1.2rem; } li { margin: 0 0 0.45rem; } li::marker { color: var(--o2); }
  em { font-style: italic; color: var(--tx); }
  /* NFR-SITE114: документы длинные — оглавление со ссылками на разделы, в стиле страницы */
  .toc { margin: 0 0 2.4rem; padding: 1rem 1.2rem 0.7rem; border: 1px solid var(--line); border-radius: 14px; }
  .toc-h { margin: 0 0 0.5rem; font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--tx3); }
  .toc ol { margin: 0; padding-left: 1.6rem; columns: 2 15rem; column-gap: 2rem; font-size: 13px; line-height: 1.5; }
  .toc li { margin: 0 0 0.3rem; break-inside: avoid; } .toc li::marker { color: var(--tx3); }
  .toc a { display: inline-block; padding: 0.15rem 0; color: var(--tx2); } .toc a:hover { color: #fff; }
  .foot { max-width: 46rem; margin: 0 auto; padding: 1.6rem clamp(16px, 4vw, 24px) 2.6rem; border-top: 1px solid var(--line); display: flex; flex-wrap: wrap; gap: 0.6rem 1.6rem;
    font-size: 11.5px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--tx3); }
  .foot a { color: var(--tx3); } .foot a:hover { color: #fff; }
"""

# Значки: у страниц сайта — от корня; у условий партнёров — свои копии из partners/ относительным путём
# (на поддомене путь от корня ушёл бы в /partners/… чужой папки, NFR-SITE110).
ICONS_ROOT = """<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png">
<link rel="icon" type="image/png" sizes="48x48" href="/favicon-48x48.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">"""

ICONS_PARTNERS = """<link rel="icon" href="{up}favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="{up}favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="{up}favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="{up}apple-touch-icon.png">"""

PAGE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#050505">
<meta name="color-scheme" content="dark">
<title>{title} | Andre AI Technologies</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="en" href="{canon_en}">
<link rel="alternate" hreflang="ru" href="{canon_ru}">
<meta name="robots" content="index, follow">
{icons}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&display=swap" rel="stylesheet">
<!-- FR-SITE96, FR-SITE150…152: юридическая страница; собрана tools/build_legal.py — правки текста там, не здесь -->
<style>{css}</style>
</head>
<body>
<header class="hdr">
  <a class="logo" href="{home}" aria-label="Andre AI Technologies"><img src="{logo}" alt="AIT" width="42" height="42"></a>
  <nav class="hdr-r">
    <a href="{home}">{ui_home}</a>
    <span class="lang-switch"><a class="lang-opt{en_on}" data-lang="en" href="{href_en}">EN</a><span>|</span><a class="lang-opt{ru_on}" data-lang="ru" href="{href_ru}">RU</a></span>
  </nav>
</header>
<main>
  <h1>{title}</h1>
  <p class="upd">{ui_updated}: {updated}</p>
  <p class="lead">{lead}</p>
  <nav class="toc" aria-labelledby="toc-h">
    <p class="toc-h" id="toc-h">{ui_toc}</p>
    <ol>
{toc}
    </ol>
  </nav>
{body}
</main>
<footer class="foot">
  <span>{copy}</span>
{foot_links}
  <a href="mailto:{email}">{email}</a>
</footer>
<script>
  /* язык страницы запоминается для главной, биографии, курса и сайта партнёров — общий ключ ait_lang */
  try {{ localStorage.setItem('ait_lang', '{lang}'); }} catch (e) {{}}
</script>
</body>
</html>
"""


def is_partners(kind):
    """Страница из папки partners/ — её отдают два адреса (NFR-SITE110, NFR-SITE114)."""
    return PATHS[kind]["en"].startswith("/partners/")


def href(target, lang, kind, page_lang):
    """Адрес документа target на языке lang для ссылки со страницы kind на языке page_lang."""
    if is_partners(kind):
        if target == kind:
            # переключатель языка внутри папки: partners/terms/ ↔ partners/terms/ru/ — относительно
            if page_lang == "en":
                return "ru/" if lang == "ru" else "./"
            return "./" if lang == "ru" else "../"
        return SITE + PATHS[target][lang]
    return PATHS[target][lang]


def _links(text, lang, kind):
    """{MAIL} и {privacy}/{terms}/{partner_terms} → готовые адреса для этой страницы."""
    def sub(m):
        key = m.group(1)
        return MAIL if key == "MAIL" else href(key, lang, kind, lang)
    return re.sub(r"\{(MAIL|privacy|terms|partner_terms)\}", sub, text)


def _typo(text, lang):
    """Правило переносов сайта (tools/typo.py): служебное слово не остаётся в конце строки. Только в тексте
    страницы — в описании для поисковиков пробелы обычные. Неразрывного дефиса U+2011 (keep_hyphen) здесь нет:
    в JetBrains Mono от Google Fonts этого знака нет, и на части устройств он выглядел как «_» (FR-SITE100)."""
    return bind_short_words(text, lang)


def _section(n, title, items, lang, kind):
    out = ['  <h2 id="s%d">%s</h2>' % (n, html.escape(title))]
    ul = []
    for it in items:
        it = _typo(_links(it, lang, kind), lang)
        if it.startswith("- "):
            ul.append("    <li>%s</li>" % it[2:])
            continue
        if ul:
            out.append("  <ul>\n" + "\n".join(ul) + "\n  </ul>"); ul = []
        if it.startswith("### "):
            out.append("  <h3>%s</h3>" % html.escape(it[4:]))
        else:
            out.append("  <p>%s</p>" % it)
    if ul:
        out.append("  <ul>\n" + "\n".join(ul) + "\n  </ul>")
    return "\n".join(out)


def render(kind, lang):
    """HTML одной страницы."""
    doc, ui = LEGAL[kind][lang], UI[lang]
    if is_partners(kind):
        up = "../" if lang == "en" else "../../"          # из partners/terms/ и partners/terms/ru/ — в partners/
        icons = ICONS_PARTNERS.format(up=up)
        home, ui_home = "%s?lang=%s" % (up, lang), ui["partners"]
    else:
        icons = ICONS_ROOT
        home, ui_home = "/?lang=%s" % lang, ui["home"]
    sections = doc["sections"]
    toc = "\n".join('      <li><a href="#s%d">%s</a></li>' % (i, html.escape(t)) for i, (t, _) in enumerate(sections, 1))
    body = "\n".join(_section(i, t, items, lang, kind) for i, (t, items) in enumerate(sections, 1))
    foot = "\n".join('  <a href="%s">%s</a>' % (href(k, lang, kind, lang), html.escape(LEGAL[k][lang]["title"]))
                     for k in ORDER if k != kind)
    return PAGE.format(
        lang=lang, title=html.escape(doc["title"]), desc=html.escape(doc["lead"]),
        canon=CANON[kind][lang], canon_en=CANON[kind]["en"], canon_ru=CANON[kind]["ru"], icons=icons,
        css=CSS, home=home, logo=LOGO, ui_home=ui_home,
        en_on=" active" if lang == "en" else "", ru_on=" active" if lang == "ru" else "",
        href_en=href(kind, "en", kind, lang), href_ru=href(kind, "ru", kind, lang),
        ui_updated=ui["updated"], updated=UPDATED[lang], lead=_typo(doc["lead"], lang), ui_toc=ui["toc"],
        toc=toc, body=body, copy=ui["copy"], foot_links=foot, email=EMAIL)


def build():
    written = []
    for kind in ORDER:
        for lang in ("en", "ru"):
            rel = PATHS[kind][lang].strip("/") + "/index.html"
            path = os.path.join(ROOT, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(render(kind, lang))
            written.append(rel)
    return written


if __name__ == "__main__":
    for rel in build():
        print("written", rel)
