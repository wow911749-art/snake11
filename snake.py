"""
╔══════════════════════════════════════════════════════════════╗
║                    NEON SNAKE  v2.0                          ║
║   Меню, скины, рекорды, звуки, эффекты                       ║
║   Сохранения: snake_save.json рядом с .exe                   ║
╚══════════════════════════════════════════════════════════════╝
"""

import pygame
import random
import sys
import math
import json
import os
import time

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# ══════════════════════════════════════════════════════════════
#  ПУТЬ К ФАЙЛУ СОХРАНЕНИЙ — всегда рядом с .exe / snake.py
# ══════════════════════════════════════════════════════════════

def get_save_path():
    """
    Возвращает путь к snake_save.json рядом с исполняемым файлом.
    Работает как для .py так и для собранного .exe (PyInstaller).
    """
    if getattr(sys, "frozen", False):
        # Запущен как .exe собранный PyInstaller
        base = os.path.dirname(sys.executable)
    else:
        # Запущен как .py скрипт
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "snake_save.json")

SAVE_FILE = get_save_path()

# ══════════════════════════════════════════════════════════════
#  КОНСТАНТЫ
# ══════════════════════════════════════════════════════════════

COLS       = 20
ROWS       = 20
PANEL      = 72
WIN_W      = 900
WIN_H      = 900
FPS        = 60

STATE_MENU     = "menu"
STATE_GAME     = "game"
STATE_SKINS    = "skins"
STATE_RECORDS  = "records"
STATE_SETTINGS = "settings"

# ══════════════════════════════════════════════════════════════
#  СКИНЫ
# ══════════════════════════════════════════════════════════════

SKINS = {
    "neon_green": {
        "name": "Неон",
        "head1": (0, 255, 180), "head2": (0, 180, 120),
        "head_dark": (0, 100, 65), "body1": (0, 220, 150),
        "body2": (0, 80, 50), "glow": (0, 255, 160), "outline": (0, 140, 90),
    },
    "fire": {
        "name": "Огонь",
        "head1": (255, 160, 30), "head2": (220, 80, 10),
        "head_dark": (140, 40, 5), "body1": (255, 120, 20),
        "body2": (160, 30, 5), "glow": (255, 140, 30), "outline": (200, 60, 10),
    },
    "ice": {
        "name": "Лёд",
        "head1": (160, 220, 255), "head2": (80, 160, 230),
        "head_dark": (40, 90, 160), "body1": (140, 200, 255),
        "body2": (40, 90, 180), "glow": (180, 230, 255), "outline": (70, 140, 220),
    },
    "purple": {
        "name": "Плазма",
        "head1": (220, 100, 255), "head2": (160, 40, 220),
        "head_dark": (90, 20, 130), "body1": (200, 80, 255),
        "body2": (80, 15, 120), "glow": (220, 120, 255), "outline": (150, 50, 200),
    },
    "gold": {
        "name": "Золото",
        "head1": (255, 220, 60), "head2": (220, 160, 20),
        "head_dark": (140, 90, 10), "body1": (255, 200, 40),
        "body2": (160, 100, 10), "glow": (255, 230, 80), "outline": (200, 140, 20),
    },
    "rainbow": {
        "name": "Радуга",
        "head1": (255, 80, 80), "head2": (200, 40, 40),
        "head_dark": (120, 20, 20), "body1": (255, 80, 80),
        "body2": (80, 40, 200), "glow": (255, 120, 120), "outline": (180, 40, 40),
    },
}
SKIN_KEYS = list(SKINS.keys())

# ══════════════════════════════════════════════════════════════
#  ЦВЕТА UI
# ══════════════════════════════════════════════════════════════

BG          = (6,   8,  16)
GRID_C      = (14, 18,  34)
PANEL_C     = (10, 13,  24)
PANEL_LINE  = (25, 32,  62)
T_ACC       = (0,  240, 160)
T_DIM       = (60,  80, 120)
T_MN        = (200, 215, 240)
T_DANGER    = (255, 60,  90)
T_GOLD      = (255, 215, 60)
T_WHITE     = (240, 248, 255)
CARD_BG     = (14,  18,  35)
CARD_BORDER = (30,  40,  80)
BTN_HOVER   = (20,  28,  55)
AP_R1       = (255, 45,  80)
AP_R2       = (180, 20,  45)
AP_GLOW     = (255, 60,  90)
AP_SHINE    = (255, 180, 190)
AP_STEM     = (100, 200, 50)
AP_LEAF     = (60,  220, 90)

# ══════════════════════════════════════════════════════════════
#  ШРИФТЫ
# ══════════════════════════════════════════════════════════════

try:
    F_TITLE = pygame.font.SysFont("segoeui", 72, bold=True)
    F_BIG   = pygame.font.SysFont("segoeui", 52, bold=True)
    F_MED   = pygame.font.SysFont("segoeui", 28, bold=True)
    F_SM    = pygame.font.SysFont("segoeui", 18)
    F_XSM   = pygame.font.SysFont("segoeui", 14)
except:
    F_TITLE = pygame.font.SysFont(None, 72, bold=True)
    F_BIG   = pygame.font.SysFont(None, 52, bold=True)
    F_MED   = pygame.font.SysFont(None, 28, bold=True)
    F_SM    = pygame.font.SysFont(None, 18)
    F_XSM   = pygame.font.SysFont(None, 14)

# ══════════════════════════════════════════════════════════════
#  СОХРАНЕНИЯ
# ══════════════════════════════════════════════════════════════

DEFAULT_SAVE = {
    "highscores":   [],
    "current_skin": "neon_green",
    "sound_on":     True,
    "total_games":  0,
    "total_score":  0,
    "best_score":   0,
}

def load_save():
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in DEFAULT_SAVE.items():
            if k not in data:
                data[k] = v
        return data
    except:
        return DEFAULT_SAVE.copy()

def save_data(data):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения: {e}")

def add_score(data, score):
    data["total_games"] += 1
    data["total_score"] += score
    data["best_score"]   = max(data["best_score"], score)
    entry = {"score": score, "date": time.strftime("%d.%m.%Y")}
    data["highscores"].append(entry)
    data["highscores"].sort(key=lambda x: x["score"], reverse=True)
    data["highscores"] = data["highscores"][:10]
    save_data(data)

# ══════════════════════════════════════════════════════════════
#  КЕШ СВЕЧЕНИЙ
# ══════════════════════════════════════════════════════════════

_glow_cache = {}

def make_glow(radius, color, alpha=55):
    key = (radius, color, alpha)
    if key not in _glow_cache:
        size = radius * 2 + 2
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        for r in range(radius, 0, -1):
            a = int(alpha * (r / radius) ** 0.6)
            pygame.draw.circle(s, (*color, a), (radius+1, radius+1), r)
        _glow_cache[key] = s
    return _glow_cache[key]

def clear_glow_cache():
    _glow_cache.clear()

# ══════════════════════════════════════════════════════════════
#  ЗВУКИ
# ══════════════════════════════════════════════════════════════

def gen_eat():
    sr = 44100; n = int(sr * 0.12); buf = []
    for i in range(n):
        t = i/sr; f = 400 + 600*(i/n)
        buf.append(int(math.sin(2*math.pi*f*t)*math.exp(-4*t/0.12)*0.4*32767))
    return pygame.sndarray.make_sound(
        pygame.sndarray.array(buf).astype("int16").reshape(-1,1).repeat(2,axis=1))

def gen_death():
    sr = 44100; n = int(sr * 0.4); buf = []
    for i in range(n):
        t = i/sr; f = 300 - 250*(i/n)
        v = math.sin(2*math.pi*f*t)*math.exp(-2*t/0.4) + random.uniform(-0.08,0.08)*(1-i/n)
        buf.append(int(v*0.35*32767))
    return pygame.sndarray.make_sound(
        pygame.sndarray.array(buf).astype("int16").reshape(-1,1).repeat(2,axis=1))

def gen_levelup():
    sr = 44100; n = int(sr * 0.3); buf = []
    for i in range(n):
        t = i/sr; p = i/n; f = 300 + 500*p + 200*math.sin(10*math.pi*p)
        buf.append(int(math.sin(2*math.pi*f*t)*(1-p*0.5)*0.3*32767))
    return pygame.sndarray.make_sound(
        pygame.sndarray.array(buf).astype("int16").reshape(-1,1).repeat(2,axis=1))

def gen_click():
    sr = 44100; n = int(sr * 0.06); buf = []
    for i in range(n):
        t = i/sr
        buf.append(int(math.sin(2*math.pi*800*t)*math.exp(-8*t/0.06)*0.2*32767))
    return pygame.sndarray.make_sound(
        pygame.sndarray.array(buf).astype("int16").reshape(-1,1).repeat(2,axis=1))

try:
    SND_EAT     = gen_eat()
    SND_DEATH   = gen_death()
    SND_LEVELUP = gen_levelup()
    SND_CLICK   = gen_click()
    SOUND_OK    = True
except:
    SOUND_OK = False

def play_snd(snd, save):
    if SOUND_OK and save.get("sound_on", True):
        try: snd.play()
        except: pass

# ══════════════════════════════════════════════════════════════
#  УТИЛИТЫ
# ══════════════════════════════════════════════════════════════

def lerp(a, b, t):    return a + (b-a)*t
def lerpC(c1,c2,t):   return tuple(max(0,min(255,int(lerp(c1[i],c2[i],t)))) for i in range(3))
def clamp(v,lo,hi):   return max(lo,min(hi,v))
def ease_out(t):      return 1-(1-t)**3

def draw_text_glow(surf, font, text, color, cx, cy, glow_color=None, passes=3):
    if glow_color is None: glow_color = color
    for i in range(passes, 0, -1):
        gs = font.render(text, True, glow_color)
        gs.set_alpha(int(55/i))
        surf.blit(gs, (cx-gs.get_width()//2+i, cy+i))
        surf.blit(gs, (cx-gs.get_width()//2-i, cy-i))
    t = font.render(text, True, color)
    surf.blit(t, (cx-t.get_width()//2, cy))

# ══════════════════════════════════════════════════════════════
#  ЗВЁЗДЫ
# ══════════════════════════════════════════════════════════════

class Star:
    def __init__(self, W, H):
        self.W = W; self.H = H
        self.reset(random.uniform(0, H))

    def reset(self, y=None):
        self.x   = random.uniform(0, self.W)
        self.y   = float(y if y is not None else -2)
        self.r   = random.uniform(0.3, 2.2)
        self.sp  = random.uniform(0.008, 0.12)
        self.a   = random.randint(40, 210)
        self.tw  = random.uniform(0, math.tau)
        self.tws = random.uniform(0.008, 0.045)
        self.col = random.choice([(255,255,255),(200,220,255),(255,240,200),(180,200,255)])

    def update(self, dt):
        self.y  += self.sp * dt * 0.05
        self.tw += self.tws
        if self.y > self.H: self.reset()

    def draw(self, surf):
        f = 0.65 + 0.35*math.sin(self.tw)
        a = int(self.a * f)
        r = max(1, int(self.r))
        c = tuple(min(255, int(self.col[i]*a/255)) for i in range(3))
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), r)
        if r >= 2:
            cs = pygame.Surface((r*6, r*6), pygame.SRCALPHA)
            pygame.draw.line(cs, (*c, int(a*0.3)), (r*3,0),(r*3,r*6), 1)
            pygame.draw.line(cs, (*c, int(a*0.3)), (0,r*3),(r*6,r*3), 1)
            surf.blit(cs, (int(self.x)-r*3, int(self.y)-r*3))

def make_stars(W, H, n=220):
    return [Star(W, H) for _ in range(n)]

# ══════════════════════════════════════════════════════════════
#  ЧАСТИЦЫ
# ══════════════════════════════════════════════════════════════

class Particle:
    COLORS = [(255,45,80),(255,130,60),(255,215,70),(0,255,160),(80,200,255),(200,90,255),(255,255,255)]

    def __init__(self, x, y, CELL, color=None):
        a  = random.uniform(0, math.tau)
        sp = random.uniform(1.2, 6.5) * CELL/38
        self.x=float(x); self.y=float(y)
        self.vx=math.cos(a)*sp; self.vy=math.sin(a)*sp - random.uniform(0,2.0)
        self.life=1.0; self.decay=random.uniform(0.016,0.030)
        self.r=random.uniform(2.5, CELL*0.32)
        self.c=color if color else random.choice(self.COLORS)
        self.trail=[]; self.glow=random.random()>0.4

    def update(self, dt):
        f=dt*0.06
        self.trail.append((int(self.x),int(self.y)))
        if len(self.trail)>4: self.trail.pop(0)
        self.x+=self.vx*f; self.y+=self.vy*f
        self.vy+=0.12*f; self.life-=self.decay*f
        self.r=max(1,self.r-0.05*f)

    def draw(self, surf):
        if self.life<=0: return
        a=max(0,int(self.life*255)); r=int(self.r)
        for i,(tx,ty) in enumerate(self.trail):
            ta=int(a*(i/len(self.trail))*0.35)
            if ta>0 and r>0:
                pygame.draw.circle(surf, (*self.c,ta), (tx,ty), max(1,r//2))
        if self.glow and r>=2:
            gs=pygame.Surface((r*5,r*5),pygame.SRCALPHA)
            pygame.draw.circle(gs,(*self.c,a//4),(r*2+1,r*2+1),r*2)
            surf.blit(gs,(int(self.x)-r*2-1,int(self.y)-r*2-1))
        if r>0:
            pygame.draw.circle(surf,(*self.c,a),(int(self.x),int(self.y)),r)

class ScorePopup:
    def __init__(self, x, y, text, color=None):
        self.x=float(x); self.y=float(y)
        self.vy=-1.5; self.text=text
        self.life=1.0; self.color=color or T_GOLD

    def update(self, dt):
        f=dt*0.06; self.y+=self.vy*f; self.life-=0.022*f

    def draw(self, surf):
        if self.life<=0: return
        img=F_MED.render(self.text, True, self.color)
        img.set_alpha(max(0,int(self.life*255)))
        surf.blit(img,(int(self.x)-img.get_width()//2,int(self.y)))

class ScreenFlash:
    def __init__(self, color, dur=0.3):
        self.color=color; self.life=1.0; self.dur=dur

    def update(self, dt):
        self.life-=dt/(self.dur*1000)

    def draw(self, surf, W, H):
        if self.life<=0: return
        a=int(clamp(self.life*110,0,110))
        s=pygame.Surface((W,H),pygame.SRCALPHA)
        s.fill((*self.color,a)); surf.blit(s,(0,0))

# ══════════════════════════════════════════════════════════════
#  КНОПКА
# ══════════════════════════════════════════════════════════════

class Button:
    def __init__(self, x, y, w, h, text, color=T_ACC, font=None):
        self.rect=pygame.Rect(x,y,w,h)
        self.text=text; self.color=color
        self.font=font or F_MED
        self.hover_t=0.0; self.click_t=0.0

    def update(self, mx, my, dt):
        hov=self.rect.collidepoint(mx,my)
        self.hover_t=lerp(self.hover_t, 1.0 if hov else 0.0, dt*0.012)
        self.click_t=max(0,self.click_t-dt*0.003)

    def is_clicked(self, event):
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if self.rect.collidepoint(event.pos):
                self.click_t=1.0
                # Звук воспроизводится снаружи через play_snd
                return True
        return False

    def draw(self, surf, icon_fn=None):
        t=ease_out(self.hover_t)
        sc=1.0+0.03*t-0.02*self.click_t
        rw=int(self.rect.w*sc); rh=int(self.rect.h*sc)
        rx=self.rect.x-(rw-self.rect.w)//2
        ry=self.rect.y-(rh-self.rect.h)//2
        r=pygame.Rect(rx,ry,rw,rh)
        pygame.draw.rect(surf,lerpC(CARD_BG,BTN_HOVER,t),r,border_radius=12)
        pygame.draw.rect(surf,lerpC(CARD_BORDER,self.color,t*0.8),r,1+int(t),border_radius=12)
        if t>0.1:
            gl=make_glow(max(4,rh//3),self.color,int(28*t))
            surf.blit(gl,(rx+rw//2-rh//3-1,ry+rh//2-rh//3-1))
        # Иконка слева если передана функция
        icon_x = rx + 22
        icon_y = ry + rh//2
        text_offset = 0
        if icon_fn:
            icon_fn(surf, icon_x, icon_y, rh//3, lerpC(T_DIM, self.color, t))
            text_offset = rh//3 + 14
        tc=lerpC(T_MN,self.color,t)
        txt=self.font.render(self.text, True, tc)
        tx=rx+rw//2-txt.get_width()//2+text_offset//2
        ty=ry+rh//2-txt.get_height()//2
        # Свечение текста при ховере
        if t>0.3:
            glow_txt=self.font.render(self.text, True, self.color)
            glow_txt.set_alpha(int(40*t))
            surf.blit(glow_txt,(tx+1,ty+1))
        surf.blit(txt,(tx,ty))

# ══════════════════════════════════════════════════════════════
#  ПОЛЕ И СЕТКА
# ══════════════════════════════════════════════════════════════

_field_cache = {}

def draw_field_bg(surf, ox, oy, W, H):
    key=(W,H)
    if key not in _field_cache:
        s=pygame.Surface((W,H),pygame.SRCALPHA)
        s.fill((10,13,26))
        cx,cy=W//2,H//2; md=math.sqrt(cx*cx+cy*cy)
        for i in range(30):
            p=i/30; d=md*(1-p*0.6)
            a=int(40*(1-p))
            pygame.draw.ellipse(s,(0,0,0,a),(cx-int(d),cy-int(d*H/W),int(d*2),int(d*2*H/W)),2)
        _field_cache[key]=s
    surf.blit(_field_cache[key],(ox,oy))

def draw_grid(surf, ox, oy, CELL):
    W=COLS*CELL; H=ROWS*CELL
    for c in range(COLS+1): pygame.draw.line(surf,GRID_C,(ox+c*CELL,oy),(ox+c*CELL,oy+H))
    for r in range(ROWS+1): pygame.draw.line(surf,GRID_C,(ox,oy+r*CELL),(ox+W,oy+r*CELL))
    pygame.draw.rect(surf,(32,42,88),(ox,oy,W,H),2)

# ══════════════════════════════════════════════════════════════
#  ЗМЕЙКА
# ══════════════════════════════════════════════════════════════

def draw_snake(surf, sn, CELL, ox, oy, skin, tk):
    n=len(sn)
    if n==0: return
    for i in reversed(range(n)):
        seg=sn[i]
        cx2=ox+seg[0]*CELL+CELL//2
        cy2=oy+seg[1]*CELL+CELL//2
        t=i/max(n-1,1)
        pad=max(1,CELL//12); R=CELL//2-pad
        glow_col=skin["glow"]

        if i==0:
            g=make_glow(R+10,glow_col,75)
            surf.blit(g,(cx2-R-11,cy2-R-11))
            pulse=1.0+0.04*math.sin(tk*0.08)
            Rp=int(R*pulse)
            pygame.draw.circle(surf,skin["head_dark"],(cx2,cy2),Rp)
            pygame.draw.circle(surf,skin["head2"],(cx2,cy2),int(Rp*0.82))
            pygame.draw.circle(surf,skin["head1"],(cx2,cy2),int(Rp*0.58))
            pygame.draw.circle(surf,skin["glow"],(cx2,cy2),Rp,2)
            pygame.draw.ellipse(surf,lerpC(skin["head1"],(255,255,255),0.5),
                pygame.Rect(cx2-Rp//3,cy2-int(Rp*0.55),Rp//2,Rp//3))
            nd=(sn[1][0]-sn[0][0],sn[1][1]-sn[0][1]) if n>1 else (0,0)
            er=max(2,R//5)
            EM={(1,0):[(int(R*.5),int(-R*.35)),(int(R*.5),int(R*.35))],
                (-1,0):[(int(-R*.5),int(-R*.35)),(int(-R*.5),int(R*.35))],
                (0,1):[(int(-R*.35),int(R*.5)),(int(R*.35),int(R*.5))],
                (0,-1):[(int(-R*.35),int(-R*.5)),(int(R*.35),int(-R*.5))]}
            for ex,ey2 in EM.get((-nd[0],-nd[1]),[(int(R*.35),int(-R*.35)),(int(-R*.35),int(-R*.35))]):
                ex2=cx2+ex; ey3=cy2+ey2
                pygame.draw.circle(surf,(230,248,255),(ex2,ey3),er)
                pygame.draw.circle(surf,(5,8,16),(ex2+1,ey3-1),max(1,er-1))
                pygame.draw.circle(surf,(255,255,255),(ex2-1,ey3-1),max(1,er//3))
        else:
            ga=max(0,int(65*(1-t**0.5)))
            if ga>6:
                g=make_glow(R+5,glow_col,ga)
                surf.blit(g,(cx2-R-6,cy2-R-6))
            col_out=lerpC(skin["body1"],skin["body2"],t)
            col_mid=lerpC(skin["head1"],skin["head_dark"],t)
            col_in=lerpC(skin["head2"],skin["body1"],min(1,t*1.5))
            pygame.draw.circle(surf,col_out,(cx2,cy2),R)
            pygame.draw.circle(surf,col_mid,(cx2,cy2),int(R*0.76))
            if t<0.55: pygame.draw.circle(surf,col_in,(cx2,cy2),int(R*0.46))
            pygame.draw.circle(surf,lerpC(skin["outline"],skin["body2"],t),(cx2,cy2),R,2)
            if t<0.42:
                ba=int(160*(1-t/0.42))
                bl=lerpC(skin["head1"],(200,255,220),0.4)
                pygame.draw.ellipse(surf,(*bl,ba),
                    pygame.Rect(cx2-R//3,cy2-int(R*0.55),R//2+1,R//3))

# ══════════════════════════════════════════════════════════════
#  ЕДА
# ══════════════════════════════════════════════════════════════

def draw_food(surf, fx, fy, tk, CELL, ox, oy):
    pulse=math.sin(tk*0.07)*0.08+0.92
    beat=abs(math.sin(tk*0.07))
    cx=ox+fx*CELL+CELL//2; cy=oy+fy*CELL+CELL//2
    R=max(4,int((CELL//2-3)*pulse))
    gr=min(R+9,CELL//2-1)
    g=make_glow(gr,AP_GLOW,int(38+22*beat))
    surf.blit(g,(cx-gr-1,cy-gr-1))
    pygame.draw.circle(surf,AP_R2,(cx,cy),R)
    pygame.draw.circle(surf,AP_R1,(cx,cy),int(R*0.86))
    pygame.draw.circle(surf,(255,95,115),(cx,cy),int(R*0.58))
    pygame.draw.circle(surf,AP_R1,(cx,cy),R,2)
    br=max(2,R//4)
    pygame.draw.circle(surf,AP_SHINE,(cx-R//3,cy-R//3),br)
    pygame.draw.circle(surf,(255,235,240),(cx-R//3,cy-R//3),max(1,br//2))
    sw=max(1,CELL//20)
    pygame.draw.line(surf,AP_STEM,(cx,cy-R),(cx+max(1,CELL//10),cy-R-max(3,CELL//8)),sw+1)
    ls=CELL/32.0
    lx=cx+max(1,int(CELL//10)); ly=cy-R-max(1,int(CELL//12))
    leaf=[(lx,ly),(lx+int(9*ls),ly-int(6*ls)),(lx+int(6*ls),ly+int(3*ls))]
    pygame.draw.polygon(surf,AP_LEAF,leaf)
    pygame.draw.line(surf,(40,185,65),leaf[0],leaf[1],max(1,int(ls)))

def place_food(sn):
    while True:
        fx=random.randint(0,COLS-1); fy=random.randint(0,ROWS-1)
        if (fx,fy) not in sn: return fx,fy

# ══════════════════════════════════════════════════════════════
#  ПАНЕЛЬ
# ══════════════════════════════════════════════════════════════

def draw_panel(surf, W, score, best, lv, skin_key):
    pygame.draw.rect(surf,PANEL_C,(0,0,W,PANEL))
    for i,a in enumerate([50,140,50]):
        pygame.draw.line(surf,(*T_ACC,a),(0,PANEL-2+i),(W,PANEL-2+i))
    logo=F_MED.render("NEON SNAKE",True,T_ACC)
    surf.blit(logo,(W//2-logo.get_width()//2,8))
    surf.blit(F_XSM.render("СЧЁТ",True,T_DIM),(28,8))
    surf.blit(F_MED.render(str(score),True,T_ACC),(28,26))
    surf.blit(F_XSM.render("РЕКОРД",True,T_DIM),(170,8))
    surf.blit(F_MED.render(str(best),True,T_MN),(170,26))
    surf.blit(F_XSM.render("УРОВЕНЬ",True,T_DIM),(325,8))
    surf.blit(F_MED.render(str(lv),True,T_MN),(325,26))
    hint=F_XSM.render("F=экран  P=пауза  ESC=меню",True,T_DIM)
    surf.blit(hint,(W-hint.get_width()-16,30))
    skin=SKINS.get(skin_key,SKINS["neon_green"])
    pygame.draw.circle(surf,skin["glow"],(W-14,14),6)
    pygame.draw.circle(surf,skin["head1"],(W-14,14),4)

# ══════════════════════════════════════════════════════════════
#  ИКОНКИ ДЛЯ КНОПОК (рисуются через pygame, без файлов)
# ══════════════════════════════════════════════════════════════

def icon_play(surf, cx, cy, r, color):
    """Треугольник-плей"""
    pts = [
        (cx - r//2, cy - r),
        (cx - r//2, cy + r),
        (cx + r,    cy),
    ]
    pygame.draw.polygon(surf, color, pts)
    g = make_glow(r+2, color, 50)
    surf.blit(g, (cx-r-3, cy-r-3))

def icon_palette(surf, cx, cy, r, color):
    """Палитра — круг с точками"""
    pygame.draw.circle(surf, color, (cx, cy), r, 2)
    dots = [(cx, cy-r+4), (cx+r-4, cy), (cx, cy+r-4), (cx-r+4, cy)]
    dot_colors = [(255,80,80),(80,180,255),(80,255,120),(255,220,60)]
    for i,(dx,dy) in enumerate(dots):
        pygame.draw.circle(surf, dot_colors[i], (dx,dy), max(2, r//4))

def icon_trophy(surf, cx, cy, r, color):
    """Кубок"""
    # Чаша
    pygame.draw.arc(surf, color,
        pygame.Rect(cx-r, cy-r, r*2, r*2), math.pi, math.tau, 2)
    # Ручки
    pygame.draw.arc(surf, color,
        pygame.Rect(cx-r-r//2, cy-r//2, r, r), math.pi*0.5, math.pi*1.5, 2)
    pygame.draw.arc(surf, color,
        pygame.Rect(cx+r//2, cy-r//2, r, r), math.pi*1.5, math.pi*2.5, 2)
    # Ножка
    pygame.draw.line(surf, color, (cx, cy+r//2), (cx, cy+r), 2)
    pygame.draw.line(surf, color, (cx-r//2, cy+r), (cx+r//2, cy+r), 2)

def icon_gear(surf, cx, cy, r, color):
    """Шестерёнка"""
    pygame.draw.circle(surf, color, (cx, cy), r//2, 2)
    for i in range(8):
        a = i * math.tau / 8
        x1 = cx + int((r//2) * math.cos(a))
        y1 = cy + int((r//2) * math.sin(a))
        x2 = cx + int(r * math.cos(a))
        y2 = cy + int(r * math.sin(a))
        pygame.draw.line(surf, color, (x1,y1), (x2,y2), 2)

def icon_exit(surf, cx, cy, r, color):
    """Крестик выхода"""
    pygame.draw.line(surf, color, (cx-r, cy-r), (cx+r, cy+r), 3)
    pygame.draw.line(surf, color, (cx+r, cy-r), (cx-r, cy+r), 3)

MENU_ICONS = [icon_play, icon_palette, icon_trophy, icon_gear, icon_exit]

# ══════════════════════════════════════════════════════════════
#  ГЛАВНОЕ МЕНЮ
# ══════════════════════════════════════════════════════════════

class MainMenu:
    def __init__(self, W, H, save):
        self.save=save; self.tk=0
        cx=W//2; bw,bh=280,52; by=H//2-20; gap=66
        self.btns=[
            Button(cx-bw//2, by,        bw,bh,"▶  ИГРАТЬ",    T_ACC),
            Button(cx-bw//2, by+gap,     bw,bh,"🎨  СКИНЫ",    (200,100,255)),
            Button(cx-bw//2, by+gap*2,   bw,bh,"🏆  РЕКОРДЫ",  T_GOLD),
            Button(cx-bw//2, by+gap*3,   bw,bh,"⚙  НАСТРОЙКИ",T_MN),
            Button(cx-bw//2, by+gap*4,   bw,bh,"✕  ВЫХОД",    T_DANGER),
        ]

    def handle(self, event, save):
        for i,b in enumerate(self.btns):
            if b.is_clicked(event):
                if i==4: pygame.quit(); sys.exit()
                play_snd(SND_CLICK, save)
                return [STATE_GAME, STATE_SKINS, STATE_RECORDS, STATE_SETTINGS, None][i]
        return None

    def update(self, mx, my, dt):
        self.tk+=1
        for b in self.btns: b.update(mx,my,dt)

    def draw(self, surf, stars, W, H):
        surf.fill(BG)
        for st in stars: st.draw(surf)
        self._bg_snake(surf,W,H)
        draw_text_glow(surf,F_TITLE,"SNAKE",T_ACC,W//2,H//2-190,T_ACC,passes=4)
        sub=F_SM.render("NEON EDITION",True,T_DIM)
        surf.blit(sub,(W//2-sub.get_width()//2,H//2-118))
        best=self.save.get("best_score",0)
        games=self.save.get("total_games",0)
        st2=F_XSM.render(f"Игр: {games}   Лучший счёт: {best}   Сохранения: snake_save.json",True,T_DIM)
        surf.blit(st2,(W//2-st2.get_width()//2,H-36))
        for i, b in enumerate(self.btns):
            b.draw(surf, MENU_ICONS[i])

    def _bg_snake(self, surf, W, H):
        t=self.tk*0.025; skin=SKINS["neon_green"]; n=20
        for i in range(n):
            p=i/n; ax=t+p*math.tau*0.7; ay=t*0.7+p*math.tau*0.5
            x=int(W*0.08+W*0.84*(0.5+0.45*math.sin(ax)))
            y=int(H*0.08+H*0.84*(0.5+0.45*math.sin(ay)))
            r=max(3,int(18*(1-p*0.5))); al=int(25*(1-p))
            if al>2:
                col=lerpC(skin["head1"],skin["body2"],p)
                gs=pygame.Surface((r*4,r*4),pygame.SRCALPHA)
                pygame.draw.circle(gs,(*col,al),(r*2,r*2),r*2)
                surf.blit(gs,(x-r*2,y-r*2))

# ══════════════════════════════════════════════════════════════
#  ЭКРАН СКИНОВ
# ══════════════════════════════════════════════════════════════

class SkinsScreen:
    def __init__(self, W, H, save):
        self.selected=save.get("current_skin","neon_green"); self.tk=0
        self.back=Button(30,H-70,140,46,"← НАЗАД",T_DIM)
        self.apply=Button(W//2-100,H-70,200,46,"✔ ПРИМЕНИТЬ",T_ACC)
        self.cards=[]
        pr=3; cw,ch=220,140; gx,gy=30,24
        tw=pr*cw+(pr-1)*gx; sx=W//2-tw//2; sy=140
        for idx,key in enumerate(SKIN_KEYS):
            row=idx//pr; col=idx%pr
            cx=sx+col*(cw+gx); cy=sy+row*(ch+gy)
            self.cards.append({"key":key,"rect":pygame.Rect(cx,cy,cw,ch),"hover":0.0})

    def handle(self, event, save):
        if self.back.is_clicked(event):
            play_snd(SND_CLICK, save); return STATE_MENU, save
        if self.apply.is_clicked(event):
            save["current_skin"]=self.selected; save_data(save)
            play_snd(SND_CLICK, save); return STATE_MENU, save
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            for c in self.cards:
                if c["rect"].collidepoint(event.pos):
                    self.selected=c["key"]; play_snd(SND_CLICK, save)
        return None, save

    def update(self, mx, my, dt):
        self.tk+=1; self.back.update(mx,my,dt); self.apply.update(mx,my,dt)
        for c in self.cards:
            c["hover"]=lerp(c["hover"],1.0 if c["rect"].collidepoint(mx,my) else 0.0,dt*0.01)

    def draw(self, surf, stars, W, H):
        surf.fill(BG)
        for st in stars: st.draw(surf)
        draw_text_glow(surf,F_BIG,"СКИНЫ",T_ACC,W//2,48,T_ACC,passes=3)
        for c in self.cards:
            key=c["key"]; skin=SKINS[key]; r=c["rect"]
            t=ease_out(c["hover"]); is_sel=(key==self.selected)
            pygame.draw.rect(surf,lerpC(CARD_BG,BTN_HOVER,t),r,border_radius=14)
            bc=skin["glow"] if is_sel else lerpC(CARD_BORDER,skin["outline"],t*0.6)
            pygame.draw.rect(surf,bc,r,2 if is_sel else 1,border_radius=14)
            if is_sel:
                pygame.draw.circle(surf,skin["glow"],(r.right-16,r.top+16),10)
                pygame.draw.circle(surf,skin["head1"],(r.right-16,r.top+16),7)
                chk=F_XSM.render("✓",True,skin["head_dark"])
                surf.blit(chk,(r.right-23,r.top+8))
            segs=5; sr2=r.w//(segs*2+2)
            for si in range(segs):
                st2=si/max(segs-1,1); sx2=r.x+sr2+si*sr2*2; sy2=r.y+55
                col=lerpC(skin["head1"],skin["body2"],st2)
                pygame.draw.circle(surf,col,(sx2,sy2),sr2)
                gc=make_glow(sr2+3,skin["glow"],int(40*(1-st2)))
                surf.blit(gc,(sx2-sr2-4,sy2-sr2-4))
            nm=F_SM.render(skin["name"],True,lerpC(T_MN,skin["head1"],t))
            surf.blit(nm,(r.x+r.w//2-nm.get_width()//2,r.y+85))
            for di,dc in enumerate([skin["head1"],skin["head2"],skin["body1"],skin["glow"]]):
                pygame.draw.circle(surf,dc,(r.x+20+di*18,r.y+115),6)
        self.back.draw(surf); self.apply.draw(surf)

# ══════════════════════════════════════════════════════════════
#  ЭКРАН РЕКОРДОВ
# ══════════════════════════════════════════════════════════════

class RecordsScreen:
    def __init__(self, W, H):
        self.back=Button(30,H-70,140,46,"← НАЗАД",T_DIM)

    def handle(self, event, save):
        if self.back.is_clicked(event):
            play_snd(SND_CLICK, save)
            return STATE_MENU
        return None

    def update(self, mx, my, dt):
        self.back.update(mx,my,dt)

    def draw(self, surf, stars, save, W, H):
        surf.fill(BG)
        for st in stars: st.draw(surf)
        draw_text_glow(surf,F_BIG,"РЕКОРДЫ",T_GOLD,W//2,48,T_GOLD,passes=3)
        scores=save.get("highscores",[])
        if not scores:
            msg=F_MED.render("Пока нет рекордов — сыграй!",True,T_DIM)
            surf.blit(msg,(W//2-msg.get_width()//2,H//2))
        else:
            cw=420; ch=48; gap=10
            total_h=len(scores)*(ch+gap)
            sy=H//2-total_h//2+20
            for i,entry in enumerate(scores):
                cy2=sy+i*(ch+gap); cr=pygame.Rect(W//2-cw//2,cy2,cw,ch)
                bg=pygame.Surface((cw,ch),pygame.SRCALPHA)
                bg.fill((*CARD_BG,max(30,90-i*5))); surf.blit(bg,cr.topleft)
                bc=T_GOLD if i==0 else (T_MN if i<=2 else CARD_BORDER)
                pygame.draw.rect(surf,bc,cr,1,border_radius=8)
                medals=["🥇","🥈","🥉"]
                mc=F_SM.render(medals[i] if i<3 else f"{i+1}.",True,T_GOLD if i==0 else T_MN)
                surf.blit(mc,(cr.x+14,cy2+ch//2-mc.get_height()//2))
                sc_col=T_GOLD if i==0 else (T_ACC if i<3 else T_MN)
                sct=F_MED.render(str(entry["score"]),True,sc_col)
                surf.blit(sct,(cr.x+70,cy2+ch//2-sct.get_height()//2))
                dt2=F_XSM.render(entry.get("date",""),True,T_DIM)
                surf.blit(dt2,(cr.right-dt2.get_width()-14,cy2+ch//2-dt2.get_height()//2))
        # Путь к файлу сохранений
        path_t=F_XSM.render(f"Файл сохранений: {SAVE_FILE}",True,T_DIM)
        surf.blit(path_t,(W//2-path_t.get_width()//2,H-110))
        total=save.get("total_games",0); ts=save.get("total_score",0)
        avg=ts//total if total>0 else 0
        for i,txt in enumerate([f"Игр: {total}",f"Средний счёт: {avg}",f"Очков всего: {ts}"]):
            s2=F_SM.render(txt,True,T_DIM)
            surf.blit(s2,(W//2-s2.get_width()//2,H-88+i*24))
        self.back.draw(surf)

# ══════════════════════════════════════════════════════════════
#  НАСТРОЙКИ
# ══════════════════════════════════════════════════════════════

class SettingsScreen:
    def __init__(self, W, H, save):
        self.back=Button(30,H-70,140,46,"← НАЗАД",T_DIM)
        lbl="🔊 ЗВУК: ВКЛ" if save.get("sound_on",True) else "🔇 ЗВУК: ВЫКЛ"
        self.sound_btn=Button(W//2-140,H//2-50,280,52,lbl,T_ACC)
        self.clear_btn=Button(W//2-140,H//2+20,280,52,"🗑  ОЧИСТИТЬ РЕКОРДЫ",T_DANGER)
        self.open_btn =Button(W//2-140,H//2+90,280,52,"📂  ОТКРЫТЬ ПАПКУ",T_MN)

    def handle(self, event, save):
        if self.back.is_clicked(event):
            play_snd(SND_CLICK, save); return STATE_MENU, save
        if self.sound_btn.is_clicked(event):
            save["sound_on"]=not save.get("sound_on",True)
            self.sound_btn.text="🔊 ЗВУК: ВКЛ" if save["sound_on"] else "🔇 ЗВУК: ВЫКЛ"
            save_data(save)
        if self.clear_btn.is_clicked(event):
            save["highscores"]=[]; save["total_games"]=0
            save["total_score"]=0; save["best_score"]=0; save_data(save)
        if self.open_btn.is_clicked(event):
            folder=os.path.dirname(SAVE_FILE)
            try:
                import subprocess
                subprocess.Popen(f'explorer "{folder}"')
            except: pass
        return None, save

    def update(self, mx, my, dt):
        self.back.update(mx,my,dt); self.sound_btn.update(mx,my,dt)
        self.clear_btn.update(mx,my,dt); self.open_btn.update(mx,my,dt)

    def draw(self, surf, stars, save, W, H):
        surf.fill(BG)
        for st in stars: st.draw(surf)
        draw_text_glow(surf,F_BIG,"НАСТРОЙКИ",T_MN,W//2,48,T_MN,passes=3)
        path_t=F_XSM.render(f"Файл сохранений: {SAVE_FILE}",True,T_DIM)
        surf.blit(path_t,(W//2-path_t.get_width()//2,H//2-110))
        self.back.draw(surf); self.sound_btn.draw(surf)
        self.clear_btn.draw(surf); self.open_btn.draw(surf)

# ══════════════════════════════════════════════════════════════
#  ИГРОВОЙ ЭКРАН
# ══════════════════════════════════════════════════════════════

class GameScreen:
    def __init__(self, save):
        self.sn=[(10,10),(9,10),(8,10)]; self.d=(1,0); self.nd=(1,0)
        self.fd=place_food(self.sn); self.score=0
        self.best=save.get("best_score",0); self.lv=1; self.iv=165
        self.ma=0.0; self.tk=0; self.particles=[]; self.popups=[]; self.flashes=[]
        self.run=True; self.ps=False; self.go=False; self.new_best=False
        self.skin_key=save.get("current_skin","neon_green")
        self.skin=SKINS.get(self.skin_key,SKINS["neon_green"])

    def handle_key(self, key, save):
        if key==pygame.K_p and not self.go: self.ps=not self.ps
        if self.run and not self.ps and not self.go:
            if key in(pygame.K_UP,pygame.K_w) and self.d!=(0,1):  self.nd=(0,-1)
            if key in(pygame.K_DOWN,pygame.K_s) and self.d!=(0,-1):self.nd=(0,1)
            if key in(pygame.K_LEFT,pygame.K_a) and self.d!=(1,0): self.nd=(-1,0)
            if key in(pygame.K_RIGHT,pygame.K_d) and self.d!=(-1,0):self.nd=(1,0)

    def update(self, dt, save, ox, oy, CELL):
        self.tk+=1
        for f in self.flashes[:]:
            f.update(dt)
            if f.life<=0: self.flashes.remove(f)
        for p in self.particles[:]:
            p.update(dt)
            if p.life<=0: self.particles.remove(p)
        for pp in self.popups[:]:
            pp.update(dt)
            if pp.life<=0: self.popups.remove(pp)
        if not self.run or self.ps or self.go: return
        self.ma+=dt
        if self.ma>=self.iv:
            self.ma=0; self.d=self.nd
            hx=(self.sn[0][0]+self.d[0])%COLS
            hy=(self.sn[0][1]+self.d[1])%ROWS
            if(hx,hy) in self.sn[1:]:
                self.go=True
                if self.score>self.best: self.best=self.score; self.new_best=True
                add_score(save,self.score)
                play_snd(SND_DEATH,save)
                hcx=ox+self.sn[0][0]*CELL+CELL//2
                hcy=oy+self.sn[0][1]*CELL+CELL//2
                for _ in range(40): self.particles.append(Particle(hcx,hcy,CELL,T_DANGER))
                self.flashes.append(ScreenFlash(T_DANGER,0.4))
            else:
                self.sn.insert(0,(hx,hy))
                if(hx,hy)==self.fd:
                    self.score+=1
                    if self.score>self.best: self.best=self.score
                    play_snd(SND_EAT,save)
                    px=ox+self.fd[0]*CELL+CELL//2; py=oy+self.fd[1]*CELL+CELL//2
                    for _ in range(32): self.particles.append(Particle(px,py,CELL))
                    self.popups.append(ScorePopup(px,py-20,"+1",T_GOLD))
                    old_lv=self.lv; self.lv=self.score//5+1
                    self.iv=max(50,165-(self.lv-1)*14)
                    self.fd=place_food(self.sn)
                    if self.lv>old_lv:
                        play_snd(SND_LEVELUP,save)
                        self.flashes.append(ScreenFlash(T_ACC,0.25))
                        self.popups.append(ScorePopup(ox+COLS*CELL//2,oy+ROWS*CELL//2,f"УРОВЕНЬ {self.lv}!",T_ACC))
                else:
                    self.sn.pop()

    def draw(self, surf, stars, W, H, ox, oy, CELL):
        surf.fill(BG)
        for st in stars: st.draw(surf)
        draw_field_bg(surf,ox,oy,COLS*CELL,ROWS*CELL)
        draw_grid(surf,ox,oy,CELL)
        draw_food(surf,self.fd[0],self.fd[1],self.tk,CELL,ox,oy)
        draw_snake(surf,self.sn,CELL,ox,oy,self.skin,self.tk)
        for p in self.particles: p.draw(surf)
        for pp in self.popups: pp.draw(surf)
        for f in self.flashes: f.draw(surf,W,H)
        draw_panel(surf,W,self.score,self.best,self.lv,self.skin_key)
        if self.ps: self._draw_pause(surf,W,H)
        elif self.go: self._draw_gameover(surf,W,H)

    def _draw_pause(self, surf, W, H):
        ov=pygame.Surface((W,H),pygame.SRCALPHA); ov.fill((0,0,0,160)); surf.blit(ov,(0,0))
        draw_text_glow(surf,F_BIG,"ПАУЗА",T_ACC,W//2,H//2-60,T_ACC,passes=4)
        for i,t in enumerate(["P — продолжить","ESC — в меню"]):
            s=F_MED.render(t,True,T_DIM)
            surf.blit(s,(W//2-s.get_width()//2,H//2+10+i*44))

    def _draw_gameover(self, surf, W, H):
        ov=pygame.Surface((W,H),pygame.SRCALPHA); ov.fill((0,0,0,175)); surf.blit(ov,(0,0))
        draw_text_glow(surf,F_BIG,"КОНЕЦ ИГРЫ",T_DANGER,W//2,H//2-100,T_DANGER,passes=4)
        sc_t=F_BIG.render(str(self.score),True,T_ACC)
        surf.blit(sc_t,(W//2-sc_t.get_width()//2,H//2-30))
        if self.new_best:
            nb=F_MED.render("🏆  НОВЫЙ РЕКОРД!",True,T_GOLD)
            surf.blit(nb,(W//2-nb.get_width()//2,H//2+40))
        t2=F_MED.render("ENTER — снова    ESC — меню",True,T_DIM)
        surf.blit(t2,(W//2-t2.get_width()//2,H//2+90))

# ══════════════════════════════════════════════════════════════
#  ГЛАВНЫЙ ЦИКЛ
# ══════════════════════════════════════════════════════════════

def main():
    global _field_cache

    screen=pygame.display.set_mode((WIN_W,WIN_H),pygame.RESIZABLE)
    fullscreen=False
    save=load_save()
    stars=make_stars(WIN_W,WIN_H)

    state=STATE_MENU
    menu=MainMenu(WIN_W,WIN_H,save)
    skins_scr=SkinsScreen(WIN_W,WIN_H,save)
    records_scr=RecordsScreen(WIN_W,WIN_H)
    settings_scr=SettingsScreen(WIN_W,WIN_H,save)
    game=None

    clock=pygame.time.Clock()

    while True:
        dt=min(clock.tick(FPS),50)
        W=screen.get_width(); H=screen.get_height()
        avail_H=H-PANEL; CELL=min(W//COLS,avail_H//ROWS)
        field_W=COLS*CELL; field_H=ROWS*CELL
        ox=(W-field_W)//2; oy=PANEL+(avail_H-field_H)//2
        mx,my=pygame.mouse.get_pos()

        for st in stars: st.update(dt)

        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()

            if event.type==pygame.VIDEORESIZE and not fullscreen:
                screen=pygame.display.set_mode((event.w,event.h),pygame.RESIZABLE)
                stars=make_stars(event.w,event.h)
                _field_cache.clear(); clear_glow_cache()

            if event.type==pygame.KEYDOWN:
                key=event.key

                if key==pygame.K_f:
                    fullscreen=not fullscreen
                    screen=pygame.display.set_mode((0,0),pygame.FULLSCREEN) if fullscreen \
                        else pygame.display.set_mode((WIN_W,WIN_H),pygame.RESIZABLE)
                    stars=make_stars(screen.get_width(),screen.get_height())
                    _field_cache.clear(); clear_glow_cache()

                if key==pygame.K_ESCAPE:
                    if fullscreen:
                        fullscreen=False
                        screen=pygame.display.set_mode((WIN_W,WIN_H),pygame.RESIZABLE)
                        stars=make_stars(WIN_W,WIN_H)
                    elif state==STATE_GAME:
                        state=STATE_MENU; menu=MainMenu(W,H,save)
                    elif state in(STATE_SKINS,STATE_RECORDS,STATE_SETTINGS):
                        state=STATE_MENU
                    else:
                        pygame.quit(); sys.exit()

                if state==STATE_GAME and game:
                    if key in(pygame.K_RETURN,pygame.K_SPACE) and (game.go or not game.run):
                        game=GameScreen(save)
                    else:
                        game.handle_key(key,save)

            if state==STATE_MENU:
                r=menu.handle(event,save)
                if r==STATE_GAME: state=STATE_GAME; game=GameScreen(save)
                elif r==STATE_SKINS: state=STATE_SKINS; skins_scr=SkinsScreen(W,H,save)
                elif r==STATE_RECORDS: state=STATE_RECORDS; records_scr=RecordsScreen(W,H)
                elif r==STATE_SETTINGS: state=STATE_SETTINGS; settings_scr=SettingsScreen(W,H,save)
            elif state==STATE_SKINS:
                ns,save=skins_scr.handle(event,save)
                if ns: state=ns; menu=MainMenu(W,H,save)
            elif state==STATE_RECORDS:
                ns=records_scr.handle(event,save)
                if ns: state=ns
            elif state==STATE_SETTINGS:
                ns,save=settings_scr.handle(event,save)
                if ns: state=ns

        # Update
        if state==STATE_MENU: menu.update(mx,my,dt)
        elif state==STATE_SKINS: skins_scr.update(mx,my,dt)
        elif state==STATE_RECORDS: records_scr.update(mx,my,dt)
        elif state==STATE_SETTINGS: settings_scr.update(mx,my,dt)
        elif state==STATE_GAME and game: game.update(dt,save,ox,oy,CELL)

        # Draw
        if state==STATE_MENU: menu.draw(screen,stars,W,H)
        elif state==STATE_SKINS: skins_scr.draw(screen,stars,W,H)
        elif state==STATE_RECORDS: records_scr.draw(screen,stars,save,W,H)
        elif state==STATE_SETTINGS: settings_scr.draw(screen,stars,save,W,H)
        elif state==STATE_GAME and game: game.draw(screen,stars,W,H,ox,oy,CELL)

        pygame.display.flip()

if __name__ == "__main__":
    main()
