Highly customisable terminal cellular automaton visualiser, written in python, with a range of features including auto-scaling to terminal, custom seeds, custom rule definition, and custom visualisations (including colour by age). 


<img width="2662" height="1057" alt="SCR-20260223-rise" src="https://github.com/user-attachments/assets/3da6c2c9-3893-4e1b-9ed1-649eaf11ff89" />




**Install:**

Homebrew:

```
brew tap BitPeppr/formulae
brew install cautom
```

Pip:

```
pip install --upgrade pip
pip install cautom
```





**Usage:**

```
usage: cautom [-h] [--seed SEED] [--prob PROB] [--infinite]
              [--customrules CUSTOMRULES] [--customcolors CUSTOMCOLORS]
              [--randomcolors] [--age]

A visual cellular automaton simulator

options:
  -h, --help            show this help message and exit
  --seed SEED           Specify seed
  --prob PROB           Specify the probability that each cell is alive (from 1-100)
  --infinite            Generate new seed on complete death
  --customrules CUSTOMRULES
                        Specify custom game rules (B##/S##)
  --customcolors CUSTOMCOLORS
                        Specify custom colours for living and dead cells
  --randomcolors        Make alive cells generate with random colors
  --age                 Darken colours of cells as they get older
```
