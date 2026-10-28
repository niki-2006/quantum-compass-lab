import sys
sys.stdout.reconfigure(encoding='utf-8')
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ns = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
}

def analyze_shapes(pptx_file):
    zf = zipfile.ZipFile(pptx_file)
    slide_xml = zf.read('ppt/slides/slide1.xml')
    root = ET.fromstring(slide_xml)
    spTree = root.find('.//p:spTree', ns)
    
    shapes_info = []
    for elem in spTree:
        tag = elem.tag.split('}')[-1]
        cNvPr = elem.find('.//p:cNvPr', ns)
        name = cNvPr.attrib.get('name', '') if cNvPr is not None else ''
        sid = cNvPr.attrib.get('id', '') if cNvPr is not None else ''
        
        xfrm = elem.find('.//a:xfrm', ns)
        off = xfrm.find('a:off', ns) if xfrm is not None else None
        ext = xfrm.find('a:ext', ns) if xfrm is not None else None
        x = int(off.attrib['x'])/914400 if off is not None else 0
        y = int(off.attrib['y'])/914400 if off is not None else 0
        w = int(ext.attrib['cx'])/914400 if ext is not None else 0
        h = int(ext.attrib['cy'])/914400 if ext is not None else 0
        
        txBody = elem.find('.//p:txBody', ns)
        runs = []
        if txBody is not None:
            for p in txBody.findall('a:p', ns):
                p_runs = []
                for r in p.findall('.//a:r', ns):
                    t = r.find('a:t', ns)
                    rPr = r.find('a:rPr', ns)
                    sz = int(rPr.attrib.get('sz', 0))/100 if rPr is not None else 0
                    bold = rPr.attrib.get('b', '0') == '1' if rPr is not None else False
                    txt = t.text if t is not None else ''
                    p_runs.append((txt, sz, bold))
                runs.append(p_runs)
                
        shapes_info.append({
            'tag': tag,
            'id': sid,
            'name': name,
            'rect': (x, y, w, h),
            'runs': runs
        })
    return shapes_info

print("=== Analyzing poster_output/Quantum_Compass_Lab_Poster_v3.pptx ===")
s_v3 = analyze_shapes('poster_output/Quantum_Compass_Lab_Poster_v3.pptx')
for s in s_v3:
    if s['runs']:
        flat_txt = ' | '.join([''.join([r[0] for r in p]) for p in s['runs'] if p])
        if flat_txt:
            print(f"[{s['name']}] ({s['rect'][0]:.2f}, {s['rect'][1]:.2f}, {s['rect'][2]:.2f}x{s['rect'][3]:.2f}) -> {flat_txt[:100]}")
