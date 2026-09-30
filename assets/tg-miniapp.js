/* ============================================================
   FR-SITE87 — страницы сайта внутри Telegram Mini App.

   Файл НЕ подключается в разметке: его вставляет инлайновая проверка в
   <head> (tools/tg_miniapp.py), и только когда в hash адреса есть параметры
   запуска Telegram. Вне Telegram браузер его не запрашивает. SDK Telegram
   (telegram-web-app.js) вставлен перед ним с async=false и к этому моменту
   уже выполнен — или не загрузился, тогда страница остаётся обычной.

   Страница у мини-аппа та же, что у сайта: тёмная по бренду. Поэтому не
   сайт перекрашивается в тему Telegram, а шапка, фон и нижняя панель
   Telegram красятся в цвет страницы (meta theme-color): иначе в светлой
   теме Telegram над тёмной страницей стояла бы белая полоса.
   ============================================================ */
(function () {
  'use strict';

  var W = window.Telegram && window.Telegram.WebApp;
  if (!W) return;

  /* Мост к клиенту Telegram. Если ссылку с параметрами запуска открыли в
     обычном браузере, SDK молча глотает вызовы — openLink тогда не открыл
     бы ссылку вовсе. Без моста ничего не трогаем. */
  var bridge = !!(window.TelegramWebviewProxy ||
                  (window.external && 'notify' in window.external) ||
                  window.parent !== window);
  if (!bridge) return;

  var root = document.documentElement;
  var deck = root.getAttribute('data-tg') === 'deck';

  function at(v) { try { return W.isVersionAtLeast(v); } catch (e) { return false; } }
  function safe(fn) { try { fn(); } catch (e) {} }
  function launch() { try { return sessionStorage.getItem('ait_tg') || ''; } catch (e) { return ''; } }

  /* ---------- готово, во всю высоту ----------
     ready() убирает заглушку загрузки Telegram, expand() раскрывает окно на
     весь экран: лендинг и биография листаются экранами и в половине окна
     не помещаются. */
  safe(function () { W.ready(); });
  safe(function () { W.expand(); });

  /* На листающихся страницах свайп вниз — это «предыдущий экран». В Telegram
     тот же жест сворачивает мини-апп: на каждом втором свайпе окно уезжало
     бы вниз. На странице с обычной прокруткой жест Telegram не трогаем —
     там он срабатывает только у верхнего края, как и должен. */
  if (deck && at('7.7')) safe(function () { W.disableVerticalSwipes(); });

  /* ---------- цвета шапки, фона и нижней панели ----------
     Цвет — из meta theme-color страницы: у /automation/ светлая тема
     переписывает его на лету, поэтому meta ещё и слушаем. themeParams —
     только запасной цвет, если у страницы своего нет. Шестнадцатеричный
     цвет шапки Telegram принимает с 6.9, раньше — только ключ темы, и там
     шапку не трогаем, чтобы не получить светлую полосу. */
  var meta = document.querySelector('meta[name="theme-color"]');
  var painted = '';
  function pageColor() {
    var c = meta && meta.getAttribute('content');
    if (/^#[0-9a-f]{6}$/i.test(c || '')) return c;
    return (W.themeParams && W.themeParams.bg_color) || '#050505';
  }
  function paint(force) {
    var c = pageColor();
    if (c === painted && !force) return;
    painted = c;
    if (at('6.1')) safe(function () { W.setBackgroundColor(c); });
    if (at('6.9')) safe(function () { W.setHeaderColor(c); });
    if (at('7.10')) safe(function () { W.setBottomBarColor(c); });
  }
  paint(true);
  if (meta && window.MutationObserver) {
    new MutationObserver(function () { paint(false); })
      .observe(meta, { attributes: true, attributeFilter: ['content'] });
  }
  /* смена темы в самом Telegram может вернуть шапке цвет темы */
  safe(function () { W.onEvent('themeChanged', function () { paint(true); }); });

  /* ---------- безопасные отступы ----------
     Стили страниц берут нижний отступ из --safe-b (по умолчанию
     env(safe-area-inset-bottom)), верхний — из --safe-t (по умолчанию 0).
     В Telegram env() на части клиентов равен нулю, а в полноэкранном режиме
     сверху ещё и кнопки Telegram: отступы берём из safeAreaInset и
     contentSafeAreaInset (Bot API 8.0). */
  var lastInsets = '';
  function insets() {
    var s = W.safeAreaInset || {}, c = W.contentSafeAreaInset || {};
    var top = (s.top || 0) + (c.top || 0);
    var bottom = (s.bottom || 0) + (c.bottom || 0);
    var key = top + '/' + bottom;
    if (key === lastInsets) return;
    var first = !lastInsets;
    lastInsets = key;
    root.style.setProperty('--safe-t', top + 'px');
    root.style.setProperty('--safe-b', 'max(env(safe-area-inset-bottom, 0px), ' + bottom + 'px)');
    /* подгонка экранов (fitScreen, кегли) слушает resize: без него экран,
       сдвинутый отступом, остался бы подогнанным под прежнюю высоту */
    if (!first) safe(function () { window.dispatchEvent(new Event('resize')); });
  }
  insets();
  ['safeAreaChanged', 'contentSafeAreaChanged', 'fullscreenChanged', 'viewportChanged']
    .forEach(function (ev) { safe(function () { W.onEvent(ev, insets); }); });

  /* ---------- ссылки ----------
     - свой сайт — обычный переход внутри мини-аппа;
     - продукт (strategy., maturity.) — тоже внутри мини-аппа: там свой
       режим мини-аппа, и ему нужны параметры запуска Telegram. Они уезжают
       в hash — он не уходит на сервер и не попадает в Referer;
     - t.me — openTelegramLink: канал открывается в самом Telegram, а не в
       браузере, который потом всё равно отправит обратно в Telegram;
     - всё остальное внешнее — openLink, во внешнем браузере: иначе чужой
       сайт открылся бы вместо страницы, и вернуться было бы нечем;
     - mailto: и прочие схемы — как есть. */
  var SITE = /^(www\.)?andre\.technology$/i;
  var PRODUCT = /^(strategy|maturity)\.andre\.technology$/i;
  var TME = /^(www\.)?(t|telegram)\.me$/i;

  function intoProduct(href) {
    var p = launch();
    if (!p) return href;
    return href + (href.indexOf('#') < 0 ? '#' : '&') + p;
  }

  document.addEventListener('click', function (e) {
    /* страница могла обработать клик сама — тогда не вмешиваемся */
    if (e.defaultPrevented || e.button > 0) return;
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (!a || a.hasAttribute('download')) return;
    var u;
    try { u = new URL(a.getAttribute('href'), location.href); } catch (err) { return; }
    if (u.protocol !== 'https:' && u.protocol !== 'http:') return;
    if (u.host === location.host || SITE.test(u.hostname)) return;
    e.preventDefault();
    if (PRODUCT.test(u.hostname)) { location.href = intoProduct(u.href); return; }
    try {
      if (TME.test(u.hostname) && at('6.1')) W.openTelegramLink(u.href);
      else W.openLink(u.href);
    } catch (err) { window.open(u.href, '_blank'); }
  });

  /* ---------- «Назад» ----------
     В мини-аппе нет кнопки «назад» браузера: ушёл со страницы запуска —
     вернуться можно только закрыв окно. Поэтому ведём стек страниц этой
     вкладки и, если есть куда вернуться, показываем кнопку «Назад» Telegram
     (на Android её же вызывает системная «назад»). Запуск из Telegram
     (параметры в hash) — всегда корень стека. */
  var STACK = 'ait_tg_stack';
  function navType() {
    try {
      var n = performance.getEntriesByType('navigation')[0];
      if (n && n.type) return n.type;
    } catch (e) {}
    var t = performance.navigation && performance.navigation.type;
    return t === 1 ? 'reload' : t === 2 ? 'back_forward' : 'navigate';
  }
  function syncBack(type) {
    var s;
    try { s = JSON.parse(sessionStorage.getItem(STACK)) || []; } catch (e) { s = []; }
    if (!(s instanceof Array)) s = [];
    var here = location.pathname + location.search;
    if (/(^|[#?&])tgWebApp(Data|Platform)=/.test(location.hash)) s = [here];
    else if (type === 'back_forward') {
      var i = s.lastIndexOf(here);
      s = i >= 0 ? s.slice(0, i + 1) : [here];
    } else if (type === 'reload') {
      if (!s.length) s = [here];
    } else if (s[s.length - 1] !== here) s.push(here);
    try { sessionStorage.setItem(STACK, JSON.stringify(s.slice(-50))); } catch (e) {}
    if (!at('6.1')) return;
    safe(function () { if (s.length > 1) W.BackButton.show(); else W.BackButton.hide(); });
  }
  if (at('6.1')) safe(function () { W.BackButton.onClick(function () { history.back(); }); });
  syncBack(navType());
  /* Уходя, прячем кнопку: следующая страница может быть без этого скрипта
     (главная, продукт) — там осталась бы кнопка, которая ничего не делает.
     Своя страница покажет её снова. Из кэша «назад» страница возвращается
     без перезапуска скриптов — там стек пересчитываем сами. */
  window.addEventListener('pagehide', function () {
    if (at('6.1')) safe(function () { W.BackButton.hide(); });
  });
  window.addEventListener('pageshow', function (e) {
    if (e.persisted) { syncBack('back_forward'); paint(true); }
  });
})();
