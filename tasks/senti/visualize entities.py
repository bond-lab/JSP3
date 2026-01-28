import json
import matplotlib.pyplot as plt

data_path = "entities locations.json"

def read_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def plot_entities_positions_from_json(file_path, categories=None, exclude=None):

    exclude = exclude or []

    # názvy klíčů JSON
    text_length_key = "text length"
    entities_key = "entities locations"

    # načtení JSON
    data = read_json(file_path)

    entities = data.get(entities_key, {})
    text_length = data.get("word_count") or data.get(text_length_key)

    # filtr kategorií
    if categories is not None:
        entities = {cat: entities.get(cat, {}) for cat in categories if cat in entities}

    # sběr všech entit, odstranění duplicit
    all_entities = {}
    for cat, items in entities.items():
        for entity_name, positions in items.items():
            if entity_name in exclude:
                continue
            if entity_name not in all_entities:
                all_entities[entity_name] = positions
            else:
                all_entities[entity_name] = sorted(set(all_entities[entity_name] + positions))

    # příprava grafu
    total_rows = len(all_entities)
    plt.figure(figsize=(12, max(3, total_rows * 0.5)))

    y_labels = []
    y_positions = []
    y_index = 0

    for entity_name, positions in all_entities.items():
        plt.scatter(positions, [y_index] * len(positions), s=40, alpha=0.5)
        y_labels.append(entity_name)
        y_positions.append(y_index)
        y_index += 1

    plt.yticks(y_positions, y_labels)
    plt.ylim(-0.5, total_rows - 0.5)  # odskok nahoře a dole
    plt.xlabel("Pozice ve slovech")
    plt.xlim(0, text_length)
    plt.title("Rozložení entit v textu")
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()


def main():
    categories = ["PERSON", "ORG", "manually found"]
    exclude = ["Gregor Samsa", "Gregor awoke", "Unnecessary", "Gregor tried", "Samsa"]
    plot_entities_positions_from_json(data_path, categories, exclude)

if __name__ == "__main__":
    main()
