import argparse
from collections import defaultdict as dd
import sqlite3
import json
import os
import sys

def escape(s):
    # s=s.replace("'","&quote;")
    s = html.escape(s, quote=True)
    return s

def sents_by_docid(c, did):
    """return all sentences for a given docid"""
    c.execute("""SELECT sid, pid, sent, comment 
    FROM sent WHERE docid=?
    ORDER BY sid""", (did,))  
    sents = dd(dict)
    for (sid, pid, sent, comment) in c:
        if pid == None:
            pid = ''
        sents[sid]['text'] = sent
        sents[sid]['com'] = comment
    return sents

def add_stype(c, sents):
    """
    return the type of a sentence:
    h1 .. h7   header of level 1-7
    p          first sentence of a paragraph
    """
    sid_min = min(sents)
    sid_max = max(sents)
    stype = dd(str)
    c.execute("""SELECT sid, stype 
    FROM stype 
    WHERE sid >= ? AND sid <=?
    AND stype IS NOT NULL
    ORDER BY sid""", (sid_min, sid_max))
    for (sid, styp) in c:
        sents[sid]['stype'] = styp
    return sents

def words_by_docid(c, did):
    """return all words for all sentences for a given docid"""
    c.execute("""SELECT word.sid, wid, word, lemma, pos, word.comment
    FROM (SELECT sid FROM sent WHERE docid=?
    ORDER BY sid) as sent
    JOIN word on sent.sid=word.sid ORDER by word.sid, wid""", (did,))  
    words = dd(lambda: dd(lambda: dd()))
    for (sid, wid, word, lemma, pos, comment) in c:
        words[sid][wid]['text'] = word
        words[sid][wid]['lemma'] = lemma
        words[sid][wid]['pos'] = pos
        if comment:
            words[sid][wid]['com'] = comment
    return words

def concepts_by_docid(c, did):
    """return all cids for all sentences for a given docid"""
    c.execute("""SELECT cwl.sid, cwl.wid, cwl.cid
    FROM (SELECT sid FROM sent WHERE docid=?
    ORDER BY sid) as sent
    JOIN cwl on sent.sid=cwl.sid""", (did,))  
    clink = dd(lambda: dd(list))
    for (sid, wid, cid) in c:
        clink[sid][cid].append(wid)

    c.execute("""SELECT sent.sid, cid, clemma, tag, comment
    FROM (SELECT sid FROM sent WHERE docid=?
    ORDER BY sid) as sent
    JOIN concept on sent.sid=concept.sid""", (did,))  
    conc = dd(lambda: dd(lambda: dd()))
    for (sid, cid, clemma, tag, comment) in c:
        conc[sid][cid]['clemma'] = clemma
        conc[sid][cid]['tag'] = tag
        conc[sid][cid]['wids'] = clink[sid][cid]
        if comment: 
            conc[sid][cid]['com'] = comment
    return conc

def print_corpus(doc, data):
    with open(f'{doc}.json', 'w', encoding='utf8') as f:
        json.dump(data, f, indent=2)

def process_document(conn, did, name, annotator):
    """
    Process a single document and export to JSON

    """
    c = conn.cursor()
    data = dict()
    data['meta'] = {'code':name,'annotator':annotator}
    
    sents = sents_by_docid(c, did)
    sents = add_stype(c, sents)
    words = words_by_docid(c, did)
    concepts = concepts_by_docid(c, did)
    
    data['sent'] = sents
    data['word'] = words
    data['conc'] = concepts

    docname = f"{name}_{annotator}"
    print_corpus(docname, data)
    print(f"Successfully exported document '{name}' (ID: {did}, Annotator: {annotator}) to {docname}.json")

def main():
    parser = argparse.ArgumentParser(
        description='Export annotated documents from NTUMC corpus database to JSON format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s -d 440 -n spec
  %(prog)s -d 441 -n danc -c /path/to/corpus.db
  %(prog)s --docid 500 --name kumo-no-ito --corpus eng.db
        '''
    )
    
    parser.add_argument('-d', '--docid', 
                        type=int, 
                        required=True,
                        help='Document ID to export')
    
    parser.add_argument('-n', '--name', 
                        type=str, 
                        required=True,
                        help='Document name (used for output filename)')
    parser.add_argument('-a', '--annotator', 
                        type=str, 
                        default='human',
                        help='Who annotated this corpus')
    
    parser.add_argument('-c', '--corpus', 
                        type=str, 
                        default='eng.db',
                        help='Path to corpus database file (default: eng.db)')
    
    args = parser.parse_args()
    
    # Check if database exists
    if not os.path.isfile(args.corpus):
        print(f"Error: Could not find database file '{args.corpus}'", file=sys.stderr)
        sys.exit(1)
    
    # Connect to database
    try:
        conn = sqlite3.connect(args.corpus)
        print(f"Connected to database: {args.corpus}")
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Process the document
    try:
       
        process_document(conn, args.docid,
                         args.name, args.annotator)
    except Exception as e:
        print(f"Error processing document: {e}", file=sys.stderr)
        conn.close()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
