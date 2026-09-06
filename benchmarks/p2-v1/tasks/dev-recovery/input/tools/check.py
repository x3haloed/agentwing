import pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from queue_names import normalize
assert normalize('  High--Priority  ')=='high_priority'
assert normalize('Straße')=='strasse'
print('queue validation passed')
