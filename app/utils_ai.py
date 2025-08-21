import re

def simple_flashcards_from_text(text, max_cards=10):
    """
    Heuristic generator:
    - Split into sentences
    - Turn definition-like sentences into Q/A
    - Fallback cloze deletions
    """
    # normalize spaces
    text = re.sub(r'\s+', ' ', text).strip()

    # naive sentence split
    sentences = re.split(r'(?<=[.!?])\s+', text)
    cards = []

    for s in sentences:
        s = s.strip()
        if len(s.split()) < 6:
            continue

        # Pattern: "<Term> is/are/means/was ..."
        m = re.match(r'^([\w\s\-()]+?)\s+(is|are|means|was|refers to|can be defined as)\s+(.*)$', s, flags=re.I)
        if m:
            term = m.group(1).strip().rstrip(':').strip()
            definition = m.group(3).strip().rstrip('.')
            if 3 <= len(term.split()) <= 8 and len(definition.split()) >= 3:
                q = f"What is {term}?"
                a = definition
                cards.append((q, a))
                if len(cards) >= max_cards:
                    break
                continue

        # Fallback cloze: blank the last noun-ish word (very naive)
        words = s.split()
        target = None
        for w in reversed(words):
            if re.search(r'[A-Za-z]', w) and len(w) > 4:
                target = w.strip('.,:;!?()[]{}"\'')
                break
        if target:
            q = s.replace(target, "_____")
            a = target
            cards.append((q, a))
            if len(cards) >= max_cards:
                break

    return [{"question": q, "answer": a} for q, a in cards]



