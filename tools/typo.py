# -*- coding: utf-8 -*-
"""Типографика переносов: служебное слово не остаётся в конце строки.

Общий модуль для генераторов биографии и лендинга — правило владельца одно
на весь сайт («ты видишь, по какому принципу я переношу предлоги, чтобы
красиво выглядело?»), поэтому и код один.
"""
import re

# ── переносы: служебное слово не остаётся в конце строки ─────────────────────
# Правило владельца («ты видишь, по какому принципу я переношу предлоги, чтобы
# красиво выглядело?»): предлог, союз, частица и короткое местоимение уезжают
# на следующую строку ВМЕСТЕ со своим словом. Технически — неразрывный пробел
# после такого слова. Ставится автоматически на все тексты биографии и
# лендинга, чтобы правило держалось и в новых главах, а не чинилось поштучно.
_BIND_RU = ("в во и к ко с со у о об на за по из от до не но а я мы то же вы их им "
            "для при под над без что как это или так уже про чем где да ни ли бы "
            # притяжательные — из той же серии: «изменило моё / представление»
            # владельцу режет глаз так же, как повисший предлог
            "мой моя моё мои свой своя своё свои её").split()
# «am» здесь по той же причине, что и «is»: владелец отдельно просил
# «I am building» одной строкой
_BIND_EN = ("a an the to of in on at for and but or nor so as by is am it i my we do no not "
            "that this with from into than then if up we're i'm").split()
_NB = u"\u00a0"


def bind_short_words(text, lang):
    """Склеивает служебное слово со следующим неразрывным пробелом.

    Работает только по тексту: куски между `<` и `>` (теги, атрибуты, классы
    иконок) не трогаются вообще."""
    words = _BIND_RU if lang == "ru" else _BIND_EN
    alt = "|".join(sorted((re.escape(w) for w in words), key=len, reverse=True))
    # после пробела может стоять и открывающий тег («an <span>AI-native…»):
    # именно так рвались «an / AI-native ecosystem» и «to / Chief Data Officer»
    rx = re.compile(r"(?<![\w\u0400-\u04ff-])(%s)([ ]+)(?=[^\s])" % alt, re.I | re.U)
    # хвост куска: «I build an » перед <span> — служебное слово стоит на стыке
    # с тегом, и обычный просмотр вперёд его не видит
    rx_tail = re.compile(r"(?<![\w\u0400-\u04ff-])(%s)([ ]+)$" % alt, re.I | re.U)
    parts = re.split(r"(<[^>]+>)", text)
    for i, part in enumerate(parts):
        if part.startswith("<"):
            continue
        part = rx.sub(lambda m: m.group(1) + _NB, part)
        if i + 1 < len(parts):
            part = rx_tail.sub(lambda m: m.group(1) + _NB, part)
        parts[i] = part
    return "".join(parts)


_NB_HYPHEN = u"\u2011"
# Дефис ВНУТРИ слова делаем неразрывным: «топ-менеджменту», «ИИ-зрелость»,
# «бизнес-анализа» рвались по дефису и выглядели как две половинки (правка
# владельца). В JetBrains Mono U+2011 той же ширины, что обычный дефис, —
# замер показал 105.97px против 105.97px, так что строки не сдвигаются.
_RX_HYPHEN = re.compile(u"(?<=[0-9A-Za-z\u0400-\u04ff])-(?=[0-9A-Za-z\u0400-\u04ff])")


# Строка из одних строчных латинских букв, цифр, пробелов, дефисов и
# подчёркиваний — это НЕ текст, а идентификатор: имя класса иконки
# («fa-solid fa-pen-nib»), ключ, техническое значение. Неразрывный дефис там
# ломает всё: Font Awesome перестаёт находить класс и значки исчезают.
_RX_TECH = re.compile(r"^[a-z0-9 _-]+$")


def keep_hyphen(text):
    """Неразрывный дефис в составных словах. Не трогаем ни куски между < и >,
    ни строки-идентификаторы целиком (классы иконок приходят отдельными
    значениями словаря, а не внутри тега)."""
    if _RX_TECH.match(text):
        return text
    parts = re.split(r"(<[^>]+>)", text)
    for i, part in enumerate(parts):
        if part.startswith("<"):
            continue
        parts[i] = _RX_HYPHEN.sub(_NB_HYPHEN, part)
    return "".join(parts)


def bind_copy(obj, lang, key=""):
    """Тот же проход по всему словарю текстов. Метаданные и ссылки пропускаем:
    неразрывные пробелы там не нужны."""
    # метаданные пропускаем целиком: неразрывные пробелы не нужны ни в
    # заголовке вкладки, ни в описании для поисковика и соцсетей
    if key in ("title", "og_title", "desc", "og_desc", "meta_desc",
               "cta_href", "video_aria"):
        return obj
    if isinstance(obj, str):
        if "://" in obj:
            return obj
        out = bind_short_words(obj, lang) if " " in obj else obj
        return keep_hyphen(out)
    if isinstance(obj, list):
        return [bind_copy(x, lang, key) for x in obj]
    if isinstance(obj, tuple):
        return tuple(bind_copy(x, lang, key) for x in obj)
    if isinstance(obj, dict):
        return dict((k, bind_copy(v, lang, k)) for k, v in obj.items())
    return obj
