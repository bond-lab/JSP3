#scp -p compling.upol.cz:/var/www/ntumc/db/eng.db .
#scp -p compling.upol.cz:/var/www/ntumc/db/ces.db .
#scp -p compling.upol.cz:/var/www/ntumc/db/wn-ntumc.db .

python ntumc2json.py -d 440 -n spec --corpus ./eng.db
python ntumc2json.py -d 440 -n spec -a "qwen3:14b" --corpus sample/eng.db
python ntumc2json.py -d 501 -n "twwtn-cs" --corpus ./ces.db
python ntumc2json.py -d 501 -n "twwtn-en" --corpus ./eng.db


python db2lmf.py eng wn-ntumc.db omw > wn-ntumc-eng.xml
python -m wn validate  wn-ntumc-eng.xml > poi.eng

python db2lmf.py ces wn-ntumc.db omw > wn-ntumc-ces.xml
python -m wn validate  wn-ntumc-ces.xml > poi.ces

xz wn-ntumc-ces.xml
xz wn-ntumc-eng.xml
