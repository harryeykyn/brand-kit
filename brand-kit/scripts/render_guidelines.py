#!/usr/bin/env python3
"""Render agent-authored findings and the organised asset index to PDF and Markdown."""
import argparse
import html
import io
import json
from pathlib import Path
import re
import sys
import urllib.parse


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',required=True);p.add_argument('--report',required=True)
    p.add_argument('--font',help='Optional Unicode TTF with glyphs for the report language')
    a=p.parse_args();run=Path(a.run).resolve()
    try:
        from PIL import Image as PILImage
        from reportlab import rl_config
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,Image,KeepTogether,Flowable
    except ImportError as e:
        p.exit(1,'PDF dependencies missing. Use a workspace environment with reportlab and Pillow. '+str(e)+'\n')
    rl_config.useA85=0
    if not hasattr(rl_config,'autoGenerateTTFMissingTTFName'):
        rl_config.autoGenerateTTFMissingTTFName=getattr(rl_config,'autoGenerateMissingTTFName',True)
    m=json.loads((run/'13-Sources/manifest.json').read_text(encoding='utf-8'))
    report=json.loads(Path(a.report).read_text(encoding='utf-8'))
    sections=report.get('sections',[])
    if not sections:p.exit(1,'Report must contain agent-authored sections.\n')
    font='Helvetica';bold='Helvetica-Bold'
    candidates=[a.font] if a.font else ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/Library/Fonts/Arial Unicode.ttf','C:/Windows/Fonts/arial.ttf']
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            pdfmetrics.registerFont(TTFont('KitFont',candidate));font=bold='KitFont';break
    if a.font and font=='Helvetica':p.exit(1,'Requested font not found.\n')
    full=json.dumps([m['brand'],sections,m.get('products',[]),m.get('colors',[])],ensure_ascii=False)
    if font=='Helvetica':
        try:full.encode('cp1252')
        except UnicodeEncodeError:p.exit(1,'This report needs a Unicode font. Supply --font with a suitable TTF.\n')
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle('KitBody',fontName=font,fontSize=10,leading=14,spaceAfter=9))
    styles.add(ParagraphStyle('KitSmall',fontName=font,fontSize=7,leading=9,spaceAfter=5,wordWrap='CJK'))
    styles.add(ParagraphStyle('KitTitle',fontName=bold,fontSize=29,leading=35,spaceAfter=20))
    styles.add(ParagraphStyle('KitHeading',fontName=bold,fontSize=19,leading=25,spaceAfter=14,keepWithNext=True))
    styles.add(ParagraphStyle('KitSub',fontName=bold,fontSize=11,leading=15,spaceAfter=9,keepWithNext=True))
    def para(text,style='KitBody'):return Paragraph(html.escape(str(text)),styles[style])
    def source(url,label=None):
        u=urllib.parse.urlsplit(str(url))
        if u.scheme not in ('https','http') or not u.hostname:raise ValueError('Invalid report source URL')
        return Paragraph('<link href="'+html.escape(str(url),quote=True)+'" color="#555555">'+html.escape(label or str(url))+'</link>',styles['KitSmall'])
    def grid(rows,widths):
        data=[[para(v,'KitSmall') for v in row] for row in rows]
        t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eeeeee')),('LINEBELOW',(0,0),(-1,-1),.3,colors.HexColor('#dddddd')),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
        return t
    issues=[];images={x['id']:x for x in m['assets']};buffers=[]
    def image(asset,maxw=475,maxh=250):
        path=(run/asset['paths'][0]).resolve()
        if not path.is_relative_to(run):raise ValueError('Image path escapes run')
        if path.suffix.lower()=='.svg':return None
        try:
            im=PILImage.open(path);im.load();im.thumbnail((int(maxw*2),int(maxh*2)))
            stream=io.BytesIO();im.save(stream,format='PNG');stream.seek(0);buffers.append(stream)
            w,h=im.size;scale=min(maxw/w,maxh/h)
            return Image(stream,width=w*scale,height=h*scale)
        except Exception as e:
            issues.append({'id':asset['id'],'issue':'Image preview unavailable: '+str(e)})
            return None
    story=[];md=[];brand=m['brand'];title=report.get('title',brand['name']+' | Brand reference')
    story+=[Spacer(1,50),para(brand['name'],'KitTitle'),para('Brand reference & working guidelines','KitHeading'),para('Captured '+brand['captured_at']),source(brand['url']),Spacer(1,22)]
    cover=report.get('cover_asset_id')
    if cover:
        if cover not in images:raise ValueError('Unknown cover asset ID')
        im=image(images[cover])
        if im:story += [im,Spacer(1,20)]
    story+=[para('Independent research from available sources. Inferred guidance is not an official brand standard.'),PageBreak()]
    md += ['# '+title,'','Captured: '+brand['captured_at'],'Source: '+brand['url'],'']
    for sec in sections:
        heading=sec['title'];evidence=sec.get('evidence','mixed; see source notes')
        story += [para(heading,'KitHeading'),para('Evidence: '+evidence,'KitSmall')]
        md += ['## '+heading,'','Evidence: '+evidence,'']
        for body in sec.get('paragraphs',[]):story.append(para(body));md += [body,'']
        if sec.get('rows'):
            columns=len(sec['rows'][0])
            if columns>4 or any(len(row)!=columns for row in sec['rows']):raise ValueError('Use rectangular tables with 1-4 columns')
            story += [grid(sec['rows'],[475/columns]*columns),Spacer(1,16)]
            md += [' | '.join(str(v) for v in row) for row in sec['rows']];md.append('')
        for aid in sec.get('asset_ids',[]):
            if aid not in images:raise ValueError('Unknown section asset ID: '+aid)
            im=image(images[aid],475,235)
            if im:story += [im,para(aid+' - '+images[aid].get('filename',''),'KitSmall'),source(images[aid]['url'])]
            md += [f'Asset: {aid} - {images[aid]["url"]}','']
        for u in sec.get('sources',[]):story.append(source(u));md += [u,'']
        story.append(PageBreak())
    palette=m.get('colors',[])
    if palette:
        class Swatch(Flowable):
            def __init__(self,hx):super().__init__();self.hx=hx;self.width=48;self.height=22
            def draw(self):self.canv.setFillColor(colors.HexColor(self.hx));self.canv.rect(0,0,48,22,stroke=0,fill=1)
        story.append(para('Palette reference','KitHeading'));md += ['## Palette reference','']
        for col in palette:
            if not re.fullmatch(r'#[0-9A-Fa-f]{6}',col['hex']):raise ValueError('Colours require six-digit HEX values')
            desc=f"{col['hex']} | {col['name']} | {col.get('role','')} | {col.get('evidence','unverified')}"
            story.append(KeepTogether([Swatch(col['hex']),Spacer(1,5),para(desc),source(col['source_url'])]))
            md += [desc,col['source_url'],'']
        story.append(PageBreak())
    for heading,key in [('Product directory','products'),('Collection directory','collections')]:
        if not m.get(key):continue
        story.append(para(heading,'KitHeading'));md += ['## '+heading,'']
        for item in m[key]:
            story.append(para(item['name'],'KitSub'));md += ['### '+item['name'],'']
            if item.get('summary'):story.append(para(item['summary']));md += [item['summary'],'']
            if item.get('url'):story.append(source(item['url']));md += [item['url'],'']
            if key=='collections':
                desc='Product IDs: '+(', '.join(item.get('product_ids',[])) or 'No verified membership recorded')
                story.append(para(desc,'KitSmall'));md += [desc,'']
        story.append(PageBreak())
    story.append(para('Coverage and unresolved items','KitHeading'))
    coverage=json.loads((run/'13-Sources/coverage.json').read_text(encoding='utf-8'))
    counts=f"Saved asset records: {coverage['saved_records']}. Unique source files: {coverage['unique_files']}. Failed downloads: {len(coverage['failed_assets'])}."
    story.append(para(counts));md += ['## Coverage and unresolved items','',counts,'']
    for title,key in [('Research coverage','research'),('Missing items','missing'),('Conflicts','conflicts'),('Failed assets','failed_assets')]:
        val=coverage.get(key)
        if val:
            story.append(para(title,'KitSub'))
            items=val if isinstance(val,list) else [val]
            for item in items:
                txt=json.dumps(item,ensure_ascii=False) if not isinstance(item,str) else item
                story.append(para(txt,'KitSmall'));md += [title+': '+txt,'']
    visible=[x for x in m['assets'] if Path(x['paths'][0]).suffix.lower() in {'.png','.jpg','.jpeg','.webp','.gif','.tif','.tiff','.avif'}]
    if visible:
        story.append(PageBreak());story.append(para('Visual asset directory','KitHeading'))
        story.append(para('Original files and source links are in index.html. Thumbnails are previews, not production masters.'))
        cells=[]
        for asset in visible:
            im=image(asset,140,105)
            if not im:continue
            cells.append([im,para(asset['id'],'KitSmall'),source(asset['url'],'Original source')])
        for off in range(0,len(cells),12):
            batch=cells[off:off+12];rows=[batch[i:i+3] for i in range(0,len(batch),3)]
            for row in rows:
                while len(row)<3:row.append('')
            t=Table(rows,colWidths=[158]*3,hAlign='LEFT');t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),12)]))
            story.append(t)
            if off+12<len(cells):story.append(PageBreak())
    out=run/'01-Brand-Guidelines';out.mkdir(exist_ok=True)
    def footer(canvas,doc):
        canvas.saveState();canvas.setFont(font,7);canvas.setFillColor(colors.HexColor('#777777'))
        canvas.drawString(42,25,'Independent brand reference / '+brand['captured_at']);canvas.drawRightString(553,25,str(doc.page));canvas.restoreState()
    dest=out/'Brand-Guidelines.pdf'
    SimpleDocTemplate(str(dest),pagesize=(595,842),rightMargin=42,leftMargin=42,topMargin=46,bottomMargin=48,title=title,author='Brand Kit').build(story,onFirstPage=footer,onLaterPages=footer)
    (out/'Brand-Reference.md').write_text('\n'.join(md),encoding='utf-8')
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    coverage['render_issues']=issues
    (run/'13-Sources/coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'pdf':str(dest),'markdown':str(out/'Brand-Reference.md'),'preview_issues':issues}))
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,OSError) as e:sys.exit('Error: '+str(e))
