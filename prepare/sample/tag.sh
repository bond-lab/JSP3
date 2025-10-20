#!/bin/bash

# Check if the virtual environment directory exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install the requirements if not already installed
pip install -r /home/bond/git/NTUMC/requirements.txt

# Run
time python /home/bond/git/NTUMC/ntumc/taggers/tag-llm.py 10337:10490 eng.db wn-ntumc.db --verbose -m qwen3:14b  > spec-dev-qwen3:14b   2>&1

time python /home/bond/git/NTUMC/ntumc/taggers/tag-llm.py 10000:10336 eng.db wn-ntumc.db --verbose -m qwen3:14b  > spec-train-qwen3:14b   2>&1

time python /home/bond/git/NTUMC/ntumc/taggers/tag-llm.py 10491:10598 eng.db wn-ntumc.db --verbose -m qwen3:14b  > spec-test-qwen3:14b   2>&1



#time python /home/bond/ntumc/taggers/tag-llm.py 10337:10338 eng.db wn-ntumc.db --verbose -m qwen3:14b  > dev-qwen3:14b   2>&1
