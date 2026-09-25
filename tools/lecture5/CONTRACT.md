# Контракт вёрстки слайда лекции 5

Ты верстаешь ОДИН слайд презентации. Результат — кусок HTML, который вставят
в `automation/5/index.html` между соседними слайдами. Никакого другого вывода.

Канон целиком: `/home/user/andre-ait-page/LECTURE-GUIDE.md` (§2, §4 — обязательно).
Образцы, на которые надо смотреть глазами: `/home/user/andre-ait-page/automation/4/index.html`,
слайды лежат подряд начиная со строки 2049 (`id="slide-0"`).

## 1. Форма результата

```html
    <div class="slide-container px-3 sm:px-6 md:px-12 opacity-0 pointer-events-none translate-y-8" id="slide-NN">
        <div class="content-z max-w-5xl w-full">
            ...содержимое...
        </div>
    </div>
```

* `NN` — номер из задания. Отступ ровно как выше (4 и 8 пробелов).
* `max-w-5xl` можно менять на `max-w-4xl` / `max-w-6xl` по плотности слайда.
* Файл записать в `/home/user/andre-ait-page/build/l5/out/slide-NN.html`
  (инструментом Write). В файле — ТОЛЬКО эта разметка, без ```-обрамления.

## 2. Железные запреты (нарушение = слайд не принят)

1. Никаких `<style>`, `<script>`, `<svg>`, `:has()`, внешних картинок.
2. Никакого `style="..."` — КРОМЕ единственного разрешённого случая: блок с
   заливкой `bg-solar`, где текст должен быть чёрным:
   `style="color:#111;-webkit-text-fill-color:#111"`.
3. Никаких `hidden md:block`, `md:hidden`, `sr-only` — на телефоне видно ровно
   то же, что на компьютере. Прятать содержимое нельзя ничем.
4. Никаких теней (`shadow-*`, `drop-shadow-*`).
5. Никаких размеров в `vw`/`vh`, никаких `h-screen`, `overflow-auto`,
   `absolute inset-0` на весь слайд.
6. **Перед каждым `<br>` — пробел**: `Плохие <br>данные`. Без пробела замерщик
   склеивает слова в одно и роняет кегль всего ряда.
7. **Каждый размер текста — парой**: `text-[10px] md:text-sm`. Одиночный
   `text-sm` без телефонного напарника запрещён. То же для `leading-*`:
   если задал `md:text-2xl`, задай и `md:leading-none` при необходимости.
8. Иконка не отрывается от слова: `<span class="whitespace-nowrap"><i class="ph-fill ph-x"></i> Слово</span>`.
9. Имена иконок — только существующие Phosphor (список ниже). Выдуманное имя
   рисуется пустотой.
10. Латиница только в именах документов, методов и продуктов (Product Brief,
    PRD, TRD, C4, User Stories, Use Case, Gherkin, Given, When, Then, BDD, TDD,
    Evals, End-to-End, Context Engineering, API, CRM, JSON, MCP, Model Context
    Protocol, Telegram, GitHub Copilot, Gemini Code Assist, Cursor, Windsurf,
    Replit, Lovable, Redis, Postgres, first_name, firstName). Всё остальное —
    по-русски: «вебхук», «серверная часть», «резервный сценарий», «управляющий
    слой», «повторные попытки». Запрещены слова: workflow, reasoning, retrieval,
    fallback, polling, guardrail, governance, throughput, human review, webhook,
    backend, backlog, adoption, baseline, code generation, summarization,
    оркестрация, продакшен, чекпоинт, снапшот. Отдельно: сочетание букв «AI»
    запрещено, пишем «ИИ».

## 3. Плотность: слайд обязан влезть в 1380×864

Полезная площадь компьютерной формы — 1380×648 (сверху 128 под шапку, снизу
88 под стрелки). Подгонщик умеет уменьшать, но ниже 10px кегля на телефоне
слайд не принимается. Поэтому:

* всего на слайде **не больше 6 крупных блоков** (заголовок и подзаголовок —
  два из них);
* рубрика над блоком — обычный центрированный `<p>`, а НЕ подпись между двумя
  линиями с `shrink-0`: длинная подпись в такой строке не переносится и
  вылезает за экран на 320-414 (слайд 27, круг 1);
* карточек в сетке — не больше 8;
* текст внутри карточки — **не длиннее 90 знаков** и не больше 3 строк;
* подзаголовок слайда — **одна строка**, не длиннее 70 знаков;
* ряд коротких плашек-тегов — всегда в одну строку, по 1-2 слова в плашке;
* если материала больше — лишнее уходит в панель «Текст», не на слайд.

## 4. Словарь: из чего собираются слайды

**Заголовок** (обязателен, ровно один `<h2>`):
```html
<h2 class="text-xl sm:text-3xl md:text-5xl font-black mb-3 md:mb-5 text-center text-black">Первое слово <span class="text-solar">акцент</span></h2>
```
**Подзаголовок** (обязателен, ровно один, сразу за заголовком):
```html
<p class="text-center text-black/60 mb-4 md:mb-7 text-[10px] md:text-lg font-medium max-w-3xl mx-auto">Одна строка</p>
```
**Белая карточка**:
```html
<div class="bg-white border border-grayBase rounded-[14px] md:rounded-[20px] p-2.5 md:p-5 flex flex-col items-center text-center a-in">
    <i class="ph-fill ph-cube text-xl md:text-3xl text-solar mb-1 md:mb-2"></i>
    <h3 class="font-black text-[11px] md:text-lg text-black mb-0.5 md:mb-1.5 leading-tight">Название</h3>
    <p class="text-[9px] md:text-xs text-black/60 leading-tight m-0">Пояснение в одну-две строки</p>
</div>
```
**Акцентная (тёмная) карточка** — ровно одна-две на слайд, на главном узле:
`bg-black border-2 border-solar` + заголовок `text-solar` + текст `text-white/70`.
**Серая карточка** (второстепенное, «как было»): `bg-grayBase/30 border border-grayBase`.
**Плашка-тег**:
```html
<span class="bg-white border border-grayBase rounded-lg md:rounded-xl px-2 py-1 md:px-3 md:py-1.5 text-[9px] md:text-xs font-bold text-black whitespace-nowrap"><i class="ph-fill ph-tag text-solar"></i> Слово</span>
```
**Надпись-рубрика над блоком**:
```html
<p class="text-center text-black/40 text-[9px] md:text-xs font-bold uppercase tracking-widest mb-2 md:mb-3">Рубрика</p>
```
**Соединитель между шагами** (горизонтальный бегущий пунктир):
```html
<div class="h-[2px] w-4 md:w-12 shrink-0 text-solar/40 a-flow"></div>
```
вертикальный — `<div class="w-[2px] h-4 md:h-8 text-solar/40 a-flow-y mx-auto"></div>`;
стрелка — `<i class="ph-bold ph-arrow-right text-black/25 text-xl md:text-3xl self-center shrink-0 rotate-90 md:rotate-0"></i>`.
**Полоса вывода** (последний блок слайда, почти всегда нужна):
```html
<div class="bg-solar/20 border-l-4 border-solar p-2.5 md:p-4 rounded-r-xl md:rounded-r-2xl w-full max-w-3xl mx-auto text-center mt-3 md:mt-5">
    <p class="text-[10px] md:text-base text-black font-medium leading-snug m-0">Мысль обычная <span class="font-black">и её ударная часть</span></p>
</div>
```
**Кольцо вокруг центра** (для схем «ядро и спутники») — образец: слайд 29
лекции 3, строки 4241-4303. Центр `absolute left-1/2 top-1/2 -translate-x-1/2
-translate-y-1/2`, спутники по точкам `top-[12%]`, `left-[83%] top-[31%]` и т.д.
**Анимация** (только эти классы, других нет):
`a-in` + `a-in-2`…`a-in-6` (появление по очереди), `a-pulse` (дыхание акцента),
`a-flow` / `a-flow-y` (бегущий пунктир по линии), `a-orbit` (вращение кольца),
`a-step` (подсветка узлов строго по одному, в порядке разметки — FR-SITE74).
Анимация не имеет права двигать коробки — только прозрачность и масштаб.

Сетки: `grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-4`. На телефоне ряд из
четырёх складывается в 2×2 — это норма. Ряд из трёх на телефоне —
`grid-cols-1 md:grid-cols-3` (стопка) или `grid-cols-3` (если подписи короткие).

Длинное слово в узкой колонке разбивается мягким переносом: `Инстру&shy;менты`.
Если из-за одного длинного заголовка мельчает весь ряд — этому заголовку
даётся свой размер: `<h3 ...><span class="block w-full text-center md:text-[15px]">Производи&shy;тельность</span></h3>`.

## 5. Иконки

Разрешены любые существующие имена Phosphor — полный список имён собирается
в `build/l5/icons.txt` из вендорной копии (см. README). Проверенный набор
под лекцию 4, который годится и здесь:
ph-brain ph-graph ph-tree-structure ph-git-branch ph-git-merge ph-git-fork
ph-arrows-split ph-arrow-u-down-left ph-arrows-clockwise ph-arrow-right
ph-arrow-down ph-flow-arrow ph-path ph-signpost ph-compass ph-crosshair
ph-target ph-magnifying-glass ph-funnel ph-database ph-books ph-file-text
ph-files ph-folder ph-folders ph-archive ph-table ph-image ph-video-camera
ph-microphone ph-presentation-chart ph-chart-line ph-chart-bar ph-calculator
ph-code ph-terminal-window ph-browser ph-desktop ph-cpu ph-cloud ph-plugs
ph-plugs-connected ph-plug ph-usb ph-lego ph-puzzle-piece ph-stack ph-cube
ph-cubes-three ph-squares-four ph-grid-four ph-list-checks ph-check-circle
ph-check ph-x ph-x-circle ph-warning ph-warning-circle ph-question ph-info
ph-lightbulb ph-sparkle ph-shield-check ph-lock-simple ph-lock-key ph-key
ph-identification-card ph-user-circle ph-users-three ph-users-four ph-user-focus
ph-handshake ph-chats-circle ph-chat-teardrop-text ph-megaphone ph-broadcast
ph-wifi-high ph-share-network ph-network ph-link ph-repeat ph-recycle
ph-clock ph-clock-countdown ph-hourglass ph-timer ph-gauge ph-speedometer
ph-scales ph-coins ph-currency-circle-dollar ph-wrench ph-gear ph-toolbox
ph-robot ph-person-simple-run ph-flag ph-flag-checkered ph-map-trifold
ph-clipboard-text ph-notebook ph-note-pencil ph-pencil-simple ph-stamp
ph-seal-check ph-medal ph-trophy ph-gavel ph-scroll ph-ladder-simple
ph-stairs ph-steps ph-tray ph-package ph-shopping-cart ph-buildings
ph-bank ph-briefcase ph-lightning ph-fire ph-snowflake ph-heartbeat
ph-pulse ph-eye ph-binoculars ph-bug ph-first-aid-kit ph-lifebuoy

## 6. Самопроверка перед записью файла

1. Есть ровно один `<h2>` и ровно один подзаголовок-`<p>` за ним.
2. Каждый `text-[...]`/`text-xs` имеет пару для другой формы.
3. Перед каждым `<br>` стоит пробел.
4. Нет `style=` (кроме разрешённого), нет `<style>`, нет `hidden md:`.
5. Все имена иконок — из списка выше или из реального Phosphor.
6. Крупных блоков не больше шести, карточек в сетке не больше восьми.
7. Содержание слайда покрывает ВЕСЬ список «обязательное содержание» из задания.
8. Латиницей — только разрешённые имена методов.
