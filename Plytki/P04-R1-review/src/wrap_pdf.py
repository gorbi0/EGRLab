"""Wrap full-resolution PCB views in exact A4 pages using ReportLab."""
from pathlib import Path
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

folder, out = map(Path, sys.argv[1:3])
c = canvas.Canvas(str(out), pagesize=(297*mm,210*mm), pageCompression=1, invariant=1)
c.setTitle('EGRLab P04-R1 - PCB i montaz')
c.setAuthor('EGRLab')
for i in range(1,5):
    c.drawImage(str(folder/f'pcb-page-{i}.png'),0,0,width=297*mm,height=210*mm)
    c.showPage()
c.save()
