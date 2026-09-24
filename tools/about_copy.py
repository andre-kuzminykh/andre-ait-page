# -*- coding: utf-8 -*-
"""Тексты биографии на двух языках. Структура экранов — в build_about.py,
здесь только строки: так RU и EN не могут разойтись по составу блоков.

Правила владельца (те же, что на лендинге /ai-strategy/):
  * страница листается ПО БЛОКАМ, внутри экрана ничего не прокручивается;
  * поэтому глава разрезана на несколько коротких экранов, а не ужата кеглем;
  * заголовок — максимум две строки с осмысленным переносом;
  * на телефоне и в вебе один и тот же крупный масштаб.
"""

EN = {
    "lang": "en",
    "title": "About Me | Andre AI Technologies",
    "desc": ("Andre Kuzminykh: from chess and mathematics in the Russian Far East to Chief Data "
             "Officer at Sberbank, CTO of an AI startup studio and founder of Andre AI Technologies "
             "— an AI-native ecosystem for human good."),
    "og_desc": "I build an AI-native ecosystem for human good.",
    "role": "AI Consultant",
    "cta": "Free AI Diagnostic",
    "home": "Home",
    "privacy": "Privacy Policy",
    "terms": "Terms of Use",
    "nav": {
        "childhood": "Childhood",
        "education": "Education",
        "career": "Career",
        "startups": "Startups",
        "ecosystem": "Ecosystem",
        "mission": "Mission",
    },

    # ── детство ──────────────────────────────────────────────────────────
    "eyebrow": "About Me",
    "h1": ('<span class="l">I build an <span class="hl-p"><span class="nb">AI-native</span> ecosystem</span></span>'
           '<span class="l">for <span class="hl-o">human good</span></span>'),
    "c1_lead": "I grew up in Ussuriysk, in the Russian Far East — home to the largest tigers on Earth.",
    "c1_p1": ("My grandfather gave me my first computer when I was three, and artificial intelligence "
              "became my chess opponent long before AI became part of everyday life."),

    "c2_head": "Chess and Discipline",
    "c2_p1": ("I won chess tournaments, as well as mathematics and computer science competitions. "
              "At the same time, I spent more than a decade in martial arts and later moved into "
              "powerlifting and bodybuilding."),
    "c2_p2": "Very early, I learned two things that still define the way I work today:",
    "c2_quote": "Intelligence creates possibilities, but discipline turns them into reality.",


    # ── образование ──────────────────────────────────────────────────────
    "e1_head": "From Education to AI",
    "e1_lead": "Education became my way forward.",
    "e1_facts": [
        ("fa-circle-check", "<strong>Bachelor’s degree in Business Informatics</strong><span class=\"l\">— Far Eastern Federal University</span>"),
        ("fa-circle-check", "<strong>Master’s degree in Business Informatics</strong><span class=\"l\">— Higher School of Economics, after moving to Moscow</span>"),
        ("fa-circle-check", "<strong>Diploma</strong> from the International Institute of Business Analysis"),
    ],

    "e2_head": "Research and Teaching",
    "e2_p1": ('<span class="l">Then came postgraduate research in AI and data analysis</span>'
              '<span class="l">— and teaching at universities myself.</span>'),
    "e2_p2": ("During those years, I won machine-learning competitions and the National Olympiad "
              "in Business Informatics."),
    "e2_note": ('<span class="l">University gave me the foundation.</span>'
                '<span class="l">The next step was to test it against real business.</span>'),

    # ── карьера ──────────────────────────────────────────────────────────
    "k1_head": "From Data to AI Transformation",
    "k1_p1": ("I started my professional career at <strong>Accenture</strong>, working with data "
              "for major financial institutions."),
    "k1_p2": ("Later, I joined <strong>Sberbank</strong>, the largest bank in Eastern Europe, as a "
              "<strong>Data Engineer</strong>. Over the next few years, I progressed to "
              "<strong>Chief Data Officer</strong> and <strong>Chief Data Scientist</strong>, moving "
              "from building data infrastructure to leading large-scale AI transformation."),

    "k2_head": "AI Across the Bank",
    "k2_p1": ("There, I built analytics and AI systems that helped senior management make better "
              "decisions, and led AI adoption across strategic management, macroeconomic analysis, "
              "HR, organizational design and thousands of business processes."),
    "k2_stat": ("$40M+", "The work generated more than $40 million in measurable business impact and "
                         "changed the way hundreds of people worked. I was recognized as one of the "
                         "bank’s top leaders."),

    "k3_head": "Why I Left",
    "k3_p1": ("While working at Sberbank, I also won the company’s startup accelerator with my own "
              "AI-powered dating service."),
    "k3_p2": ("That experience made something clear to me: I no longer wanted to build only inside "
              "other people’s systems. I wanted to create my own."),
    "k3_p3": "And yet, reaching a top management position taught me something even more important:",
    "k3_quote": "Status, salary and career success do not necessarily make a person free.",

    # ── стартапы ─────────────────────────────────────────────────────────
    "s1_head": "Startup Studio",
    "s1_p1": ("I wanted to create products that could be useful to people around the world. So I "
              "left my corporate career, left postgraduate studies and moved to Cyprus."),
    "s1_p2": ("There, I became <strong>CTO of an AI startup studio</strong>, building technology "
              "across very different domains."),

    "s2_head": "What I Built",
    "s2_facts": [
        ("fa-car-side", "Trained <strong>self-driving cars</strong> in simulation"),
        ("fa-bolt", "Built an <strong>AI digital twin</strong> for power-grid loss detection"),
        ("fa-users", "Helped create <strong>thousands of virtual influencers</strong>"),
        ("fa-flask", "Worked on many other AI startups across different industries"),
    ],
    "s2_stat": ("200K+", '<span class="l">One of those startups became <strong>Product of the Day</strong> and</span>'
                         '<span class="l"><strong>Product of the Week</strong> on Product Hunt</span>'
                         '<span class="l">and grew to more than 200,000 users.</span>'),

    "s3_head": "One Person, a Whole Company",
    "s3_p1": ("Over the years, I learned how to <span class=\"nb\">manage teams of engineers</span>, launch products and turn "
              "technologies into real businesses."),
    "s3_p2": ("But then something changed. As AI systems became more capable, I realized that many "
              "things that once required entire teams could now be built by one person."),
    "s3_p3": ("I started learning how to create products and launch businesses without building a "
              "traditional team. That completely <span class=\"nb\">changed the way</span> I thought about entrepreneurship."),

    "s4_head": "A System, Not a Startup",
    "s4_note": ("I no longer wanted to build another startup the old way. I wanted to build a system "
                "that would allow one person or a small team to create what previously required an "
                "entire company."),
    "s4_p1": "That idea became <strong>Andre AI Technologies</strong>.",

    # ── экосистема ───────────────────────────────────────────────────────
    "x1_head": "An AI-Native Ecosystem",
    "x1_p1": ("After more than a decade working across corporations, startups, research and "
              "education, I decided to bring everything I had learned into one system."),
    "x1_p2": "I had seen both sides of the market.",
    "x1_cards": [
        ("fa-building", "Large companies", "Had resources, but often moved too slowly.", ""),
        ("fa-bolt-lightning", "Startups", "Move fast, but limited resources constrain execution.", "o"),
    ],

    "x2_head": "Corporate Power, Startup Speed",
    "x2_note": ("My goal became to give solopreneurs and small teams the power of a corporation, "
                "while helping established companies gain the speed and adaptability of startups."),
    "x2_p1": ('<span class="l">I began working with both. I advised startups and large companies on AI strategy,</span>'
              '<span class="l">AI product development and AI transformation.</span>'),
    "x2_stat": ("$20M+", "Across these projects, the financial impact of the solutions I helped "
                         "create reached more than $20 million."),

    "x3_head": "From Advice to a System",
    "x3_p1": ('<span class="l">But consulting alone could never scale far enough.</span>'
              '<span class="l">There is only one of me, and I cannot personally work</span>'
              '<span class="l">with every entrepreneur or company that wants to transform.</span>'),
    "x3_p2": ('<span class="l">So I started turning my experience into a system: a methodology that diagnoses a business,</span>'
              '<span class="l">finds where AI can create real value and turns that</span>'
              '<span class="l">into an AI strategy with a clear direction.</span>'),
    "x3_note": "The strategy becomes the roadmap. The next step is execution.",

    "x4_head": "An AI Operating System",
    "x4_p1": ('<span class="l">Now I am building an <strong>AI operating system for business</strong>,</span>'
              '<span class="l">powered by hundreds of specialized AI employees that work across the company:</span>'),
    # Состав ролей — правка владельца: после менеджмента HR, после маркетинга
    # SMM, затем поддержка, аналитика, дизайн, разработка и инженерия.
    "x4_facts": [
        ("fa-sitemap", "Management"),
        ("fa-user-group", "HR"),
        ("fa-bullhorn", "Marketing"),
        ("fa-hashtag", "SMM"),
        ("fa-handshake", "Sales"),
        ("fa-headset", "Support"),
        ("fa-chart-simple", "Analytics"),
        ("fa-palette", "Design"),
        ("fa-code", "Development"),
        ("fa-gears", "Engineering"),
    ],

    # ── миссия ───────────────────────────────────────────────────────────
    "m1_head": "New Skills, New Roles",
    "m1_p1": ('<span class="l">A new economy needs more than technology:</span>'
              '<span class="l">new skills, new roles and new ways of working.</span>'),
    "m1_p2": ("That is why I collaborate with <strong>universities</strong> to help people prepare "
              "for emerging AI roles and make applied AI education accessible to more people. I also "
              "collaborate with <strong>research centers</strong> to develop new technologies and "
              "turn them into products that create real value."),

    "m2_head": "Parts of the Same Ecosystem",
    "m2_p1": ('<span class="l">Education, research, technology, products and business</span>'
              '<span class="l">transformation are not separate directions for me.</span>'
              '<span class="l">They are parts of the same ecosystem.</span>'),
    "m2_p2": ("I build products for my own work, turn the most useful ones into tools that others "
              "can use, and bring together entrepreneurs, researchers and engineers who want to "
              "participate in building the next economy."),
    "m2_p3": ("And I make the educational layer accessible for free. This is what I am building at "
              "<strong>Andre AI Technologies</strong>."),

    "finale": ('<span class="l">Welcome to the new economy — an economy where</span>'
               '<span class="l"><span class="hl-p">people</span> and <span class="hl-o">AI</span> '
               'work together for Human Good.</span>'),
    "finale_btn": "Start AI Transformation",
}

RU = {
    "lang": "ru",
    "title": "Обо мне | Andre AI Technologies",
    "desc": ("Андрей Кузьминых: от шахмат и олимпиад на Дальнем Востоке до директора по данным и ИИ "
             "в Сбербанке, CTO ИИ-стартап-студии и основателя Andre AI Technologies — AI-native "
             "экосистемы во благо людей."),
    "og_desc": "Я строю AI-Native экосистему во благо людей.",
    "role": "ИИ-консультант",
    "cta": "ИИ-диагностика",
    "home": "На главную",
    "privacy": "Политика конфиденциальности",
    "terms": "Условия использования",
    "nav": {
        "childhood": "Детство",
        "education": "Образование",
        "career": "Карьера",
        "startups": "Стартапы",
        "ecosystem": "Экосистема",
        "mission": "Миссия",
    },

    "eyebrow": "Обо мне",
    "h1": ('<span class="l">Я строю <span class="hl-p nb">AI-Native экосистему</span></span>'
           '<span class="l">во <span class="hl-o">благо людей</span></span>'),
    "c1_lead": ("Я родился и вырос в Уссурийске, на Дальнем Востоке — там, где живут самые крупные "
                "тигры на планете."),
    "c1_p1": ("Когда мне было три года, дедушка купил мне первый компьютер, и искусственный интеллект "
              "стал моим соперником по шахматам задолго до того, как ИИ вошёл в повседневную жизнь."),

    "c2_head": "Шахматы и дисциплина",
    "c2_p1": ("Я выигрывал шахматные турниры, олимпиады по математике и информатике. Параллельно "
              "больше двенадцати лет занимался единоборствами, а позже — пауэрлифтингом и "
              "бодибилдингом."),
    "c2_p2": "Довольно рано я понял две вещи, которые до сих пор определяют мой подход к жизни:",
    "c2_quote": "Интеллект открывает возможности, но именно дисциплина позволяет превратить их в результат.",


    "e1_head": "От образования к ИИ",
    "e1_lead": "Образование помогало мне расти.",
    "e1_facts": [
        ("fa-circle-check", "<strong>Бакалавр по бизнес-информатике</strong><span class=\"l\">— Дальневосточный федеральный университет</span>"),
        ("fa-circle-check", "<strong>Магистр по бизнес-информатике</strong><span class=\"l\">— Высшая школа экономики, после переезда в Москву</span>"),
        ("fa-circle-check", "<strong>Диплом</strong> Международного института бизнес-анализа"),
    ],

    "e2_head": "Наука и преподавание",
    "e2_p1": ('<span class="l">Дальше была аспирантура в области ИИ</span>'
              '<span class="l">и анализа данных — и преподавание в университетах.</span>'),
    "e2_p2": ("В эти же годы я побеждал в соревнованиях по машинному обучению и выиграл "
              "Всероссийскую олимпиаду по бизнес-информатике."),
    "e2_note": "Университет дал мне фундамент. Следующим шагом было проверить эти знания в реальном бизнесе.",

    "k1_head": "От данных к ИИ-трансформации",
    "k1_p1": ("Свою профессиональную карьеру я начал в <strong>Accenture</strong>, работая с данными "
              "крупнейших финансовых организаций."),
    "k1_p2": ("Позже я пришёл в <strong>Сбербанк</strong> на позицию <strong>инженера по данным</strong>. "
              "За несколько лет я прошёл путь до <strong>директора по данным и ИИ</strong> — от "
              "построения инфраструктуры данных до руководства масштабной ИИ-трансформацией."),

    "k2_head": "ИИ во всём банке",
    "k2_p1": ("Там я создавал аналитические и ИИ-системы, которые помогали топ-менеджменту принимать "
              "более качественные решения, а также внедрял ИИ в стратегическое управление, "
              "макроэкономический анализ, HR, организационный дизайн и тысячи бизнес-процессов."),
    "k2_stat": ("3 млрд ₽", "Экономический эффект от этой работы составил 3 млрд рублей, а созданные "
                            "решения изменили работу сотен людей. Я был признан одним из лучших "
                            "руководителей банка."),

    "k3_head": "Почему я ушёл",
    "k3_p1": ("Работая в Сбербанке, я также выиграл корпоративный стартап-акселератор со своим "
              "ИИ-дейтинг-сервисом."),
    "k3_p2": ("Тогда я понял: я больше не хотел создавать что-то только внутри чужих систем. "
              "Я хотел строить свои."),
    "k3_p3": "А достижение позиции топ-менеджера помогло понять кое-что ещё более важное:",
    "k3_quote": "Статус, высокая зарплата и карьерный успех сами по себе не делают человека свободным.",

    "s1_head": "Стартап-студия",
    "s1_p1": ("Я хотел создавать продукты, которые могли бы приносить пользу людям по всему миру. "
              "Поэтому я оставил корпоративную карьеру, ушёл из аспирантуры и переехал на Кипр."),
    "s1_p2": ("Там я стал <strong>CTO ИИ-стартап-студии</strong> и начал создавать технологии в "
              "совершенно разных направлениях."),

    "s2_head": "Что я строил",
    "s2_facts": [
        ("fa-car-side", "Обучал <strong>беспилотные автомобили</strong> в симуляции"),
        ("fa-bolt", "Создал <strong>ИИ-двойника энергосети</strong> для поиска потерь."),
        ("fa-users", "Помогал создавать <strong>тысячи виртуальных инфлюенсеров</strong>"),
        ("fa-flask", "Работал над ИИ-стартапами в разных индустриях."),
    ],
    "s2_stat": ("200 тыс.+", "Один из этих стартапов стал <strong>продуктом дня и недели</strong> на "
                             "Product Hunt и вырос до более чем 200 тыс. пользователей."),

    # правка владельца: «„Один вместо команды“ — в одну строчку». В 27 знаков
    # заголовок на телефоне не влезал (надо 380px при 355px колонки)
    "s3_head": "Один вместо команды",
    "s3_p1": ("За эти годы я научился управлять командами инженеров, запускать продукты и превращать "
              "технологии в реальные бизнесы."),
    "s3_p2": ("Но затем всё изменилось. По мере развития ИИ я увидел, что многие вещи, для которых "
              "раньше требовались целые команды, теперь способен создавать один человек."),
    "s3_p3": ("Я начал учиться создавать продукты и запускать бизнесы без традиционной команды. "
              "Это полностью изменило моё представление о предпринимательстве."),

    "s4_head": "Система вместо стартапа",
    "s4_note": ("Я больше не хотел строить очередной стартап по старым правилам. Я хотел создать "
                "систему, которая позволила бы одному человеку или небольшой команде делать то, для "
                "чего раньше требовалась целая компания."),
    "s4_p1": "Так появилась <strong>Andre AI Technologies</strong>.",

    "x1_head": "AI-Native экосистема",
    "x1_p1": ("После более чем десяти лет работы в корпорациях, стартапах, исследованиях и "
              "образовании я решил объединить весь накопленный опыт в одну систему."),
    "x1_p2": "Я видел рынок с обеих сторон.",
    "x1_cards": [
        ("fa-building", "Крупные компании", "У них были ресурсы, но зачастую не хватало скорости.", ""),
        ("fa-bolt-lightning", "Стартапы", "Двигались очень быстро, но ресурсов хватало не на все идеи.", "o"),
    ],

    "x2_head": "Сила корпорации, скорость стартапа",
    "x2_note": ("Моей целью стало дать соло-предпринимателям и небольшим командам силу корпорации, "
                "а крупным компаниям — скорость и гибкость стартапа."),
    "x2_p1": ("Я начал работать и с теми, и с другими: консультировал стартапы и крупные компании по "
              "ИИ-стратегии, ИИ-продуктам и ИИ-трансформации."),
    "x2_stat": ("$20M+", "Совокупный финансовый эффект решений, которые я помогал создавать, "
                         "превысил $20 миллионов."),

    "x3_head": "От консалтинга к системе",
    "x3_p1": ("Но одним консалтингом такую экспертизу не масштабировать. Я один и физически не могу "
              "лично работать с каждым предпринимателем и каждой компанией."),
    "x3_p2": ("Поэтому я начал превращать свой опыт в систему: методологию, которая диагностирует "
              "бизнес, находит, где ИИ создаёт реальную ценность, и превращает это в ИИ-стратегию с "
              "понятным направлением."),
    "x3_note": "Стратегия становится дорожной картой. Следующий этап — исполнение.",

    "x4_head": "ИИ-операционная система",
    "x4_p1": ('<span class="l">Сейчас я создаю <strong>ИИ-операционную систему для бизнеса</strong>,</span>'
              '<span class="l">в основе которой сотни ИИ-сотрудников:</span>'),
    "x4_facts": [
        ("fa-sitemap", "Управление"),
        ("fa-user-group", "HR"),
        ("fa-bullhorn", "Маркетинг"),
        ("fa-hashtag", "SMM"),
        ("fa-handshake", "Продажи"),
        ("fa-headset", "Поддержка"),
        ("fa-chart-simple", "Аналитика"),
        ("fa-palette", "Дизайн"),
        ("fa-code", "Разработка"),
        ("fa-gears", "Инжиниринг"),
    ],

    "m1_head": "Новые навыки и роли",
    "m1_p1": ("Новой экономике нужны не только технологии: новые навыки, новые роли и новые "
              "способы работы."),
    "m1_p2": ("Поэтому я сотрудничаю с <strong>университетами</strong>, чтобы помогать людям осваивать "
              "новые ИИ-роли и делать прикладное ИИ-образование доступным. И с <strong>исследовательскими "
              "центрами</strong> — чтобы создавать новые технологии и превращать их в продукты, "
              "которые приносят реальную пользу."),

    "m2_head": "Части одной экосистемы",
    "m2_p1": ("Образование, исследования, технологии, продукты и трансформация бизнеса для меня — "
              "не отдельные направления. Это части одной экосистемы."),
    "m2_p2": ("Я создаю продукты для собственной работы, превращаю самые полезные из них в "
              "инструменты для других и объединяю предпринимателей, исследователей и инженеров, "
              "которые хотят участвовать в создании новой экономики."),
    "m2_p3": ("А образование я делаю доступным бесплатно. Вот что я строю в "
              "<strong>Andre AI Technologies</strong>."),

    "finale": ('<span class="l">Добро пожаловать в новую экономику — экономику, в которой</span>'
               '<span class="l"><span class="hl-p">люди</span> и <span class="hl-o">ИИ-агенты</span> '
               'работают вместе на благо людей.</span>'),
    "finale_btn": "Начать ИИ-трансформацию",
}
