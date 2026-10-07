"""SheSafe@School - Pure Python + FastAPI + Kivy.

All handwritten application code is Python.
"""
from __future__ import annotations

import json
import threading
import urllib.request
from pathlib import Path

import uvicorn
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.utils import platform

from backend import analyze_message, app as fastapi_app

BASE=Path(__file__).resolve().parent
ASSETS=BASE/"assets"
API="http://127.0.0.1:8765/api/analyze"

INK=(0.08,0.07,0.19,1)
MUTED=(0.34,0.31,0.43,1)
PURPLE=(0.43,0.20,0.88,1)
PINK=(0.91,0.10,0.47,1)
WHITE=(1,1,1,1)
PAGE=(0.985,0.98,1,1)
RED=(0.93,0.18,0.25,1)
BLUE=(0.25,0.48,0.95,1)
MINT=(0.17,0.73,0.55,1)

def hx(v):
    h=v.lstrip("#")
    return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))+(1,)

def run_api():
    uvicorn.Server(uvicorn.Config(fastapi_app,host="127.0.0.1",port=8765,log_level="critical",access_log=False)).run()

def api_analyze(msg):
    req=urllib.request.Request(API,data=json.dumps({"message":msg}).encode(),headers={"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(req,timeout=3) as r:
        return json.loads(r.read().decode())

def dial(number):
    if platform!="android" or not number:
        return False
    try:
        from jnius import autoclass
        Intent=autoclass("android.content.Intent"); Uri=autoclass("android.net.Uri")
        PythonActivity=autoclass("org.kivy.android.PythonActivity")
        intent=Intent(Intent.ACTION_DIAL); intent.setData(Uri.parse("tel:"+number))
        PythonActivity.mActivity.startActivity(intent)
        return True
    except Exception:
        return False

class Card(BoxLayout):
    bg=ListProperty(WHITE)
    radius=NumericProperty(dp(22))
    def __init__(self,**kw):
        super().__init__(**kw)
        with self.canvas.before:
            self._c=Color(*self.bg)
            self._r=RoundedRectangle(pos=self.pos,size=self.size,radius=[self.radius])
        self.bind(pos=self._sync,size=self._sync,bg=self._color,radius=self._sync)
    def _sync(self,*_):
        self._r.pos=self.pos; self._r.size=self.size; self._r.radius=[self.radius]
    def _color(self,*_): self._c.rgba=self.bg

class Pill(Button):
    bg=ListProperty(PURPLE)
    radius=NumericProperty(dp(22))
    def __init__(self,**kw):
        kw.setdefault("background_normal",""); kw.setdefault("background_down","")
        kw.setdefault("background_color",(0,0,0,0)); kw.setdefault("color",WHITE)
        kw.setdefault("font_size","16sp")
        super().__init__(**kw)
        with self.canvas.before:
            self._c=Color(*self.bg)
            self._r=RoundedRectangle(pos=self.pos,size=self.size,radius=[self.radius])
        self.bind(pos=self._sync,size=self._sync,bg=self._color,radius=self._sync)
    def _sync(self,*_):
        self._r.pos=self.pos; self._r.size=self.size; self._r.radius=[self.radius]
    def _color(self,*_): self._c.rgba=self.bg

class Wrap(Label):
    def __init__(self,**kw):
        kw.setdefault("markup",True); kw.setdefault("color",INK); kw.setdefault("halign","left")
        kw.setdefault("valign","middle"); kw.setdefault("size_hint_y",None)
        super().__init__(**kw)
        self.bind(width=self._w,texture_size=self._h)
    def _w(self,*_): self.text_size=(max(1,self.width-dp(4)),None)
    def _h(self,*_): self.height=self.texture_size[1]+dp(8)

class Home(Screen):
    def __init__(self,**kw):
        super().__init__(**kw)
        scroll=ScrollView(do_scroll_x=False,bar_width=0)
        root=BoxLayout(orientation="vertical",size_hint_y=None,padding=dp(20),spacing=dp(10))
        root.bind(minimum_height=root.setter("height"))

        root.add_widget(Image(source=str(ASSETS/"logo.jpg"),size_hint_y=None,height=dp(135),allow_stretch=True,keep_ratio=True))
        root.add_widget(Label(text="[b][color=5E2BC9]SheSafe[/color][color=E31D7A]@School[/color][/b]",markup=True,font_size="34sp",color=INK,size_hint_y=None,height=dp(48)))
        root.add_widget(Label(text="AI support for student safety",font_size="18sp",color=MUTED,size_hint_y=None,height=dp(30)))
        root.add_widget(Label(text="[color=7B4ED8]Listen[/color]   |   [color=7B4ED8]Guide[/color]   |   [color=7B4ED8]Support[/color]",markup=True,font_size="14sp",size_hint_y=None,height=dp(26)))
        root.add_widget(Image(source=str(ASSETS/"home_hero.jpg"),size_hint_y=None,height=dp(220),allow_stretch=True,keep_ratio=False))

        b=Pill(text="●   Get Help    ›",size_hint_y=None,height=dp(68),font_size="23sp")
        b.bind(on_release=lambda *_: self.open_chat(""))
        root.add_widget(b)
        root.add_widget(Label(text="[b]Quick Actions[/b]",markup=True,color=MUTED,halign="left",text_size=(dp(340),None),size_hint_y=None,height=dp(32),font_size="16sp"))

        grid=GridLayout(cols=2,spacing=dp(10),size_hint_y=None,height=dp(156))
        actions=[
            ("●  Bullying  ›","#FCE7F1",PINK,"Some senior students keep threatening me after school. What should I do?"),
            ("▣  Unsafe Travel  ›","#E5F1FF",BLUE,"I feel unsafe while travelling."),
            ("⬟  Harassment  ›","#EEE8FF",PURPLE,"Someone is harassing me and making me uncomfortable."),
            ("▰  Cyber Safety  ›","#E0F8F1",MINT,"I am worried about an online or cyber safety problem.")
        ]
        for text,bg,fg,prompt in actions:
            x=Pill(text=text,bg=hx(bg),color=fg,font_size="13sp")
            x.bind(on_release=lambda _b,p=prompt:self.open_chat(p))
            grid.add_widget(x)
        root.add_widget(grid)
        root.add_widget(Label(text="🔒  Your chats are private and not stored.",color=MUTED,font_size="14sp",size_hint_y=None,height=dp(34)))
        root.add_widget(Label(text="We respect your privacy.",color=(0.5,0.48,0.58,1),font_size="12sp",size_hint_y=None,height=dp(25)))
        scroll.add_widget(root); self.add_widget(scroll)

    def open_chat(self,prompt):
        app=App.get_running_app()
        chat=app.root.get_screen("chat")
        if prompt: chat.prefill(prompt)
        app.root.current="chat"

class Chat(Screen):
    def __init__(self,**kw):
        super().__init__(**kw); self.result=None
        outer=BoxLayout(orientation="vertical",padding=(dp(16),dp(10)),spacing=dp(8))
        header=BoxLayout(size_hint_y=None,height=dp(58),spacing=dp(6))
        back=Pill(text="‹",bg=(0,0,0,0),color=INK,size_hint_x=None,width=dp(44),font_size="32sp")
        back.bind(on_release=lambda *_:setattr(App.get_running_app().root,"current","home"))
        header.add_widget(back)
        header.add_widget(Image(source=str(ASSETS/"icon.png"),size_hint=(None,None),size=(dp(42),dp(42))))
        header.add_widget(Label(text="[b][color=5D2BC8]SheSafe[/color][color=E31C78]@School[/color][/b]\n[color=777080]AI Support[/color]",markup=True,halign="left",text_size=(dp(260),None),font_size="18sp"))
        outer.add_widget(header)

        self.scroll=ScrollView(do_scroll_x=False,bar_width=0)
        self.content=BoxLayout(orientation="vertical",size_hint_y=None,spacing=dp(10),padding=(0,dp(4),0,dp(10)))
        self.content.bind(minimum_height=self.content.setter("height")); self.scroll.add_widget(self.content); outer.add_widget(self.scroll)

        user=Card(orientation="vertical",bg=hx("#EEE9FF"),size_hint_y=None,height=dp(90),padding=dp(14))
        self.user=Wrap(text="Some senior students keep threatening me after school.\nWhat should I do?",font_size="16sp")
        user.add_widget(self.user); self.content.add_widget(user)

        ai=Card(orientation="vertical",bg=WHITE,size_hint_y=None,padding=dp(14)); ai.bind(minimum_height=ai.setter("height"))
        self.ai=Wrap(text="I’m here to help you stay safe. Tell me what is happening and share only what you are comfortable sharing.",font_size="15sp")
        ai.add_widget(self.ai); self.content.add_widget(ai)

        self.risk=Card(orientation="vertical",bg=hx("#FFF5D6"),size_hint_y=None,padding=dp(14),spacing=dp(2)); self.risk.bind(minimum_height=self.risk.setter("height"))
        self.category=Wrap(text="[color=5B5668]Concern detected:[/color]\n[b]Bullying / Personal Safety[/b]",font_size="15sp")
        self.level=Wrap(text="Risk level: [b][color=B97800]Medium[/color][/b]",font_size="15sp")
        self.risk.add_widget(self.category); self.risk.add_widget(self.level); self.content.add_widget(self.risk)

        steps=Card(orientation="vertical",bg=WHITE,size_hint_y=None,padding=dp(14),spacing=dp(7)); steps.bind(minimum_height=steps.setter("height"))
        steps.add_widget(Wrap(text="[b]▣  Recommended next steps[/b]",font_size="18sp"))
        self.steps=Wrap(text="[b]1[/b]  Stay near teachers or other students.\n\n[b]2[/b]  Tell a trusted adult today.\n\n[b]3[/b]  Do not confront them alone.",font_size="15sp")
        steps.add_widget(self.steps); self.content.add_widget(steps)

        row=BoxLayout(size_hint_y=None,height=dp(58),spacing=dp(8))
        why=Pill(text="ⓘ  Why this advice?",bg=hx("#EEE9FF"),color=PURPLE,font_size="13sp")
        why.bind(on_release=lambda *_:self.show_why())
        trusted=Pill(text="● Contact\nTrusted Adult",font_size="13sp")
        trusted.bind(on_release=lambda *_:setattr(App.get_running_app().root,"current","help"))
        row.add_widget(why); row.add_widget(trusted); self.content.add_widget(row)

        compose=BoxLayout(size_hint_y=None,height=dp(62),spacing=dp(8))
        self.input=TextInput(hint_text="Type a message...",multiline=False,background_normal="",background_active="",background_color=hx("#F5F3FB"),foreground_color=INK,cursor_color=PURPLE,padding=(dp(14),dp(16)),font_size="15sp")
        send=Pill(text="➤",size_hint_x=None,width=dp(58),font_size="24sp")
        send.bind(on_release=lambda *_:self.submit()); self.input.bind(on_text_validate=lambda *_:self.submit())
        compose.add_widget(self.input); compose.add_widget(send); outer.add_widget(compose)
        self.add_widget(outer)

    def prefill(self,msg): self.input.text=msg

    def submit(self):
        msg=self.input.text.strip()
        if not msg:return
        self.user.text=msg; self.ai.text="Checking your concern..."; self.input.text=""
        threading.Thread(target=self._worker,args=(msg,),daemon=True).start()

    def _worker(self,msg):
        try: result=api_analyze(msg)
        except Exception:
            m=analyze_message(msg); result=m.dict() if hasattr(m,"dict") else m.model_dump()
        Clock.schedule_once(lambda _dt:self.render(result))

    def render(self,r):
        self.result=r; self.ai.text=r["response"]; self.category.text=f"[color=5B5668]Concern detected:[/color]\n[b]{r['category']}[/b]"
        c={"Low":"2C9A65","Medium":"B97800","High":"D62332"}.get(r["risk"],"B97800")
        self.level.text=f"Risk level: [b][color={c}]{r['risk']}[/color][/b]"
        self.risk.bg={"Low":hx("#E9F8F0"),"Medium":hx("#FFF5D6"),"High":hx("#FFE6E9")}.get(r["risk"],hx("#FFF5D6"))
        self.steps.text="\n\n".join(f"[b]{i}[/b]   {s}" for i,s in enumerate(r["steps"],1))
        Clock.schedule_once(lambda _dt:setattr(self.scroll,"scroll_y",0),0.1)

    def show_why(self):
        App.get_running_app().modal("Why this advice?",(self.result or {}).get("why","The app uses simple explainable safety rules."),PURPLE)

class Help(Screen):
    def __init__(self,**kw):
        super().__init__(**kw)
        scroll=ScrollView(do_scroll_x=False,bar_width=0)
        root=BoxLayout(orientation="vertical",size_hint_y=None,padding=dp(18),spacing=dp(10)); root.bind(minimum_height=root.setter("height"))
        head=BoxLayout(size_hint_y=None,height=dp(48))
        back=Pill(text="‹",bg=(0,0,0,0),color=INK,size_hint_x=None,width=dp(44),font_size="32sp")
        back.bind(on_release=lambda *_:setattr(App.get_running_app().root,"current","home"))
        head.add_widget(back); head.add_widget(Label(text="[b]Get Immediate Help[/b]",markup=True,color=INK,font_size="24sp",halign="left",text_size=(dp(300),None)))
        root.add_widget(head)
        root.add_widget(Label(text="You are not alone. Help is always available.",color=MUTED,font_size="14sp",size_hint_y=None,height=dp(28)))
        root.add_widget(Image(source=str(ASSETS/"help_hero.jpg"),size_hint_y=None,height=dp(165),allow_stretch=True,keep_ratio=False))
        for text,bg,fg,kind in [
            ("☎   Call Parent\n     Talk to your parent or guardian","#DFF8EF",hx("#075B4B"),"parent"),
            ("●   Call Teacher\n     Reach out to your class teacher","#E3F0FF",hx("#174EAE"),"teacher"),
            ("⚠   Emergency Help\n     Contact emergency services","#FFE2E7",hx("#B10C25"),"emergency")]:
            x=Pill(text=text,bg=hx(bg),color=fg,size_hint_y=None,height=dp(82),font_size="15sp")
            x.bind(on_release=lambda _b,k=kind:self.action(k)); root.add_widget(x)
        warn=Card(orientation="horizontal",bg=hx("#FFF0F2"),size_hint_y=None,height=dp(96),padding=dp(14),spacing=dp(10))
        warn.add_widget(Label(text="⚠",color=RED,font_size="36sp",size_hint_x=None,width=dp(50)))
        warn.add_widget(Wrap(text="[b][color=D7192D]If you are in immediate danger, contact a trusted adult or emergency service now.[/color][/b]",font_size="15sp")); root.add_widget(warn)
        root.add_widget(Label(text="[b]💡  Safety Tips[/b]",markup=True,color=INK,halign="left",text_size=(dp(340),None),size_hint_y=None,height=dp(34),font_size="18sp"))
        tips=Card(orientation="vertical",bg=WHITE,size_hint_y=None,padding=dp(14),spacing=dp(7)); tips.bind(minimum_height=tips.setter("height"))
        for t in ["● Stay in well-lit and populated areas.","● Share your live location with a trusted person when travelling.","● Keep important phone numbers saved and easily accessible."]:
            tips.add_widget(Wrap(text=t,font_size="14sp"))
        root.add_widget(tips); scroll.add_widget(root); self.add_widget(scroll)

    def action(self,kind):
        app=App.get_running_app()
        if kind=="emergency":
            if not dial("112"): app.modal("Emergency Help","If you are in immediate danger in India, dial 112 and move to a safe, populated place.",RED)
            return
        number=app.contacts.get(kind,"")
        if not (number and dial(number)):
            title="Call Parent" if kind=="parent" else "Call Teacher"
            app.modal(title,"No personal number is stored in this sample. Add a trusted contact in config.json before the school demonstration.",PURPLE)

class SheSafeApp(App):
    title="SheSafe@School"
    def build(self):
        Window.clearcolor=PAGE
        if platform not in ("android","ios"): Window.size=(390,844)
        try:self.contacts=json.loads((BASE/"config.json").read_text())
        except Exception:self.contacts={"parent":"","teacher":""}
        threading.Thread(target=run_api,daemon=True).start()
        sm=ScreenManager(transition=FadeTransition(duration=.18))
        sm.add_widget(Home(name="home")); sm.add_widget(Chat(name="chat")); sm.add_widget(Help(name="help"))
        return sm
    def modal(self,title,message,accent):
        m=ModalView(size_hint=(.9,None),height=dp(320),background_color=(0,0,0,.35))
        card=Card(orientation="vertical",bg=WHITE,padding=dp(20),spacing=dp(12))
        card.add_widget(Label(text=f"[b]{title}[/b]",markup=True,color=accent,font_size="22sp",size_hint_y=None,height=dp(44)))
        card.add_widget(Wrap(text=message,font_size="15sp"))
        ok=Pill(text="OK",bg=accent,size_hint_y=None,height=dp(52)); ok.bind(on_release=lambda *_:m.dismiss())
        card.add_widget(ok); m.add_widget(card); m.open()

if __name__=="__main__":
    SheSafeApp().run()
