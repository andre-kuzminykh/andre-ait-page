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
    "cta_how": "See how it works",

    # ── 1. Первый экран ──
    "h1": ('<span class="l"><span class="lm">Where should</span>'
           '<span class="lm"><span class="hl-o">you</span> start</span></span>'
           '<span class="l"><span class="lm">with <span class="hl-p">AI</span></span>'
           '<span class="lm">in your <span class="hl-o">business</span>?</span></span>'),
    # Первая фраза стоит отдельной строкой: одной строкой «Tell how… operating
    # model,» требует 597px, а колонка текста рядом с роликом даёт 502–621.
    # Перенос владельца перед «the AI agents…» сохранён.
    "hero_lead": ('<span class="l">Tell how your business works.</span>'
                  '<span class="l">Get an AI-First operating model,</span>'
                  '<span class="l">the AI agents you need, and an implementation roadmap</span>'),

    # ── 3. Цифры ──
    "n_eyebrow": "The market today",
    "n_head": 'Using <span class="hl-p">AI</span> is not the same as becoming <span class="hl-p">AI-First</span>',
    "numbers": [
        ("76%", "SMBs use AI"),
        ("14%", "use it in core operations"),
        ("81%", "don’t know how to use it effectively"),
        ("73%", '<span class="l">need more support</span><span class="l">to implement AI</span>'),
    ],
    "n_foot": "Don’t let your competitors get ahead with AI",

    # ── 4. Кейсы ──
    "b_eyebrow": "Use cases",
    "b_head": ('<span class="l">Built for the way your <span class="hl-o">business</span></span>'
               '<span class="l">actually <span class="hl-p">works</span></span>'),
    "biz_explore": "",
    "businesses": [
        ("Consulting Business", "Revenue growth"),
        ("Recruitment Agency", "Hiring speed"),
        ("Marketing Agency", "Return on marketing"),
        ("Content Agency", "Audience engagement"),
        ("Call Center", "Cost per call"),
        ("Customer Support", "Customer satisfaction"),
        ("Design Agency", "Delivery speed"),
        ("Software Development", "Launch speed"),
    ],
    "b_all": "Explore all business types",

    # ── 5. Решение ──
    "d_eyebrow": "Solution",
    "d_head": ('<span class="l">An <span class="hl-p">AI-First</span> operating model</span>'
               '<span class="l">for your <span class="hl-o">business</span></span>'),
    "d_sub": "Built around how your business actually works",
    "deliverables": [
        ("AI Maturity Index", '<span class="l">See where you stand</span>'
                              '<span class="l">— and what’s holding you back</span>'),
        ("Process Map", '<span class="l">Your business broken down</span>'
                         '<span class="l">into processes</span>'),
        ("Cognitive Map", '<span class="l">How people think</span>'
                           '<span class="l">and use knowledge</span>'),
        ("AI Opportunities", "Operations AI can take over, with potential impact"),
        ("Human + AI", '<span class="l">Who does what</span><span class="l">— human or AI</span>'),
        ("AI-First Model", "How your business should work with AI"),
        ("AI Agents", '<span class="l">What each AI agent should do</span>'
                       '<span class="l">and how it should work</span>'),
        ("Roadmap", '<span class="l">What to implement</span><span class="l">— and in what order</span>'),
    ],
    "d_hint": "Scroll the cards",

    # ── 6. Как это работает ──
    "s_eyebrow": "How it works",
    "steps": [
        ("AI Maturity", 'Understand where <span class="hl-o">you</span> are today',
         "Assess your AI maturity and see what’s holding you back"),
        ("Voice input", "Just talk",
         "Describe how your business works"),
        ("Business Processes", 'Your <span class="hl-o">business</span> as <span class="hl-p">processes</span>',
         "I map what I heard into processes"),
        ("AI Opportunities", 'See what <span class="hl-p">AI</span> can <span class="hl-o">automate</span>',
         "Identify automatable operations by impact"),
        ("AI-First Model", 'How your <span class="hl-o">business</span> should work with <span class="hl-p">AI</span>',
         "I redesign your processes around AI"),
        ("AI Agents", 'Know <span class="hl-o">what</span> to build',
         "Each AI agent becomes a build-ready specification"),
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
        "s2_cards": [("Lead arrives", "human"), ("CRM update", "sys"), ("Qualification", "human"),
                     ("Meeting", "human"), ("Proposal", "human"), ("Follow-up", "human")],
        "s3_bar": "Sales process",
        "s3_cards": [("Lead arrives", "human"), ("CRM update", "sys"), ("Qualification", "human"),
                     ("Meeting", "human"), ("Proposal", "human"), ("Follow-up", "human")],
        "s4_bar": "AI Opportunities",
        "s4_ops": [("Lead arrives", 0), ("CRM update", 1), ("Qualification", 1), ("Meeting", 0),
                   ("Proposal", 1), ("Follow-up", 0), ("Document analysis", 1), ("Reporting", 1)],
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
    "l_head": 'New <span class="hl-o">business</span> model. New <span class="hl-p">roles</span>',
    "l_sub": ("<span class=\"l\">Free training helps your team learn how to work with AI</span>"
              "<span class=\"l\">and build agents themselves</span>"),
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
    "pr_head": 'Start <span class="hl-p">free</span>. Scale as you <span class="hl-o">grow</span>',
    "pr_sub": "One-time purchase. No subscription required",
    "plans": [
        ("", "Free", "$0", "1 process", "Start free"),
        ("", "Startup", "$59", "60 operations", "Choose Startup"),
        ("", "SMB", "$199", "300 operations", "Choose SMB"),
        ("best", "Company", "$499", "1,000 operations", "Choose Company"),
    ],
    "best_value": "Best value",
    "compare": [("Consulting firm — $100K+", True), ("AI consultant — $10K+", True),
                ("Build your AI strategy yourself", False)],

    # ── 9. Финал ──
    "f_1": 'Where should <span class="hl-o">you</span> start with <span class="hl-p">AI</span>?',
    "f_2": "You don’t need to know",
    "f_3": '<span class="hl-p">AI</span> Strategy shows <span class="hl-o">you</span>',
    "f_cta": "Start AI transformation",
    "legal": ["Privacy Policy", "Terms of Use"],
    "company": "Andre AI Technologies",
}

RU = {
    "title": "AI Strategy | С чего начать внедрять ИИ в вашем бизнесе?",
    "meta_desc": "AI Strategy показывает, как трансформировать бизнес с помощью ИИ: расскажите, как работает компания, и получите AI-First операционную модель, спецификации ИИ-агентов и дорожную карту",
    "video_aria": "Андре рассказывает про AI Strategy",
    "role": "ИИ-стратегия",
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

    "h1": ('<span class="l"><span class="lm">С чего начать</span>'
           '<span class="lm">внедрять</span></span>'
           '<span class="l"><span class="lm"><span class="hl-p">ИИ</span> в вашем</span>'
           '<span class="lm"><span class="hl-o">бизнесе</span>?</span></span>'),
    "hero_lead": ('<span class="l">Расскажите, как работает ваш бизнес.</span>'
                  '<span class="l">Получите AI-First операционную модель,</span>'
                  '<span class="l">нужных ИИ-агентов и дорожную карту внедрения</span>'),

    "n_eyebrow": "Рынок сегодня",
    "n_head": 'Пользоваться <span class="hl-p">ИИ</span> и быть <span class="hl-p">AI-First</span> — не одно и то же',
    "numbers": [
        ("76%", "малых и средних компаний используют ИИ"),
        ("14%", "встроили его в основную работу"),
        ("81%", "не знают, как применять его эффективно"),
        ("73%", '<span class="l">нужна поддержка</span><span class="l">во внедрении</span>'),
    ],
    "n_foot": "Не дайте конкурентам уйти вперёд с ИИ",

    "b_eyebrow": "Кейсы",
    "b_head": ('<span class="l">Собрано под то, как ваш <span class="hl-o">бизнес</span></span>'
               '<span class="l"><span class="hl-p">работает</span> на самом деле</span>'),
    "biz_explore": "",
    "businesses": [
        ("Консалтинг", "Рост выручки"),
        ("Кадровое агентство", "Скорость найма"),
        ("Маркетинговое агентство", "Отдача от маркетинга"),
        ("Контент-агентство", "Вовлечённость аудитории"),
        ("Колл-центр", "Стоимость звонка"),
        ("Поддержка клиентов", "Удовлетворённость клиентов"),
        ("Дизайн-агентство", "Скорость поставки"),
        ("Разработка ПО", "Скорость запуска"),
    ],
    "b_all": "Посмотреть все типы бизнеса",

    "d_eyebrow": "Решение",
    "d_head": ('<span class="l"><span class="hl-p">AI-First</span> операционная модель</span>'
               '<span class="l">вашего <span class="hl-o">бизнеса</span></span>'),
    "d_sub": "Построена вокруг того, как ваш бизнес работает на самом деле",
    "deliverables": [
        ("Индекс ИИ-зрелости", '<span class="l">Где вы сейчас</span><span class="l">— и что вас тормозит</span>'),
        ("Карта процессов", '<span class="l">Ваш бизнес, разложенный</span>'
                             '<span class="l">на процессы</span>'),
        ("Когнитивная карта", '<span class="l">Как люди думают</span>'
                               '<span class="l">и используют знания</span>'),
        ("Возможности ИИ", "Операции, которые ИИ может взять на себя, с потенциальным эффектом"),
        ("Человек + ИИ", '<span class="l">Кто что делает</span><span class="l">— человек или ИИ</span>'),
        ("AI-First модель", "Как ваш бизнес должен работать с ИИ"),
        ("ИИ-агенты", '<span class="l">Что должен делать каждый агент</span>'
                       '<span class="l">и как он должен работать</span>'),
        ("Дорожная карта", '<span class="l">Что внедрять</span><span class="l">— и в каком порядке</span>'),
    ],
    "d_hint": "Листайте карточки",

    "s_eyebrow": "Как это работает",
    "steps": [
        ("ИИ-зрелость", 'Понять, где <span class="hl-o">вы</span> сейчас',
         "Оцените ИИ-зрелость, и вы увидите, что тормозит компанию"),
        ("Голос", "Просто расскажите",
         "Расскажите, как работает бизнес"),
        ("Бизнес-процессы", 'Ваш <span class="hl-o">бизнес</span> как <span class="hl-p">процессы</span>',
         "Я разложу услышанное на бизнес-процессы"),
        ("Возможности ИИ", 'Что <span class="hl-p">ИИ</span> может <span class="hl-o">автоматизировать</span>',
         "Найду операции, которые ИИ возьмёт на себя"),
        ("AI-First модель", 'Как <span class="hl-o">бизнес</span> должен работать с <span class="hl-p">ИИ</span>',
         "Я перестрою процессы вокруг ИИ"),
        ("ИИ-агенты", 'Знать, <span class="hl-o">что</span> именно строить',
         "Каждый ИИ-агент превращается в готовую спецификацию к разработке"),
    ],
    "stage": {
        "dims": ["Стратегия", "Люди", "Инфраструктура", "Данные", "Модели", "Внедрение", "R&D"],
        "s1_bar": "Индекс ИИ-зрелости",
        "s1_score": "",
        "s2_bar": "Ваши слова",
        "s2_quote": ("«Большинство заявок приходит с сайта. Менеджер квалифицирует их, "
                     "назначает созвон и отправляет предложение. Если клиент замолчал — "
                     "пишем вручную, и всё это руками заносится в CRM…»"),
        "s2_cards": [("Пришёл лид", "human"), ("Обновление CRM", "sys"), ("Квалификация", "human"),
                     ("Встреча", "human"), ("Предложение", "human"), ("Follow-up", "human")],
        "s3_bar": "Процесс продаж",
        "s3_cards": [("Пришёл лид", "human"), ("Обновление CRM", "sys"), ("Квалификация", "human"),
                     ("Встреча", "human"), ("Предложение", "human"), ("Follow-up", "human")],
        "s4_bar": "Возможности ИИ",
        "s4_ops": [("Пришёл лид", 0), ("Обновление CRM", 1), ("Квалификация", 1), ("Встреча", 0),
                   ("Предложение", 1), ("Follow-up", 0), ("Разбор документов", 1), ("Отчётность", 1)],
        "s5_bar": "AI-First модель",
        "s5_flow": [("Пришёл лид", "human"), ("ИИ-квалификация", "ai"), ("Обновление CRM", "sys"),
                    ("Встреча", "human"), ("ИИ-предложение", "ai"), ("Follow-up", "human"),
                    ("ИИ-отчётность", "ai")],
        "s6_bar": "ИИ-агент квалификации продаж",
        "s6_name": "ИИ-агент квалификации продаж",
        "s6_spokes": ["Функции", "Входы", "Выходы", "Системы", "Правила", "Метрики", "Роль человека", "Инструкции"],
    },

    "l_eyebrow": "Обучение",
    "l_head": 'Новая <span class="hl-o">бизнес</span>-модель. Новые <span class="hl-p">роли</span>',
    "l_sub": ("<span class=\"l\">Бесплатное обучение помогает команде работать с ИИ</span>"
              "<span class=\"l\">и собирать агентов самостоятельно</span>"),
    "l_note": "Для более сложных задач — пишите мне",
    "roles": [
        ("AI Automation Engineer", "fa-robot"), ("AI Product Engineer", "fa-cubes"),
        ("AI Product Manager", "fa-compass-drafting"), ("AI Engineer", "fa-microchip"),
        ("AI CEO", "fa-crown"), ("AI CTO", "fa-screwdriver-wrench"),
        ("CAIO", "fa-brain"), ("AI Founder", "fa-rocket"),
        ("Data Engineer", "fa-database"), ("Data Analyst", "fa-chart-simple"),
        ("Data Scientist", "fa-flask"), ("ML Engineer", "fa-diagram-project"),
    ],

    "pr_eyebrow": "Тарифы",
    "pr_head": 'Начните <span class="hl-p">бесплатно</span>. Масштабируйтесь по мере <span class="hl-o">роста</span>',
    "pr_sub": "Разовая покупка. Без подписки",
    "plans": [
        ("", "Бесплатно", "$0", "1 процесс", "Начать бесплатно"),
        ("", "Стартап", "$59", "60 операций", "Выбрать «Стартап»"),
        ("", "SMB", "$199", "300 операций", "Выбрать SMB"),
        ("best", "Компания", "$499", "1 000 операций", "Выбрать «Компанию»"),
    ],
    "best_value": "Лучшее предложение",
    "compare": [("Консалтинговая компания — $100K+", True), ("ИИ-консультант — $10K+", True),
                ("Собрать ИИ-стратегию самому", False)],

    "f_1": 'С чего начать внедрять <span class="hl-p">ИИ</span>?',
    "f_2": "Вам не обязательно это знать",
    "f_3": '<span class="hl-p">ИИ</span>-стратегия <span class="hl-o">покажет</span>',
    "f_cta": "Начать ИИ-трансформацию",
    "legal": ["Политика конфиденциальности", "Условия использования"],
    "company": "Andre AI Technologies",
}
