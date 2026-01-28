from nltk.tokenize import sent_tokenize
import json
import re

text_path = "Metamorphosis.txt"
wordnet_path = "sentiment_wordnet.yml"
data_path = "3th method senti data.json"

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
    """function removes a given number of lines from the start (head) and end (tail) of the text"""
    rows = text.splitlines()
    remaining = rows[head:len(rows) - tail] # [start:end] it gives smaller required list
    return "\n".join(remaining)


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

    chapters, chapters_locations = split_and_locate_chapters(text, r"(?:\n\s*)+([IVXLCDM]+)(?:\s*\n)+")

    print(block_locations)
    print(chapters_locations)

    data = text_blocks, chapters
    
    print(data)

    #save_json(data, data_path)

if __name__ == "__main__":
    main()
