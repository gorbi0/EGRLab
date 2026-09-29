from pathlib import Path
import os, urllib.request, hashlib, json
from pypdf import PdfReader
P=Path(__file__).resolve().parents[1]
os.environ.pop('SSLKEYLOGFILE',None)
urls={
'WIMA_MKS2':'https://www.tme.eu/Document/a1d7ff07b330f8f08de986bd168d8c92/WIMA_MKS_2.pdf',
'Fischer_SK129_STS':'https://www.triopak.fi/files/product/Fisher%20Elektronik/SK129-25STS.pdf',
'TRACO_TSR2':'https://www.tracopower.com/products/tsr2.pdf',
}
records=[]
for name,url in urls.items():
    f=P/'reference'/(name+'.pdf')
    if not f.exists():
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=40) as r: b=r.read()
        assert b.startswith(b'%PDF'),name
        f.write_bytes(b)
    pdf=PdfReader(f)
    f.with_suffix('.txt').write_text('\n\n'.join(f'PDF page {i+1}\n'+(p.extract_text() or '') for i,p in enumerate(pdf.pages)),encoding='utf-8')
    records.append({'file':f.name,'url':url,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(P/'reference/r3-downloaded.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print('Fetched',len(records),'manufacturer documents.')
