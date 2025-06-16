import spacy
from word2number import w2n

nlp = spacy.load("en_core_web_sm")

def extract_prompt_info_structured(prompt):
    doc = nlp(prompt)
    
    extracted_items = []
    temp_nouns_by_index = {} 
    
    temp_verbs_by_lemma = {}

    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"]:
            if token.i not in temp_nouns_by_index:
                temp_nouns_by_index[token.i] = {
                    "raw_text": token.text,
                    "lemma": token.lemma_,
                    "adjectives": [],
                    "count": 1
                }
            
            for child in token.children:
                if child.dep_ == "amod" and child.pos_ == "ADJ":
                    temp_nouns_by_index[token.i]["adjectives"].append(child.text)
            

            for child in token.children:
                if child.dep_ == "nummod" and child.pos_ == "NUM": # Explicitly nummod dependency
                    try:
                        temp_nouns_by_index[token.i]["count"] = int(child.text)
                    except ValueError:
                        try:
                            temp_nouns_by_index[token.i]["count"] = w2n.word_to_num(child.text.lower())
                        except:
                            pass
            
            if token.i > 0 and doc[token.i - 1].pos_ == "NUM":
                try:
                    if temp_nouns_by_index[token.i]["count"] == 1: # Default value
                        temp_nouns_by_index[token.i]["count"] = int(doc[token.i - 1].text)
                except ValueError:
                    try:
                        if temp_nouns_by_index[token.i]["count"] == 1:
                            temp_nouns_by_index[token.i]["count"] = w2n.word_to_num(doc[token.i - 1].text.lower())
                    except:
                        pass
                        
    for token in doc:
        if token.pos_ == "VERB":
            verb_lemma = token.lemma_
            
            if verb_lemma not in temp_verbs_by_lemma:
                temp_verbs_by_lemma[verb_lemma] = {
                    "type": "verb",
                    "lemma": verb_lemma,
                    "adverbs": []
                }
            
            for child in token.children:
                if child.dep_ == "advmod" and child.pos_ == "ADV":
                    temp_verbs_by_lemma[verb_lemma]["adverbs"].append(child.text)

    for token_index, noun_data in temp_nouns_by_index.items():
        noun_data["adjectives"] = list(set(noun_data["adjectives"])) 
        
        for _ in range(noun_data["count"]):
            output_noun = {
                "type": "noun",
                "lemma": noun_data["lemma"],
                "adjectives": noun_data["adjectives"]
            }
            extracted_items.append(output_noun)
            
    for verb_lemma, verb_data in temp_verbs_by_lemma.items():
        verb_data["adverbs"] = list(set(verb_data["adverbs"]))
        extracted_items.append(verb_data)

    return extracted_items


print("Testfall 1: 'A tall fat elefent steps on a small mouse on the street'")
print(extract_prompt_info_structured("A tall fat elefent steps on a small mouse on the street"))

print("\nTestfall 2: 'Two big scary tigers and a cute little bunny which play chess together'")
print(extract_prompt_info_structured("Two big scary tigers and a cute little bunny which play chess together"))

print("\nTestfall 3: 'Three red apples and a green pear'")
print(extract_prompt_info_structured("Three red apples and a green pear"))