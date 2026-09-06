import pathlib,sys,tempfile
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from records import lines
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d)/'sample.txt';p.write_text('a\n\n');assert lines(p)==['a']
print('validated')
