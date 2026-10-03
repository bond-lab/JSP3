import argparse
import json
from collections import defaultdict
from nltk.corpus import wordnet as wn

MISSING = "MISSING"

def tag_to_synset(tag):
    try:
        offset, pos = tag.rsplit("-", 1)
        pos = pos.lower()
        return wn.synset_from_pos_and_offset(pos, int(offset))
    except Exception:
        return None
    
def near_miss_from_tags(tag_gold, tag_pred):
    s1 = tag_to_synset(tag_gold)
    s2 = tag_to_synset(tag_pred)
    if s1 and s2:
        return s1.wup_similarity(s2)
    return None

def evaluate(target, gold):
    correct = 0
    total = 0
    tag_type_total = {}
    tag_correct_total = {}
    confusion_pos = defaultdict(lambda: defaultdict(int))
    confusion_synset = defaultdict(lambda: defaultdict(int))

    errors = defaultdict(int)
    near_miss_scores = []
    error_examples = []

    weighted_tp = 0.0
    weighted_fp = 0.0
    weighted_fn = 0.0

    correct_no_x = 0
    total_no_x = 0

    for group_name in gold["conc"]:
        gold_group = gold["conc"][group_name]
        target_group = target["conc"].get(group_name, {})

        for item_name in gold_group:
            gold_item = gold_group[item_name]
            target_item = target_group.get(item_name)

            tag_g = gold_item.get("tag")

            if not target_item:
                errors["missing_item"] += 1
                g_pos = tag_g.split("-")[-1] if tag_g else MISSING
                t_pos = MISSING
                confusion_pos[g_pos][t_pos] += 1
                total += 1
                continue

            tag_t = target_item.get("tag")

            if not tag_g:
                errors["missing_gold_tag"] += 1
                g_pos = MISSING
                t_pos = tag_t.split("-")[-1] if tag_t else MISSING
                confusion_pos[g_pos][t_pos] += 1
                total += 1
                continue

            if not tag_t:
                errors["missing_target_tag"] += 1
                g_pos = tag_g.split("-")[-1]
                t_pos = MISSING
                confusion_pos[g_pos][t_pos] += 1
                total += 1
                continue    

            g_pos = tag_g.split("-")[-1]
            t_pos = tag_t.split("-")[-1]

            if g_pos != "x":
                total_no_x += 1
                if g_pos == t_pos:
                    correct_no_x += 1

            confusion_pos[g_pos][t_pos] += 1


            general_tag = ["num", "oth", "per", "loc", "dat:year"]

            total += 1
            tag_type_total[g_pos] = tag_type_total.get(g_pos, 0) + 1

            gold_syn = tag_to_synset(tag_g)
            pred_syn = tag_to_synset(tag_t)

            if g_pos != t_pos:
                weighted_fp += 1
                weighted_fn += 1
            else:
                score = near_miss_from_tags(tag_g, tag_t)
                if score is None:
                    weighted_fp += 1
                    weighted_fn += 1
                elif score >= 0.9:
                    weighted_tp += 1.0
                elif score >= 0.8:
                    weighted_tp += 0.7
                    weighted_fp += 0.3
                    weighted_fn += 0.3
                elif score >= 0.7:
                    weighted_tp += 0.4
                    weighted_fp += 0.6
                    weighted_fn += 0.6
                else:
                    weighted_fp += 1
                    weighted_fn += 1

            if tag_t == tag_g:
                correct += 1
                tag_correct_total[g_pos] = tag_correct_total.get(g_pos, 0) + 1
            else:  
                if tag_t in general_tag and tag_g not in general_tag:
                    errors["coarse_tag"] += 1
                elif tag_t not in general_tag and tag_g in general_tag:
                    errors["generalized_tag"] += 1
                elif g_pos != t_pos:
                    errors["mismatch_pos"] += 1
                elif gold_syn and pred_syn and gold_syn.offset() != pred_syn.offset():
                    errors["mismatch_offset"] += 1
                else:
                    errors["unknown_tag"] += 1

                if (g_pos == t_pos and tag_g not in general_tag and tag_t not in general_tag):
                    score = near_miss_from_tags(tag_g, tag_t)

                    error_examples.append({
                        "group": group_name,
                        "item": item_name,
                        "gold_tag": tag_g,
                        "pred_tag": tag_t,
                        "gold_synset": tag_to_synset(tag_g),
                        "pred_synset": tag_to_synset(tag_t),
                        "near_miss": score
                        })
                    if score is not None:
                        near_miss_scores.append(score)
        
            gold_syn = tag_to_synset(tag_g)
            pred_syn = tag_to_synset(tag_t)

            g_key = gold_syn.name() if gold_syn else MISSING
            t_key = pred_syn.name() if pred_syn else MISSING

            if g_key != MISSING and t_key != MISSING:
                confusion_synset[g_key][t_key] += 1

    print(f"\n\033[1m---Total accuracy---\033[0m")
    accuracy = correct / total if total > 0 else 0
    print(f"{accuracy:.2%} correct\n")
    print("\n\033[1m---Accuracy without x---\033[0m")
    acc_no_x = correct_no_x / total_no_x if total_no_x > 0 else 0
    print(f"{acc_no_x:.2%} correct ({correct_no_x}/{total_no_x})")

    print(f"\n\033[1m---Break down results by tag type---\033[0m")
    for tag in sorted(tag_type_total.keys()):
        correct_type = tag_correct_total.get(tag, 0)
        total_type = tag_type_total[tag]
        accuracy_tag = correct_type / total_type
        print(f"{tag}: {accuracy_tag:.2%} correct ({correct_type}/{total_type})")

    print("\n\033[1m---Confusion pos matrix---\033[0m")
    all_tags = sorted(set(confusion_pos.keys()) | {t for preds in confusion_pos.values() for t in preds})
    print("gold/pred".ljust(10), end="")
    for t in all_tags:
        print(f"{t:>10}", end="")
    print()

    for g in all_tags:
        print(f"{g:<10}", end="")
        for t in all_tags:
            value = confusion_pos[g].get(t, 0)
            if g == t and value > 0:
                print(f"\033[32m{value:>10}\033[0m", end="")
            elif value > 0:
                print(f"\033[31m{value:>10}\033[0m", end="") 
            else:
                print(f"{value:>10}", end="")
        print()

    print("\n\033[1m---Top synset confusions---\033[0m")
    pairs = []
    for g in confusion_synset:
        for t, c in confusion_synset[g].items():
            if g != t and c > 0:
                pairs.append((c, g, t))

    for c, g, t in sorted(pairs, reverse=True)[:10]:
        print(f"{g} → {t}: {c}")

    macro_precision = 0.0
    macro_recall = 0.0
    macro_f1 = 0.0
    tags = 0

    tp_total = fp_total = fn_total = 0

    for tag in all_tags:
        tp = confusion_pos[tag].get(tag, 0)
        fp = sum(confusion_pos[g].get(tag, 0) for g in all_tags if g != tag)
        fn = sum(confusion_pos[tag].get(t, 0) for t in all_tags if t != tag)

        tp_total += tp
        fp_total += fp
        fn_total += fn

        if tp + fp == 0 or tp + fn == 0:
            continue

        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1 = (2 * precision * recall / (precision + recall) if precision + recall > 0 else 0.0)

        macro_precision += precision
        macro_recall += recall
        macro_f1 += f1
        tags += 1

    if tags > 0:
        macro_precision /= tags
        macro_recall /= tags
        macro_f1 /= tags

    micro_precision = tp_total / (tp_total + fp_total) if tp_total + fp_total > 0 else 0
    micro_recall = tp_total / (tp_total + fn_total) if tp_total + fn_total > 0 else 0
    micro_f1 = (2 * micro_precision * micro_recall / (micro_precision + micro_recall) if micro_precision + micro_recall > 0 else 0)

    print("\n\033[1m---F1 Summary---\033[0m")
    print("Type".ljust(10), "Precision".rjust(10), "Recall".rjust(10), "F1".rjust(10))
    print(f"Macro".ljust(10), f"{macro_precision:>10.3f}", f"{macro_recall:>10.3f}", f"{macro_f1:>10.3f}")
    print(f"Micro".ljust(10), f"{micro_precision:>10.3f}", f"{micro_recall:>10.3f}", f"{micro_f1:>10.3f}")

    print("\n\033[1m---Type of error---\033[0m")
    for error, count in errors.items():
        print(f"{error:<20} {count:>5}")

    print("\n\033[1m---Near-miss error examples---\033[0m")
    error_examples = sorted(
    [e for e in error_examples if e["near_miss"] is not None],
    key=lambda x: x["near_miss"],
    reverse=True
    )

    for e in error_examples[:10]: 
        print(
            f"\nItem: {e['group']} / {e['item']}\n"
            f"  Gold: {e['gold_synset']} ({e['gold_tag']})\n"
            f"  Pred: {e['pred_synset']} ({e['pred_tag']})\n"
            f"  Near-miss score: {e['near_miss']:.3f}"
        )

    histogram = {"Almost correct": 0, "Close meaning": 0, "Rather wrongly": 0}

    for e in error_examples:
        h = e["near_miss"]
        if h >= 0.9:
            histogram["Almost correct"] += 1
        elif h >= 0.8:
            histogram["Close meaning"] += 1
        else:
            histogram["Rather wrongly"] += 1

    print("\n\033[1m----Near-miss quality histogram:---\033[0m")
    for i, j in histogram.items():
        print(f"{i}: {j}")

    if near_miss_scores:
        print("\nAverage near-miss score: ",
            sum(near_miss_scores) / len(near_miss_scores))
    
        precision_nm = weighted_tp / (weighted_tp + weighted_fp) if weighted_tp + weighted_fp > 0 else 0
        recall_nm = weighted_tp / (weighted_tp + weighted_fn) if weighted_tp + weighted_fn > 0 else 0
        f1_nm = (2 * precision_nm * recall_nm / (precision_nm + recall_nm) if precision_nm + recall_nm > 0 else 0)

    print("\n\033[1m---Near-miss weighted F1---\033[0m")
    print(f"Precision: {precision_nm:.3f}")
    print(f"Recall:    {recall_nm:.3f}")
    print(f"F1:        {f1_nm:.3f}")
        
def main():
    parser = argparse.ArgumentParser(description="Evaluate model output against gold data")
    parser.add_argument("--target", required=True, help="Path to model output JSON")
    parser.add_argument("--gold", required=True, help="Path to human-annotated JSON")
    args = parser.parse_args()

    with open(args.target, "r", encoding="utf-8") as f:
        target = json.load(f)
    with open(args.gold, "r", encoding="utf-8") as f:
        gold = json.load(f)

    evaluate(target, gold)


if __name__ == "__main__":
    main()
