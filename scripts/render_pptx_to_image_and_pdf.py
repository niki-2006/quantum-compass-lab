import os
import sys
from pathlib import Path
# using powershell COM automation

def export_with_powershell(pptx_path, out_pdf_path=None, out_png_path=None):
    pptx_abs = str(Path(pptx_path).resolve())
    cmd_parts = []
    
    ps_script = f"""
$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue
try {{
    $pres = $ppt.Presentations.Open('{pptx_abs}', [Microsoft.Office.Core.MsoTriState]::msoTrue, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)
"""
    if out_pdf_path:
        pdf_abs = str(Path(out_pdf_path).resolve())
        ps_script += f"""
    $pres.SaveAs('{pdf_abs}', 32)
    Write-Host "Exported PDF to {pdf_abs}"
"""
    if out_png_path:
        png_abs = str(Path(out_png_path).resolve())
        # Export slide 1 at high resolution (e.g., width 2250, height 3750)
        ps_script += f"""
    $slide = $pres.Slides.Item(1)
    $slide.Export('{png_abs}', 'PNG', 2250, 3750)
    Write-Host "Exported PNG to {png_abs}"
"""
    ps_script += """
    $pres.Close()
} finally {
    $ppt.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) | Out-Null
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}
"""
    ps_file = Path("scripts/export_temp.ps1")
    ps_file.write_text(ps_script, encoding="utf-8")
    os.system(f"powershell -ExecutionPolicy Bypass -File {ps_file}")
    if ps_file.exists():
        ps_file.unlink()

if __name__ == '__main__':
    export_with_powershell(
        'poster_output/Quantum_Compass_Lab_Poster_v3.pptx',
        out_pdf_path='poster_output/Quantum_Compass_Lab_Poster_v3_preview.pdf',
        out_png_path='poster_output/Quantum_Compass_Lab_Poster_v3_preview.png'
    )
