"""Create the deterministic, dependency-free companion download."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
root=Path(__file__).resolve().parents[1]
out=root/'public/downloads/TypeFlow-Windows-Companion.zip'
out.parent.mkdir(parents=True,exist_ok=True)
with ZipFile(out,'w',ZIP_DEFLATED) as archive:
    for name in ('README.txt','Start-TypeFlow.cmd','Setup-TypeFlow.ps1','typeflow_companion.py'):
        entry=ZipInfo(name,(2026,1,1,0,0,0));entry.compress_type=ZIP_DEFLATED
        archive.writestr(entry,(root/'companion/windows'/name).read_bytes())
print(out)
