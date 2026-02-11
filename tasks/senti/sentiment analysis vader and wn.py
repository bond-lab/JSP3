from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize, sent_tokenize
import yaml
import statistics
import re
import json
import pprint

text_path = "Metamorphosis.txt"
wordnet_path = "sentiment_wordnet.yml"
data_path = "sentiment data.json"


def read_document(file_path):
    """
    Reads the content of a text file (.txt) and returns it as a string.
    """
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


def vader_senti_sentences(text):
    """Splits text into sentences and returns VADER compound sentiment value for each sentence."""
    analyzer = SentimentIntensityAnalyzer() # analyzátor sentimentu
    sentences = sent_tokenize(text) 
    compound_values = [analyzer.polarity_scores(sentence)['compound'] 
                       for sentence in sentences]
    return compound_values


def load_yaml_file(yaml_path):
    """Loads a YAML file and returns a dictionary."""
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


def new_wn_senti_sentences(text, wordnet_file):
    """
    Tokenizes the text into sentences and words, finds all synsets of each word in a WordNet, and retrieves
    their sentiment values from a sentiment WordNet. This determines the overall sentiment of a word in isolation.
    It then averages the sentiment values for each word and calculates the average sentiment per sentence.
    Returns a list of average sentiment values per sentence.
    """

    senti_wordnet_dict = load_yaml_file(wordnet_file)

    sentences = sent_tokenize(text)
    compound_values = []

    for sentence in sentences:
        words = word_tokenize(sentence)
        word_values = []

        for word in words:
            if not word.isalpha():
                continue
            synsets = wn.synsets(word.lower())
            if not synsets:
                continue

            # Average sentiment of all synsets for this word
            synset_values = []
            for synset in synsets:
                synset_id = f"{synset.offset():08d}-{synset.pos()}"

                for dict_synset in senti_wordnet_dict:
                    if dict_synset.endswith(synset_id):  # only add synsets that exist in the new wordnet
                        synset_values.append(senti_wordnet_dict[dict_synset])
                        break  # stop searching after the first match

            if synset_values:
                word_values.append(statistics.mean(synset_values))

        if word_values:
            compound_values.append(statistics.mean(word_values))

    return compound_values


def safe_block_split(text, max_block_size):
    """
    Splits the text into blocks of up to max_block_size characters. 
    If a block ends with an incomplete sentence, that sentence is moved to the following block. 
    The resulting blocks are typically slightly shorter than max_block_size, but no sentence
    is ever cut in half.
    """
    all_sentences = sent_tokenize(text)
    longest_sentence = max(all_sentences, key=len)

    if len(longest_sentence) > max_block_size:
        raise ValueError(
        f"Cannot satisfy the condition: the longest sentence has {len(longest_sentence)} characters, "
        f"which is more than max_block_size: {max_block_size}"
        )

    blocks = []
    remaining_text = text

    while remaining_text:

        # If the remaining portion of the text is shorter than the maximum allowed block size, simply add it as the final segment and finish the process.
        if len(remaining_text) <= max_block_size:
            blocks.append(remaining_text)
            break

        current_block = remaining_text[:max_block_size]
        sentences_in_block = sent_tokenize(current_block)
        last_sentence = sentences_in_block[-1]

        if last_sentence[-1] not in ".!?":  
            # the last sentence is incomplete
            block_text = ' '.join(sentences_in_block[:-1])  
            blocks.append(block_text)
            remaining_text = remaining_text[len(block_text):].lstrip() # returns tail to remaining_text
        else:
            # the last sentence is complete
            block_text = ' '.join(sentences_in_block)
            blocks.append(block_text)
            remaining_text = remaining_text[len(block_text):].lstrip()

    return blocks


def cumulative_text_lengths(blocks):
    """
    Returns cumulative block lengths in words.
    """
    locations = []
    total = 0
    for block in blocks:
        total += len(block.split())
        locations.append(total)
        
    return locations


def split_and_locate_chapters(text, pattern):
    """
    Splits the text into blocks using the given regular expression pattern, then applies find_block_locations
    to the resulting parts. 
    Returns the chapter segments and their locations.
    """
    matches = list(re.finditer(pattern, text))

    if not matches:
        blocks = [text]
        return blocks, cumulative_text_lengths(blocks)

    blocks = []
    start = 0

    for match in matches:
        idx = match.start()
        if idx > start:
            blocks.append(text[start:idx])
        start = idx

    blocks.append(text[start:])

    locations = cumulative_text_lengths(blocks)

    return blocks, locations


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)  # ensure_ascii=False zachová české znaky, indent=4 je hezké odsazení


def main():
    max_block_size = 7000
    text = read_document(text_path)
    text = trim_text_edges(text,5,0)

    text_blocks = safe_block_split(text, max_block_size)
    block_locations = cumulative_text_lengths(text_blocks)

    blocks_vader_sentiment = []
    blocks_new_wn_sentiment = []
    for block in text_blocks:
        # For both methods: this line below adds the average sentiment of the BLOCK to the list
        blocks_vader_sentiment.append(statistics.mean(vader_senti_sentences(block)))
        blocks_new_wn_sentiment.append(statistics.mean(new_wn_senti_sentences(block, wordnet_path)))

    chapters, chapters_locations = split_and_locate_chapters(text, r"(?:\n\s*)+([IVXLCDM]+)(?:\s*\n)+")

    chapters_vader_sentiment = []
    chapters_new_wn_sentiment = []
    for chapter in chapters:
        # For both methods: this line below adds the average sentiment of the CHAPTER to the list
        chapters_vader_sentiment.append(statistics.mean(vader_senti_sentences(chapter)))
        chapters_new_wn_sentiment.append(statistics.mean(new_wn_senti_sentences(chapter, wordnet_path)))

    data = {
    "block_locations": {
        loc: [blocks_vader_sentiment[i], blocks_new_wn_sentiment[i]]
        for i, loc in enumerate(block_locations)
    },
    "chapter_locations": {
        loc: [chapters_vader_sentiment[i], chapters_new_wn_sentiment[i]]
        for i, loc in enumerate(chapters_locations)
        }
    }
    
    pprint.pprint(data)

    #save_json(data, data_path)

if __name__ == "__main__":
    main()
