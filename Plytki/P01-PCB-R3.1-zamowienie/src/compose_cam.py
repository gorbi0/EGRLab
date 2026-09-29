"""Colour previews from parsed, rasterized Gerber layers; no design geometry added."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageOps
import warnings
from gerbonara import LayerStack
R=Path(__file__).resolve().parents[1]
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    cam=LayerStack.open(R/'gerber')
for side in ['top','bottom']:
    imgs={k:Image.open(R/'podglad'/f'CAM-{side}-{k}.png').convert('L') for k in ['copper','mask','silk']}
    copper,mask,silk=(ImageOps.invert(imgs[k]) for k in ['copper','mask','silk'])
    board=Image.new('RGB',copper.size,(20,80,51))
    board.paste((40,117,75),mask=copper)
    board.paste((196,185,151),mask=ImageChops.multiply(mask,copper))
    board.paste((249,248,226),mask=silk)
    draw=ImageDraw.Draw(board)
    for layer in [cam.drill_pth,cam.drill_npth]:
        for o in layer.objects:
            x=o.x/160*board.width; y=-o.y/120*board.height
            rx=o.aperture.diameter/2/160*board.width; ry=o.aperture.diameter/2/120*board.height
            draw.ellipse((x-rx,y-ry,x+rx,y+ry),fill=(24,25,28))
    if side=='bottom': board=ImageOps.mirror(board)
    board.save(R/'podglad'/f'CAM-{side}.png')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',28)
names=['CAM-top','CAM-bottom','CAM-top-copper','CAM-bottom-copper','CAM-top-mask','CAM-bottom-mask','CAM-top-silk','CAM-bottom-silk']
sheet=Image.new('RGB',(1640,2640),'#eceef0'); draw=ImageDraw.Draw(sheet)
for i,n in enumerate(names):
    image=Image.open(R/'podglad'/f'{n}.png').convert('RGB'); image.thumbnail((790,600))
    x=10+(i%2)*820;y=10+(i//2)*660
    draw.text((x,y),n,font=font,fill='black'); sheet.paste(image,(x,y+42))
sheet.save(R/'podglad/CAM-kontrola-warstw.png')
