#!/usr/bin/python3
###
### python3 db2lmf.py jpn /home/bond/svn/ntu-mc/db/2014-06-23/wn-ntumc.db omw > wn-ntu-jpn.xml
### python3 db2lmf.py jpn /home/bond/svn/wn/omw/wns/wikt/wn-wikt-jpn.tab tab > wn-wikt-jpn.xml
### 
### mode='tab'
###   only add sysnets that are used in senses
###   don't add links 
###   read from tab file! (use on omw)
###
### mode='omw'
###  get full db
###
import sys
import sqlite3, re

from collections import defaultdict as dd
from xml.sax.saxutils import escape
# from pyme import readcepy
# from pyme import pinyin
# from pyme import py2dia
# from pyme import py2plain

import omwmeta
from omwmeta import meta

log = open("log-wn2db.txt", mode='w')
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







def print_header(meta, comment, lang):
    """print the header of the lexicon, filled in with meta data"""

    print ("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-1.0.dtd">
<LexicalResource xmlns:dc="http://purl.org/dc/elements/1.1/">
""")

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
           dc:format="OMW-LMF"
           dc:description="{}"
           confidenceScore="{}">""".format(meta[lang]['id'], 
                                           meta[lang]['label'], 
                                           meta[lang]['lg'],
                                           meta[lang]['email'],
                                           meta[lang]['license'], 
                                           meta[lang]['version'], 
                                           meta[lang]['citation'],
                                           meta[lang]['url'],
                                           meta[lang]['description'].strip(),               
                                           meta[lang]['conf']))

 
###
### Make some lexical entries
###



# zhs2py, chr2py = readcepy()
# def w2py(w):
#      """return a list of tuples (pinyin, type, conf)"""
#      pys = []
#      w=w.replace(' ', '␣')
#      p = pinyin(w,zhs2py, chr2py)
#      if p:
#          pys.append((py2dia(p[0]).replace(' ','').replace('␣',' '), 'pīnyīn', p[1]))
#          pys.append((p[0].replace(' ','').replace('␣',' '), 'pin1yin1', p[1]))
#          pys.append((py2plain(p[0]).replace(' ','').replace('␣',' '), 'pinyin', p[1]))
#          if 'ü' in p[0]:
#              pys.append((p[0].replace('ü', 'v').replace(' ','').replace('␣',' '),
#                         'pin1yin1', p[1]))
#              pys.append((py2plain(p[0]).replace('ü', 'v').replace(' ','').replace('␣',' '),
#                         'pinyin', p[1]))
#      return pys



def print_senses(meta, words, senses, lang): 
    for (wid, word, pos) in words:
        print ('   <LexicalEntry id="w{}">'.format(wid))
        print ('       <Lemma writtenForm="{}" partOfSpeech="{}"/>'.format(quotescape(word), pos))
        if lang=='cmn':
            for (form, cat, conf) in w2py(word):
                print ('''          <Form writtenForm="{}">
                <Tag category="{}">{}</Tag>
                <Tag category="{}">{}</Tag>
                </Form>'''.format(quotescape(form),
                                  'transliteration', cat,
                                  'confidence', conf))

        for (synset, freq, confidence) in senses[wid]:
            if synset in badsynsets:
                continue
            print ('        <Sense id="{0}-{1}-{2}" synset="{0}-{1}">'.format(
                meta[lang]['id'], synset, wid))
            print ('        </Sense>')
        print ('  </LexicalEntry>')



def print_synsets(meta, lang, synsets, defs, edefs, ilimap, synlink):
    for (synset,) in synsets:
        if synset in badsynsets:  ## check if it has lemma or def or synset not in defs :
            continue
        
        pos = synset[-1].replace('s', 'a')
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
                ili='in'
            
        print ('   <Synset id="{}-{}" partOfSpeech="{}" ili="{}">'.format(meta[lang]['id'],
                                                                              synset, 
                                                                              pos,
                                                                              ili))
        if defs[synset]:
            print('      <Definition>{}</Definition>'.format(escape(defs[synset])))
        if ili == 'in':
            print('      <ILIDefinition>{}</ILIDefinition>'.format(escape(edefs[synset])))
        for (relation, target) in synlink[synset]:
            print ('      <SynsetRelation relType="{}" target="{}-{}"/>'.format(
                relation, meta[lang]['id'], target))
    
        print ('   </Synset>')
    

def print_footer():
    print ("</Lexicon>")
    print ("</LexicalResource>")




def get_wn_db(prog, lang, db):
   
    con = sqlite3.connect(db)
    c = con.cursor()

    synsets= list()  
    senses = dd(set) # senses[wid] = ((synset, freq, confidence), ...)
    words = list()   # [( wordid, lemma, pos), ..]
    defs = dd(str)  #def[synset] = def
    edefs = dd(str)  #def[synset] = def
    synlink = dd(set) #synlink[synset1].add((relation[link], synset2))
    
    ### senses  ## FIXME use confidence and freq
    c.execute("""SELECT synset, wordid, freq, confidence 
                 FROM sense WHERE lang = ?""", (lang,))
    for (synset, wid, freq, confidence) in c:
        senses[wid].add((synset, freq, confidence))
        synsets.append((synset,))
    
    ### Words
    
    c.execute("SELECT wordid, lemma, pos FROM word WHERE lang = ?", (lang,))
    words = c.fetchall()

    ###
    ### Make some synsets
    ###
    
    defsep = ';; '
    ### Definitions
    c.execute("""SELECT synset, def, sid 
                 FROM synset_def WHERE lang = ?
                 ORDER BY sid""", (lang,))
    for (synset, df, sid) in c:
        if defs[synset]:
            defs[synset] += defsep + df 
        else:
            defs[synset] = df
    
    ### Definitions
    c.execute("""SELECT synset, def, sid 
                 FROM synset_def WHERE lang = 'eng'
                 ORDER BY sid""")
    for (synset, df, sid) in c:
        if edefs[synset]:
            edefs[synset] += defsep + df 
        else:
            edefs[synset] = df
    
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
        'eqls':'eq_synonym',
        'hasq':'restricted_by',
        'qant':'restricts',
    }
    c.execute("SELECT synset1, synset2, link FROM synlink")
    for (synset1, synset2, link) in c:
        synlink[synset1].add((relation[link], synset2))
    
    
    ### Synsets
    if mode=='omw':
        c.execute("SELECT synset FROM synset")
        synsets = c.fetchall()
    else:
        synsets.extend(defs.keys())
        
    con.close()
    synsets =list(set(synsets))
    
    return words, senses, synsets, synlink, defs, edefs 


def get_wn_tab(prog, lang, wnfile):
    synsets= list()  
    senses = dd(set) # senses[wid] = ((synset, freq, confidence), ...)
    words = list()   # [( wordid, lemma, pos), ..]
    defs = dd(str)  #def[synset] = def
    exes = dd(str)  #def[synset] = def
    edefs = dd(str)  #def[synset] = def
    synlink = dd(set) #synlink[synset1].add((relation[link], synset2))
    defsep = ';; '
    wn = dd(lambda: dd(set))
    
    sys.stderr.write('Reading "%s"\n' % (wnfile,))
    f = open(wnfile, encoding='utf-8', mode = 'r')
    (name, lang, src, lic) = f.readline()[1:].strip().split('\t')
    (poi, proj, lg) =   wnfile.split('/')[-1].split('-')
    meta[lang] = { 'id':proj + ':' + lang, 
                   'label':name,
                   'lg':'zu',  
                   'email':'',
                   'license':lic,
                   'version':'0.1',
                   'citation':'',
                   'url':src,
                   'conf':'0.9'
   }
    for l in f:
        if l.startswith('#') :  ### discard comments
            continue
        else:
            sense = l.strip().split('\t')
            if (len(sense) == 3):  ### check there are three things: ss, type, thing
                if sense[1].endswith('lemma'):  ### and it is a lemma
                    ll = sense[2].strip()
                    pos = sense[0][-1]
                    wn[ll][pos].add(sense[0])
                    mm= re.search(r'(.*)\+(.*)',ll)
                    if ll.startswith('-'):
                        wn[ll[1:]][pos].add(sense[0])
                        sys.stderr.write('removed hyphen (%s)\n' % ll)
                    elif mm:
                        sys.stderr.write('removed +... (%s)\n' % ll)
                        wn[mm.group(1)][pos].add(sense[0])
            elif (len(sense) == 4):  ### check there are three things: ss, type, id, thing
                ### assume that they are sorted
                if sense[1].endswith(':def'):  ### and it is a definition  
                    thislang = sense[1][0:3]
                    if defs[sense[0]]:
                        defs[sense[0]] += defsep + sense[2]
                    else:
                        defs[sense[0]] = sense[2]
                elif sense[1].endswith(':exe'):  ### and it is an example
                    thislang = sense[1][0:3]
                    if exes[sense[0]]:
                        exes[sense[0]] += defsep + sense[2]
                    else:
                        exes[sense[0]] = sense[2]
    return words, senses, synsets, synlink, defs, edefs


(prog, lang, db, mode) = sys.argv

if mode == 'omw':
    words, senses, synsets, synlink, defs, edefs =  get_wn_db(prog, lang, db)
    #print(senses)
elif mode == 'tab':
    words, senses, synsets, synlink, defs, edefs =  get_wn_tab(prog, lang, db)

    
print_header(meta, prog, lang) #, db, lang)
print_senses(meta, words, senses, lang)
print_synsets(meta, lang, synsets, defs, edefs, ilimap, synlink)
print_footer()

