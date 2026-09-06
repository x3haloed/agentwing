def location(text):
 if text.startswith('/') or '\\' in text:raise ValueError('path')
 parts=text.split('/')
 if '..' in parts:raise ValueError('parent')
 value='/'.join(p for p in parts if p not in ('','.'))
 if not value:raise ValueError('empty')
 return 'stored/'+value
