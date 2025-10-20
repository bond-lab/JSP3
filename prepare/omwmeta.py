### metadata to dumb wordnets

from collections import defaultdict as dd
meta = dd(lambda: dd(str))

meta['jpn'] = { 'id':'wnja', 
              'label':'Japanese Wordnet',
              'lg':'ja',
              'email':'jwordnet@gmail.com',
              'license':'wordnet',
              'version':'1.2',
              'citation':'Cite me',
              'url':'http://compling.hss.ntu.edu.sg/wnja/',
                'conf':'1.0',
              'description':"""\ 
              The Japanese Wordnet is a wordnet for the Japanese language.  Its structure is based on theat of the Princeton wordnet, although there have been some extensions.
It was started by NICT in 2008.
"""}

meta['eng'] = {'id':'ntumc', 
              'label':'Princeton WordNet',
              'lg':'en',
              'email':'wordnet@gmail.com',
              'license':'wordnet',
              'version':'3.0',
              'citation':'Cite me',
              'url':'URL',
               'conf':'1.0',
               'description':"An enhanced English wordnet, forked from Princeton WordNet 3.0."
   }

meta['ces'] = {'id':'cswn', 
              'label':'Czech WordNet',
              'lg':'cs',
              'email':'wordnet@gmail.com',
              'license':'wordnet',
              'version':'3.0',
              'citation':'Cite me',
              'url':'URL',
               'conf':'1.0',
               'description':"An enhanced Czech wordnet, forked from Masarych's WordNet."
   }


meta['cmn'] = {'id':'cow', 
              'label':'Chinese Open Wordnet',
              'lg':'cmn-Hans',
              'email':'bond@ieee.org',
              'license':'wordnet',
              'version':'1.0',
              'citation':'Shan Wang and Francis Bond (2013) Building the Chinese Wordnet (COW): Starting from Core Synsets. In Proceedings of the 11th Workshop on Asian Language Resources: ALR-2013 a Workshop of The 6th International Joint Conference on Natural Language Processing (IJCNLP-6). Nagoya. pp.10-18.',
              'url':'http://compling.hss.ntu.edu.sg/cow/',
               'conf':'1.0',
               'description':"""We are creating a large scale, freely available, semantic dictionary of Mandarin Chinese: the Chinese Open Wordnet, inspired by the Princeton WordNet and the Global WordNet Grid.

As well as being searchable online, the data from this project is available to download. If you are interested in joining in the construction, or have any questions, please contact us."""
   }

meta['ind'] = { 'id':'bhsind', 
              'label':'Bahasa Wordnet Indonesia',
              'lg':'id',
              'email':'wn-msa-devel@lists.sourceforge.net',
              'license':'https://opensource.org/licenses/MIT/',
              'version':'1.1',
              'citation':'Francis Bond, Lian Tze Lim, Enya Kong Tang and Hammam Riza (2014)  The combined Wordnet Bahasa, NUSA: Linguistic studies of languages in and around Indonesia 57: pp 83–10',
              'url':'http://wn-msa.sourceforge.net/',
                'conf':'1.0',
                'description':'A wordnet for the Indonesian Language'
   }

meta['isl'] = { 'id':'icewn', 
              'label':'IceWordNet',
              'lg':'is',
              'email':'None available',
              'license':'https://creativecommons.org/licenses/by/3.0/',  #CC BY 3.0
              'version':'1.0',
              'citation':'None available',
              'url':'http://www.malfong.is/index.php?lang=en&pg=icewordnet',
              'conf':'1.0',
              'description':"""
IceWordNet is based on Princeton Core WordNet.

The file core-isl.txt has the same format as core-wordnet.txt which can be downloaded from http://wordnetcode.princeton.edu/standoff-files/core-wordnet.txt.

Core WordNet is a list of approximately 5000 of the most common words from the Princeton list. The Icelandic wordnet, IceWordNet, contains Icelandic translations of the words in the core list in addition to the Icelandic synonyms. For now, only synonyms are given and other relations are not shown.

The Princeton Core WordNet list was downloaded from the Internet. Then the English words were translated into Icelandic and finally the synonyms of the Icelandic words were listed with the help from the Icelandic Thesaurus (Svavar Sigmundsson 1985) and the web site snara.is. The work was carried out by Kristín M. Jóhannsdóttir.

Converted to LMF for the OMW by Francis Bond.
"""
   }
meta['nciwn'] = {'id':'nciwn', 
                 'label':'NCI–Thesaurus-based WN',
             'lg':'en',
             'email':'bond@ieee.org',
             'license':'CC BY',
             'version':'0.1',
             'citation':'',
             'url':'',
             'conf':'1.0',
             'description':'''This is an experimental wordnet based on the National Institue of Cancer Thesaurus <https://ncit.nci.nih.gov/ncitbrowser/>.

The NCI Thesaurus (NCIt) provides reference terminology for many NCI and other systems. It covers vocabulary for clinical care, translational and basic research, and public information and administrative activities. 

This wordnet is based on the thesaurus, changed so as to make it easier to link with wordnets and with some links to the Collaborative Interlingual Index.

It is based on version 17.02d (release date 2016-02-27).

This is an unstable testing release.  
             '''}



meta['x'] = {'id':'', 
             'label':'',
             'lg':'',
             'email':'',
             'license':'',
             'version':'',
             'citation':'',
             'url':'',
             'conf':'1.0',
             'description':''}


