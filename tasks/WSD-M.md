#  test different models **WSD-M**

## Minimum

Get a tagger running on a cloud machine, using an existing model.  Run with different models, evaluate which works better.

## Desired

* Find a good Czech model
* Look at settings to make it more efficient
  *  e.g., prompt caching
* run on some SOA models (needs mony)


## Difficulty

Not so hard, but results are slow, and free resources have cutoff

## Next steps

* collaborate with WSD-*
* take a look at https://github.com/bond-lab/NTUMC/blob/refactored-tagdb/ntumc/taggers/tag-llm.py
* make sure you know exactly what your models are
* use wn <https://pypi.org/project/wn/> for the wordnet module, wordnets are in prepare/wn-ntumc*.xml



## Notes 

* I have code, use that and adapt to collab/Kagle

https://github.com/bond-lab/NTUMC/tree/refactored-tagdb
