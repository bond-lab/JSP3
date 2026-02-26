import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================
# 1. UPGRADED EXTRACTION FUNCTION
# ==========================================
def extract_sentences(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    sentences = []
    
    for sent_id, sent_data in data.get('sent', {}).items():
        if 'text' in sent_data:
            sentences.append((sent_id, sent_data['text']))
        else:
            words = []
            word_keys = sorted([k for k in sent_data.keys() if k.isdigit()], key=int)
            for key in word_keys:
                word_info = sent_data[key]
                # Prefer exact 'word' if it exists, otherwise use 'clemma' (lemma)
                if 'word' in word_info:
                    words.append(word_info['word'])
                elif 'clemma' in word_info:
                    words.append(word_info['clemma'])
                    
            if words:
                sentences.append((sent_id, " ".join(words)))
    
    sentences.sort(key=lambda x: int(x[0]))
    return sentences

# --- Set your file paths here ---
CS_FILE_PATH = r"C:\Users\Mahdal\Desktop\data 2\twwtn-cs_human.json"
EN_FILE_PATH = r"C:\Users\Mahdal\Desktop\data 2\twwtn-en_human.json"

cs_data = extract_sentences(CS_FILE_PATH)
en_data = extract_sentences(EN_FILE_PATH)

cs_sentences = [item[1] for item in cs_data]
en_sentences = [item[1] for item in en_data]

print("--- Data Check ---")
print(f"Loaded {len(cs_sentences)} Czech sentences.")
print(f"Loaded {len(en_sentences)} English sentences.")
print("First CS:", cs_sentences[0])
print("First EN:", en_sentences[0])
print("------------------\n")

# ==========================================
# 2. LOAD SEMANTIC MODEL (LaBSE)
# ==========================================
print("Loading LaBSE model...")
model = SentenceTransformer('sentence-transformers/LaBSE')

print("Encoding sentences (this may take a moment)...")
cs_embeddings = model.encode(cs_sentences, show_progress_bar=True)
en_embeddings = model.encode(en_sentences, show_progress_bar=True)

# ==========================================
# 3. ALIGNMENT WITH LOOKAHEAD RE-ANCHORING
# ==========================================
def align_with_drift_correction(src_sents, src_embs, tgt_sents, tgt_embs, threshold=0.55):
    aligned_pairs = []
    unmatched_src = []
    merged_emb_cache = {}
    
    def get_merged_emb(text):
        if text not in merged_emb_cache:
            merged_emb_cache[text] = model.encode([text])[0]
        return merged_emb_cache[text]

    i, j = 0, 0
    while i < len(src_sents) and j < len(tgt_sents):
        sim_1_1 = cosine_similarity([src_embs[i]], [tgt_embs[j]])[0][0]
        
        sim_1_2 = 0
        if j + 1 < len(tgt_sents):
            sim_1_2 = cosine_similarity([src_embs[i]], [get_merged_emb(tgt_sents[j] + " " + tgt_sents[j+1])])[0][0]
            
        sim_2_1 = 0
        if i + 1 < len(src_sents):
            sim_2_1 = cosine_similarity([get_merged_emb(src_sents[i] + " " + src_sents[i+1])], [tgt_embs[j]])[0][0]
            
        sim_skip_tgt = 0
        if j + 1 < len(tgt_sents):
            sim_skip_tgt = cosine_similarity([src_embs[i]], [tgt_embs[j+1]])[0][0]

        best_sim = max(sim_1_1, sim_1_2, sim_2_1, sim_skip_tgt)
        
        # --- THE FIX: LOOKAHEAD WINDOW TO PREVENT STUCK POINTERS ---
        if best_sim < threshold:
            best_lookahead_sim = 0
            best_i_jump, best_j_jump = 1, 1
            
            # Scan a 6x6 grid of upcoming sentences to find the next valid alignment
            for x in range(6):
                for y in range(6):
                    if x == 0 and y == 0: continue
                    if i + x < len(src_sents) and j + y < len(tgt_sents):
                        sim = cosine_similarity([src_embs[i+x]], [tgt_embs[j+y]])[0][0]
                        if sim > best_lookahead_sim:
                            best_lookahead_sim = sim
                            best_i_jump, best_j_jump = x, y
            
            if best_lookahead_sim >= threshold:
                # We found a match further down! Catch up the pointers.
                for skipped_i in range(best_i_jump):
                    unmatched_src.append(src_sents[i + skipped_i])
                i += best_i_jump
                j += best_j_jump
            else:
                # Total dead zone (neither side matches). Force advance both pointers by 1
                unmatched_src.append(src_sents[i])
                i += 1
                j += 1
        # -----------------------------------------------------------
        
        elif best_sim == sim_1_2:
            aligned_pairs.append({'czech': src_sents[i], 'english': tgt_sents[j] + " " + tgt_sents[j+1], 'score': float(sim_1_2)})
            i += 1; j += 2
        elif best_sim == sim_2_1:
            aligned_pairs.append({'czech': src_sents[i] + " " + src_sents[i+1], 'english': tgt_sents[j], 'score': float(sim_2_1)})
            i += 2; j += 1
        elif best_sim == sim_skip_tgt:
            j += 1 
        else:
            aligned_pairs.append({'czech': src_sents[i], 'english': tgt_sents[j], 'score': float(sim_1_1)})
            i += 1; j += 1

    return aligned_pairs, unmatched_src

# ==========================================
# 4. EXECUTION & OUTPUT
# ==========================================
print("Aligning texts and fixing sequential drift...")
aligned_corpus, rejected = align_with_drift_correction(cs_sentences, cs_embeddings, en_sentences, en_embeddings, threshold=0.55)

print(f"\nSuccessfully aligned {len(aligned_corpus)} blocks.")
print(f"Rejected {len(rejected)} Czech sentences due to low semantic match.")
print("-" * 50)

for pair in aligned_corpus[:5]:
    print(f"Score: {pair['score']:.2f}")
    print(f"CS: {pair['czech']}")
    print(f"EN: {pair['english']}\n")