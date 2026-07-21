# SPEC-SITE — требования к сайту andre.technology (andre-ait-page)

Требования с ID и привязкой к тестам (`tests/test_site.py`). Сайт — статический
`index.html`, деплой через GitHub Pages (CNAME `andre.technology`) с ветки `main`.

## FR-SITE1 — «Free AI Diagnostic» ведёт в кабинет ИИ-стратегии

**Story.** Как посетитель andre.technology, я хочу по кнопке «Free AI Diagnostic»
попасть на `strategy.andre.technology`, чтобы начать с ИИ-стратегии; если я не
авторизован — сам кабинет уводит меня на бесплатную диагностику
(`maturity.andre.technology`).

**Требование.** ВСЕ кнопки/ссылки с текстом «Free AI Diagnostic» — это ссылки
`<a href="https://strategy.andre.technology/">` (не `data-action="contact"`).
Редирект неавторизованного на maturity. обеспечивает сам кабинет (FR-W16 в
andre-ai-maturity), сайту достаточно вести на `strategy.andre.technology/`.

**Тесты (tests/test_site.py):**
- `[FE]` test_free_diagnostic_links_to_strategy — каждая «Free AI Diagnostic» — это `<a href=strategy.>`.
- `[FE]` test_no_free_diagnostic_button_with_contact — нет кнопки «Free AI Diagnostic» с `data-action="contact"`.

## FR-SITE2 — роль/подпись «AI Consultant», а не «Chief AI Officer»

**Story.** Как владелец бренда, я хочу, чтобы Andre AI везде подписывался как
«AI Consultant», а не «Chief AI Officer».

**Требование.** Нигде в `index.html` нет строки «Chief AI Officer»: бейдж-роль
(`<p class="role">`) и анимированная подпись героя (`CUES`) — «AI Consultant».

**Тесты:**
- `[FE]` test_no_chief_ai_officer — «Chief AI Officer» отсутствует в index.html.
- `[FE]` test_role_and_subtitle_are_ai_consultant — бейдж и подпись = «AI Consultant».

## FR-SITE3 — раскрытые списки карточек не обрезаются сверху/снизу (только край экрана)

**Story.** Как посетитель andre.technology на компе, я открываю список
«AI Employees» (или AI Products / AI Education) и хочу видеть все карточки — они
НЕ должны обрезаться сверху и снизу; резать может только край экрана, никаких
«обрезков» внутри.

**Проблема.** Сайт — фикс-вьюпорт слайд-дек (`html,body{overflow:hidden}`).
Каждый `.screen` живёт в `.content-layer{position:fixed;inset:0}` → `.panel` →
`.scroll`. На десктопе `.scroll{max-height:calc(100dvh - 13rem);overflow-y:auto}`
и центрируется по вертикали (`.content-layer{justify-content:center}`). Пока
список свёрнут — экран короткий, центрируется красиво. Но раскрытый список
(10 карточек колонкой) ВЫШЕ экрана: бокс `100dvh - 13rem` оставлял ~6.5rem
«мёртвых» чёрных полей сверху и снизу, и карточки резались ВНУТРИ этих полей, а
не по краю экрана (жалоба: «обрезается и сверху и снизу… только краями экрана,
не надо вообще обрезок»).

**Требование.** Когда раскрыт любой список карточек, бокс прокрутки на десктопе
(≥1024px) = **вся высота вьюпорта**, режет только край экрана:
- `applyExpanded()` ставит на `<body>` класс **`list-open`**, если открыт хотя
  бы один из списков (employees/products/education), и снимает иначе.
- CSS (внутри `@media (min-width:1024px)`):
  `body.list-open .scroll { box-sizing: border-box; max-height: 100dvh; height: 100dvh; justify-content: flex-start; padding-top: 6rem; padding-bottom: 2rem; }`.
  `box-sizing: border-box` обязателен — иначе `max-height:100dvh` ограничивает
  только контент, а padding добавляется сверху и бокс вылезает за оба края экрана.
- Помещается — виден целиком; не помещается — нативная прокрутка В САМОМ
  полноэкранном боксе, линия отреза строго по краю экрана, без «мёртвых» полей.
- Короткие экраны (список свёрнут, `body` без `list-open`) по-прежнему
  центрируются базовым правилом — поведение не меняется.
- На мобилке (<1024px) карточки — горизонтальная лента (свайп), вертикальной
  обрезки нет; правило десктопа туда не действует.

**Проверено e2e Playwright** (реальный клик по «Explore Employees» →
`applyExpanded` → `body.list-open`): на 1280×800/1440×900/1366×768/1536×864/
1024×768 внутренних клипперов, режущих не по краю экрана, НЕТ; первая карточка
ниже шапки; последняя достижима прокруткой. На 520×1637/390×844 — лента,
обрезки нет.

**Тесты (tests/test_site.py):**
- `[FE]` test_apply_expanded_toggles_list_open — `applyExpanded` тогглит `body.list-open` по признаку раскрытого списка.
- `[FE]` test_list_open_scroll_is_full_viewport — CSS-правило `body.list-open .scroll` с `box-sizing:border-box`, `max-height:100dvh`, `padding` — внутри `@media (min-width:1024px)`.

## FR-SITE4 — навигация в шапке ЧИТАЕМАЯ, никогда не 8px

**Story.** Как посетитель andre.technology на ноутбуке, я хочу видеть пункты
меню нормальным шрифтом, а не «очень малым» — жалоба: «на главном сайте очень
малый шрифт и кнопки; они чуть больше если развернуть, но всё равно узко —
надо чтобы никогда такого узкого не было, сделай побольше».

**Проблема.** Центрированная пилюля из 6 пунктов на средних десктоп-ширинах
ужималась целиком через `transform: scale(0.66)` (1024–1319px) и `scale(0.85)`
(1320–1479px) поверх базового `font-size:12px` → эффективный шрифт **~8px** на
ноутбуках и ~10px на 14″, и лишь 12px при разворачивании на весь монитор.

**Требование.** Базовый размер пункта меню (`.nav-tab` в `@media min-width:1024px`)
— **14px** (было 12px). Ужимающие скейлы больше НЕ роняют шрифт до 8px:
- на 1024–1319px скейл держится **≥0.86** (эффективно ≥12px), плюс прячутся
  разделители «·» и уплотняются отступы — ширины хватает без потери читабельности;
- на 1320–1479px скейл **0.95** (эффективно ~13.3px);
- на ≥1480px — полный **14px**.
Пилюля при этом НЕ сталкивается с логотипом слева и правым CTA «Free AI
Diagnostic» ни на одной ширине.

**Проверено рендером Playwright** на 1024/1152/1280/1366/1440/1536/1920:
эффективный размер шрифта = 12 / 12 / 12 / 13.3 / 13.3 / 14 / 14 px (нигде не
8px); пересечений nav↔логотип и nav↔CTA нет (минимальный зазор до CTA — 29px
на 1024px). Скриншоты 1024/1280/1440.

**Тесты (tests/test_site.py):**
- `[FE]` test_nav_font_readable — базовый `.nav-tab` десктопа = `font-size: 14px`; строк `scale(0.66)`/`scale(0.85)` в CSS нет; мид-скейлы `scale(0.86)`/`scale(0.95)` присутствуют.
