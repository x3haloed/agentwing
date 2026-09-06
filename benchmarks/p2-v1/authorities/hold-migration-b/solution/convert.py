import configparser,json,sys
def convert(text):
 c=configparser.ConfigParser(interpolation=None);c.read_string(text);s=dict(c['server']) if c.has_section('server') else {}
 port=int(s.pop('port','8080'));timeout=int(s.pop('timeout_ms','1500'));enabled=s.pop('enabled','true').lower()
 if not 1<=port<=65535 or timeout<0 or enabled not in ('true','false','yes','no','1','0'):raise ValueError('invalid setting')
 s.update(port=port,enabled=enabled in ('true','yes','1'),timeout_seconds=timeout/1000)
 return {'server':s,'extras':{name:dict(c[name]) for name in c.sections() if name!='server'}}
if __name__=='__main__':
 with open(sys.argv[1]) as f:result=convert(f.read())
 with open(sys.argv[2],'w') as f:json.dump(result,f)
