from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT=Path("assets"); OUT.mkdir(exist_ok=True)
PURPLE=(103,52,220); PINK=(230,35,121); INK=(28,22,55); BG=(252,248,255)

def font(size,bold=False):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",):
        try: return ImageFont.truetype(p,size)
        except: pass
    return ImageFont.load_default()

# Icon
im=Image.new("RGB",(512,512),BG); d=ImageDraw.Draw(im)
d.rounded_rectangle((90,55,422,455),radius=120,outline=PURPLE,width=24,fill=(245,235,255))
d.ellipse((190,130,320,260),fill=(95,55,170)); d.polygon([(255,245),(145,390),(365,390)],fill=(95,55,170))
d.ellipse((315,225,385,295),fill=PINK)
im.save(OUT/"icon.png")

# Logo
im=Image.new("RGB",(1000,300),BG); d=ImageDraw.Draw(im)
d.text((95,60),"SheSafe",font=font(82,True),fill=PURPLE); d.text((465,60),"@School",font=font(82,True),fill=PINK)
d.text((280,175),"AI support for student safety",font=font(34),fill=(90,82,110))
im.save(OUT/"logo.jpg",quality=92)

def hero(path,title,subtitle,pink=False):
    im=Image.new("RGB",(900,520),(255,241,248) if pink else (245,238,255)); d=ImageDraw.Draw(im)
    d.ellipse((80,70,360,350),fill=(232,218,255)); d.ellipse((175,120,285,230),fill=(80,48,120))
    d.polygon([(230,220),(115,430),(355,430)],fill=(116,82,190))
    d.ellipse((540,90,800,350),fill=(255,220,234) if pink else (232,224,255))
    d.text((505,155),title,font=font(44,True),fill=PINK if pink else PURPLE)
    d.multiline_text((505,225),subtitle,font=font(30),fill=INK,spacing=12)
    im.save(path,quality=92)

hero(OUT/"home_hero.jpg","You Are Safe","You Are\nNot Alone")
hero(OUT/"help_hero.jpg","Your Safety","Matters",True)
