import sys
sys.stdout.reconfigure(encoding='utf-8')
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

def inspect_pptx(pptx_path):
    zf = zipfile.ZipFile(pptx_path)
    slide_xml = zf.read('ppt/slides/slide1.xml')
    root = ET.fromstring(slide_xml)

    ns = {
        'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
        'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
        'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    }

    # Presentation dimensions
    pres_xml = zf.read('ppt/presentation.xml')
    proot = ET.fromstring(pres_xml)
    sldSz = proot.find('p:sldSz', ns)
    w_in = int(sldSz.attrib.get('cx', 0)) / 914400
    h_in = int(sldSz.attrib.get('cy', 0)) / 914400
    print(f"Presentation Dimensions: {w_in:.2f} x {h_in:.2f} inches ({w_in*25.4:.1f} x {h_in*25.4:.1f} mm)")

    # Relationships (images etc)
    rels_xml = zf.read('ppt/slides/_rels/slide1.xml.rels')
    rroot = ET.fromstring(rels_xml)
    rel_map = {}
    for rel in rroot.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
        rel_map[rel.attrib['Id']] = rel.attrib['Target']

    spTree = root.find('.//p:spTree', ns)
    print(f"Total elements in spTree: {len(spTree)}")

    for i, child in enumerate(spTree):
        tag = child.tag.split('}')[-1]
        cNvPr = child.find('.//p:cNvPr', ns)
        name = cNvPr.attrib.get('name') if cNvPr is not None else 'unknown'
        shape_id = cNvPr.attrib.get('id') if cNvPr is not None else '?'

        # text
        txBody = child.find('.//p:txBody', ns)
        paragraphs = []
        if txBody is not None:
            for p in txBody.findall('a:p', ns):
                # get all runs with formatting if any
                p_text = ''
                for r in p.findall('.//a:r', ns):
                    t = r.find('a:t', ns)
                    if t is not None and t.text:
                        p_text += t.text
                if not p_text:
                    # check simple field or fallback
                    t = p.find('.//a:t', ns)
                    if t is not None and t.text:
                        p_text += t.text
                if p_text:
                    paragraphs.append(p_text.strip())

        # bounding box
        xfrm = child.find('.//a:xfrm', ns)
        off = xfrm.find('a:off', ns) if xfrm is not None else None
        ext = xfrm.find('a:ext', ns) if xfrm is not None else None
        x = int(off.attrib['x'])/914400 if off is not None else 0.0
        y = int(off.attrib['y'])/914400 if off is not None else 0.0
        cx = int(ext.attrib['cx'])/914400 if ext is not None else 0.0
        cy = int(ext.attrib['cy'])/914400 if ext is not None else 0.0

        blip = child.find('.//a:blip', ns)
        blip_id = blip.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed') if blip is not None else ''
        target_img = rel_map.get(blip_id, '')

        print(f"\n--- Item [{i}] <{tag}> id={shape_id} name='{name}' ---")
        print(f"    Position: left={x:.2f}\", top={y:.2f}\", width={cx:.2f}\", height={cy:.2f}\"")
        if target_img:
            print(f"    Image target: {blip_id} -> {target_img}")
        if paragraphs:
            print(f"    Paragraphs ({len(paragraphs)}):")
            for p_idx, p_str in enumerate(paragraphs):
                print(f"      [{p_idx}]: {p_str}")

if __name__ == '__main__':
    inspect_pptx('poster_output/Quantum_Compass_Lab_Poster_v3.pptx')
