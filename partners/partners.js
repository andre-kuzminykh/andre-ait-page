/* Партнёры Andre AI — каталог, публичная карточка партнёра, заявки (FR-SITE120…139, NFR-SITE106…110).
   Vanilla ES5 без сборки и зависимостей, как главная andre.technology. Данные — partners.json (fetch), при сбое и на file:// —
   встроенная копия #partners-data. Все адреса внутри сайта относительные: страница одна и та же на andre.technology/partners/
   и на partners.andre.technology (NFR-SITE110). */
(function () {
  'use strict';
  window.__pjs = 1;

  /* I18N:BEGIN — английские тексты разметки (русские стоят в самой разметке) и строки, которые собирает скрипт, на обоих языках.
     Это JSON — двойные кавычки, без запятой в конце: тест читает его как есть и сверяет ключи языков (FR-SITE139). */
  var I18N = {
    "en": {
      "skip": "Skip to the catalog",
      "logo": "Partners",
      "aria.nav": "Sections",
      "aria.lang": "Language",
      "aria.close": "Close",
      "aria.rmin": "Rate from",
      "aria.rmax": "Rate up to",
      "nav.catalog": "Catalog",
      "nav.become": "Become a partner",
      "cta.join": "Become a partner",
      "hero.k": "Andre AI Partners",
      "hero.h": "Certified <span class=\"pv\">AI transformation</span> consultants",
      "hero.sub": "They take your company further after the Andre AI strategy: review your AS-IS → TO-BE process maps, train your team and launch processes in Neuronium.",
      "st.1.v": "10 maps an hour",
      "st.1": "process map review pace",
      "st.2.v": "12 sessions",
      "st.2": "team bootcamp over 3 months",
      "st.3": "consultant rate per hour",
      "cat.h": "Partner catalog",
      "cat.sub": "best first — by rating adjusted for the number of reviews",
      "cat.examples": "For now the catalog shows example profiles — this is how the cards of certified partners will look.",
      "cat.empty.h": "No one found",
      "cat.empty.p": "Change the search or reset the filters — there are other consultants in the catalog.",
      "f.q": "Search partners",
      "f.q.ph": "Name, skill, industry…",
      "f.toggle": "Filters",
      "f.sort": "Sort",
      "s.best": "Best first",
      "s.rate_up": "Rate: low to high",
      "s.rate_down": "Rate: high to low",
      "s.projects": "Most projects",
      "f.svc": "Service",
      "f.svc.all": "All",
      "svc.review": "Map review",
      "svc.bootcamp": "Bootcamp",
      "svc.neuronium": "Neuronium implementation",
      "f.ind": "Industry",
      "f.any.ind": "All industries",
      "f.lng": "Language",
      "f.any.lng": "Any language",
      "f.loc": "Location",
      "f.any.loc": "Any location",
      "f.rate": "Hourly rate",
      "f.reset": "Reset filters",
      "be.k": "Partner program",
      "be.h": "How to become a <span class=\"pv\">partner</span>",
      "be.sub": "Partners take Andre AI clients further after their AI strategy: they review process maps, train teams and implement processes in Neuronium. Three steps — and your profile is in the catalog.",
      "be.s1.h": "Complete the Andre AI Academy",
      "be.s1.p": "A course for future AI consultants: AS-IS → TO-BE processes, AI agents and launching processes in Neuronium.",
      "be.s1.a": "Open the course",
      "be.s2.h": "Get certified",
      "be.s2.p": "An exam on process analysis and map review — and you are an Andre AI Certified Consultant.",
      "be.s3.h": "Pass the interview",
      "be.s3.p": "We go through a real case with the Andre AI team, agree on your rate — and your profile appears in the catalog.",
      "be.earn": "Earn from <span class=\"go\">$50</span> to <span class=\"go\">$300</span> an hour",
      "be.e1.h": "You set your own rate",
      "be.e1.p": "From $50 an hour. A new rate applies to new orders.",
      "be.e2.h": "70% of every service is yours",
      "be.e2.p": "Map reviews and bootcamps: the client pays rate × hours ÷ 0.70 — you get 70%, Andre AI 30%.",
      "be.e3.h": "+10% for clients with your promo code",
      "be.e3.p": "The client gets 10% off the AI strategy and the first Neuronium month, you get 10% of what they pay.",
      "calc.rate": "Your rate",
      "calc.client": "Client pays",
      "calc.you": "You get",
      "calc.r1": "Review of 10 maps · 1 hour",
      "calc.r2": "Bootcamp · 12 sessions over 3 months",
      "calc.r3": "Promo code · e.g. a $500 strategy",
      "calc.note": "Review pace — 10 maps an hour. Bootcamp — 12 weekly 60-minute sessions for one team of 10 people.",
      "be.cta": "Apply",
      "foot.strategy": "AI strategy",
      "foot.neuronium": "Neuronium",
      "foot.academy": "Academy",
      "legal.privacy": "Privacy policy",
      "legal.terms": "Terms of use",
      "req.h": "Request to a consultant",
      "req.example": "This is an example profile: the Andre AI team will get your request and match you with a certified consultant.",
      "fm.name": "Name",
      "fm.email": "Email",
      "fm.company": "Company",
      "fm.msg": "Message",
      "fm.msg.ph": "Which processes you want to review or launch, timing, team size",
      "req.send": "Send request",
      "req.ok.h": "Request sent",
      "req.ok.p": "We will pass it to the consultant — the reply will come to your email.",
      "ok": "Done",
      "app.h": "Partner application",
      "app.sub": "Tell us about yourself — we will reply by email and invite you to the Academy and the interview.",
      "app.in": "LinkedIn profile",
      "app.exp": "Experience",
      "app.exp.ph": "What you have done: processes, industries, tools, AI projects",
      "app.rate": "Rate, $ per hour",
      "app.send": "Send application",
      "app.ok.h": "Application received",
      "app.ok.p": "Thank you! We will reply by email and tell you about the Academy and the interview.",
      "err.name": "Enter your name.",
      "err.email": "Enter a valid email.",
      "err.in": "We need a link to a LinkedIn profile: linkedin.com/in/…",
      "err.exp": "Tell us about your experience — a couple of sentences at least.",
      "err.rate": "The rate is from $50 to $300 an hour.",

      "title": "Andre AI Partners — AI transformation consultants",
      "title.p": "%s — Andre AI Partners",
      "found": ["<b>%n</b> consultant found", "<b>%n</b> consultants found", "<b>%n</b> consultants found"],
      "more": "Show more · %n",
      "reviews": ["%n review", "%n reviews", "%n reviews"],
      "projects": ["%n project", "%n projects", "%n projects"],
      "c.projects": "Projects",
      "c.rate": "Rate",
      "per.h": "/h",
      "c.open": "View profile",
      "c.in": "LinkedIn — %s (opens in a new tab)",
      "c.svc": "Services",
      "c.place": "Location",
      "c.lng": "Languages",
      "bdg.cert": "Andre AI Certified",
      "bdg.ex": "Example profile",
      "remote": "remote",
      "onsite": "on-site",
      "loc.remote": "Remote",
      "rating.sr": "Rated %r out of 5",
      "pf.ex": "Example profile: the person, the reviews and the LinkedIn link are fictional — this is how a partner's card will look.",
      "pf.about": "About",
      "pf.services": "Services and prices",
      "pf.skills": "Skills",
      "pf.ind": "Industries",
      "pf.lng": "Languages",
      "pf.certs": "Certificates",
      "pf.reviews": "Reviews",
      "pf.since": "In the catalog since %s",
      "pf.choose": "Choose this consultant",
      "pf.copy": "Copy link",
      "pf.copied": "Link copied",
      "svcl.review": "Process map review",
      "svcl.bootcamp": "Team bootcamp",
      "svcl.neuronium": "Neuronium implementation",
      "sd.review": "Expert review of the AS-IS / TO-BE maps you pick, with recommendations on what to fix. Pace — 10 maps an hour.",
      "sd.bootcamp": "12 weekly 60-minute sessions for one team of 10 people: you launch your chosen processes in Neuronium together with the consultant.",
      "sd.neuronium": "Launching processes in Neuronium end to end: integrations, AI agents, support.",
      "pu.review": "per 10 maps",
      "pu.one": "%s per map",
      "pu.bootcamp": "for 3 months",
      "pu.month": "≈ %s a month",
      "pu.quote": "By estimate",
      "pu.quote.s": "scope and price agreed before payment",
      "pf.note": "Service price = rate × hours ÷ 0.70: the consultant gets 70%, Andre AI 30%. The final amount is shown in the order before payment.",
      "req.sub": "%name · rate %rate",
      "sending": "Sending…",
      "calc.l.client": "Client:",
      "calc.l.you": "You:",
      "months": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
      "date": "%m %d, %y",
      "since": "%m %y",

      "ind.retail": "Retail",
      "ind.ecommerce": "E-commerce",
      "ind.logistics": "Logistics",
      "ind.manufacturing": "Manufacturing",
      "ind.finance": "Finance",
      "ind.healthcare": "Healthcare",
      "ind.education": "Education",
      "ind.services": "Professional services",
      "ind.realestate": "Real estate",
      "ind.construction": "Construction",
      "ind.hospitality": "Hospitality",
      "ind.marketing": "Marketing and agencies",
      "ind.it": "IT and SaaS",

      "lng.ru": "Russian",
      "lng.en": "English",
      "lng.de": "German",
      "lng.kk": "Kazakh",
      "lng.es": "Spanish",
      "lng.pt": "Portuguese",
      "lng.fr": "French",
      "lng.it": "Italian",
      "lng.uk": "Ukrainian",
      "lng.be": "Belarusian",
      "lng.uz": "Uzbek",
      "lng.tr": "Turkish",
      "lng.pl": "Polish",
      "lng.zh": "Chinese",
      "lng.ar": "Arabic",
      "lng.hy": "Armenian",
      "lng.ka": "Georgian",
      "lng.sr": "Serbian",
      "lng.he": "Hebrew",
      "lng.nl": "Dutch"
    },
    "ru": {
      "title": "Партнёры Andre AI — консультанты по ИИ-трансформации",
      "title.p": "%s — Партнёры Andre AI",
      "found": ["Найден <b>%n</b> консультант", "Найдено <b>%n</b> консультанта", "Найдено <b>%n</b> консультантов"],
      "more": "Показать ещё · %n",
      "reviews": ["%n отзыв", "%n отзыва", "%n отзывов"],
      "projects": ["%n проект", "%n проекта", "%n проектов"],
      "c.projects": "Проектов",
      "c.rate": "Ставка",
      "per.h": "/ч",
      "c.open": "Открыть профиль",
      "c.in": "LinkedIn — %s (откроется в новой вкладке)",
      "c.svc": "Услуги",
      "c.place": "Где работает",
      "c.lng": "Языки",
      "bdg.cert": "Andre AI Certified",
      "bdg.ex": "Пример профиля",
      "remote": "удалённо",
      "onsite": "очно",
      "loc.remote": "Удалённо",
      "rating.sr": "Рейтинг %r из 5",
      "pf.ex": "Пример профиля: человек, отзывы и ссылка на LinkedIn вымышлены — так будет выглядеть карточка партнёра.",
      "pf.about": "О консультанте",
      "pf.services": "Услуги и цены",
      "pf.skills": "Навыки",
      "pf.ind": "Отрасли",
      "pf.lng": "Языки",
      "pf.certs": "Сертификаты",
      "pf.reviews": "Отзывы",
      "pf.since": "В каталоге с %s",
      "pf.choose": "Выбрать консультанта",
      "pf.copy": "Скопировать ссылку",
      "pf.copied": "Ссылка скопирована",
      "svc.review": "Проверка схем",
      "svc.bootcamp": "Буткемп",
      "svc.neuronium": "Внедрение в Нейронии",
      "svcl.review": "Проверка схем",
      "svcl.bootcamp": "Буткемп для команды",
      "svcl.neuronium": "Внедрение в Нейронии",
      "sd.review": "Экспертное ревью выбранных схем «как есть / как будет» и рекомендации по правкам. Темп — 10 схем в час.",
      "sd.bootcamp": "12 еженедельных занятий по 60 минут для одной команды из 10 человек: вместе с консультантом запускаете выбранные процессы в Нейронии.",
      "sd.neuronium": "Запуск процессов в Нейронии под ключ: интеграции, ИИ-агенты, сопровождение.",
      "pu.review": "за 10 схем",
      "pu.one": "%s за схему",
      "pu.bootcamp": "за 3 месяца",
      "pu.month": "≈ %s в месяц",
      "pu.quote": "По смете",
      "pu.quote.s": "объём и цена — до оплаты",
      "pf.note": "Цена услуги = ставка × часы ÷ 0,70: 70 % получает консультант, 30 % — Andre AI. Итоговая сумма — в заказе до оплаты.",
      "req.sub": "%name · ставка %rate",
      "sending": "Отправляем…",
      "calc.l.client": "Клиент:",
      "calc.l.you": "Вам:",
      "months": ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"],
      "date": "%d %m %y",
      "since": "%m %y",

      "ind.retail": "Ритейл",
      "ind.ecommerce": "E-commerce",
      "ind.logistics": "Логистика",
      "ind.manufacturing": "Производство",
      "ind.finance": "Финансы",
      "ind.healthcare": "Медицина",
      "ind.education": "Образование",
      "ind.services": "Профессиональные услуги",
      "ind.realestate": "Недвижимость",
      "ind.construction": "Строительство",
      "ind.hospitality": "Гостиницы и рестораны",
      "ind.marketing": "Маркетинг и агентства",
      "ind.it": "IT и SaaS",

      "lng.ru": "Русский",
      "lng.en": "Английский",
      "lng.de": "Немецкий",
      "lng.kk": "Казахский",
      "lng.es": "Испанский",
      "lng.pt": "Португальский",
      "lng.fr": "Французский",
      "lng.it": "Итальянский",
      "lng.uk": "Украинский",
      "lng.be": "Белорусский",
      "lng.uz": "Узбекский",
      "lng.tr": "Турецкий",
      "lng.pl": "Польский",
      "lng.zh": "Китайский",
      "lng.ar": "Арабский",
      "lng.hy": "Армянский",
      "lng.ka": "Грузинский",
      "lng.sr": "Сербский",
      "lng.he": "Иврит",
      "lng.nl": "Нидерландский"
    }
  };
  /* I18N:END */

  /* ---------- правила каталога и цен ---------- */
  var SVC = ['review', 'bootcamp', 'neuronium'];          // FR-SITE126: услуги — в этом порядке и в фильтре, и в карточке
  var PAGE = 12, AUTO_PAGES = 3;                         // FR-SITE128: порция и сколько порций подгружается само подряд
  var RATE_MIN = 50, RATE_MAX = 300, RATE_STEP = 10;     // FR-SITE126: фильтр ставки $50–300 (на краю 300 — «и выше»)
  var PRIOR_RATING = 4.0, PRIOR_WEIGHT = 5;              // FR-SITE122: байесовская поправка рейтинга на число отзывов
  var CERT_ID = 'andre-ai-certified';
  var ENDPOINT = 'https://formsubmit.co/ajax/admin@andre.technology';  // FR-SITE133/136: тот же канал, что у заявок главной
  var SORTS_LIST = ['best', 'rate_up', 'rate_down', 'projects'];

  /* FR-SITE132: цены услуг — по ценовой политике Andre AI (§4): клиент платит вознаграждение консультанта ÷ 0,70.
     Деньги — в центах, каждая позиция округляется до цента вверх от половины (half-up). Проверка: 10 схем = 1 час;
     буткемп: 12 часов за 3 месяца. Промокод (§5): −10 % клиенту, партнёру 10 % от оплаченного. */
  function divHalfUp(num, den) { return Math.floor((2 * num + den) / (2 * den)); }
  var PRICING = {
    rateCents: function (rate) { return Math.round(rate * 100); },
    /* проверка k схем: часы = k / 10; клиент = ставка × часы ÷ 0,70 = ставка_в_центах × k ÷ 7 */
    review: function (rate, maps) {
      var rc = Math.round(rate * 100), k = maps == null ? 10 : maps;
      var client = divHalfUp(rc * k, 7), consultant = divHalfUp(rc * k, 10);
      return { client: client, consultant: consultant, andre: client - consultant };
    },
    /* буткемп: 12 часов; клиент = 12 × ставка ÷ 0,70 = ставка_в_центах × 120 ÷ 7; средняя цена месяца — курс ÷ 3 */
    bootcamp: function (rate) {
      var rc = Math.round(rate * 100), client = divHalfUp(rc * 120, 7), consultant = rc * 12;
      return { client: client, consultant: consultant, andre: client - consultant, month: divHalfUp(client, 3) };
    },
    /* промокод: скидка 10 % от цены по прайсу, комиссия партнёру — 10 % от того, что клиент заплатил */
    promo: function (listCents) {
      var discount = divHalfUp(listCents, 10), client = listCents - discount, commission = divHalfUp(client, 10);
      return { discount: discount, client: client, commission: commission, andre: client - commission };
    }
  };

  /* ---------- мелочи ---------- */
  var D = document, root = D.documentElement;
  function $(s, r) { return (r || D).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || D).querySelectorAll(s)); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function sget(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function sset(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function own(o, k) { return Object.prototype.hasOwnProperty.call(o, k); }
  /* короткие слова через дефис («ИИ-агенты», «e-commerce») не рвутся по дефису — как на главной (FR-SITE100) */
  function nb(s) { return esc(s).replace(/[^\s«»"()\/,.:;!?]+-[^\s«»"()\/,.:;!?]+/g, function (w) { return w.length <= 24 ? '<span class="nw">' + w + '</span>' : w; }); }
  function icon(id, cls) { return '<svg class="ic' + (cls ? ' ' + cls : '') + '" aria-hidden="true"><use href="#i-' + id + '"/></svg>'; }
  var REDUCED = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  var state = { lang: root.lang === 'en' ? 'en' : 'ru', q: '', svc: '', ind: '', lng: '', loc: '', min: RATE_MIN, max: RATE_MAX, sort: 'best',
    shown: 0, auto: 0, open: null, pushed: false, langInUrl: false };
  var DATA = [], VIEW = [], RU = null, RU_PH = null, RU_ARIA = null, ready = false;

  function tx(k) { var d = I18N[state.lang]; if (own(d, k)) return d[k]; if (own(I18N.ru, k)) return I18N.ru[k]; return state.lang === 'ru' && RU && own(RU, k) ? RU[k] : k; }
  function fmt(s, map) { return String(s).replace(/%(\w+)/g, function (m, k) { return own(map, k) ? map[k] : m; }); }
  function plural(n, forms) {
    if (state.lang === 'en') return fmt(forms[n === 1 ? 0 : 1], { n: n });
    var a = n % 10, b = n % 100;
    return fmt(forms[a === 1 && b !== 11 ? 0 : a >= 2 && a <= 4 && (b < 12 || b > 14) ? 1 : 2], { n: n });
  }
  function L(o) { if (o == null) return ''; if (typeof o !== 'object') return String(o); return o[state.lang] != null ? o[state.lang] : (o.ru != null ? o.ru : o.en); }
  /* $1 234,56 по-русски (неразрывный пробел есть в JetBrains Mono — FR-SITE100), $1,234.56 по-английски; целые доллары — без копеек */
  function money(cents) {
    var neg = cents < 0, c = Math.abs(Math.round(cents)), d = Math.floor(c / 100), r = c % 100, en = state.lang === 'en';
    var s = String(d).replace(/\B(?=(\d{3})+(?!\d))/g, en ? ',' : ' ');
    if (r) s += (en ? '.' : ',') + (r < 10 ? '0' : '') + r;
    return (neg ? '−' : '') + '$' + s;
  }
  function rateTxt(r) { var s = (Math.round(r * 10) / 10).toFixed(1); return state.lang === 'en' ? s : s.replace('.', ','); }
  function dateTxt(iso, kind) {
    var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso || ''); if (!m) return '';
    return fmt(tx(kind === 'since' ? 'since' : 'date'), { y: m[1], m: tx('months')[+m[2] - 1], d: String(+m[3]) });
  }
  /* поиск без учёта регистра, «ё/е» и надстрочных знаков (NFD) */
  function norm(s) { s = String(s == null ? '' : s).toLowerCase(); if (s.normalize) s = s.normalize('NFD').replace(/[̀-ͯ]/g, ''); return s.replace(/ё/g, 'е'); }

  /* ---------- данные (FR-SITE137): проверка профиля по схеме из SPEC-SITE.md ---------- */
  var SLUG_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
  var IN_RE = /^https:\/\/(?:[a-z]{2,3}\.)?linkedin\.com\/in\/[A-Za-z0-9\-_%.]+\/?$/;
  function both(o) { return !!o && typeof o === 'object' && typeof o.ru === 'string' && typeof o.en === 'string' && o.ru.length > 0 && o.en.length > 0; }
  function isInt(n) { return typeof n === 'number' && isFinite(n) && Math.floor(n) === n && n >= 0; }
  function strs(a) { return Array.isArray(a) && a.every(function (x) { return typeof x === 'string' && x.length > 0; }); }
  function problem(p) {
    if (!p || typeof p !== 'object') return 'not an object';
    if (typeof p.slug !== 'string' || !SLUG_RE.test(p.slug)) return 'slug';
    if (!both(p.name) || !both(p.headline) || !both(p.about)) return 'name/headline/about';
    if (typeof p.rating !== 'number' || !(p.rating >= 0 && p.rating <= 5)) return 'rating';
    if (!isInt(p.reviews_count) || !isInt(p.projects)) return 'reviews_count/projects';
    if (typeof p.rate_usd !== 'number' || !(p.rate_usd >= RATE_MIN)) return 'rate_usd';
    if (!strs(p.services) || !p.services.length || !p.services.every(function (s) { return SVC.indexOf(s) >= 0; })) return 'services';
    if (!strs(p.industries) || !strs(p.languages) || !p.languages.length) return 'industries/languages';
    var l = p.location; if (!l || !both(l.city) || !both(l.country) || typeof l.country_code !== 'string' || typeof l.remote !== 'boolean') return 'location';
    if (typeof p.linkedin !== 'string' || !IN_RE.test(p.linkedin)) return 'linkedin';
    if (!p.skills || !strs(p.skills.ru) || !strs(p.skills.en)) return 'skills';
    if (!Array.isArray(p.certificates) || !Array.isArray(p.reviews)) return 'certificates/reviews';
    if (typeof p.joined !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(p.joined)) return 'joined';
    return '';
  }
  function prepare(list) {
    var out = [], seen = {};
    (Array.isArray(list) ? list : []).forEach(function (p, i) {
      var why = problem(p);
      if (why || seen[p.slug]) { if (window.console && console.warn) console.warn('partners.json: профиль #' + i + ' пропущен (' + (why || 'повтор slug') + ')'); return; }
      seen[p.slug] = 1;
      p.certificates = p.certificates.filter(function (c) { return c && typeof c.id === 'string' && both(c.title); });
      p.reviews = p.reviews.filter(function (r) { return r && both(r.author) && both(r.text) && typeof r.rating === 'number'; })
        .sort(function (a, b) { return (b.date || '') < (a.date || '') ? -1 : (b.date || '') > (a.date || '') ? 1 : 0; });
      p._score = (PRIOR_WEIGHT * PRIOR_RATING + p.rating * p.reviews_count) / (PRIOR_WEIGHT + p.reviews_count);
      var hay = [p.name.ru, p.name.en, p.headline.ru, p.headline.en, p.about.ru, p.about.en, p.skills.ru.join(' '), p.skills.en.join(' '),
        p.location.city.ru, p.location.city.en, p.location.country.ru, p.location.country.en,
        p.location.remote ? I18N.ru.remote + ' ' + I18N.en.remote : I18N.ru.onsite + ' ' + I18N.en.onsite];
      p.industries.forEach(function (k) { hay.push(I18N.ru['ind.' + k] || k, I18N.en['ind.' + k] || k); });
      p.services.forEach(function (k) { hay.push(I18N.ru['svc.' + k], I18N.en['svc.' + k], I18N.ru['svcl.' + k], I18N.en['svcl.' + k]); });
      p.languages.forEach(function (k) { hay.push(I18N.ru['lng.' + k] || k, I18N.en['lng.' + k] || k); });
      p._hay = norm(hay.join(' \u0001 '));
      out.push(p);
    });
    return out;
  }
  function inlineData() { try { return JSON.parse($('#partners-data').textContent || '[]'); } catch (e) { return []; } }
  /* сначала partners.json (его опубликует и будущий кабинет партнёра), при сбое, долгом ответе и на file:// — встроенная копия */
  function load(cb) {
    var finished = false;
    function finish(list, src) { if (finished) return; finished = true; API.source = src; cb(list); }
    if (location.protocol === 'file:' || !window.fetch) { finish(inlineData(), 'inline'); return; }
    var t = setTimeout(function () { finish(inlineData(), 'inline'); }, 3500);
    fetch('partners.json', { cache: 'no-cache' }).then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (j) { clearTimeout(t); if (!Array.isArray(j)) throw new Error('partners.json: not an array'); finish(j, 'fetch'); })
      .catch(function () { clearTimeout(t); finish(inlineData(), 'inline'); });
  }

  /* ---------- адрес: фильтры, язык и открытый профиль (FR-SITE129, FR-SITE130) ---------- */
  function parseQS(search) {
    var o = {};
    String(search || '').replace(/^\?/, '').split('&').forEach(function (kv) {
      if (!kv) return; var i = kv.indexOf('='), k = i < 0 ? kv : kv.slice(0, i), v = i < 0 ? '' : kv.slice(i + 1);
      try { o[decodeURIComponent(k.replace(/\+/g, ' '))] = decodeURIComponent(v.replace(/\+/g, ' ')); } catch (e) {}
    });
    return o;
  }
  function urlWith(over) {
    var cur = parseQS(location.search), o = {}, k, keys = ['lang', 'q', 'svc', 'ind', 'lng', 'loc', 'rate', 'sort', 'p'];
    for (k in cur) if (own(cur, k) && keys.indexOf(k) < 0) o[k] = cur[k];       // чужие метки (utm и т. п.) не теряем
    if (state.langInUrl) o.lang = state.lang;
    if (state.q) o.q = state.q;
    if (state.svc) o.svc = state.svc;
    if (state.ind) o.ind = state.ind;
    if (state.lng) o.lng = state.lng;
    if (state.loc) o.loc = state.loc;
    if (state.min > RATE_MIN || state.max < RATE_MAX) o.rate = state.min + '-' + state.max;
    if (state.sort !== 'best') o.sort = state.sort;
    if (state.open) o.p = state.open;
    for (k in over) if (own(over, k)) { if (over[k] == null || over[k] === '') delete o[k]; else o[k] = over[k]; }
    var qs = Object.keys(o).map(function (x) { return encodeURIComponent(x) + '=' + encodeURIComponent(o[x]); }).join('&');
    return location.pathname + (qs ? '?' + qs : '') + location.hash;
  }
  var urlT = 0;
  function syncUrl(now) {
    clearTimeout(urlT);
    var go = function () { try { history.replaceState(history.state, '', urlWith({})); } catch (e) {} };
    if (now) go(); else urlT = setTimeout(go, 300);
  }
  function readUrl() {
    var o = parseQS(location.search);
    state.langInUrl = o.lang === 'ru' || o.lang === 'en';
    state.q = (o.q || '').slice(0, 120);
    state.svc = SVC.indexOf(o.svc) >= 0 ? o.svc : '';
    state.ind = o.ind || ''; state.lng = o.lng || ''; state.loc = o.loc || '';
    state.sort = SORTS_LIST.indexOf(o.sort) >= 0 ? o.sort : 'best';
    var m = /^(\d+)-(\d+)$/.exec(o.rate || '');
    if (m) { state.min = snap(+m[1]); state.max = snap(+m[2]); if (state.min > state.max) { var t = state.min; state.min = state.max; state.max = t; } }
    return o.p || '';
  }
  function snap(v) { v = Math.round(v / RATE_STEP) * RATE_STEP; return v < RATE_MIN ? RATE_MIN : v > RATE_MAX ? RATE_MAX : v; }

  /* ---------- отбор и порядок (FR-SITE122, 125, 126, 127) ---------- */
  function cmpBest(a, b) {
    return (b._score - a._score) || (b.projects - a.projects) || (b.reviews_count - a.reviews_count) ||
      (a.joined < b.joined ? -1 : a.joined > b.joined ? 1 : 0) || (a.slug < b.slug ? -1 : a.slug > b.slug ? 1 : 0);
  }
  var SORTS = {
    best: cmpBest,
    rate_up: function (a, b) { return (a.rate_usd - b.rate_usd) || cmpBest(a, b); },
    rate_down: function (a, b) { return (b.rate_usd - a.rate_usd) || cmpBest(a, b); },
    projects: function (a, b) { return (b.projects - a.projects) || cmpBest(a, b); }
  };
  function matches(p, toks) {
    if (state.svc && p.services.indexOf(state.svc) < 0) return false;
    if (state.ind && p.industries.indexOf(state.ind) < 0) return false;
    if (state.lng && p.languages.indexOf(state.lng) < 0) return false;
    if (state.loc === 'remote' && !p.location.remote) return false;
    if (state.loc.indexOf('c:') === 0 && p.location.country_code !== state.loc.slice(2)) return false;
    if (p.rate_usd < state.min) return false;
    if (state.max < RATE_MAX && p.rate_usd > state.max) return false;
    for (var i = 0; i < toks.length; i++) if (p._hay.indexOf(toks[i]) < 0) return false;
    return true;
  }
  function activeFilters() { return (state.svc ? 1 : 0) + (state.ind ? 1 : 0) + (state.lng ? 1 : 0) + (state.loc ? 1 : 0) + (state.min > RATE_MIN || state.max < RATE_MAX ? 1 : 0); }

  /* ---------- карточка каталога (FR-SITE123, FR-SITE124) ---------- */
  var AVA = [['#8854F3', '#F97316'], ['#6d3fd8', '#e0708f'], ['#a071ff', '#ff8a33'], ['#5b3fd8', '#c06bc9'], ['#c06bc9', '#F97316'], ['#7c4dff', '#38bdf8']];
  function hash(s) { var h = 0; for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0; return Math.abs(h); }
  function initials(name) { var w = String(name).trim().split(/\s+/); return ((w[0] || '').charAt(0) + (w.length > 1 ? w[w.length - 1].charAt(0) : '')).toUpperCase(); }
  function ava(p) { var c = AVA[hash(p.slug) % AVA.length]; return '<span class="ava" aria-hidden="true" style="--a1:' + c[0] + ';--a2:' + c[1] + '">' + esc(initials(L(p.name))) + '</span>'; }
  function starsHTML(r) {
    var five = '', i; for (i = 0; i < 5; i++) five += icon('star');
    return '<span class="stars" aria-hidden="true">' + five + '<span class="fill" style="width:' + Math.max(0, Math.min(100, r / 5 * 100)).toFixed(1) + '%">' + five + '</span></span>';
  }
  function ratingHTML(p) {
    return '<p class="rating"><span class="sr">' + esc(fmt(tx('rating.sr'), { r: rateTxt(p.rating) })) + '</span>' + starsHTML(p.rating) +
      '<b aria-hidden="true">' + rateTxt(p.rating) + '</b><span>' + esc(plural(p.reviews_count, tx('reviews'))) + '</span></p>';
  }
  function certified(p) { return p.certificates.some(function (c) { return c.id === CERT_ID; }); }
  function badgesHTML(p) {
    return (certified(p) ? '<span class="bdg bdg-cert">' + icon('check') + esc(tx('bdg.cert')) + '</span>' : '') +
      (p.example ? '<span class="bdg bdg-ex">' + esc(tx('bdg.ex')) + '</span>' : '');
  }
  function inHTML(p, cls, label) {
    return '<a class="' + cls + '" href="' + esc(p.linkedin) + '" target="_blank" rel="noopener" aria-label="' + esc(fmt(tx('c.in'), { s: L(p.name) })) + '">' + icon('in') + (label ? '<span>LinkedIn</span>' : '') + '</a>';
  }
  function indLabel(k) { return tx('ind.' + k) === 'ind.' + k ? k : tx('ind.' + k); }
  function lngLabel(k) { return tx('lng.' + k) === 'lng.' + k ? k.toUpperCase() : tx('lng.' + k); }
  function placeTxt(p) { return L(p.location.city) + ', ' + L(p.location.country) + ' · ' + tx(p.location.remote ? 'remote' : 'onsite'); }
  function svcOrder(p) { return SVC.filter(function (s) { return p.services.indexOf(s) >= 0; }); }
  function cardHTML(p, i, fx) {
    var inds = p.industries.slice(0, 3).map(function (k) { return '<li class="tag">' + esc(indLabel(k)) + '</li>'; }).join('') +
      (p.industries.length > 3 ? '<li class="tag more">+' + (p.industries.length - 3) + '</li>' : '');
    return '<li><article class="pc' + (fx === 'enter' ? ' new' : fx === 'swap' ? ' swap' : '') + '" style="--i:' + i + '" data-slug="' + esc(p.slug) + '">' +
      '<div class="pc-top">' + ava(p) +
        '<div class="pc-id"><h3 class="pc-name"><a class="pc-link" href="?p=' + encodeURIComponent(p.slug) + '" data-open="' + esc(p.slug) + '">' + esc(L(p.name)) + '</a></h3>' +
        '<p class="pc-head">' + nb(L(p.headline)) + '</p></div>' + inHTML(p, 'pc-in') + '</div>' +
      '<div class="badges">' + badgesHTML(p) + '</div>' + ratingHTML(p) +
      '<dl class="kv"><div><dt>' + esc(tx('c.projects')) + '</dt><dd>' + p.projects + '</dd></div>' +
        '<div><dt>' + esc(tx('c.rate')) + '</dt><dd>' + money(Math.round(p.rate_usd * 100)) + '<small>' + esc(tx('per.h')) + '</small></dd></div></dl>' +
      '<ul class="tags">' + inds + '</ul>' +
      '<div class="meta">' +
        '<p>' + icon('case') + '<span class="sr">' + esc(tx('c.svc')) + ': </span><span>' + esc(svcOrder(p).map(function (s) { return tx('svc.' + s); }).join(' · ')) + '</span></p>' +
        '<p>' + icon('pin') + '<span class="sr">' + esc(tx('c.place')) + ': </span><span>' + esc(placeTxt(p)) + '</span></p>' +
        '<p>' + icon('globe') + '<span class="sr">' + esc(tx('c.lng')) + ': </span><span>' + esc(p.languages.map(function (k) { return k.toUpperCase(); }).join(' · ')) + '</span></p>' +
      '</div>' +
      '<span class="pc-go" aria-hidden="true">' + esc(tx('c.open')) + icon('arrow') + '</span>' +
    '</article></li>';
  }

  /* ---------- список: отрисовка порциями (FR-SITE128, NFR-SITE109) ---------- */
  var grid = $('#grid'), moreBtn = $('#more'), emptyEl = $('#empty'), foundEl = $('#found'), resetBtn = $('#reset'), sentinel = $('#sentinel'), io = null;
  /* fx: 'enter' — карточки въезжают по одной (первая загрузка и новые порции), 'swap' — после фильтра и поиска только короткое
     проявление (иначе список мигал бы на каждой букве), 'none' — смена языка */
  function apply(fx) {
    var toks = norm(state.q).split(/\s+/).filter(Boolean);
    VIEW = DATA.filter(function (p) { return matches(p, toks); }).sort(SORTS[state.sort] || cmpBest);
    state.shown = 0; state.auto = 0; grid.innerHTML = '';
    renderMore(false, PAGE, fx || 'swap');
    bar();
  }
  function renderMore(focusFirst, count, fx) {
    var from = state.shown, to = Math.min(VIEW.length, from + (count || PAGE)), html = '', i;
    if (to <= from) { moreState(); return; }
    $$('.pc.new, .pc.swap', grid).forEach(function (c) { c.classList.remove('new', 'swap'); });
    for (i = from; i < to; i++) html += cardHTML(VIEW[i], i - from, fx || 'enter');
    grid.insertAdjacentHTML('beforeend', html);
    state.shown = to;
    moreState();
    if (focusFirst) { var a = $$('.pc-link', grid)[from]; if (a) try { a.focus({ preventScroll: true }); } catch (e) { a.focus(); } }
    if (io) { io.unobserve(sentinel); io.observe(sentinel); }   // список всё ещё короче окна — сторож сработает снова
  }
  function moreState() {
    var left = VIEW.length - state.shown;
    moreBtn.hidden = left <= 0;
    if (left > 0) moreBtn.textContent = fmt(tx('more'), { n: left });
  }
  function bar() {
    var n = VIEW.length, act = activeFilters();
    foundEl.innerHTML = plural(n, tx('found'));
    $('#rank').hidden = state.sort !== 'best' || !n;
    emptyEl.hidden = n > 0 || !ready;
    resetBtn.hidden = !(act || state.q);
    var fc = $('#fcount'); fc.hidden = !act; fc.textContent = act;
    $('#ex-note').hidden = !DATA.some(function (p) { return p.example; });
  }

  /* ---------- фильтры (FR-SITE125, 126, 127) ---------- */
  var qIn = $('#q'), sortSel = $('#sort'), indSel = $('#ind'), lngSel = $('#lng'), locSel = $('#loc'), rmin = $('#rmin'), rmax = $('#rmax'), dual = $('#dual');
  function fillSelect(sel, items, value) {
    while (sel.options.length > 1) sel.remove(1);
    items.forEach(function (it) { var o = D.createElement('option'); o.value = it[0]; o.textContent = it[1]; sel.appendChild(o); });
    sel.value = value; if (sel.value !== value) sel.value = '';
    return sel.value;
  }
  function byLabel(a, b) { return a[1].localeCompare(b[1], state.lang); }
  function buildOptions() {
    var ind = {}, lng = {}, cc = {}, remote = false;
    DATA.forEach(function (p) {
      p.industries.forEach(function (k) { ind[k] = 1; });
      p.languages.forEach(function (k) { lng[k] = 1; });
      cc[p.location.country_code] = p.location.country;
      if (p.location.remote) remote = true;
    });
    state.ind = fillSelect(indSel, Object.keys(ind).map(function (k) { return [k, indLabel(k)]; }).sort(byLabel), state.ind);
    state.lng = fillSelect(lngSel, Object.keys(lng).map(function (k) { return [k, lngLabel(k)]; }).sort(byLabel), state.lng);
    var locs = Object.keys(cc).map(function (k) { return ['c:' + k, L(cc[k])]; }).sort(byLabel);
    if (remote) locs.unshift(['remote', tx('loc.remote')]);
    state.loc = fillSelect(locSel, locs, state.loc);
  }
  function rateUI() {
    rmin.value = state.min; rmax.value = state.max;
    var span = RATE_MAX - RATE_MIN;
    dual.style.setProperty('--ka', ((state.min - RATE_MIN) / span).toFixed(4));
    dual.style.setProperty('--kb', ((state.max - RATE_MIN) / span).toFixed(4));
    /* оба бегунка у правого края — сверху должен быть «от», иначе его не сдвинуть */
    rmin.style.zIndex = state.min >= RATE_MAX - RATE_STEP ? 3 : 1; rmax.style.zIndex = 2;
    var txt = money(state.min * 100) + ' — ' + money(state.max * 100) + (state.max >= RATE_MAX ? '+' : '');
    $('#rate-v').textContent = txt;
    rmin.setAttribute('aria-valuetext', money(state.min * 100)); rmax.setAttribute('aria-valuetext', money(state.max * 100) + (state.max >= RATE_MAX ? '+' : ''));
  }
  function controlsUI() {
    qIn.value = state.q; sortSel.value = state.sort;
    $$('#svc input').forEach(function (r) { r.checked = r.value === state.svc; });
    indSel.value = state.ind; lngSel.value = state.lng; locSel.value = state.loc;
    rateUI();
  }
  function changed(now) { apply(); syncUrl(now); }
  var qT = 0;
  qIn.addEventListener('input', function () { clearTimeout(qT); qT = setTimeout(function () { state.q = qIn.value.trim().slice(0, 120); changed(); }, 140); });
  qIn.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); clearTimeout(qT); state.q = qIn.value.trim().slice(0, 120); changed(true); } });
  sortSel.addEventListener('change', function () { state.sort = sortSel.value; changed(true); });
  $('#svc').addEventListener('change', function (e) { if (e.target.name === 'svc') { state.svc = e.target.value; changed(true); } });
  indSel.addEventListener('change', function () { state.ind = indSel.value; changed(true); });
  lngSel.addEventListener('change', function () { state.lng = lngSel.value; changed(true); });
  locSel.addEventListener('change', function () { state.loc = locSel.value; changed(true); });
  function onRate(e) {
    var a = +rmin.value, b = +rmax.value;
    if (a > b) { if (e.target === rmin) a = b; else b = a; }
    state.min = a; state.max = b; rateUI(); changed();
  }
  rmin.addEventListener('input', onRate); rmax.addEventListener('input', onRate);
  function resetAll() {
    state.q = ''; state.svc = ''; state.ind = ''; state.lng = ''; state.loc = ''; state.min = RATE_MIN; state.max = RATE_MAX;
    controlsUI(); changed(true);
  }
  resetBtn.addEventListener('click', function () { resetAll(); qIn.focus(); });
  $('#empty-reset').addEventListener('click', function () { resetAll(); qIn.focus(); });
  $('#ftoggle').addEventListener('click', function () {
    var f = $('#filters'), open = !f.classList.contains('open');
    f.classList.toggle('open', open); this.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  moreBtn.addEventListener('click', function () { state.auto = 0; renderMore(true); });
  if ('IntersectionObserver' in window) {
    /* листание (FR-SITE128): следующая порция подгружается сама, когда низ списка близко, но не больше трёх порций подряд —
       иначе до «Как стать партнёром» не долистать; дальше — кнопка «Показать ещё» */
    io = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting && ready && state.shown < VIEW.length && state.auto < AUTO_PAGES) { state.auto++; renderMore(false); } });
    }, { rootMargin: '0px 0px 320px 0px' });
    io.observe(sentinel);
  }

  /* ---------- окна: фокус, Esc, ловушка Tab, фон неактивен (NFR-SITE106) ---------- */
  var stack = [];
  function focusables(el) {
    return $$('a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]):not(.hp), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])', el)
      .filter(function (x) { return x.getClientRects().length > 0; });
  }
  function lockScroll(on) {
    if (on) { var w = window.innerWidth - root.clientWidth; root.style.setProperty('--sbw', (w > 0 ? w : 0) + 'px'); root.classList.add('lock'); }
    else { root.classList.remove('lock'); root.style.removeProperty('--sbw'); }
  }
  function inertAll() {
    var top = stack.length ? stack[stack.length - 1].ov : null;
    $$('body > *').forEach(function (el) {
      if (el.tagName === 'SCRIPT' || el.tagName === 'NOSCRIPT') return;
      if (top && el !== top) el.setAttribute('inert', ''); else el.removeAttribute('inert');
    });
  }
  function openDlg(ov, opener, focusEl) {
    if (!stack.length) lockScroll(true);
    stack.push({ ov: ov, opener: opener || null });
    ov.hidden = false; inertAll();
    var f = focusEl || ov.firstElementChild;
    try { f.focus({ preventScroll: true }); } catch (e) { f.focus(); }
  }
  function closeDlg(ov, fallback) {
    var i, s = null;
    for (i = stack.length - 1; i >= 0; i--) if (stack[i].ov === ov) { s = stack.splice(i, 1)[0]; break; }
    if (!s) return;
    ov.hidden = true; inertAll();
    if (!stack.length) lockScroll(false);
    var back = s.opener && D.contains(s.opener) && s.opener.getClientRects().length ? s.opener : (fallback || null);
    if (back) try { back.focus({ preventScroll: true }); } catch (e) { back.focus(); }
  }
  function closeTop() { var top = stack[stack.length - 1]; if (!top) return; if (top.ov === pfOv) requestCloseProfile(); else closeDlg(top.ov); }
  D.addEventListener('keydown', function (e) {
    if (!stack.length) return;
    var top = stack[stack.length - 1].ov;
    if (e.key === 'Escape' || e.key === 'Esc') { e.preventDefault(); closeTop(); return; }
    if (e.key !== 'Tab') return;
    var f = focusables(top); if (!f.length) { e.preventDefault(); return; }
    var first = f[0], last = f[f.length - 1], a = D.activeElement, inside = top.contains(a) && a !== top.firstElementChild;
    if (e.shiftKey && (!inside || a === first)) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && (!inside || a === last)) { e.preventDefault(); first.focus(); }
  });
  $$('.ov').forEach(function (ov) {
    ov.addEventListener('click', function (e) {
      if (e.target === ov) { if (ov === pfOv) requestCloseProfile(); else closeDlg(ov); return; }
      var x = e.target.closest ? e.target.closest('[data-close]') : null;
      if (x && ov.contains(x)) { if (ov === pfOv) requestCloseProfile(); else closeDlg(ov); }
    });
  });

  /* ---------- публичная карточка партнёра (FR-SITE130, 131, 132) ---------- */
  var pfOv = $('#profile'), pfBody = $('#pf-body');
  function bySlug(s) { for (var i = 0; i < DATA.length; i++) if (DATA[i].slug === s) return DATA[i]; return null; }
  function sec(key, inner) { return '<section class="pf-sec"><h3 class="pf-h">' + esc(tx(key)) + '</h3>' + inner + '</section>'; }
  function servicesHTML(p) {
    var rows = svcOrder(p).map(function (s) {
      var price;
      if (s === 'review') {
        var r10 = PRICING.review(p.rate_usd, 10), r1 = PRICING.review(p.rate_usd, 1);
        price = '<b data-price="' + r10.client + '">' + money(r10.client) + '</b><small>' + esc(tx('pu.review')) + '</small><small>' + esc(fmt(tx('pu.one'), { s: money(r1.client) })) + '</small>';
      } else if (s === 'bootcamp') {
        var b = PRICING.bootcamp(p.rate_usd);
        price = '<b data-price="' + b.client + '">' + money(b.client) + '</b><small>' + esc(tx('pu.bootcamp')) + '</small><small>' + esc(fmt(tx('pu.month'), { s: money(b.month) })) + '</small>';
      } else {
        price = '<b class="q">' + esc(tx('pu.quote')) + '</b><small>' + esc(tx('pu.quote.s')) + '</small>';
      }
      return '<div class="sv" data-svc="' + s + '"><div class="sv-t"><p class="sv-n">' + esc(tx('svcl.' + s)) + '</p><p class="sv-d">' + nb(tx('sd.' + s)) + '</p></div><div class="sv-p">' + price + '</div></div>';
    }).join('');
    var priced = p.services.indexOf('review') >= 0 || p.services.indexOf('bootcamp') >= 0;
    return '<div class="svcs">' + rows + '</div>' + (priced ? '<p class="pf-note">' + esc(tx('pf.note')) + '</p>' : '');
  }
  function reviewsHTML(p) {
    var head = '<p class="rev-sum">' + starsHTML(p.rating) + '<b>' + rateTxt(p.rating) + '</b><span>' + esc(plural(p.reviews_count, tx('reviews'))) + '</span></p>';
    var list = p.reviews.map(function (r) {
      return '<article class="rev"><div class="rev-h"><p class="rev-a">' + esc(L(r.author)) + (r.company ? '<span>' + esc(L(r.company)) + '</span>' : '') + '</p>' +
        '<span class="sr">' + esc(fmt(tx('rating.sr'), { r: rateTxt(r.rating) })) + '</span>' + starsHTML(r.rating) + '</div>' +
        '<p class="rev-t">' + nb(L(r.text)) + '</p>' + (r.date ? '<time datetime="' + esc(r.date) + '">' + esc(dateTxt(r.date)) + '</time>' : '') + '</article>';
    }).join('');
    return head + '<div class="revs">' + list + '</div>';
  }
  function tagsHTML(arr) { return '<ul class="tags">' + arr.map(function (t) { return '<li class="tag">' + nb(t) + '</li>'; }).join('') + '</ul>'; }
  function profileHTML(p) {
    var certs = '<ul class="certs">' + p.certificates.map(function (c) {
      return '<li>' + icon(c.id === CERT_ID ? 'award' : 'check') + '<span>' + esc(L(c.title)) + (c.year ? '<small>' + esc(c.year) + '</small>' : '') + '</span></li>';
    }).join('') + '</ul>';
    return (p.example ? '<p class="pf-ex">' + nb(tx('pf.ex')) + '</p>' : '') +
      '<div class="pf-top">' + ava(p) +
        '<div class="pf-id"><div class="badges">' + badgesHTML(p) + '</div>' +
          '<h2 class="pf-name" id="pf-name">' + esc(L(p.name)) + '</h2><p class="pf-head">' + nb(L(p.headline)) + '</p>' +
          '<div class="pf-facts">' + ratingHTML(p) +
            '<span>' + icon('case') + esc(plural(p.projects, tx('projects'))) + '</span>' +
            '<span class="pf-rate"><b>' + money(Math.round(p.rate_usd * 100)) + '</b><small>' + esc(tx('per.h')) + '</small></span>' +
            '<span>' + icon('pin') + esc(placeTxt(p)) + '</span>' +
            '<span>' + icon('globe') + esc(p.languages.map(lngLabel).join(', ')) + '</span></div></div>' +
        '<div class="pf-act"><button class="btn" type="button" data-choose>' + esc(tx('pf.choose')) + icon('arrow') + '</button>' +
          inHTML(p, 'btn btn-ghost btn-in', true) +
          '<button class="btn btn-ghost" type="button" data-copy>' + icon('link') + '<span>' + esc(tx('pf.copy')) + '</span></button></div>' +
      '</div>' +
      '<div class="pf-cols"><div class="pf-main">' +
        sec('pf.about', '<p class="pf-about">' + nb(L(p.about)) + '</p>') +
        sec('pf.services', servicesHTML(p)) +
        sec('pf.reviews', reviewsHTML(p)) +
      '</div><aside class="pf-side">' +
        sec('pf.skills', tagsHTML(L(p.skills))) +
        sec('pf.ind', tagsHTML(p.industries.map(indLabel))) +
        sec('pf.lng', tagsHTML(p.languages.map(lngLabel))) +
        sec('pf.certs', certs) +
        '<p class="pf-since">' + esc(fmt(tx('pf.since'), { s: dateTxt(p.joined, 'since') })) + '</p>' +
      '</aside></div>';
  }
  function renderProfile(p) { pfBody.innerHTML = profileHTML(p); D.title = fmt(tx('title.p'), { s: L(p.name) }); }
  function openProfile(slug, opener) {
    var p = bySlug(slug); if (!p) return false;
    state.open = slug; renderProfile(p);
    if (pfOv.hidden) { openDlg(pfOv, opener, pfOv.firstElementChild); pfOv.scrollTop = 0; }
    return true;
  }
  function closeProfile() {
    if (pfOv.hidden) return;
    if (!reqOv.hidden) closeDlg(reqOv);                       // «Назад» при открытой заявке закрывает и её
    var slug = state.open; state.open = null; D.title = tx('title');
    var a = slug ? $('a.pc-link[data-open="' + slug + '"]', grid) : null;
    closeDlg(pfOv, a || $('#cat-h'));
  }
  /* «Назад» закрывает карточку: открытие кладёт адрес ?p=… в историю, закрытие крестиком или Esc — шаг назад по ней */
  function requestCloseProfile() {
    if (state.pushed && history.state && history.state.pf) { history.back(); return; }
    try { history.replaceState(null, '', urlWith({ p: null })); } catch (e) {}
    closeProfile();
  }
  window.addEventListener('popstate', function () {
    var slug = parseQS(location.search).p;
    state.pushed = !!(history.state && history.state.pf);
    if (slug && bySlug(slug)) { if (state.open !== slug) openProfile(slug, null); }
    else closeProfile();
  });
  grid.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a[data-open]') : null;
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;   // новая вкладка — как обычная ссылка
    e.preventDefault();
    var slug = a.getAttribute('data-open');
    if (openProfile(slug, a)) { try { history.pushState({ pf: slug }, '', urlWith({ p: slug })); state.pushed = true; } catch (er) {} }
  });
  pfBody.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target.closest('[data-choose], [data-copy]') : null; if (!t) return;
    var p = bySlug(state.open); if (!p) return;
    if (t.hasAttribute('data-choose')) openReq(p, t); else copyLink(p, t);
  });
  function copyLink(p, btn) {
    var url = location.href.split('#')[0].split('?')[0] + '?p=' + encodeURIComponent(p.slug), span = $('span', btn);
    function ok() { span.textContent = tx('pf.copied'); setTimeout(function () { if (D.contains(span)) span.textContent = tx('pf.copy'); }, 2000); }
    function legacy() { var t = D.createElement('textarea'); t.value = url; t.setAttribute('readonly', ''); t.style.position = 'fixed'; t.style.opacity = '0'; btn.parentNode.appendChild(t); t.select();
      try { D.execCommand('copy'); ok(); } catch (e) {} t.parentNode.removeChild(t); btn.focus(); }
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(url).then(ok, legacy); else legacy();
  }

  /* ---------- заявки через FormSubmit — как заявки главной (FR-SITE133, FR-SITE136) ---------- */
  function send(payload) {
    if (!window.fetch) return Promise.reject(new Error('no fetch'));
    return fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(payload) })
      .then(function (r) { if (!r.ok) throw new Error('send ' + r.status); return r; });
  }
  /* не ушло (нет сети) — в очередь под тем же ключом, что у главной; отправится при следующем заходе */
  function queue(payload) { try { var q = JSON.parse(sget('ait_lead_queue') || '[]'); q.push(payload); sset('ait_lead_queue', JSON.stringify(q)); } catch (e) {} }
  function flushQueue() {
    try {
      var q = JSON.parse(sget('ait_lead_queue') || '[]'); if (!q.length) return; var h = q[0];
      send(h).then(function () { var f = JSON.parse(sget('ait_lead_queue') || '[]').filter(function (l) { return l.submitted_at !== h.submitted_at; }); sset('ait_lead_queue', JSON.stringify(f)); flushQueue(); }).catch(function () {});
    } catch (e) {}
  }
  function validEmail(v) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v); }
  function normIn(v) { v = String(v || '').trim(); if (v && !/^https?:\/\//i.test(v)) v = 'https://' + v.replace(/^\/+/, ''); return v; }
  function validIn(v) { return /^https?:\/\/([a-z]{2,3}\.)?linkedin\.com\/in\/[^\/?#\s]+\/?([?#]\S*)?$/i.test(v); }
  function mark(input, ok) {
    input.setAttribute('aria-invalid', ok ? 'false' : 'true');
    var err = D.getElementById(input.id + '-err'); if (err) err.hidden = ok;
    return ok;
  }
  function clearForm(form) { form.reset(); $$('[aria-invalid]', form).forEach(function (x) { x.removeAttribute('aria-invalid'); }); $$('.err', form).forEach(function (x) { x.hidden = true; }); }
  function submitFlow(form, btn, gen, getGen, payload, step, doneEl, ov) {
    var keep = btn.innerHTML; btn.disabled = true; btn.textContent = tx('sending');
    send(payload).catch(function () { queue(payload); }).then(function () {
      btn.disabled = false; btn.innerHTML = keep;
      if (gen !== getGen() || ov.hidden) return;
      step.hidden = true; doneEl.hidden = false;
      var b = $('[data-close]', doneEl); if (b) b.focus();
    });
  }
  function stamp(extra) {
    var o = { _template: 'table', _captcha: 'false', lang: state.lang, page: location.href, submitted_at: new Date().toISOString() };
    for (var k in extra) if (own(extra, k)) o[k] = extra[k];
    return o;
  }

  var reqOv = $('#req'), reqForm = $('#req-form'), reqFor = null, reqGen = 0;
  function openReq(p, opener) {
    reqFor = p; reqGen++; clearForm(reqForm);
    $('#req-sub').textContent = fmt(tx('req.sub'), { name: L(p.name), rate: money(Math.round(p.rate_usd * 100)) + tx('per.h') });
    $('#req-ex').hidden = !p.example;
    $('#req-step').hidden = false; $('#req-done').hidden = true;
    openDlg(reqOv, opener, $('#req-name'));
  }
  reqForm.addEventListener('submit', function (e) {
    e.preventDefault();
    var gen = reqGen;
    if (reqForm.elements._honey.value) { $('#req-step').hidden = true; $('#req-done').hidden = false; return; }
    var n = $('#req-name'), em = $('#req-email');
    var okN = mark(n, n.value.trim().length >= 2), okE = mark(em, validEmail(em.value.trim()));
    if (!okN || !okE) { (okN ? em : n).focus(); return; }
    var p = reqFor;
    var payload = stamp({ _subject: 'Consultant request — partners.andre.technology', type: 'consultant_request',
      partner: p.slug, partner_name: p.name.en + ' / ' + p.name.ru, partner_rate_usd: p.rate_usd, partner_example: !!p.example,
      name: n.value.trim(), email: em.value.trim(), company: $('#req-company').value.trim() || '—', message: $('#req-msg').value.trim() || '—' });
    submitFlow(reqForm, $('#req-btn'), gen, function () { return reqGen; }, payload, $('#req-step'), $('#req-done'), reqOv);
  });

  var appOv = $('#app'), appForm = $('#app-form'), appGen = 0;
  function openApp(opener) {
    appGen++; clearForm(appForm);
    $('#app-step').hidden = false; $('#app-done').hidden = true;
    openDlg(appOv, opener, $('#app-name'));
  }
  $('#apply').addEventListener('click', function () { openApp(this); });
  appForm.addEventListener('submit', function (e) {
    e.preventDefault();
    var gen = appGen;
    if (appForm.elements._honey.value) { $('#app-step').hidden = true; $('#app-done').hidden = false; return; }
    var n = $('#app-name'), em = $('#app-email'), li = $('#app-in'), ex = $('#app-exp'), rt = $('#app-rate');
    var inUrl = normIn(li.value), rate = Number(rt.value);
    var checks = [
      [n, n.value.trim().length >= 2],
      [em, validEmail(em.value.trim())],
      [li, validIn(inUrl)],
      [ex, ex.value.trim().length >= 20],
      [rt, rt.value !== '' && isFinite(rate) && Math.floor(rate) === rate && rate >= RATE_MIN && rate <= RATE_MAX]
    ];
    var bad = null;
    checks.forEach(function (c) { if (!mark(c[0], c[1]) && !bad) bad = c[0]; });
    if (bad) { bad.focus(); return; }
    li.value = inUrl;
    var payload = stamp({ _subject: 'Partner application — partners.andre.technology', type: 'partner_application',
      name: n.value.trim(), email: em.value.trim(), linkedin: inUrl, experience: ex.value.trim(), rate_usd: rate });
    submitFlow(appForm, $('#app-btn'), gen, function () { return appGen; }, payload, $('#app-step'), $('#app-done'), appOv);
  });

  /* ---------- калькулятор заработка (FR-SITE135) ---------- */
  var calcIn = $('#calc-rate');
  function renderCalc() {
    var r = +calcIn.value, rv = PRICING.review(r, 10), bc = PRICING.bootcamp(r), pr = PRICING.promo(50000);
    $('#calc-v').innerHTML = money(r * 100) + '<small>' + esc(tx('per.h')) + '</small>';
    calcIn.setAttribute('aria-valuetext', money(r * 100) + ' ' + tx('per.h'));
    calcIn.style.setProperty('--fill', ((r - RATE_MIN) / (RATE_MAX - RATE_MIN) * 100).toFixed(2) + '%');
    $('#c-r-client').textContent = money(rv.client); $('#c-r-you').textContent = money(rv.consultant);
    $('#c-b-client').textContent = money(bc.client); $('#c-b-you').textContent = money(bc.consultant);
    $('#c-p-client').textContent = money(pr.client); $('#c-p-you').textContent = money(pr.commission);
    $$('.calc-row dd span').forEach(function (x) { x.setAttribute('data-l', tx('calc.l.client')); });
    $$('.calc-row dd b').forEach(function (x) { x.setAttribute('data-l', tx('calc.l.you')); });
  }
  calcIn.addEventListener('input', renderCalc);

  /* ---------- язык (FR-SITE139): тот же ключ ait_lang и тот же ?lang=, что у главной ---------- */
  function setLang(lang, init) {
    if (lang !== 'en' && lang !== 'ru') return;
    if (!RU) {
      RU = {}; RU_PH = {}; RU_ARIA = {};
      $$('[data-i18n]').forEach(function (el) { var k = el.getAttribute('data-i18n'); if (!own(RU, k)) RU[k] = el.innerHTML; });
      $$('[data-i18n-ph]').forEach(function (el) { RU_PH[el.getAttribute('data-i18n-ph')] = el.getAttribute('placeholder'); });
      $$('[data-i18n-aria]').forEach(function (el) { RU_ARIA[el.getAttribute('data-i18n-aria')] = el.getAttribute('aria-label'); });
    }
    state.lang = lang; root.lang = lang;
    $$('[data-i18n]').forEach(function (el) { var k = el.getAttribute('data-i18n'), v = lang === 'en' ? I18N.en[k] : RU[k]; if (v != null && el.innerHTML !== v) el.innerHTML = v; });
    $$('[data-i18n-ph]').forEach(function (el) { var k = el.getAttribute('data-i18n-ph'); el.setAttribute('placeholder', lang === 'en' ? (I18N.en[k] || RU_PH[k]) : RU_PH[k]); });
    $$('[data-i18n-aria]').forEach(function (el) { var k = el.getAttribute('data-i18n-aria'); el.setAttribute('aria-label', lang === 'en' ? (I18N.en[k] || RU_ARIA[k]) : RU_ARIA[k]); });
    $$('[data-href-ru]').forEach(function (el) { el.setAttribute('href', el.getAttribute(lang === 'en' ? 'data-href-en' : 'data-href-ru')); });
    $$('.lang button').forEach(function (b) { var on = b.getAttribute('data-lang') === lang; b.classList.toggle('on', on); b.setAttribute('aria-pressed', on ? 'true' : 'false'); });
    sset('ait_lang', lang);
    if (!init) { state.langInUrl = true; syncUrl(true); }
    var p = state.open ? bySlug(state.open) : null;
    D.title = p ? fmt(tx('title.p'), { s: L(p.name) }) : tx('title');
    renderCalc(); rateUI();
    if (ready) {
      var shown = state.shown;
      buildOptions(); apply('none');
      if (shown > state.shown) renderMore(false, shown - state.shown, 'none');
      if (p) renderProfile(p);
      if (reqFor && !reqOv.hidden) $('#req-sub').textContent = fmt(tx('req.sub'), { name: L(reqFor.name), rate: money(Math.round(reqFor.rate_usd * 100)) + tx('per.h') });
    }
    root.className = root.className.replace(/\s*i18n-wait\b/g, '');
  }
  $$('.lang button').forEach(function (b) { b.addEventListener('click', function () { setLang(b.getAttribute('data-lang')); }); });

  /* ---------- движение: шапка, появление блоков (NFR-SITE108) ---------- */
  var hdr = $('#hdr');
  function onScroll() { hdr.classList.toggle('solid', (window.pageYOffset || root.scrollTop) > 8); }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  (function () {
    var els = $$('.rv');
    if (REDUCED || !('IntersectionObserver' in window)) { els.forEach(function (el) { el.classList.add('in'); }); return; }
    var ob = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); ob.unobserve(en.target); } }); }, { rootMargin: '0px 0px -6% 0px', threshold: 0.08 });
    els.forEach(function (el) { ob.observe(el); });
  })();

  /* ---------- старт ---------- */
  var API = window.AndrePartners = {
    source: null, pricing: PRICING, money: function (c) { return money(c); },
    view: function () { return VIEW.map(function (p) { return p.slug; }); },
    shown: function () { return state.shown; },
    state: function () { return JSON.parse(JSON.stringify(state)); }
  };
  var startP = readUrl();
  controlsUI();
  setLang(state.lang, true);
  var skT = setTimeout(function () { if (!ready) grid.innerHTML = '<li aria-hidden="true"><div class="sk"></div></li><li aria-hidden="true"><div class="sk"></div></li><li aria-hidden="true"><div class="sk"></div></li>'; }, 160);
  load(function (list) {
    clearTimeout(skT);
    DATA = prepare(list); ready = true;
    buildOptions(); controlsUI(); apply('enter');
    if (startP) {
      if (bySlug(startP)) {
        /* прямой заход по ?p=: под карточкой — каталог, «Назад» закрывает карточку, а не уводит со страницы */
        try { history.replaceState(null, '', urlWith({ p: null })); history.pushState({ pf: startP }, '', urlWith({ p: startP })); state.pushed = true; } catch (e) {}
        openProfile(startP, null);
      } else { try { history.replaceState(null, '', urlWith({ p: null })); } catch (e) {} }
    }
    API.ready = true;
    flushQueue();
  });
})();
