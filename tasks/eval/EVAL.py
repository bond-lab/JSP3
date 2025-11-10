import argparse
import json

def accuracy(target,gold):
    correct = 0
    total = 0
    tag_type_total = {}
    tag_correct_total = {}

    for group_t, group_g  in zip(target["conc"].values(), gold["conc"].values()):
        for item_t, item_g in zip(group_t.values(),group_g.values()):
            tag_t = item_t.get("tag")
            tag_g = item_g.get("tag")
        
            total += 1

            if not tag_g or not tag_t:  
                continue

            g = tag_g[-1] if "-" in tag_g else tag_g 
            t = tag_t[-1] if "-" in tag_t else tag_t

            tag_type_total[g] = tag_type_total.get(g, 0) + 1

            if t == g:
                correct += 1
                tag_correct_total[g] = tag_correct_total.get(g ,0) + 1
            
        accuracy = correct / total 

    print(f"Total accuracy : {accuracy:.2%}")
    print("Break down results by tag type:")
    for tag in tag_type_total:
        correct_type = tag_correct_total.get(tag, 0)
        total_correct = tag_type_total[tag]
        accuracy_tag = correct_type / total_correct
        print(f"{tag}: {accuracy_tag:.2%} correct ({correct_type}/{total_correct})")

def main():
    parser = argparse.ArgumentParser(description="Evaluate how well this works EVAL")
    parser.add_argument("--target", required=True, help="Path to model output JSON ")
    parser.add_argument("--gold", required=True, help="Path to human-annotated JSON ")
    args = parser.parse_args()

    with open(args.target, "r", encoding="utf-8") as f:
        target = json.load(f)
    with open(args.gold, "r", encoding="utf-8") as f:
        gold = json.load(f)
    
    accuracy(target, gold)

if __name__ == "__main__":
    main()

#py EVAL.py --gold spec_human.json --target spec_qwen3_14b.json
