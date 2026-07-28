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
  `body.list-open .scroll { box-sizing: border-box; max-height: 100dvh; height: 100dvh; justify-content: flex-start; padding-top: 6rem; padding-bottom: 6rem; }`.
  `box-sizing: border-box` обязателен — иначе `max-height:100dvh` ограничивает
  только контент, а padding добавляется сверху и бокс вылезает за оба края экрана.
  Паддинги симметричны (6rem/6rem) — см. FR-SITE5 (центрирование).
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

## FR-SITE5 — раскрытый список, помещающийся в экран, центрируется по вертикали

**Story.** Как посетитель andre.technology на компе, я раскрываю список карточек
(AI Education — 4 карточки, AI Products — 3) и хочу видеть его по центру экрана,
а не прижатым к верху (жалоба: «справа всё по верху, а надо по середине»).

**Требование.** На десктопе (≥1024px) активный экран внутри `body.list-open .scroll`
имеет `margin-top: auto; margin-bottom: auto` (приём «safe center», как у `.modal`):
- помещается в экран → auto-поля поровну делят свободное место, список ровно по
  центру вьюпорта (паддинги бокса симметричны, 6rem/6rem);
- НЕ помещается (AI Employees, 10 карточек) → свободного места нет, поля = 0,
  работает режим FR-SITE3: прижат к верху под шапку + нативная прокрутка,
  срез строго по краю экрана.

**Проверено Playwright:** education/products центрируются (равные зазоры
сверху/снизу, 259/259 на 1440×900), employees сохраняет прокрутку (последняя
карточка достижима), интро-экраны и мобилка не изменились, `body{zoom}`-экраны
(1920×1080) корректны.

**Тесты (tests/test_site.py):**
- `[FE]` test_list_open_scroll_is_full_viewport — паддинги 6rem/6rem в правиле `body.list-open .scroll`.
- `[FE]` test_list_open_content_centered_when_fits — правило `body.list-open .scroll > .screen.active { margin-top/bottom: auto }` в `@media (min-width:1024px)`.

## FR-SITE6 — страницы /automation/ в стиле главной, без меню и теней

**Story.** Как владелец бренда, я хочу, чтобы страницы курса (`/automation/`,
`/automation/roles`, `/automation/skills`, `/automation/main`) выглядели как
главная: тот же шрифт и размеры, шапка выровнена как на главной, без
навигационного меню «AI Strategy | …» и без теней за иконками героя.

**Требование.**
- Шрифт — **JetBrains Mono** (Google Fonts, веса 400/500/700/800); Montserrat нигде нет.
- **Меню убрано полностью**: ни `.navpill`, ни мобильного бургер-меню
  (`#mobileMenu`, `#burger`) — ни в разметке, ни в CSS, ни в JS.
- Шапка на всю ширину (без `max-width:80rem`), паддинги как на главной
  (1.1rem, на десктопе 2rem); лого слева, кнопки справа; CTA «Консультация» на
  десктопе = метрики CTA главной (высота 2.85rem, 11.5px/.15em).
- У плиток-иконок героя (`.tile`) НЕТ `box-shadow` (включая инлайновые).
- Лекции `/automation/1`, `/automation/2` — отдельные слайд-страницы, их стиль
  и Montserrat НЕ трогаем.

**Тесты (tests/test_automation.py):** test_no_nav_menu, test_jetbrains_mono_font,
test_no_tile_shadows, test_header_full_width_and_cta.

## FR-SITE7 — hero-CTA ведёт в стратегию; под ним ссылка «About me»

**Story.** Как посетитель, нажимая «Start AI Transformation», я хочу попасть в
кабинет ИИ-стратегии (`strategy.andre.technology`), а не в попап «Coming soon»;
под кнопкой хочу видеть скромную ссылку «About me» на страницу об авторе.

**Требование.**
- «Start AI Transformation» — ссылка `<a href="https://strategy.andre.technology/">`
  (НЕ `data-action="contact"`), стиль `.btn-white` как раньше.
- Под кнопкой — текстовая ссылка `<a class="about-link" href="https://andre.technology/about/">About me</a>`:
  серая (`rgba(255,255,255,0.5)`), тот же шрифт, не кнопка; корректна на
  мобилке и десктопе (не ломает переключение экранов).

**Тесты (tests/test_site.py):** test_start_transformation_links_to_strategy,
test_about_me_link.

## FR-SITE8 — «Get AI Strategy»; кнопки Explore открывают «Coming soon»

**Story.** Как владелец, я хочу назвать кнопку стратегии «Get AI Strategy»
(не «Open AI Strategy»), а кнопки «Explore Employees» / «Explore Products» /
«Explore Courses» — пока продукты в разработке — должны открывать тот же
попап «Coming soon» (лид-форма) с правильным источником.

**Требование.**
- Кнопка на экране AI Strategy — текст «Get AI Strategy» (ссылка на
  `strategy.andre.technology/ai-strategy` как раньше); «Open AI Strategy» нет.
- «Explore Employees» → `data-action="lead-open" data-source="AI Employees"`;
  «Explore Products» → `data-source="AI Products"`;
  «Explore Courses» → `data-source="AI Education"`.
- Разметка/JS раскрывающихся списков (FR-SITE3/5) остаётся в коде «спящей» —
  вернуть списки можно, снова поставив `data-action="toggle-*"`.

**Тесты (tests/test_site.py):** test_get_ai_strategy_label,
test_explore_buttons_open_lead_modal.

## FR-SITE9 — пункт навигации «My contacts»

**Story.** Как владелец, я хочу пункт меню «My contacts» вместо «Contacts».

**Требование.** В навигации (`.nav-label` таба `data-target="contact"`) — текст
«My contacts»; голого «Contacts» нет. Пилюля навигации не переполняется на
десктоп-ширинах (FR-SITE4 сохраняется).

**Тесты (tests/test_site.py):** test_nav_label_my_contacts.
