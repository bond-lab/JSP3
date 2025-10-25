#  test different contexts **WSD-C**

## Minimum

Get a tagger running on a cloud machine, using an existing model.  Run with different contexts, evaluate which works better.

## Desired

Make it easy for other tasks to use (WSD-T)

Find models that can be used cheaply

## Difficulty

Not so hard, but results are slow, and free resources have cutoff

## Next steps

* take a look at https://github.com/bond-lab/NTUMC/blob/refactored-tagdb/ntumc/taggers/tag-llm.py
* make sure you know exactly what your models are
* use wn <https://pypi.org/project/wn/> for the wordnet module, wordnets are in prepare/wn-ntumc*.xml

## Notes 

* I have code, use that and adapt to collab/Kagle

https://github.com/bond-lab/NTUMC/tree/refactored-tagdb
