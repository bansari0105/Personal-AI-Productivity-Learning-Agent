try:
    import spacy
    _nlp = spacy.load("en_core_web_sm")
except Exception:
    _nlp = None


def _split_sentences_fallback(text: str):
    # very small fallback: split on common separators
    import re

    parts = re.split(r"[\n\.;!?]+", text)
    return [p.strip() for p in parts if p.strip()]


def extract_tasks(text: str):
    tasks = []
    if _nlp is not None:
        doc = _nlp(text)
        for sent in doc.sents:
            tasks.append({"task": sent.text.strip(), "length": len(sent.text.strip()), "priority": 1})
    else:
        for s in _split_sentences_fallback(text):
            tasks.append({"task": s, "length": len(s), "priority": 1})

    return tasks
