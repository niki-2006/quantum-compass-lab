import sys
sys.stdout.reconfigure(encoding='utf-8')
import zipfile
import xml.etree.ElementTree as ET

ns = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
}

def get_full_details(path):
    zf = zipfile.ZipFile(path)
    slide_xml = zf.read('ppt/slides/slide1.xml')
    root = ET.fromstring(slide_xml)
    spTree = root.find('.//p:spTree', ns)

    info = {}
    for elem in spTree:
        cNvPr = elem.find('.//p:cNvPr', ns)
        name = cNvPr.attrib.get('name', '') if cNvPr is not None else ''
        xfrm = elem.find('.//a:xfrm', ns)
        off = xfrm.find('a:off', ns) if xfrm is not None else None
        ext = xfrm.find('a:ext', ns) if xfrm is not None else None
        x = int(off.attrib['x'])/914400 if off is not None else 0
        y = int(off.attrib['y'])/914400 if off is not None else 0
        w = int(ext.attrib['cx'])/914400 if ext is not None else 0
        h = int(ext.attrib['cy'])/914400 if ext is not None else 0

        paragraphs = []
        txBody = elem.find('.//p:txBody', ns)
        if txBody is not None:
            for p in txBody.findall('a:p', ns):
                runs = []
                for r in p.findall('.//a:r', ns):
                    t = r.find('a:t', ns)
                    rPr = r.find('a:rPr', ns)
                    sz = int(rPr.attrib.get('sz', 0))/100 if rPr is not None else 0
                    b = rPr.attrib.get('b', '0') == '1' if rPr is not None else False
                    color = None
                    if rPr is not None:
                        srgb = rPr.find('.//a:srgbClr', ns)
                        if srgb is not None:
                            color = srgb.attrib.get('val')
                    runs.append({'text': t.text if t is not None else '', 'sz': sz, 'bold': b, 'color': color})
                paragraphs.append(runs)
        info[name] = {'rect': (x, y, w, h), 'paragraphs': paragraphs}
    return info

orig = get_full_details('C:/Users/Nikitha/Downloads/Quantum_Compass_Lab_Qiskit_Fall_Fest_Poster.pptx')
v3 = get_full_details('poster_output/Quantum_Compass_Lab_Poster_v3.pptx')

print("=== DIFFERENCES IN SHAPE NAMES ===")
orig_names = set(orig.keys())
v3_names = set(v3.keys())
print("In Orig only:", orig_names - v3_names)
print("In v3 only:", v3_names - orig_names)

print("\n=== RECTANGLE DIFFERENCES (Card / Box layout) ===")
for name in sorted(orig_names & v3_names):
    r_orig = orig[name]['rect']
    r_v3 = v3[name]['rect']
    diff = [abs(a - b) for a, b in zip(r_orig, r_v3)]
    if max(diff) > 0.01:
        print(f"[{name}]")
        print(f"   Orig: ({r_orig[0]:.2f}, {r_orig[1]:.2f}, {r_orig[2]:.2f}x{r_orig[3]:.2f})")
        print(f"   v3:   ({r_v3[0]:.2f}, {r_v3[1]:.2f}, {r_v3[2]:.2f}x{r_v3[3]:.2f})")
