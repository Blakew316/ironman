"""Translate text between languages using googletrans.

``googletrans`` is imported lazily. Language codes are listed at the bottom of
this file for reference.
"""

_translator = None


def _get_translator():
    global _translator
    if _translator is None:
        try:
            from googletrans import Translator
            _translator = Translator()
        except ImportError:
            print("[translate] googletrans not installed")
            return None
    return _translator


def startTranslate(text, src, dest):
    """Translate ``text`` from ``src`` to ``dest``."""
    translator = _get_translator()
    if translator is None:
        return None
    trans = translator.translate(text, src=src, dest=dest)
    print(trans)
    return trans


def autoTranslateEn(text):
    """Auto-detect the source language and translate to English."""
    translator = _get_translator()
    if translator is None:
        return None
    trans = translator.translate(text)
    print(trans)
    return trans


def autoTranslate(text, dest):
    """Auto-detect the source language and translate to ``dest``."""
    translator = _get_translator()
    if translator is None:
        return None
    trans = translator.translate(text, dest=dest)
    print(trans)
    return trans


if __name__ == "__main__":
    autoTranslate("This is a demo of translate", dest="es")

# Language codes reference (ISO 639-1 / 639-2):
# af=Afrikaans  ar=Arabic  bn=Bengali  zh-cn=Chinese  cs=Czech  da=Danish
# nl=Dutch  en=English  fr=French  de=German  el=Greek  gu=Gujarati  hi=Hindi
# it=Italian  ja=Japanese  kn=Kannada  ko=Korean  la=Latin  ml=Malayalam
# mr=Marathi  ne=Nepali  pl=Polish  pt=Portuguese  pa=Panjabi  ru=Russian
# es=Spanish  sv=Swedish  ta=Tamil  te=Telugu  th=Thai  tr=Turkish
# uk=Ukrainian  ur=Urdu  vi=Vietnamese
