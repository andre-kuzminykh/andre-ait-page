# SEO-SETUP — Search Console и ручные действия для экосистемы Andre AI

Экосистема: три hostname.

| Hostname | Что это | Репозиторий / деплой |
|---|---|---|
| `andre.technology` | Основной сайт | `andre-kuzminykh/andre-ait-page`, GitHub Pages (ветка `main`, CNAME) |
| `maturity.andre.technology` | AI Maturity Assessment | `andre-kuzminykh/andre-ai-maturity`, aiohttp-сервер бота (k8s, NodePort 30080 на `34.62.139.101`) |
| `strategy.andre.technology` | AI Strategy | тот же сервер `andre-ai-maturity` (host-aware маршруты в `services/landing.py`) |

## 1. Google Search Console

### 1.1. Основная property (Domain Property)

1. Открыть [Search Console](https://search.google.com/search-console) → Add property → **Domain**.
2. Ввести `andre.technology` (без https и www).
3. Подтвердить владение TXT-записью DNS (у регистратора домена).

Domain Property покрывает сразу: `andre.technology`, `maturity.andre.technology`,
`strategy.andre.technology`, а также http/https и www варианты.

### 1.2. URL-prefix properties (для раздельной аналитики)

Дополнительно создать три URL-prefix property:

- `https://andre.technology/`
- `https://maturity.andre.technology/`
- `https://strategy.andre.technology/`

(При подтверждённой Domain Property они подтверждаются автоматически.)

### 1.3. Отправить sitemaps

В каждой property → Sitemaps → добавить:

- `https://andre.technology/sitemap.xml`
- `https://maturity.andre.technology/sitemap.xml`
- `https://strategy.andre.technology/sitemap.xml`

### 1.4. Запросить индексацию

URL Inspection → ввести URL → **Request indexing** для:

- `https://andre.technology/`
- `https://maturity.andre.technology/`
- `https://strategy.andre.technology/`

После этого стоит так же прогнать шесть новых страниц основного сайта:
`/ai-training/`, `/ai-agents/`, `/business-process-automation/`, `/about/`,
`/cases/`, `/contacts/`.

### 1.5. Что мониторить (раз в 1–2 недели)

- **Page indexing** — какие URL в индексе, причины исключений;
- **Sitemaps** — статус «Success» у всех трёх;
- **Core Web Vitals** — LCP / CLS / INP по mobile и desktop;
- **HTTPS** — все страницы должны быть https;
- **Enhancements** (FAQ, Breadcrumbs, Logo) — без ошибок структурированных данных;
- **Manual Actions** и **Security Issues** — должны быть пустыми.

## 2. Обязательные ручные действия по инфраструктуре (ВАЖНО)

Автоматически из репозиториев это сделать нельзя — нужен доступ к
инфраструктуре:

1. **HTTPS для поддоменов.** DNS `maturity.` и `strategy.` указывает на
   `34.62.139.101`, а сервис бота опубликован как NodePort **30080** (HTTP).
   Из этого окружения невозможно проверить, что отвечает на портах 80/443.
   Если на 443 никто не слушает — Google не сможет индексировать поддомены.
   Требуется ingress-контроллер (например, GKE Ingress / nginx + cert-manager)
   с TLS-сертификатами для обоих hostname, проксирующий на сервис
   `ai-maturity-bot:8080` (namespace `ai-maturity-bot`). Серверные redirect
   http→https и единый канонический хост настраиваются там же.
2. **Деплой бота.** Лендинги появятся после деплоя обновлённого образа
   `andre-ai-maturity` (маршруты `/`, `/robots.txt`, `/sitemap.xml`,
   `/site.webmanifest`, favicon/OG + заголовок `X-Robots-Tag: noindex` для
   `/report/`, `/cabinet/`, `/diagram*`, `/health`).
3. **GitHub Pages.** Основной сайт деплоится с ветки `main` — изменения из
   рабочей ветки нужно смёржить в `main`.
4. **www-редирект.** `www.andre.technology` уже указывает на GitHub Pages —
   Pages сам отдаёт 301 на канонический `andre.technology` (проверить после
   мержа: `curl -I https://www.andre.technology/`).

## 3. Аналитика (рекомендация)

Сейчас на сайтах **нет** GA/GTM — счётчик не добавлялся, чтобы не ставить
пустой/чужой ID. При подключении GA4:

- один тег GA4 на все три hostname; в Admin → Data Streams настроить
  **cross-domain tracking** для `andre.technology`, `maturity.andre.technology`,
  `strategy.andre.technology` (иначе переходы между ними станут ложными
  self-referrals);
- события уже размечены в коде: клики по продуктовым ссылкам шлют
  `click_maturity` / `click_strategy`, форма контактов — `contact_submit`
  в `window.dataLayer` (см. `data-analytics` атрибуты). Останется добавить
  `start_maturity_assessment` / `complete_maturity_assessment` /
  `start_strategy` / `complete_strategy` на стороне бота (Telegram);
- не передавать в аналитику голос, описания процессов, персональные результаты.

## 4. Автоматические проверки

- Основной сайт: `python3 scripts/check-seo.py` (падает с ненулевым кодом при
  критической ошибке) и `python3 tests/test_site.py`.
- Бот (maturity/strategy): `python3 -m pytest tests/test_landing.py` в репо
  `andre-ai-maturity`.

## 5. Проверка после деплоя (чек-лист)

На каждом hostname проверить через **View Source** (не DevTools):

- `/` → HTTP 200, один `<title>`, meta description, self-canonical, один `<h1>`,
  JSON-LD, OG-изображение;
- `/favicon.ico`, `/favicon-48x48.png`, `/favicon-96x96.png`, `/icon-512.png` →
  200, image/*;
- `/site.webmanifest` → 200, валидный JSON;
- `/robots.txt` → 200, ссылка на sitemap этого hostname;
- `/sitemap.xml` → 200, валидный XML;
- на maturity/strategy: `/report/<id>` и `/cabinet/<token>` отдают
  `X-Robots-Tag: noindex, nofollow`;
- CTA: «Free AI Diagnostic» (главная) → maturity; «Open AI Strategy» → strategy;
  кнопки лендингов → Telegram-бот;
- мобильный и десктопный рендеринг, отсутствие битых ссылок.
