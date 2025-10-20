#scp -p compling.upol.cz:/var/www/ntumc/db/eng.db .
#scp -p compling.upol.cz:/var/www/ntumc/db/wn-ntumc.db .

python ntumc2json.py -d 440 -n spec --corpus ./eng.db
python ntumc2json.py -d 440 -n spec -a "qwen3:14b" --corpus sample/eng.db


python db2lmf.py eng wn-ntumc.db omw > wn-ntu-eng.xml
python -m wn validate  wn-ntu-eng.xml > poi
