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
    "h1": ('<span class="l">Where should you start</span>'
           '<span class="l">with <span class="hl-p">AI</span> in your <span class="hl-o">business</span>?</span>'),
    "hero_lead": "AI Strategy shows how to transform your business with AI",

    # ── 3. Цифры ──
    "n_eyebrow": "The market today",
    "n_head": 'Using <span class="hl-p">AI</span> is not the same as becoming <span class="hl-p">AI-First</span>',
    "numbers": [
        ("76%", "use AI"),
        ("14%", "use it in core operations"),
        ("81%", "don’t know how to use it effectively"),
        ("73%", "need more support to implement AI"),
    ],
    "n_foot": "Don’t let your competitors get ahead with AI",

    # ── 4. Кейсы ──
    "b_eyebrow": "Use cases",
    "b_head": ('<span class="l">Built for the way your <span class="hl-o">business</span></span>'
               '<span class="l">actually <span class="hl-p">works</span></span>'),
    "biz_explore": "",
    "businesses": [
        ("Consulting Business", "20% ↑", "Revenue growth"),
        ("Recruitment Agency", "30% ↓", "Hiring time"),
        ("Marketing Agency", "25% ↑", "Return on marketing"),
        ("Content Agency", "20% ↑", "Audience engagement"),
        ("Call Center", "30% ↓", "Cost per call"),
        ("Customer Support", "15% ↑", "Customer satisfaction"),
        ("Design Agency", "40% ↓", "Delivery time"),
        ("Software Development", "30% ↓", "Time to launch"),
    ],
    "b_all": "Explore all business types",

    # ── 5. Решение ──
    "d_eyebrow": "Solution",
    "d_head": ('<span class="l">An <span class="hl-p">AI-First</span> operating model</span>'
               '<span class="l">for your <span class="hl-o">business</span></span>'),
    "d_sub": "Built around how your business actually works",
    "deliverables": [
        ("AI Maturity Index", "See where you stand — and what’s holding you back"),
        ("Process Map", "Your business broken down into processes, in your own words"),
        ("Cognitive Map", "How people think, decide, and use knowledge"),
        ("AI Opportunities", "Operations AI can take over, with potential impact"),
        ("Human + AI", "Who does what — human or AI"),
        ("AI-First Model", "How your business should work with AI"),
        ("AI Agents", "What each AI agent should do and how it should work"),
        ("Roadmap", "What to implement — and in what order"),
    ],
    "d_hint": "Scroll the cards",

    # ── 6. Как это работает ──
    "s_eyebrow": "How it works",
    "steps": [
        ("AI Maturity", "Understand where you are today",
         "Assess your AI maturity and see what’s holding you back"),
        ("Voice input", "Just talk",
         "Describe how your business works. We turn your words into structured processes. Add your team and let employees add the details"),
        ("Processes", "Your business as processes",
         "We map what we heard into processes"),
        ("Opportunities", "See what AI can automate",
         "Identify automatable operations by impact and complexity"),
        ("AI-First Model", "See how your business should work with AI",
         "We redesign your processes around AI — automating execution and moving people to approval and supervision"),
        ("AI Agents", "Know what to build",
         "Each AI agent becomes a build-ready specification"),
    ],
    "stage": {
        "dims": ["Strategy", "People", "Infrastructure", "Data", "Models", "Implementation", "R&D"],
        "s1_bar": "AI Maturity Index",
        "s1_score": "",
        "s2_bar": "Your words",
        "s2_quote": "“We get most leads through the website, then a manager qualifies them and books a call…”",
        "s2_cards": [("Lead arrives", "human"), ("CRM update", "sys"), ("Qualification", "human")],
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
    "l_note": "For more complex cases, contact Andre AI Technologies",
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
    "pr_head": 'Start <span class="hl-p">free</span>. Scale when you <span class="hl-o">need</span>',
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
    "f_1": 'Where should you start with <span class="hl-p">AI</span>?',
    "f_2": "You don’t need to know",
    "f_3": '<span class="hl-p">AI</span> Strategy shows <span class="hl-o">you</span>',
    "f_cta": "Start your AI transformation for free",
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

    "h1": ('<span class="l">С чего начать внедрять <span class="hl-p">ИИ</span></span>'
           '<span class="l">в вашем <span class="hl-o">бизнесе</span>?</span>'),
    "hero_lead": "AI Strategy показывает, как трансформировать ваш бизнес с помощью ИИ",

    "n_eyebrow": "Рынок сегодня",
    "n_head": 'Пользоваться <span class="hl-p">ИИ</span> и быть <span class="hl-p">AI-First</span> — не одно и то же',
    "numbers": [
        ("76%", "используют ИИ"),
        ("14%", "встроили его в основную работу"),
        ("81%", "не знают, как применять его эффективно"),
        ("73%", "нужна поддержка во внедрении"),
    ],
    "n_foot": "Не дайте конкурентам уйти вперёд с ИИ",

    "b_eyebrow": "Кейсы",
    "b_head": ('<span class="l">Собрано под то, как ваш <span class="hl-o">бизнес</span></span>'
               '<span class="l"><span class="hl-p">работает</span> на самом деле</span>'),
    "biz_explore": "",
    "businesses": [
        ("Консалтинг", "20% ↑", "Рост выручки"),
        ("Кадровое агентство", "30% ↓", "Срок найма"),
        ("Маркетинговое агентство", "25% ↑", "Отдача от маркетинга"),
        ("Контент-агентство", "20% ↑", "Вовлечённость аудитории"),
        ("Колл-центр", "30% ↓", "Стоимость звонка"),
        ("Поддержка клиентов", "15% ↑", "Удовлетворённость клиентов"),
        ("Дизайн-агентство", "40% ↓", "Срок поставки"),
        ("Разработка ПО", "30% ↓", "Срок запуска"),
    ],
    "b_all": "Посмотреть все типы бизнеса",

    "d_eyebrow": "Решение",
    "d_head": ('<span class="l"><span class="hl-p">AI-First</span> операционная модель</span>'
               '<span class="l">вашего <span class="hl-o">бизнеса</span></span>'),
    "d_sub": "Построена вокруг того, как ваш бизнес работает на самом деле",
    "deliverables": [
        ("Индекс ИИ-зрелости", "Где вы сейчас — и что вас тормозит"),
        ("Карта процессов", "Ваш бизнес, разложенный на процессы вашими же словами"),
        ("Когнитивная карта", "Как люди думают, решают и используют знания"),
        ("Возможности ИИ", "Операции, которые ИИ может взять на себя, с потенциальным эффектом"),
        ("Человек + ИИ", "Кто что делает — человек или ИИ"),
        ("AI-First модель", "Как ваш бизнес должен работать с ИИ"),
        ("ИИ-агенты", "Что должен делать каждый агент и как он должен работать"),
        ("Дорожная карта", "Что внедрять — и в каком порядке"),
    ],
    "d_hint": "Листайте карточки",

    "s_eyebrow": "Как это работает",
    "steps": [
        ("ИИ-зрелость", "Понять, где вы сейчас",
         "Оцените ИИ-зрелость и увидьте, что тормозит компанию"),
        ("Голос", "Просто расскажите",
         "Расскажите, как работает бизнес. Мы превратим ваши слова в структурированные процессы. Подключите команду — сотрудники добавят детали"),
        ("Процессы", "Ваш бизнес как процессы",
         "Мы раскладываем услышанное на процессы"),
        ("Возможности", "Увидеть, что ИИ может автоматизировать",
         "Находим операции, посильные ИИ, по эффекту и сложности"),
        ("AI-First модель", "Увидеть, как бизнес должен работать с ИИ",
         "Мы перестраиваем процессы вокруг ИИ: исполнение уходит агентам, люди — к утверждению и надзору"),
        ("ИИ-агенты", "Знать, что именно строить",
         "Каждый ИИ-агент превращается в готовую к сборке спецификацию"),
    ],
    "stage": {
        "dims": ["Стратегия", "Люди", "Инфраструктура", "Данные", "Модели", "Внедрение", "R&D"],
        "s1_bar": "Индекс ИИ-зрелости",
        "s1_score": "",
        "s2_bar": "Ваши слова",
        "s2_quote": "«Большинство заявок приходит с сайта, дальше менеджер квалифицирует их и назначает созвон…»",
        "s2_cards": [("Пришёл лид", "human"), ("Обновление CRM", "sys"), ("Квалификация", "human")],
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
    "l_note": "Для более сложных задач — пишите в Andre AI Technologies",
    "roles": [
        ("AI Automation Engineer", "fa-robot"), ("AI Product Engineer", "fa-cubes"),
        ("AI Product Manager", "fa-compass-drafting"), ("AI Engineer", "fa-microchip"),
        ("AI CEO", "fa-crown"), ("AI CTO", "fa-screwdriver-wrench"),
        ("CAIO", "fa-brain"), ("AI Founder", "fa-rocket"),
        ("Data Engineer", "fa-database"), ("Data Analyst", "fa-chart-simple"),
        ("Data Scientist", "fa-flask"), ("ML Engineer", "fa-diagram-project"),
    ],

    "pr_eyebrow": "Тарифы",
    "pr_head": 'Начните <span class="hl-p">бесплатно</span>. Масштабируйте, когда <span class="hl-o">нужно</span>',
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
    "f_3": '<span class="hl-p">AI</span> Strategy <span class="hl-o">покажет</span>',
    "f_cta": "Начать ИИ-трансформацию бесплатно",
    "legal": ["Политика конфиденциальности", "Условия использования"],
    "company": "Andre AI Technologies",
}
