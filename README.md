# JSP3
Semester project 3 for Linguistics

## Goals

* analyze some text
* learn techniques for analyzing text
* learn some software engineering skills


## 2025 task: Word Sense Disambiguation

Take a text, sense-annotate open-class words with a wordnet.

In previous work, we have done this manually:

[Teaching Through Tagging — Interactive Lexical Semantics](https://aclanthology.org/2021.gwc-1.32/) (Bond et al., GWC 2021)

* Do this automatically
  * evaluate how well this works **EVAL** 
    * all the WSD tasks need this
    * look at common errors
	* fix some (e.g. *se/si*)
  * test different contexts **WSD-C**
    * [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
  * test different wordnet information **WSD-W**
	* watch [Let the LLM Write the Prompts: An Intro to DSPy in Compound AI Pipelines](https://youtu.be/I9ZtkgYZnOw?si=66uDbpaDWra9TaIj)
  * test different LLM models **WSD-M**
	* look at settings to make it more effecient
  * find translations and use as context **WSD-T**
    * find epub, extract text, split into para, align
	  * use: https://github.com/averkij/lingtrain-aligner/releases/tag/0.1.0
	* then add to **WSD-C**
  * look at sentiment over the story **SENTI**
    * use general tool
	* use senses
	* compare
	* visualize
  * textual criticism --- compare versions **TEXT**
    * CNK version
	* https://cs.wikisource.org/wiki/V%C3%A1lka_s_mloky
	
  * improve Czech wordnet **EXPAND**
	* add new senses to existing concepts using aligned data
	* verify with LLM?
	* create candidate definitions/examples?
  * add new Czech concepts **NEW**
	* add new suggestions for concepts to the hierarchy *difficult*
	
