#  test different information from wordnet **WSD-W**

## Minimum

Get a tagger running on a cloud machine, using an existing model.  Run with different amounts of information from wordnet, and the lemmas and so forth.  Evaluate which works better.

## Desired

Automate the testing (maybe)?
 * watch [Let the LLM Write the Prompts: An Intro to DSPy in Compound AI Pipelines](https://youtu.be/I9ZtkgYZnOw?si=66uDbpaDWra9TaIj)

 * note model/information/context combinations

## Difficulty

* Many different possibilities, so need to plan how to test
* What works for English may not work fo Czech

## Next steps

* collaborate with WSD-*
* take a look at https://github.com/bond-lab/NTUMC/blob/refactored-tagdb/ntumc/taggers/tag-llm.py
* make sure you know exactly what your models are
* use wn <https://pypi.org/project/wn/> for the wordnet module, wordnets are in prepare/wn-ntumc*.xml

## Notes 

* I have code, use that and adapt to collab/Kagle

https://github.com/bond-lab/NTUMC/tree/refactored-tagdb
