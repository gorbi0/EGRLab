from pathlib import Path
import urllib.request,os,hashlib,json
from pypdf import PdfReader
P=Path(__file__).resolve().parent
os.environ.pop('SSLKEYLOGFILE',None)
urls={
 'DHO800_UserGuide':'https://beyondmeasure.rigoltech.com/acton/attachment/1579/f-cfe231a8-28af-4455-a64f-60017da44177/1/-/-/-/-/DHO800_UserGuide_EN.pdf',
 'DHO800_DataSheet':'https://beyondmeasure.rigoltech.com/acton/attachment/1579/f-11201b15-e890-4a0d-ba67-cbbc4c525562/1/-/-/-/-/DHO800_DataSheet_EN.pdf'}
(P/'zrodla').mkdir(exist_ok=True)
for name,url in urls.items():
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=40) as r:data=r.read()
  assert data[:4]==b'%PDF'
  f=P/'zrodla'/(name+'.pdf');f.write_bytes(data)
  reader=PdfReader(f);s='\n\n'.join(f'=== PDF page {i+1} ===\n'+(page.extract_text() or '') for i,page in enumerate(reader.pages))
  f.with_suffix('.txt').write_text(s,encoding='utf-8')
  print(name,len(reader.pages),'pages',hashlib.sha256(data).hexdigest())
 except Exception as e:print(name,type(e).__name__,str(e))
