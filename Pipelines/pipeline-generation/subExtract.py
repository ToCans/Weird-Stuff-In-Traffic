import spacy
from word2number import w2n

nlp = spacy.load("en_core_web_sm")

'''
def extract_nouns(prompt):
    doc = nlp(prompt)
    nouns = []
    for chunk in doc.noun_chunks:
        # Only keep actual noun phrases, skip pronouns/determiners
        if any(token.pos_ in ["NOUN", "PROPN"] for token in chunk):
            nouns.append(chunk.root.lemma_)
    return nouns
'''
def extract_nouns_with_counts(prompt):
    doc = nlp(prompt)
    results = []
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"]:
            count = 1
            for child in token.children:
                if child.pos_ == "NUM":
                    try:
                        # Try to parse as number (e.g., '2')
                        count = int(child.text)
                    except ValueError:
                        try:
                            # Try to parse as word-number (e.g., 'Two')
                            count = w2n.word_to_num(child.text.lower())
                        except:
                            count = 1  # fallback if it's not a valid number
            results.extend([token.lemma_] * count)
    return results

prompt = "Generate two apes and a tiger playing catch"
print(extract_nouns_with_counts(prompt))