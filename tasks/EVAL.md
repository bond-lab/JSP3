# evaluate how well this works **EVAL** 


## Minimum

Compare a tagged document with a gold standard, or compare two and see how much they overlap.  Calculate accuracy and type of error (e.g. tag for 'x', ...).  Use the wordnet structure to score near-misses ---  if a concept is close, it should get a part score.

## Desired

Show differences in a useful way

## Stretch

Look at common mistakes and try to fix them (e.g. *se/si*)

## Difficulty

Not so hard, but requires some interaction with SQL

## Next tasks

* get a simple script to evaluate `spec_qwen3:14b.json` vs `spec_human.json`
  * give one accuracy
  * take the file names as input (use argparse)
  * break down results by tag type
  

