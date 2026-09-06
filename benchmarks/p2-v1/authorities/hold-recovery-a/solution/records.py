def lines(path):
 with open(path,encoding='utf-8-sig',newline=None) as f:
  return [line.rstrip('\r\n') for line in f if line.strip()]
