from urllib.request import urlopen
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize, sent_tokenize
import yaml
import statistics
import re

wordnet_file = "best-sense.yaml"


def load_text_from_web(url):
    response = urlopen(url)
    text = response.read().decode('utf-8')
    text = text.replace('\r\n', '\n')
    return text


def trim_text_edges(text, head, tail):
    """function removes a given number of lines from the start (head) and end (tail) of the text"""
    rows = text.splitlines()
    remaining = rows[head:len(rows) - tail] # [start:end] it gives smaller required list
    return "\n".join(remaining)


def vader_senti_sentences(text):
    """
    Splits text into sentences and returns VADER compound sentiment value for each sentence.
    
    Note: VADER calculates sentiment for the entire sentence, considering word sentiment,
    intensifiers, negations, and context—not just an average of individual word scores.
    """
    analyzer = SentimentIntensityAnalyzer() # analyzátor sentimentu
    sentences = sent_tokenize(text) 
    compound_values = [analyzer.polarity_scores(sentence)['compound'] 
                       for sentence in sentences]
    return compound_values


def load_yaml_file(yaml_path):
    """Načte YAML soubor a vrátí dictionary."""
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data

def new_wn_senti_sentences(text, wordnet_file):
    """
    Tokenizes text into sentences and words, finds all synsets of each word in a sentiment wordnet,
    gets their sentiment values from a new sentiment wordnet, and averages per word and per sentence.
    Returns a list of average sentiment values (compound_values) for each sentence.
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

def safe_text_split(text, max_block_size):
    """
    Splits the text into blocks of up to max_block_size characters. 
    If a block ends with an incomplete sentence, that sentence is moved to the next block. 
    The resulting blocks are typically slightly shorter than max_block_size, 
    but no sentence is ever cut in half.
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

        # If the remaining portion of the text is shorter than the maximum allowed block size, 
        # simply add it as the final segment and finish the process.
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


def find_block_locations(blocks):
    """
    Returns cumulative block lengths in words.
    Uses simple tokenization via split().
    """
    locations = []
    total = 0
    for block in blocks:
        total += len(block.split())
        locations.append(total)
        
    return locations

def split_and_locate_chapters(text):
    """
    Splits the text into blocks starting with chapter markers like '1)', '2)', ...
    Then applies find_block_locations to the resulting parts.
    """
    matches = list(re.finditer(r"\d+\)", text))

    if not matches:
        blocks = [text]
        return blocks, find_block_locations(blocks)

    blocks = []
    start = 0

    for match in matches:
        idx = match.start()
        if idx > start:
            blocks.append(text[start:idx])
        start = idx

    blocks.append(text[start:])

    locations = find_block_locations(blocks)

    return blocks, locations


def main():
    text = load_text_from_web("https://www.gutenberg.org/files/64317/64317-0.txt")
    text = trim_text_edges(text,36,1)
    #print(text[10:])

# alternative_text simulates book, for quick results
    alternative_text = """
This interpretation of "A Day in the Life" by The Beatles is divided into chapters
based on the singer and musical section, highlighting the song’s narrative structure.
Each chapter offers a different perspective – the first and third chapters are sung
by John Lennon, providing reflective, sometimes surreal observations of everyday
events. The second chapter is Paul McCartney’s section, livelier and more humorous,
depicting the routines of daily life. The orchestral climax connects all parts,
closing the “day in the life” with a dramatic musical crescendo.

1)
I read the news today, oh boy
About a lucky man who made the grade.
And though the news was rather sad
Well, I just had to laugh.
I saw the photograph.
He blew his mind out in a car.
He didn't notice that the lights had changed.
A crowd of people stood and stared.
They'd seen his face before.
Nobody was really sure if he was from the House of Lords.
I saw a film today, oh boy
The English Army had just won the war.
A crowd of people turned away.
But I just had to look
Having read the book.
I'd love to turn you on.

2)
Woke up, fell out of bed
Dragged a comb across my head.
Found my way downstairs and drank a cup
And looking up, I noticed I was late.
Found my coat and grabbed my hat
Made the bus in seconds flat.
Found my way upstairs and had a smoke.
And somebody spoke and I went into a dream.

3)
I read the news today, oh boy
Four thousand holes in Blackburn, Lancashire.
And though the holes were rather small
They had to count them all.
Now they know how many holes it takes to fill the Albert Hall.
I'd love to turn you on
"""

    alternative_text = trim_text_edges(alternative_text,9,0)


    blocks = safe_text_split(alternative_text, 175)
    block_locations = find_block_locations(blocks)

    blocks_vader_sentiment = []
    blocks_new_wn_sentiment = []
    for block in blocks:
        blocks_vader_sentiment.append(statistics.mean(vader_senti_sentences(block)))
        blocks_new_wn_sentiment.append(statistics.mean(new_wn_senti_sentences(block, wordnet_file)))


    chapters, chapters_locations = split_and_locate_chapters(alternative_text)

    chapters_vader_sentiment = []
    chapters_new_wn_sentiment = []
    for chapter in chapters:
        vader_results = vader_senti_sentences(chapter)
        new_wn_results = new_wn_senti_sentences(chapter, wordnet_file)

        chapters_vader_sentiment.append(statistics.mean(vader_results))
        chapters_new_wn_sentiment.append(statistics.mean(new_wn_results))


    print("block_locations:", ", ".join(map(str, block_locations)))
    print("blocks_vader_sentiment:", ", ".join(f"{x:.5f}" for x in blocks_vader_sentiment))
    print("blocks_new_wn_sentiment:", ", ".join(f"{x:.5f}" for x in blocks_new_wn_sentiment))
    print("chapters_locations:", ", ".join(map(str, chapters_locations)))
    print("chapters_vader_sentiment:", ", ".join(f"{x:.5f}" for x in chapters_vader_sentiment))
    print("chapters_new_wn_sentiment:", ", ".join(f"{x:.5f}" for x in chapters_new_wn_sentiment))

if __name__ == "__main__":
    main()


"""
block_locations: 33, 61, 94, 123, 153, 184, 217
blocks_vader_sentiment: 0.26777, 0.00000, 0.10960, 0.19510, 0.00000, 0.08333, 0.15923
blocks_new_wn_sentiment: 0.01671, -0.00060, -0.00510, 0.03276, -0.00833, 0.00302, 0.04291
chapters_locations: 110, 169, 215
chapters_vader_sentiment: 0.14742, 0.03968, 0.15923
chapters_new_wn_sentiment: 0.01298, -0.00760, 0.03353
"""

"""
plot_sentiment(blocks_sentiments, block_positions, chapters_sentiments, chapters_locations)
"""




