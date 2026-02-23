AgastyaDictionary H-3.7 — CSDE_Engine_Core JSON Pack

Place into your repo as:
./CSDE_Engine_Core/
  ├─ data/agastya/H-3.7/
  │   ├─ AgastyaDictionary_H3.7.json
  │   ├─ karma_leaf_dict.json
  │   ├─ prophecy_leaf_dict.json
  │   └─ dharma_leaf_dict.json
  └─ csde/agastya_loader.py

Quick use:
from CSDE_Engine_Core.csde.agastya_loader import read_agastya
print(read_agastya("19670421_1120_Niigata_Kamakura"))
