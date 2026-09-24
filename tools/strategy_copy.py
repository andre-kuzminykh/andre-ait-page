# -*- coding: utf-8 -*-
"""Тексты лендинга AI Strategy: английская и русская версии.

Правило владельца: точек в конце строк нет. Структуру собирает
tools/build_strategy.py, вёрстка — assets/strategy.css.
"""

EN = {
    "title": "AI Strategy | Where should you start with AI in your business?",
    "meta_desc": "AI Strategy shows how to transform your business with AI: describe how your company works and get an AI-First operating model, AI agent specifications and a roadmap",
    "video_aria": "Andre explains AI Strategy",
    "role": "AI Strategy",
    "brand": "AI Strategy",
    "back": "Back",
    "home": "Home",
    "sections": "Sections",
    "close": "Close menu",
    "menu": "Menu",
    "steps_nav": "Steps",
    "nav": ["Solution", "Use Cases", "How it works", "Learning", "Pricing", "Start"],
    "cta_href": "https://strategy.andre.technology/",
    "cta_top": "Start free",
    "cta_main": "Start for free",
    "cta_how": "How it works",

    # ── 1. Первый экран ──
    # Две строки и на вебе, и на телефоне (правка владельца). Раньше строка
    # делилась ещё и на .lm, чтобы на телефоне получалось четыре.
    "h1": ('<span class="l">Where should <span class="hl-o">you</span></span>'
           '<span class="l">start with <span class="hl-p">AI</span>?</span>'),
    "hero_lead": ('<span class="l">Tell me how your business works.</span>'
                  '<span class="l">Get your AI-First model</span>'),

    # ── 3. Цифры ──
    "n_eyebrow": "The market today",
    "n_head": ('<span class="l">Using <span class="hl-p">AI</span> is not the same</span>'
               '<span class="l">as becoming <span class="hl-p nb">AI-First</span></span>'),
    "numbers": [
        ("76%", "companies use AI"),
        ("14%", "use it in core operations"),
        ("81%", "don’t use it effectively"),
        # без ручного переноса: в узкой карточке «need more support» не влезало
        # в строку и разъезжалось само — пусть текст переносится естественно
        ("73%", "need more support to implement AI"),
    ],
    "n_foot": '<span class="nb">Don’t let your competitors get ahead with AI</span>',

    # ── 4. Кейсы ──
    "b_eyebrow": "Use cases",
    "b_head": ('<span class="l">Built for how your</span>'
               '<span class="l"><span class="hl-o">business</span> <span class="hl-p">works</span></span>'),
    "biz_explore": "",
    # третий элемент — куда двигается метрика: up (растёт) или down (падает).
    # Стрелка стоит ПЕРЕД подписью и означает улучшение: выручка вверх,
    # стоимость звонка вниз.
    "businesses": [
        ("Consulting Business", "Revenue growth", "up"),
        ("Recruitment Agency", "Hiring speed", "up"),
        ("Marketing Agency", "Return on marketing", "up"),
        ("Content Agency", "Audience engagement", "up"),
        ("Call Center", "Cost per call", "down"),
        ("Customer Support", "Customer satisfaction", "up"),
        ("Design Agency", "Delivery speed", "up"),
        ("Software Development", "Launch speed", "up"),
    ],
    "b_all": "View all business types",

    # ── 5. Решение ──
    "d_eyebrow": "Solution",
    "d_head": ('<span class="l">Your <span class="hl-p">AI-First</span></span>'
               '<span class="l">operating <span class="hl-o">model</span></span>'),
    "d_sub": "Built around your business",
    # Восемь карточек стоят СЕТКОЙ и видны целиком — лента с прокруткой убрана
    # (правка владельца «внутри себя не листать»). Поэтому подпись у каждой —
    # ровно одна короткая строка.
    "deliverables": [
        ("AI Maturity Index", "Where you stand today"),
        ("Process Map", "Your business processes"),
        ("Cognitive Map", "How people think"),
        ("AI Opportunities", "What AI can take over"),
        ("Human + AI", "Who does what"),
        ("AI-First Model", "AI for your business"),
        ("AI Agents", "What each agent does"),
        ("Roadmap", "What to implement, and when"),
    ],

    # ── 6. Как это работает ──
    "s_eyebrow": "How it works",
    "steps": [
        ("AI Maturity", 'See where <span class="hl-o">you</span> stand',
         "Assess your AI maturity. Find the gaps"),
        ("Voice input", "Just talk",
         "Describe how your business works"),
        ("Business Processes", 'Your <span class="hl-o">business</span> as <span class="hl-p">processes</span>',
         "I map what I heard into business processes"),
        ("AI Opportunities", 'See what <span class="hl-p">AI</span> can <span class="hl-o">automate</span>',
         "Operations AI can take over"),
        ("AI-First Model", '<span class="hl-p">AI</span> for your <span class="hl-o">business</span>',
         "I redesign your processes around AI"),
        ("AI Agents", 'Know <span class="hl-o">what</span> to build',
         "Build-ready agent specifications"),
    ],
    "stage": {
        "dims": ["Strategy", "People", "Infrastructure", "Data", "Models", "Implementation", "R&D"],
        "s1_bar": "AI Maturity Index",
        "s1_score": "",
        "s2_bar": "Your words",
        "s2_quote": ("“We get most leads through the website. A manager qualifies them, "
                     "books a call and sends a proposal. If the client goes quiet we follow "
                     "up manually, and everything lands in the CRM by hand…”"),
        # Шесть блоков — ровно те же, что на следующем экране (правка владельца
        # «тут можно ещё три блока, как на след. слайде»): панель на телефоне
        # перестала выглядеть полупустой, а переход 02 → 03 читается как
        # продолжение одной и той же цепочки.
        "s3_bar": "Sales process",
        "s3_cards": [("Lead arrives", "human"), ("CRM update", "sys"), ("Qualification", "human"),
                     ("Meeting", "human"), ("Proposal", "human"), ("Follow-up", "human")],
        "s4_bar": "AI Opportunities",
        "s4_ops": [("Lead arrives", "human"), ("CRM update", "sys"), ("Qualification", "ai"),
                   ("Meeting", "human"), ("Proposal", "ai"), ("Follow-up", "human"),
                   ("Document analysis", "ai"), ("Reporting", "ai")],
        "s5_bar": "AI-First Model",
        "s5_flow": [("Lead arrives", "human"), ("AI Qualification", "ai"), ("CRM update", "sys"),
                    ("Meeting", "human"), ("AI Proposal", "ai"), ("Follow-up", "human"),
                    ("AI Reporting", "ai")],
        "s6_bar": "AI Sales Qualification Agent",
        "s6_name": "AI Sales Qualification Agent",
        "s6_spokes": ["Functions", "Inputs", "Outputs", "Systems", "Rules", "Metrics", "Human role", "Instructions"],
    },

    # ── 7. Обучение ──
    "l_eyebrow": "Learning",
    "l_head": ('<span class="l">New <span class="hl-o">business</span> model</span>'
               '<span class="l">New <span class="hl-p">human</span> roles</span>'),
    "l_sub": ('<span class="l">Free training for your team</span>'
              '<span class="l">Develop AI agents yourself</span>'),
    "l_note": "For more complex cases, write to me",
    "roles": [
        ("AI Automation Engineer", "fa-robot"), ("AI Product Engineer", "fa-cubes"),
        ("AI Product Manager", "fa-compass-drafting"), ("AI Engineer", "fa-microchip"),
        ("AI CEO", "fa-crown"), ("AI CTO", "fa-screwdriver-wrench"),
        ("CAIO", "fa-brain"), ("AI Founder", "fa-rocket"),
        ("Data Engineer", "fa-database"), ("Data Analyst", "fa-chart-simple"),
        ("Data Scientist", "fa-flask"), ("ML Engineer", "fa-diagram-project"),
    ],

    # ── 8. Тарифы ──
    "pr_eyebrow": "Pricing",
    "pr_head": ('<span class="l">Start <span class="hl-p">free</span></span>'
                '<span class="l">Scale as you <span class="hl-o">grow</span></span>'),
    "pr_sub": "One-time purchase. No subscription",
    "plans": [
        ("", "Free", "$0", "1 process", "Start"),
        ("", "Startup", "$59", "60 operations", "Start"),
        ("", "SMB", "$199", "300 operations", "Start"),
        ("best", "Company", "$499", "1,000 operations", "Start"),
    ],
    "best_value": "Best value",
    "compare": [("Consulting firm — $100K+", True), ("AI consultant — $10K+", True),
                ("Build your AI strategy yourself", False)],

    # ── 9. Финал ──
    "f_1": 'Where to <span class="hl-o">start</span> with <span class="hl-p">AI</span>?',
    "f_3": '<span class="hl-p">AI</span> Strategy shows <span class="hl-o">you</span>',
    "f_cta": "Start AI transformation",
    "legal": ["Privacy Policy", "Terms of Use"],
    "company": "Andre AI Technologies",
}

RU = {
    "title": "ИИ-стратегия | С чего начать внедрять ИИ в вашем бизнесе?",
    "meta_desc": "ИИ-стратегия показывает, как трансформировать бизнес с помощью ИИ: расскажите, как работает компания, и получите AI-First операционную модель, спецификации ИИ-агентов и дорожную карту",
    "video_aria": "Андре рассказывает про ИИ-стратегию",
    "role": "ИИ-стратегия",
    "brand": "ИИ-стратегия",
    "back": "Назад",
    "home": "На главную",
    "sections": "Разделы",
    "close": "Закрыть меню",
    "menu": "Меню",
    "steps_nav": "Шаги",
    "nav": ["Решение", "Кейсы", "Как это работает", "Обучение", "Тарифы", "Начать"],
    "cta_href": "https://strategy.andre.technology/",
    "cta_top": "Начать бесплатно",
    "cta_main": "Начать бесплатно",
    "cta_how": "Как это работает",

    "h1": ('<span class="l">С чего <span class="hl-o">начать</span></span>'
           '<span class="l">внедрять <span class="hl-p">ИИ</span>?</span>'),
    "hero_lead": ('<span class="l">Расскажите, как работает ваш бизнес.</span>'
                  '<span class="l">Получите свою AI-First модель</span>'),

    "n_eyebrow": "Рынок сегодня",
    "n_head": ('<span class="l">Пользоваться <span class="hl-p">ИИ</span> и быть <span class="hl-p nb">AI-First</span></span>'
               '<span class="l">— не одно и то же</span>'),
    "numbers": [
        ("76%", "компаний используют ИИ"),
        ("14%", "встроили его в основную работу"),
        ("81%", "не применяют эффективно"),
        ("73%", '<span class="l">нужна поддержка</span><span class="l">во внедрении</span>'),
    ],
    "n_foot": '<span class="nb">Не дайте конкурентам уйти вперёд с ИИ</span>',

    "b_eyebrow": "Кейсы",
    "b_head": ('<span class="l">Собрано под ваш <span class="hl-o">бизнес</span></span>'
               '<span class="l">и то, как он <span class="hl-p">работает</span></span>'),
    "biz_explore": "",
    "businesses": [
        ("Консалтинг", "Рост выручки", "up"),
        ("Кадровое агентство", "Скорость найма", "up"),
        ("Маркетинговое агентство", "Отдача от маркетинга", "up"),
        ("Контент-агентство", "Вовлечённость аудитории", "up"),
        ("Колл-центр", "Стоимость звонка", "down"),
        ("Поддержка клиентов", "Удовлетворённость клиентов", "up"),
        ("Дизайн-агентство", "Скорость поставки", "up"),
        ("Разработка ПО", "Скорость запуска", "up"),
    ],
    "b_all": "Все типы бизнеса",

    "d_eyebrow": "Решение",
    "d_head": ('<span class="l">Ваша <span class="hl-p">AI-First</span></span>'
               '<span class="l">операционная <span class="hl-o">модель</span></span>'),
    "d_sub": "Построена вокруг вашего бизнеса",
    "deliverables": [
        ("Индекс ИИ-зрелости", "Где вы сейчас"),
        ("Карта процессов", "Ваши бизнес-процессы"),
        ("Когнитивная карта", "Как люди думают"),
        ("Возможности ИИ", "Что ИИ возьмёт на себя"),
        ("Человек + ИИ", "Кто что делает"),
        ("AI-First модель", "ИИ для вашего бизнеса"),
        ("ИИ-агенты", "Что делает каждый агент"),
        ("Дорожная карта", "Что внедрять и когда"),
    ],

    "s_eyebrow": "Как это работает",
    "steps": [
        ("ИИ-зрелость", 'Посмотрите, где <span class="hl-o">вы</span> сейчас',
         "Оцените ИИ-зрелость. Найдите пробелы"),
        ("Голос", "Просто расскажите",
         "Расскажите, как работает бизнес"),
        ("Бизнес-процессы", 'Ваш <span class="hl-o">бизнес</span> как <span class="hl-p">процессы</span>',
         "Разложу услышанное на бизнес-процессы"),
        ("Возможности ИИ", 'Что <span class="hl-o">автоматизировать</span> с <span class="hl-p">ИИ</span>',
         "Операции, которые заберёт ИИ"),
        ("AI-First модель", '<span class="hl-p">ИИ</span> для вашего <span class="hl-o">бизнеса</span>',
         "Перестрою процессы вокруг ИИ"),
        ("ИИ-агенты", '<span class="hl-o">Что</span> именно разрабатывать',
         "Готовые спецификации ИИ-агентов"),
    ],
    "stage": {
        "dims": ["Стратегия", "Люди", "Инфраструктура", "Данные", "Модели", "Внедрение", "R&D"],
        "s1_bar": "Индекс ИИ-зрелости",
        "s1_score": "",
        "s2_bar": "Ваши слова",
        "s2_quote": ("«Большинство заявок приходит с сайта. Менеджер квалифицирует их, "
                     "назначает созвон и отправляет предложение. Если клиент замолчал — "
                     "пишем вручную, и всё это руками заносится в CRM…»"),
        "s3_bar": "Процесс продаж",
        "s3_cards": [("Пришёл лид", "human"), ("Обновление CRM", "sys"), ("Квалификация", "human"),
                     ("Встреча", "human"), ("Предложение", "human"), ("Follow-up", "human")],
        "s4_bar": "Возможности ИИ",
        "s4_ops": [("Пришёл лид", "human"), ("Обновление CRM", "sys"), ("Квалификация", "ai"),
                   ("Встреча", "human"), ("Предложение", "ai"), ("Follow-up", "human"),
                   ("Разбор документов", "ai"), ("Отчётность", "ai")],
        "s5_bar": "AI-First модель",
        "s5_flow": [("Пришёл лид", "human"), ("ИИ-квалификация", "ai"), ("Обновление CRM", "sys"),
                    ("Встреча", "human"), ("ИИ-предложение", "ai"), ("Follow-up", "human"),
                    ("ИИ-отчётность", "ai")],
        "s6_bar": "ИИ-агент квалификации продаж",
        "s6_name": "ИИ-агент квалификации продаж",
        "s6_spokes": ["Функции", "Входы", "Выходы", "Системы", "Правила", "Метрики", "Роль человека", "Инструкции"],
    },

    "l_eyebrow": "Обучение",
    "l_head": ('<span class="l">Новая <span class="hl-o">бизнес</span>-модель</span>'
               '<span class="l">Новые <span class="hl-p">роли</span></span>'),
    "l_sub": ('<span class="l">Бесплатное обучение для команды</span>'
              '<span class="l">Разработайте ИИ-агентов сами</span>'),
    "l_note": "Для более сложных кейсов — пишите мне",
    "roles": [
        ("AI Automation Engineer", "fa-robot"), ("AI Product Engineer", "fa-cubes"),
        ("AI Product Manager", "fa-compass-drafting"), ("AI Engineer", "fa-microchip"),
        ("AI CEO", "fa-crown"), ("AI CTO", "fa-screwdriver-wrench"),
        ("CAIO", "fa-brain"), ("AI Founder", "fa-rocket"),
        ("Data Engineer", "fa-database"), ("Data Analyst", "fa-chart-simple"),
        ("Data Scientist", "fa-flask"), ("ML Engineer", "fa-diagram-project"),
    ],

    "pr_eyebrow": "Тарифы",
    "pr_head": ('<span class="l">Начните <span class="hl-p">бесплатно</span></span>'
                '<span class="l"><span class="hl-o">Масштабируйтесь</span> дальше</span>'),
    "pr_sub": "Разовая покупка. Без подписки",
    "plans": [
        ("", "Бесплатно", "$0", "1 процесс", "Начать"),
        ("", "Стартап", "$59", "60 операций", "Начать"),
        ("", "SMB", "$199", "300 операций", "Начать"),
        ("best", "Компания", "$499", "1 000 операций", "Начать"),
    ],
    "best_value": "Лучшее предложение",
    "compare": [("Консалтинговая компания — $100K+", True), ("ИИ-консультант — $10K+", True),
                ("Собрать ИИ-стратегию самому", False)],

    # перенос задан руками, как в шапке: строка длиннее английской и на
    # телефоне ломалась сама в разных местах
    "f_1": ('<span class="l">С чего начать</span>'
            '<span class="l"><span class="hl-o">внедрять</span> <span class="hl-p">ИИ</span>?</span>'),
    "f_3": '<span class="hl-p">ИИ</span>-стратегия <span class="hl-o">покажет</span>',
    "f_cta": "Начать ИИ-трансформацию",
    "legal": ["Политика конфиденциальности", "Условия использования"],
    "company": "Andre AI Technologies",
}
