import spacy
import pprint
import json

nlp = spacy.load("en_core_web_sm")

text_path = "Metamorphosis.txt"
results_path = "entities locations.json"

def read_document(file_path):
    """Reads the content of a text file (.txt) and returns it as a string."""
    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return f"File '{file_path}' not found."
    except Exception as e:
        return f"An error occurred while reading the file: {e}"
    

def trim_text_edges(text, head, tail):
    """Removes a given number of lines from the start (head) and end (tail) of the text."""
    rows = text.splitlines()
    remaining = rows[head:len(rows) - tail] # [start:end] it gives smaller required list
    return "\n".join(remaining)


def find_entities(text):
    """
    Finds entities in the text and returns them in the format:
    {category: [entity1, entity2, ...]}
    """
    doc = nlp(text)
    entities = {}
    for ent in doc.ents:
        entities.setdefault(ent.label_, []).append(ent.text)
    return entities


def find_words(text, word_list):
    """
    Finds all occurrences of words from word_list in the text and returns their positions.

    Example:
    word_list = ["Jake", "him"] 
    result = {"Jake": [4, 27], "him": [9, 32]}
    """
    tokens = text.split()
    result = {}

    for word in word_list:
        word_tokens = word.split()
        positions = []

        for i in range(len(tokens) - len(word_tokens) + 1):
            if tokens[i:i+len(word_tokens)] == word_tokens:
                positions.append(i + 1)

        if positions:
            result[word] = positions

    return result


def entities_locations(text):
    """
    Returns:
    1) word count
    2) entity positions (dictionary): category → entity → word indices
    """
    entities = find_entities(text)
    entities_locs = {}

    words = text.split()
    text_length = len(words)

    for category, entity_list in entities.items():
        locs = find_words(text, entity_list)
        if locs:
            entities_locs[category] = locs

    return text_length, entities_locs


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)  # ensure_ascii=False zachová české znaky, indent=4 je hezké odsazení


def main():
    text = read_document(text_path)
    text = trim_text_edges(text, 5, 0)

    text_length, entities_locs = entities_locations(text)

    manualy_found_entities = {"manually found": find_words(text, ["mother", "father", "sister", "Mr. Samsa", "Mrs. Samsa"])}

    entities_locs = entities_locs | manualy_found_entities

    results = {
        "text length": text_length,
        "entities locations": entities_locs
    }

    pprint.pprint(results)

    #save_json(results, results_path)

if __name__ == "__main__":
    main()
