from pathlib import Path
import concurrent.futures,urllib.request,json,hashlib,os
os.environ.pop('SSLKEYLOGFILE',None)
P=Path(__file__).resolve().parents[1];dest=P.parent/'tmp/p01-datasheets';dest.mkdir(parents=True,exist_ok=True)
urls={
'mos':'https://www.vishay.com/docs/68633/sup53p06-20.pdf',
'diode':'https://www.st.com/resource/en/datasheet/stps20100.pdf',
'lm2936':'https://www.ti.com/lit/ds/symlink/lm2936.pdf',
'tl431':'https://www.ti.com/lit/ds/symlink/tl431.pdf',
'lm2903':'https://www.ti.com/lit/ds/symlink/lm2903.pdf',
'supervisor':'https://ww1.microchip.com/downloads/en/devicedoc/11184d.pdf',
'npn':'https://www.onsemi.com/download/data-sheet/pdf/2n5550-d.pdf',
'pnp':'https://www.onsemi.com/download/data-sheet/pdf/2n5401-d.pdf',
'pr02':'https://www.vishay.com/docs/28729/pr010203.pdf',
'mfr':'https://www.yageogroup.com/content/Resource%20Library/Datasheet/YAGEO-MFR_DATASHEET.pdf',
'film':'https://product.tdk.com/info/en/documents/data_sheet/20/20/db/fc_2009/B32520_529_w.pdf',
'electrolytic':'https://industrial.panasonic.com/cdbs/www-data/pdf/RDF0000/ABA0000C1181.pdf',
'trim':'https://www.bourns.com/docs/product-datasheets/3296.pdf',
'15kpa':'https://www.littelfuse.com/assetdocs/tvs-diodes-15kpa-datasheet?assetguid=5152edba-6eab-4c4a-9bef-2c97b144328e',
'5kp':'https://www.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_5kp_datasheet.pdf.pdf',
'1_5ke':'https://www.vishay.com/docs/88301/15ke.pdf',
'zener':'https://www.vishay.com/docs/85604/bzx55.pdf',
'4148':'https://www.vishay.com/docs/81857/1n4148.pdf',
'connector':'https://www.phoenixcontact.com/en-us/products/pcb-header-mstb-25-3-g-508-1759020?type=pdf',
}
def fetch(kv):
 k,url=kv
 try:
  f=dest/(k+'.pdf')
  if not f.exists():
   with urllib.request.urlopen(url,timeout=35) as response:data=response.read()
   assert data.startswith(b'%PDF'),data[:60];f.write_bytes(data)
  from pypdf import PdfReader
  d=PdfReader(f);(dest/(k+'.txt')).write_text('\n'.join(p.extract_text() for p in d.pages),encoding='utf-8')
  return {'id':k,'url':url,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'pages':len(d.pages),'status':'read'}
 except Exception as e:return {'id':k,'url':url,'status':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:rows=list(ex.map(fetch,urls.items()))
(P/'reference/sources.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
for x in rows:print(x['id'],x['status'])
