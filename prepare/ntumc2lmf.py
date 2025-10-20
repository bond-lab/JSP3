#!/usr/bin/python3
###
### python3 ntumc2lmf.py jpn /home/bond/svn/ntu-mc/db/2014-06-23/wn-ntumc.db omw > wn-ntu-jpn.xml
### python3 ntumc2lmf.py jpn /home/bond/svn/wn/omw/wns/wikt/wn-wikt-jpn.tab tab > wn-wikt-jpn.xml
### 
### mode='tab'
###   only add sysnets that are used in senses
###   don't add links 
###   read from tab file! (use on omw)
###
### mode='omw'
###  get full db
###
### mode = 'ntumc'
###  do all 5 languages of ntumc
### cow:cmn-Hans
### wnja:ja
### bahasa_id:id
### bahasa_zsm:zsm
### ntumc_en:en
###
### get from DB
###  * add Japanese variants
###  * add confidence for Bahasa
###  * make sure synset linking is done right
###  * add classifiers
###  * remove relations from PWN (or mark them as from there)
###  * have synsets all in one place?
###  *

import sys
import sqlite3, re
import datetime
from collections import defaultdict as dd
from xml.sax.saxutils import escape
from pyme import readcepy
from pyme import pinyin
from pyme import py2dia
from pyme import py2plain
import romkan

import omwmeta
#from omwmeta import meta

log = open("log-ntumc2db.txt", mode='w')
cilimapfile= '/home/bond/work/omw/CILI/ili-map.ttl?raw=true'
#import pinyin



def quotescape(data):
    return escape(data, entities={
        "'": "&apos;",
        "\"": "&quot;"
    })

### cruft for Chinese
badsynsets = [
    "15171739-n",
    "15173065-n",
    "15176162-n",
    "15178842-n",
    "15171858-n",
    "15172882-n",
    "15171147-n",
    "15171146-n",
    "15168570-n",
    "14869976-n",
    "15177867-n",
    "14869977-n"]

### ILI mapping  ### hack, should get from DB
ilimap = dd(str)

f = open(cilimapfile)
#<i1>	owl:sameAs	pwn30:00001740-a . # able
for l in f:
    if l.startswith('<i'):
        row = l.strip().split()
        #print (row[2][6:].replace('-s','-a'), row[0][1:-1])
        ilimap[row[2][6:].replace('-s','-a')] = row[0][1:-1] 
f.close()

### prepare Japanese
###
jvar = dd(list)
f =open('vars_tk11.tab')
for l in f:
    r = l.strip().split('\t')
    wid = "{}_{}".format(r[0],r[1])
    jvar[wid].append(r[0])
    for w in r[2:]:
        if w not in jvar[wid]:
            jvar[wid].append(w)
f.close()
# for wid in jvar:
#     print (wid,jvar[wid])
jsense=dd(set)
jsynsets=dd(set)
f = open('wn+var_tk11.tab')
for l in f:
    if l.startswith('#'):
        continue
    r = l.strip().split('\t')
    wid = "{}_{}".format(r[1],r[2])
    if r[3] == 'multi':
        conf= 0.96
    elif  r[3] in ['hand', 'mlsn']:
        conf=1.0
    elif  r[3] == 'mono':
        conf=0.86
    else:
        ### hand added by kuririn
        conf = 1.0
    synset=r[0]
    jsense[wid].add((synset,0,conf))# senses[wid] = ((synset, freq, confidence), ...)
    wordid="{}_{}".format(wid,synset[-1])
    jsynsets[synset].add((wordid,0,conf))
    if wid not in jvar: ## doesn't happen!
        print('Unknown {}: {}'.format(wid,l))
f.close()
###
### find the pos of the word
###
jwords=list()
for wid in jsense:
    ps = set()
    for (ss,freq,conf) in jsense[wid]:
        ps.add(ss[-1])
    if (len(ps) > 1):
        print('Multiple POS',wid , ps,jsense[wid],file=log)
    for pos in ps:
        wordid="{}_{}".format(wid,pos)
        jwords.append((wordid, jvar[wid][0], pos)) # # [( wordid, lemma, pos), ..] 

def print_header_lr():
    """print the header of the collection"""
    print ("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-1.0.dtd">
<LexicalResource xmlns:dc="http://purl.org/dc/elements/1.1/">
""")
 

def print_header(meta, comment):
    """print the header of the lexicon, filled in with meta data"""
    print ("""<!-- {}  -->""".format(comment))

    ###
    ### make a lexicon!
    ###
    print("""  <Lexicon id="{}"
           label="{}"
           language="{}" 
           email="{}"
           license="{}"
           version="{}"
           citation="{}"
           url="{}"
           dc:publisher="Global Wordnet Association"
           dc:description="{}"
           dc:date="{}"
           confidenceScore="{}">""".format(meta['id'], 
                                           meta['label'], 
                                           meta['lg'],
                                           meta['email'],
                                           meta['license'], 
                                           meta['version'], 
                                           meta['citation'],
                                           meta['url'],
                                           meta['description'].strip(),
                                           datetime.date.today().isoformat(), #2017-11-27
                                           meta['conf']))

 
###
### Make some lexical entries
###



zhs2py, chr2py = readcepy()
def w2py(w):
     """return a list of tuples (pinyin, type, conf)"""
     pys = []
     w=w.replace(' ', '␣')
     p = pinyin(w,zhs2py, chr2py)
     if p:
         pys.append((py2dia(p[0]).replace(' ','').replace('␣',' '), 'pīnyīn', p[1]))
         pys.append((p[0].replace(' ','').replace('␣',' '), 'pin1yin1', p[1]))
         pys.append((py2plain(p[0]).replace(' ','').replace('␣',' '), 'pinyin', p[1]))
         if 'ü' in p[0]:
             pys.append((p[0].replace('ü', 'v').replace(' ','').replace('␣',' '),
                        'pin1yin1', p[1]))
             pys.append((py2plain(p[0]).replace('ü', 'v').replace(' ','').replace('␣',' '),
                        'pinyin', p[1]))
     return pys

def script(w):
    """return the script of a word or '' if not sure"""
    katakana="゠ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヷヸヹヺ・ーヽヾヿ"
    hiragana="぀ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖ゗゘゙゚゛゜ゝゞゟ"
    if all(c in katakana for c in w):
        script =' script="Kana"'
    elif all(c in hiragana for c in w):
        script =' script="Hira"'
    else:
        script = ''
    return script


def print_senses(meta, words, senses, lang):
    newnum =1
    for (wid, word, pos) in words:
        pos = pos.replace('s', 'a')
        pos = pos.replace('z', 'u')
        vars=[]
        if lang=='jpn':
            if isinstance(wid,str) and wid[:-2] in jvar:
                vars = jvar[wid[:-2]][1:] ## omit the first one
        
        if not str(wid).isdigit():
            widxml='n'+str(newnum)
            newnum+=1
        else:
            widxml=wid
        print ('   <LexicalEntry id="w{}">'.format(widxml))
        print ('       <Lemma writtenForm="{}" partOfSpeech="{}"{}/>'.format(quotescape(word),
                                                                             pos,
                                                                             script(word)))
        if lang=='cmn':
            for (form, cat, conf) in w2py(word):
                print ('''          <Form writtenForm="{}">
                <Tag category="{}">{}</Tag>
                <Tag category="{}">{}</Tag>
                </Form>'''.format(quotescape(form),
                                  'transliteration', cat,
                                  'confidence', conf))
        for form in vars:
            ### ToDo pythontransliteration
            if script(form)==' script="Kana"':
                print ('''          <Form writtenForm="{}"{}/>'''.format(quotescape(form),
                                                                                   script(form)))
                print ('''          <Form writtenForm="{}">
            <Tag category="{}">{}</Tag>
          </Form>
          <Form writtenForm="{}">
             <Tag category="{}">{}</Tag>
          </Form>'''.format(quotescape(romkan.to_hepburn(form)),'transliteration', 'hepburn',
                                  quotescape(romkan.to_kunrei(form)), 'transliteration', 'kunrei'))
            else:
                    print ('''          <Form writtenForm="{}"{}/>'''.format(quotescape(form),
                                                                                   script(form)))
          
               

            
        for (synset, freq, confidence) in senses[wid]:
            if synset in badsynsets:
                continue
            print ('        <Sense id="{0}-{1}-{2}" synset="{0}-{1}">'.format(
                meta['id'], synset, widxml))
            print ('        </Sense>')
        print ('  </LexicalEntry>')



def print_synsets(meta, synsets, defs, edefs, ilimap, synlink):
    for synset in synsets:
        if synset in badsynsets:  ## check if it has lemma or def or synset not in defs :
            continue
        
        pos = synset[-1].replace('s', 'a')
        pos = synset[-1].replace('z', 'u')
        if pos not in "nvarstcpxu":
            print("Unknown synset '{}' in {} ({})".format(pos,synset,meta['id']))
            continue
            ## fixme check if in  (n|v|a|r|s|t|c|p|x|u)
        ili = ''
        if synset in ilimap:  ### already mapped
            ili=ilimap[synset]
        elif synset in edefs: ### maybe mappable (assume links are good)
            if  len(edefs[synset]) <25 or len(edefs[synset].split()) <5:
                print("Rejecting {} as definition is too short: <<{}>>".format(synset,
                                                                               edefs[synset]),
                file=log)
            else:
                ili='' ### 'in' NO ILI for now
            
        print ('   <Synset id="{}-{}" partOfSpeech="{}" ili="{}">'.format(meta['id'],
                                                                              synset, 
                                                                              pos,
                                                                              ili))
        if defs[synset]:
            print('      <Definition>{}</Definition>'.format(escape(defs[synset])))
        if ili == 'in':
            print('      <ILIDefinition>{}</ILIDefinition>'.format(escape(edefs[synset])))
        for (relation, target) in synlink[synset]:
            print ('      <SynsetRelation relType="{}" target="{}-{}"/>'.format(
                relation, meta['id'], target))
    
        print ('   </Synset>')
    

def print_footer_lex():
    print ("</Lexicon>")

def print_footer_lr():
    print ("</LexicalResource>")    




def get_wn_db(prog, lang, db):
   
    con = sqlite3.connect(db)
    c = con.cursor()
    synsets= set()  
    senses = dd(set) # senses[wid] = ((synset, freq, confidence), ...)
    used = set()   # wordids of the actual words we used
    words = set()  # # [( wordid, lemma, pos), ..]
    new =  set()  # # [( wordid, lemma, pos), ..]
    defs = dd(str)  #defs[synset] = def
    edefs = dd(str)  #edefs[synset] = def in English
    synlink = dd(set) #synlink[synset1].add((relation[link], synset2))

    ### senses  ## FIXME use confidence and freq
    c.execute("""SELECT synset, wordid, freq, confidence 
                 FROM sense WHERE lang = ?""", (lang,))
    for (synset, wid, freq, confidence) in c:
        if lang=='jpn':
            ### is this in jsynsets? if so replace with this
            if synset in jsynsets:
                for (wordid, freq, conf) in jsynsets[synset]:
                    senses[wordid].add((synset, freq, confidence))
                    synsets.add(synset)
                    wid = wordid[:-2]
                    pos=synset[-1]
                    if not wordid in used:
                        new.add((wordid, jvar[wid][0], pos))
                    else:    
                        used.add(wordid)

            else:
                senses[wid].add((synset, freq, confidence))
                used.add(wid)
                synsets.add(synset)
                print("Synset {} not in varfile".format(synset),file=log)
    ### Words
    
    c.execute("SELECT wordid, lemma, pos FROM word WHERE lang = ?", (lang,))
    words = set(c.fetchall())

    ### check:
    if lang=='jpn':
        for (wordid, lemma, pos) in words:
            if wordid in used:
                new.add((wordid, lemma, pos))
        words=new
    #print ('words',words)
    
    ###
    ### Make some synsets
    ###
    
    defsep = '; '
    ### Definitions
    c.execute("""SELECT synset, def, sid 
                 FROM synset_def WHERE lang = ?
                 ORDER BY sid""", (lang,))
    for (synset, df, sid) in c:
        if defs[synset]:
            defs[synset] += defsep + df 
        else:
            defs[synset] = df
        synsets.add(synset)
    
    ### Definitions
    c.execute("""SELECT synset, def, sid 
                 FROM synset_def WHERE lang = 'eng'
                 ORDER BY sid""")
    for (synset, df, sid) in c:
        if edefs[synset]:
            edefs[synset] += defsep + df 
        else:
            edefs[synset] = df
        #synsets.add(synset) if all we have is an english def, don't use
    ### Examples (should move to sense)
    
    
    
    ### Links

    relation = { 
        'attr':'attribute',
        'ants':'antonym',
        'dmnc':'domain_topic',
        'dmtc':'has_domain_topic',
        'sim':'similar',
        'also':'also',
        'dmnr':'domain_region',
        'dmtr':'has_domain_region',
        'dmnu':'exemplifies',
        'dmtu':'is_exemplified_by',
        'enta':'entails',
        'hypo':'hyponym',
        'hype':'hypernym',
        'caus':'causes',
        'mprt':'mero_part',
        'msub':'mero_substance',
        'hprt':'holo_part',
        'hmem':'holo_member',
        'inst':'instance_hyponym',
        'hasi':'instance_hypernym',
        'mmem':'mero_member',
        'hsub':'holo_substance',
        ### new things
        'hasq':'restricted_by',
        'qant':'restricts',
        'eqls':'eq_synonym'
    }
    c.execute("SELECT synset1, synset2, link FROM synlink")
    for (synset1, synset2, link) in c:
        synlink[synset1].add((relation[link], synset2))
        ## only add necessary synsets
        if synset1 in synsets:
            synsets.add(synset2)
        if synset2 in synsets:
            synsets.add(synset1)
    
    # ### Synsets
    # if mode=='omw':
    #     c.execute("SELECT synset FROM synset")
    #     synsets = c.fetchall()
    # else:
    #     synsets.extend(defs.keys())
        
    con.close()
    #synsets =list(set(synsets))
    
    return words, senses, synsets, synlink, defs, edefs 


# def get_wn_tab(prog, lang, wnfile):
#     synsets= list()  
#     senses = dd(set) # senses[wid] = ((synset, freq, confidence), ...)
#     words = list()   # [( wordid, lemma, pos), ..]
#     defs = dd(str)  #def[synset] = def
#     exes = dd(str)  #def[synset] = def
#     edefs = dd(str)  #def[synset] = def
#     synlink = dd(set) #synlink[synset1].add((relation[link], synset2))
#     defsep = ';; '
#     wn = dd(lambda: dd(set))
    
#     sys.stderr.write('Reading "%s"\n' % (wnfile,))
#     f = open(wnfile, encoding='utf-8', mode = 'r')
#     (name, lang, src, lic) = f.readline()[1:].strip().split('\t')
#     (poi, proj, lg) =   wnfile.split('/')[-1].split('-')
#     meta[lang] = { 'id':proj + ':' + lang, 
#                    'label':name,
#                    'lg':'zu',  
#                    'email':'',
#                    'license':lic,
#                    'version':'0.1',
#                    'citation':'',
#                    'url':src,
#                    'conf':'0.9'
#    }
#     for l in f:
#         if l.startswith('#') :  ### discard comments
#             continue
#         else:
#             sense = l.strip().split('\t')
#             if (len(sense) == 3):  ### check there are three things: ss, type, thing
#                 if sense[1].endswith('lemma'):  ### and it is a lemma
#                     ll = sense[2].strip()
#                     pos = sense[0][-1]
#                     wn[ll][pos].add(sense[0])
#                     mm= re.search(r'(.*)\+(.*)',ll)
#                     if ll.startswith('-'):
#                         wn[ll[1:]][pos].add(sense[0])
#                         sys.stderr.write('removed hyphen (%s)\n' % ll)
#                     elif mm:
#                         sys.stderr.write('removed +... (%s)\n' % ll)
#                         wn[mm.group(1)][pos].add(sense[0])
#             elif (len(sense) == 4):  ### check there are three things: ss, type, id, thing
#                 ### assume that they are sorted
#                 if sense[1].endswith(':def'):  ### and it is a definition  
#                     thislang = sense[1][0:3]
#                     if defs[sense[0]]:
#                         defs[sense[0]] += defsep + sense[2]
#                     else:
#                         defs[sense[0]] = sense[2]
#                 elif sense[1].endswith(':exe'):  ### and it is an example
#                     thislang = sense[1][0:3]
#                     if exes[sense[0]]:
#                         exes[sense[0]] += defsep + sense[2]
#                     else:
#                         exes[sense[0]] = sense[2]
#     return words, senses, synsets, synlink, defs, edefs


#(prog, lang, db, mode) = sys.argv

# if mode == 'omw':
#     words, senses, synsets, synlink, defs, edefs =  get_wn_db(prog, lang, db)
#     #print(senses)
# elif mode == 'tab':
#     words, senses, synsets, synlink, defs, edefs =  get_wn_tab(prog, lang, db)

db='/home/bond/ntu-mc/2016-11-30/wn-ntumc.db'  ### get latest
prog = 'ntumc2lmf.py'
mode='omw'
print_header_lr()
for lang in ['jpn']: #, 'ind', 'cmn']:
    words, senses, synsets, synlink, defs, edefs =  get_wn_db(prog, lang, db)
    meta=omwmeta.meta[lang]
    print_header(meta, prog)
    print_senses(meta, words, senses, lang)
    print_synsets(meta, synsets, defs, edefs, ilimap, synlink)
    print_footer_lex()
print_footer_lr()

