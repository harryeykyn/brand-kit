#!/usr/bin/env python3
"""Organise locally staged brand assets. No network calls or global configuration."""
import argparse
import datetime as dt
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import urllib.parse
import zipfile
import xml.etree.ElementTree as ET

FOLDERS = ['01-Brand-Guidelines','02-Logos','03-Fonts','04-Colors','05-Copy',
           '06-Products','07-Collections','08-Campaigns','09-Lifestyle',
           '10-Icons','11-Video','12-Other','13-Sources']
ROLES = {'logo':'02-Logos','font':'03-Fonts','font-license':'03-Fonts',
         'product':'06-Products','collection':'07-Collections','campaign':'08-Campaigns',
         'lifestyle':'09-Lifestyle','icon':'10-Icons','video':'11-Video','other':'12-Other'}
IMAGE_EXT = {'.png','.jpg','.jpeg','.webp','.gif','.tif','.tiff','.avif','.svg'}

def clean(value):
    s = re.sub(r'[^\w .-]+', '-', str(value), flags=re.UNICODE)
    s = re.sub(r'\s+', ' ', s).strip(' .-')[:70].rstrip(' .') or 'unnamed'
    if s.upper().split('.')[0] in {'CON','PRN','AUX','NUL',*(f'COM{i}' for i in range(1,10)),*(f'LPT{i}' for i in range(1,10))}:
        s = '_' + s
    return s

def named(item):
    suffix = hashlib.sha256(str(item['id']).encode()).hexdigest()[:8]
    return clean(item.get('name',item['id'])) + '--' + suffix

def weburl(url):
    p = urllib.parse.urlsplit(str(url))
    if p.scheme not in ('https','http') or not p.hostname or p.username or p.password:
        raise ValueError('Expected a public HTTP(S) source URL without credentials')
    return str(url)

def dump(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def contained(base, relative):
    rel = Path(relative)
    if rel.is_absolute():
        raise ValueError('Asset local_path must be relative to the manifest folder')
    p = (base/rel).resolve()
    if not p.is_relative_to(base.resolve()):
        raise ValueError('Asset path escapes staging folder')
    if not p.is_file():
        raise ValueError('Missing local file')
    return p

def inspect(path):
    with path.open('rb') as f:
        head=f.read(8192)
    ext=path.suffix.lower()
    if not head:
        raise ValueError('Empty download')
    low=head.lstrip().lower()
    if b'<!doctype html' in low or b'<html' in low[:1000]:
        raise ValueError('HTML response saved as an asset')
    checks={'.png':head.startswith(b'\x89PNG\r\n\x1a\n'),
            '.jpg':head.startswith(b'\xff\xd8\xff'),'.jpeg':head.startswith(b'\xff\xd8\xff'),
            '.gif':head[:6] in (b'GIF87a',b'GIF89a'),
            '.webp':head.startswith(b'RIFF') and head[8:12]==b'WEBP',
            '.woff':head[:4]==b'wOFF','.woff2':head[:4]==b'wOF2',
            '.ttf':head[:4] in (b'\x00\x01\x00\x00',b'true'),'.otf':head[:4]==b'OTTO',
            '.mp4':head[4:8]==b'ftyp','.mov':head[4:8] in (b'ftyp',b'moov',b'mdat',b'wide'),
            '.webm':head[:4]==b'\x1aE\xdf\xa3', '.pdf':head.startswith(b'%PDF-'),
            '.avif':head[4:8]==b'ftyp' and b'avif' in head[:64],
            '.tif':head[:4] in (b'II*\x00',b'MM\x00*'),'.tiff':head[:4] in (b'II*\x00',b'MM\x00*')}
    if ext=='.svg':
        if b'<!doctype' in low or b'<!entity' in low:
            raise ValueError('SVG contains a document type/entity; review before including')
        root=ET.parse(path).getroot()
        if root.tag.split('}')[-1]!='svg':
            raise ValueError('Not an SVG document')
    elif ext in checks:
        if not checks[ext]:
            raise ValueError('File signature does not match extension')
    elif ext not in {'.txt','.md','.json','.ai','.eps'}:
        raise ValueError('Unsupported asset extension; inspect and extend intentionally')
    if ext=='.json':
        json.loads(path.read_text(encoding='utf-8'))
    if ext in {'.txt','.md'}:
        path.read_text(encoding='utf-8')
    if ext in {'.ai','.eps'} and not head.startswith((b'%PDF-',b'%!PS')):
        raise ValueError('Invalid design-file header')
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def keyed(items, label):
    result={}
    for i in items:
        key=i.get('id')
        if not isinstance(key,str) or not key or key in result:
            raise ValueError(f'{label} IDs must be unique nonempty strings')
        result[key]=i
    return result

def organize(manifest_path, clients):
    manifest_path=Path(manifest_path).resolve();m=json.loads(manifest_path.read_text(encoding='utf-8'))
    brand=m['brand'];site=weburl(brand['url']);date=dt.date.fromisoformat(brand['captured_at']).isoformat()
    if not str(brand.get('name','')).strip():raise ValueError('Brand name is required')
    products=keyed(m.get('products',[]),'Product');collections=keyed(m.get('collections',[]),'Collection')
    assets=keyed(m.get('assets',[]),'Asset')
    for coll in collections.values():
        unknown=set(coll.get('product_ids',[]))-products.keys()
        if unknown:raise ValueError(f'Unknown collection product IDs: {unknown}')
    for a in assets.values():
        weburl(a['url'])
        if a.get('kind') not in ROLES:raise ValueError('Unsupported asset kind')
        if set(a.get('product_ids',[]))-products.keys():raise ValueError('Unknown asset product IDs')
        if set(a.get('collection_ids',[]))-collections.keys():raise ValueError('Unknown asset collection IDs')
    client=Path(clients).resolve()/(clean(brand['name'])+'--'+clean(urllib.parse.urlsplit(site).hostname))
    client.mkdir(parents=True,exist_ok=True)
    for i in range(1,10000):
        run=client/(date if i==1 else f'{date}-{i:02d}')
        try:run.mkdir();break
        except FileExistsError:continue
    else:raise ValueError('Too many dated runs')
    for folder in FOLDERS:(run/folder).mkdir()
    pf={pid:Path('06-Products')/named(p) for pid,p in products.items()}
    cf={cid:Path('07-Collections')/named(co) for cid,co in collections.items()}
    for pid,p in products.items():dump(run/pf[pid]/'product.json',p)
    for cid,co in collections.items():dump(run/cf[cid]/'collection.json',co)
    success=[];fail=[];stored={}
    for aid,a in assets.items():
        try:
            source=contained(manifest_path.parent,a['local_path']);sha=inspect(source)
            destinations=[]
            if a['kind']=='product':
                destinations=[pf[p] for p in a.get('product_ids',[])] or [Path('06-Products')/'Unmapped']
            elif a['kind']=='collection':
                destinations=[cf[co]/'Artwork' for co in a.get('collection_ids',[])] or [Path('07-Collections')/'Unmapped']
            elif a['kind']=='campaign':
                destinations=[Path('08-Campaigns')/clean(a.get('campaign','Unmapped'))]
            else:destinations=[Path(ROLES[a['kind']])]
            for cid,co in collections.items():
                for pid in a.get('product_ids',[]):
                    if pid in co.get('product_ids',[]):destinations.append(cf[cid]/'Products'/named(products[pid]))
            paths=[]
            for dest in dict.fromkeys(destinations):
                key=(str(dest),sha)
                if key not in stored:
                    original=Path(a.get('filename') or source.name)
                    name=clean(original.stem)+'--'+sha[:12]+source.suffix.lower()
                    target=run/dest/name;target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(source,target);stored[key]=target.relative_to(run).as_posix()
                paths.append(stored[key])
            record={k:v for k,v in a.items() if k!='local_path'}
            record.update(sha256=sha,bytes=source.stat().st_size,paths=paths)
            success.append(record)
        except (ValueError,OSError,ET.ParseError,UnicodeError) as e:
            fail.append({'id':aid,'url':a['url'],'reason':str(e)})
    output={k:v for k,v in m.items() if k!='assets'};output['assets']=success
    dump(run/'13-Sources/manifest.json',output)
    dump(run/'13-Sources/coverage.json',{'research':m.get('coverage',{}),'asset_records':len(assets),
         'saved_records':len(success),'unique_files':len({a['sha256'] for a in success}),
         'failed_assets':fail,'missing':m.get('missing',[]),'conflicts':m.get('conflicts',[])})
    dump(run/'13-Sources/source-pages.json',m.get('pages',[]))
    dump(run/'04-Colors/palette.json',m.get('colors',[]));dump(run/'03-Fonts/font-reference.json',m.get('fonts',[]))
    dump(run/'05-Copy/page-copy-reference.json',m.get('pages',[]))
    (run/'README.txt').write_text(f"{brand['name']} - brand reference\nCaptured: {date}\nSource: {site}\nOpen index.html for the asset directory.\nRead 13-Sources/coverage.json for missing items and conflicts.\nPDF and editable guidelines are under 01-Brand-Guidelines once rendered.\nAsset ownership/licensing stays with the respective rights holders.\n",encoding='utf-8')
    cards=[]
    for a in success:
        path=a['paths'][0];href=urllib.parse.quote(path);ext=Path(path).suffix.lower()
        preview=f'<img loading="lazy" src="{href}" alt="{html.escape(a["id"],quote=True)}">' if ext in IMAGE_EXT else '<span class="file">'+html.escape(ext.upper())+'</span>'
        search=' '.join([a['id'],a.get('filename',''),a.get('kind',''),*a.get('product_ids',[]),*a.get('collection_ids',[])])
        search+=' '+' '.join(products[p].get('name',p) for p in a.get('product_ids',[]))
        search+=' '+' '.join(co.get('name',cid) for cid,co in collections.items() if set(co.get('product_ids',[]))&set(a.get('product_ids',[])) or cid in a.get('collection_ids',[]))
        cards.append(f'<article data-search="{html.escape(search.lower(),quote=True)}"><a href="{href}">{preview}</a><b>{html.escape(a["id"])}</b><p>{html.escape(a.get("filename",Path(path).name))}</p><small>{html.escape(a["kind"])} / {a["bytes"]:,} bytes</small><p><a href="{html.escape(a["url"],quote=True)}">Source</a></p></article>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Brand asset library</title><style>body{font:15px system-ui,sans-serif;margin:32px;background:#f5f5f5;color:#181818}input{font:inherit;padding:14px;width:min(85%,700px);margin-bottom:25px}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:18px}article{background:white;padding:14px;overflow-wrap:anywhere}img,.file{width:100%;height:180px;object-fit:contain;background:#eee}.file{display:grid;place-items:center}a{color:#222}small{color:#555}</style>'''
    page+='<h1>'+html.escape(brand['name'])+' / Asset library</h1><p>'+date+' · '+str(len(success))+' asset records. See coverage.json for limits.</p><input id="search" aria-label="Search assets" placeholder="Search products, collections, filenames or IDs"><main>'+''.join(cards)+'</main>'
    page+='''<script>document.querySelector('#search').addEventListener('input',e=>{const q=e.target.value.toLowerCase();document.querySelectorAll('article').forEach(a=>a.hidden=!a.dataset.search.includes(q))})</script></html>'''
    (run/'index.html').write_text(page,encoding='utf-8')
    print(json.dumps({'run':str(run),'saved':len(success),'failures':fail},ensure_ascii=False))
    return run

def package(run):
    run=Path(run).resolve()
    if not (run/'13-Sources/manifest.json').is_file():raise ValueError('Not an organised client run')
    required=[run/'01-Brand-Guidelines/Brand-Guidelines.pdf',run/'01-Brand-Guidelines/Brand-Reference.md']
    if not all(p.is_file() and p.stat().st_size for p in required):
        raise ValueError('Render guidelines before packaging; do not label an incomplete kit complete')
    target=run.parent/(run.name+'-Brand-Kit.zip')
    if target.exists():raise ValueError('Archive exists; preserve it or choose a new run')
    files=[]
    for folder in FOLDERS:
        for p in (run/folder).rglob('*'):
            if p.is_symlink():raise ValueError('Symlinks must not be packaged')
            if p.is_file():
                if p.name.startswith('.') or any(x.startswith('.') for x in p.relative_to(run).parts):continue
                files.append(p)
    files.extend(run/n for n in ('README.txt','index.html'))
    try:
        with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED) as z:
            for p in files:z.write(p,run.parent.name+'/'+run.name+'/'+p.relative_to(run).as_posix())
        with zipfile.ZipFile(target) as z:
            if z.testzip():raise ValueError('Archive integrity check failed')
    except Exception:
        if target.exists():target.unlink()
        raise
    print(json.dumps({'zip':str(target),'files':len(files),'bytes':target.stat().st_size}))
    return target

def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='command',required=True)
    o=s.add_parser('organize');o.add_argument('--manifest',required=True);o.add_argument('--clients',required=True)
    z=s.add_parser('package');z.add_argument('--run',required=True)
    a=p.parse_args()
    try:
        if a.command=='organize':organize(a.manifest,a.clients)
        else:package(a.run)
    except (ValueError,KeyError,TypeError,OSError) as e:p.exit(1,f'Error: {e}\n')
if __name__=='__main__':main()
