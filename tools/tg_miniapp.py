# -*- coding: utf-8 -*-
"""FR-SITE87 — страницы сайта внутри Telegram Mini App.

Telegram-бот открывает /ai-strategy/ru/, /automation_ru/ и /about/ru как
Mini App (кнопка web_app), и владелец хочет, чтобы там всё было «максимально
нативно». Общий модуль для трёх генераторов (build_strategy, build_about,
build_course_entry): проверка запуска одна на все страницы, чтобы режим не
разъезжался между ними.

В <head> каждой страницы встаёт маленький инлайновый скрипт. Он смотрит на
параметры запуска, которые Telegram дописывает в hash адреса
(`#tgWebAppData=…&tgWebAppPlatform=…`), и ТОЛЬКО если они есть подгружает SDK
Telegram и `/assets/tg-miniapp.js` с самим поведением (ready/expand, цвета,
отступы, ссылки, «Назад»). Вне Telegram страница не делает ни одного лишнего
запроса и ведёт себя как раньше: скрипт в <head> ничего не меняет.

Параметры запуска запоминаются на вкладку (sessionStorage `ait_tg`): переход
по сайту внутри мини-аппа (EN|RU, «Обо мне» → лендинг) теряет hash, а режим
мини-аппа должен остаться. Отсюда же их берёт переход в продукт — там они
снова уезжают в hash (см. assets/tg-miniapp.js и FR-SITE87 в SPEC-SITE.md).
"""

SDK = "https://telegram.org/js/telegram-web-app.js"
SCRIPT = "/assets/tg-miniapp.js"

# Режим страницы: «deck» — экраны листаются жестом (лендинг, «Обо мне»),
# там свайп вниз должен листать назад, а не сворачивать мини-апп; «page» —
# обычная прокрутка (вход в курс), там жест Telegram оставляем как есть.
MODES = ("deck", "page")

_TEMPLATE = """<script>
/* FR-SITE87: страница открыта как Telegram Mini App? Признак — параметры
   запуска в hash (tgWebAppData / tgWebAppPlatform). Только тогда грузим SDK
   Telegram и поведение мини-аппа; вне Telegram лишних запросов нет. */
(function () {
  try {
    var p = location.hash.slice(1).split(/[?&]/).filter(function (x) {
      return /^tgWebApp\\w*=/.test(x);
    }).join('&');
    /* параметры живут на вкладку: переход по сайту внутри мини-аппа теряет
       hash, а режим должен остаться */
    if (/(^|&)tgWebApp(Data|Platform)=/.test(p)) sessionStorage.setItem('ait_tg', p);
    else p = sessionStorage.getItem('ait_tg');
    if (!p) return;
    var r = document.documentElement;
    r.classList.add('tg');
    r.setAttribute('data-tg', '@@MODE@@');
    /* async=false: SDK выполняется раньше нашего скрипта, но разбор
       страницы ни один из них не держит */
    ['@@SDK@@', '@@SCRIPT@@'].forEach(function (u) {
      var s = document.createElement('script');
      s.src = u;
      s.async = false;
      document.head.appendChild(s);
    });
  } catch (e) {}
})();
</script>"""


def head_snippet(mode):
    """Инлайновая проверка запуска в Telegram — ставится в <head> страницы."""
    assert mode in MODES, mode
    return (_TEMPLATE.replace("@@MODE@@", mode)
            .replace("@@SDK@@", SDK)
            .replace("@@SCRIPT@@", SCRIPT))
