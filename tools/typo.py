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


def bind_copy(obj, lang, key=""):
    """Тот же проход по всему словарю текстов. Метаданные и ссылки пропускаем:
    неразрывные пробелы там не нужны."""
    # метаданные пропускаем целиком: неразрывные пробелы не нужны ни в
    # заголовке вкладки, ни в описании для поисковика и соцсетей
    if key in ("title", "og_title", "desc", "og_desc", "meta_desc",
               "cta_href", "video_aria"):
        return obj
    if isinstance(obj, str):
        return bind_short_words(obj, lang) if " " in obj and "://" not in obj else obj
    if isinstance(obj, list):
        return [bind_copy(x, lang, key) for x in obj]
    if isinstance(obj, tuple):
        return tuple(bind_copy(x, lang, key) for x in obj)
    if isinstance(obj, dict):
        return dict((k, bind_copy(v, lang, k)) for k, v in obj.items())
    return obj
