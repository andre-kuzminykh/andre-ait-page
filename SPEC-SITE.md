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
