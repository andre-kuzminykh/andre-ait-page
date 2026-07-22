# SPEC-SITE — требования к сайту andre.technology (andre-ait-page)

Требования с ID и привязкой к тестам (`tests/test_site.py`). Сайт — статический
`index.html`, деплой через GitHub Pages (CNAME `andre.technology`) с ветки `main`.

## FR-SITE1 — «Free AI Diagnostic» ведёт на бесплатную диагностику AI-зрелости (maturity.)

**Story.** Как посетитель andre.technology, я хочу по кнопке «Free AI Diagnostic»
попасть на `maturity.andre.technology` — бесплатную оценку AI-зрелости компании.
Это первый шаг воронки; ИИ-стратегия (`strategy.andre.technology`) — следующий шаг.

**Требование (SEO-архитектура экосистемы).** ВСЕ кнопки/ссылки, относящиеся к
диагностике/оценке («Free AI Diagnostic», «Start AI Transformation», «Assess AI
Maturity», «Check AI Readiness»), — это ссылки
`<a href="https://maturity.andre.technology/">` (не `data-action="contact"` и НЕ
strategy.). Все CTA, относящиеся к стратегии («Open AI Strategy», «Build AI
Strategy», «Analyze Business Processes»), ведут на корень
`https://strategy.andre.technology/` (без внутренних путей вида /ai-strategy).

**Тесты (tests/test_site.py):**
- `[FE]` test_free_diagnostic_links_to_maturity — каждая «Free AI Diagnostic» — это `<a href=maturity.>`.
- `[FE]` test_free_diagnostic_never_links_to_strategy — «Free AI Diagnostic» никогда не ведёт на strategy.
- `[FE]` test_no_free_diagnostic_button_with_contact — нет кнопки «Free AI Diagnostic» с `data-action="contact"`.
- Полная SEO-проверка (метаданные, canonical, sitemap, ссылки) — `scripts/check-seo.py`.

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
— **14px** и **НЕ жирный** (`font-weight: 500`, было 700). **`transform: scale()`
на `.nav` УБРАН полностью** (он менял высоту бара) — на средних ширинах пилюля
уплотняется ТОЛЬКО по горизонтали (меньше шрифт/трекинг/зазор/паддинги), высота
постоянна:
- 1024–1319px — шрифт 12px; 1320–1479px — 13px; ≥1480px — 14px (нигде не 8px);
- **вертикальные разделители «·»/«|» видны на ВСЕХ десктоп-ширинах** — при
  сжатии окна не пропадают (уточнение пользователя: «когда сжимаешь — пропадают
  вертикальные полосы»).

Дополнительно (уточнения пользователя):
- **Буквы меню не жирные** (`font-weight: 500`).
- **Кнопка «Free AI Diagnostic» (CTA) — ВСЕГДА одной высоты с баром навигации**:
  и `.nav`, и десктопный `.cta` имеют `height: 2.85rem; box-sizing: border-box`;
  на узких ширинах CTA ужимается только по горизонтали (padding/шрифт), высота
  не трогается. Раньше CTA ужимался «в такт» скейлу nav и был непропорционален.

**Проверено рендером Playwright** на 1024/1152/1280/1366/1440/1536/1920:
`navH == ctaH` на каждой ширине (46/46 … 59/59); `font-weight = 500`;
разделители видны везде; пересечения nav↔CTA нет (мин. зазор 3px на 1024px).
Скриншоты 1024/1280/1440.

**Тесты (tests/test_site.py):**
- `[FE]` test_nav_font_readable — `.nav-tab` десктопа = `font-size:14px; font-weight:500`; `scale(0.66|0.85|0.86|0.95)` в CSS НЕТ; `.nav` и `.cta` — `height:2.85rem; box-sizing:border-box`.
- `[FE]` test_nav_dividers_never_hidden_on_desktop — в мид-брейкпоинте 1024–1319 нет `.nav-divider { display: none }`.
