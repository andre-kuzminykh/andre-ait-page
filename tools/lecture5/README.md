# Как собиралась лекция 5

Колода `automation/5/index.html` — 47 слайдов и столько же текстов панели
«Текст» — собрана генератором из каркаса лекции 4 и подготовленных кусков.
Здесь лежит оснастка, чтобы лекцию можно было пересобрать и чтобы лекция 6
делалась тем же путём.

| Файл | Что это |
|---|---|
| `source.md` | исходная речь лекции от владельца: введение, десять разделов по четыре темы, заключение |
| `CONTRACT.md` | контракт вёрстки слайда: словарь классов, запреты, плотность |
| `lint.py` | механическая проверка разметки слайда до браузера |
| `lint_notes.py` | проверка текста панели |
| `measure_notes.py` | нормы статьи: 6-10 блоков, минимум 4 абзаца, ровно один `note`, 2500-4000 знаков |
| `assemble.py` | сборка `automation/5/index.html` из каркаса лекции 4 и готовых слайдов |
| `quiz.json` | вопросы финального теста, по одному на раздел |

Рабочий каталог — `build/l5/` (он в `.gitignore`):

```
build/l5/out/slide-NN.html     разметка слайда NN
build/l5/notes/slide-NN.json   текст панели к слайду NN
build/l5/floor.json            {"pc": ..., "mob": ...} — общий кегль заголовков
build/l5/icons.txt             имена иконок Phosphor для линтера
```

`icons.txt` собирается из вендорной копии Phosphor:

```bash
python3 tools/lecture_check.py vendor         # если vendor/ ещё нет
python3 - <<'PY'
import re, io
css = io.open('vendor/phosphor/src/regular/style.css', encoding='utf-8').read()
io.open('build/l5/icons.txt', 'w', encoding='utf-8').write(
    "\n".join(sorted(set(re.findall(r'\.(ph-[a-z0-9-]+):before', css)))))
PY
```

Порядок сборки:

```bash
python3 tools/lecture5/lint.py                 # разметка слайдов чистая
python3 tools/lecture5/lint_notes.py           # тексты панели чистые
python3 tools/lecture5/measure_notes.py        # статьи в норме по объёму и составу
python3 tools/lecture5/assemble.py             # automation/5/index.html
python3 tools/build_lecture_css.py 5           # assets/lecture-5.css
python3 tools/measure_floor.py 5               # общий кегль → build/l5/floor.json
python3 tools/lecture5/assemble.py             # пересобрать с новым __FLOOR
python3 tools/lecture_check.py vse 5           # все сканеры приёмки
```

Каркас берётся у лекции 4 целиком: общие блоки (`portal-fit`, `slide-polish`,
`radial-fig`, `notes-panel-*`) обязаны совпадать побайтово со всеми лекциями,
иначе падает `test_shared_blocks_identical`. Своё у лекции — превью, слайды,
число слайдов, тест, панель «Текст» и константы формы (`lecture-floor`).

Роликов к лекции 5 пока нет: `videoIds` пустой, кружок с головой не
показывается. Обложки для превью тоже нет — `twitter:card` остаётся
`summary`, как у лекций 3 и 4, и станет `summary_large_image`, когда придёт
картинка 960×540 (LECTURE-GUIDE §8).
