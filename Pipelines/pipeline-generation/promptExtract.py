import spacy 
from word2number import w2n

nlp = spacy.load("en_core_web_sm")

def extract_prompt_info(prompt):
    doc = nlp(prompt)
    results = []

    for token in doc:
        # Noun and 
        if token.pos_ in ["NOUN", "PROPN"]:
            count = 1
            adjectives = [child.text for child in token.children if child.dep_ == "amod"]

            # Nach Zahl (numerisch oder ausgeschrieben) suchen
            for child in token.children:
                if child.pos_ == "NUM":
                    try:
                        count = int(child.text)
                    except ValueError:
                        try:
                            count = w2n.word_to_num(child.text.lower())
                        except:
                            count = 1  # Fallback bei nicht erkennbarer Zahl

            # Nomen mehrfach entsprechend der Anzahl einfügen
            for _ in range(count):
                results.append(("noun", token.lemma_, adjectives))

        # Verben
        elif token.pos_ == "VERB":
            adverbs = [child.text for child in token.children if child.dep_ == "advmod"]
            results.append(("verb", token.lemma_, adverbs))

    return results

print(extract_prompt_info("Two big scary tigers and one cute little bunny playing chess"))