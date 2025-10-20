# Data Structure for an annotated document

## meta
meta['title']
meta['subtitle']
meta['code']
meta['url']
meta['annotator'] = who annotated it (human or model_name)

ToDo: add date, version, lang, ...

## sent

A dictionary, indexed by sid (sentence id)

sent[sid]['text'] raw text of the sentence
sent[sid]['stype'] stype (only when appropriate)
sent[sid]['com'] (only when appropriate)

### stype
h1 .. h7   header of level 1-7
p          first sentence of a paragraph

## word

A dictionary, indexed by sid and wid  (word id)

word[sid][wid]['text'] = surface form
word[sid][wid]['lemma']
word[sid][wid]['pos']
word[sid][wid]['com']

## conc[ept]

A dictionary, indexed by sid and cid  (concept id)

conc[sid][cid]['clemma'] = concept lemma
conc[sid][cid]['tag'] = annotators tag (synset ID or special tag)
conc[sid][cid]['wids'] = [wid0, wid1, ...]
conc[sid][cid]['senti'] = sentiment score (if non-zero)
conc[sid][cid]['com'] = comment

