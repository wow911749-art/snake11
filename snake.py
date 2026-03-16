import pygame, random, sys, math

pygame.init()

W, H, COLS, ROWS, CELL, PANEL = 700, 700, 25, 25, 28, 60
BG = (10,12,20); GC = (20,25,40); SH = (100,240,180); SB = (40,180,120)
SO = (20,120,80); FC = (230,60,80); FG = (255,100,100); PB = (14,18,32)
TM = (220,220,220); TD = (80,90,120); AC = (100,240,180); DG = (230,60,80)

sc = pygame.display.set_mode((W, H+PANEL))
pygame.display.set_caption("Snake")
cl = pygame.time.Clock()
fb = pygame.font.SysFont("consolas", 36, bold=True)
fm = pygame.font.SysFont("consolas", 22, bold=True)
fs = pygame.font.SysFont("consolas", 16)

class Star:
    def __init__(self): self.rs(random.randint(0, H+PANEL))
    def rs(self, y=None):
        self.x=random.randint(0,W); self.y=y if y is not None else 0
        self.r=random.uniform(.5,2); self.sp=random.uniform(.05,.25); self.a=random.randint(60,200)
    def up(self):
        self.y+=self.sp
        if self.y>H+PANEL: self.rs()
    def dw(self): pygame.draw.circle(sc,(self.a,self.a,self.a),(int(self.x),int(self.y)),max(1,int(self.r)))

stars = [Star() for _ in range(120)]

class Pt:
    def __init__(self,x,y):
        a=random.uniform(0,math.tau); sp=random.uniform(2,6)
        self.x=x; self.y=y; self.vx=math.cos(a)*sp; self.vy=math.sin(a)*sp
        self.l=1.; self.r=random.randint(3,7); self.c=random.choice([FC,FG,AC])
    def up(self): self.x+=self.vx; self.y+=self.vy; self.vy+=.15; self.l-=.04; self.r=max(1,self.r-.15)
    def dw(self):
        if self.l>0: pygame.draw.circle(sc,self.c,(int(self.x),int(self.y)),int(self.r))

pts = []

def dr(c,r,rd=6,bc=None,bw=2):
    pygame.draw.rect(sc,c,r,border_radius=rd)
    if bc: pygame.draw.rect(sc,bc,r,bw,border_radius=rd)

def dgr():
    for x in range(0,W,CELL): pygame.draw.line(sc,GC,(x,PANEL),(x,PANEL+H))
    for y in range(PANEL,PANEL+H+1,CELL): pygame.draw.line(sc,GC,(0,y),(W,y))

def dpn(score,best,lv,ps):
    pygame.draw.rect(sc,PB,(0,0,W,PANEL)); pygame.draw.line(sc,GC,(0,PANEL),(W,PANEL),2)
    sc.blit(fs.render("SCORE",True,TD),(24,8)); sc.blit(fm.render(str(score),True,AC),(24,26))
    sc.blit(fs.render("BEST",True,TD),(180,8)); sc.blit(fm.render(str(best),True,TM),(180,26))
    sc.blit(fs.render("LEVEL",True,TD),(340,8)); sc.blit(fm.render(str(lv),True,TM),(340,26))
    sc.blit(fs.render("P=pause  ESC=quit",True,TD),(420,22))
    if ps: p=fm.render("[ PAUSE ]",True,DG); sc.blit(p,(W//2-p.get_width()//2,18))

def dsn(sn):
    for i,(cx,cy) in enumerate(sn):
        x=cx*CELL; y=cy*CELL+PANEL; rect=pygame.Rect(x+2,y+2,CELL-4,CELL-4)
        if i==0:
            dr(SH,rect,8,AC,2)
            nd=(sn[1][0]-cx,sn[1][1]-cy) if len(sn)>1 else (0,0)
            eyes={(1,0):[(CELL-10,6),(CELL-10,CELL-10)],(-1,0):[(4,6),(4,CELL-10)],
                  (0,1):[(6,CELL-10),(CELL-10,CELL-10)],(0,-1):[(6,4),(CELL-10,4)]}.get((-nd[0],-nd[1]),[(6,6),(CELL-10,6)])
            for ex,ey in eyes:
                pygame.draw.circle(sc,BG,(x+ex,y+ey),3); pygame.draw.circle(sc,TM,(x+ex,y+ey),1)
        else:
            t=i/len(sn); co=(int(SB[0]*(1-t*.5)),int(SB[1]*(1-t*.4)),int(SB[2]*(1-t*.2))); dr(co,rect,6,SO,1)

def dfd(fx,fy,tk):
    p=math.sin(tk*.1)*.3+.7; x=fx*CELL+PANEL//2; y=fy*CELL+PANEL
    g=int((CELL//2+6)*p); gs=pygame.Surface((g*2+4,g*2+4),pygame.SRCALPHA)
    pygame.draw.circle(gs,(*FG,40),(g+2,g+2),g); sc.blit(gs,(x-g-2,y-g+CELL//2-2))
    rf=int((CELL//2-4)*p+3); pygame.draw.circle(sc,FC,(x+CELL//2,y+CELL//2),rf)
    pygame.draw.circle(sc,FG,(x+CELL//2-2,y+CELL//2-2),max(1,rf//3))

def dov(ti,su,score=None,best=None):
    ov=pygame.Surface((W,H+PANEL),pygame.SRCALPHA); ov.fill((0,0,0,170)); sc.blit(ov,(0,0))
    t1=fb.render(ti,True,AC); sc.blit(t1,(W//2-t1.get_width()//2,H//2-60+PANEL//2))
    t2=fm.render(su,True,TD); sc.blit(t2,(W//2-t2.get_width()//2,H//2+PANEL//2))
    if score is not None:
        s2=fm.render(f"Score: {score}   Best: {best}",True,TM)
        sc.blit(s2,(W//2-s2.get_width()//2,H//2+40+PANEL//2))

def pf(sn):
    while True:
        fx=random.randint(0,COLS-1); fy=random.randint(0,ROWS-1)
        if (fx,fy) not in sn: return fx,fy

def main():
    global pts
    sn=[(12,12),(11,12),(10,12)]; d=(1,0); fd=pf(sn)
    best=0; lv=1; tk=0; ma=0.; iv=150; nd=d
    score=0; run=False; ps=False; go=False; pts=[]
    while True:
        dt=cl.tick(60)
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_ESCAPE: pygame.quit(); sys.exit()
                if ev.key in (pygame.K_RETURN,pygame.K_SPACE):
                    if not run or go:
                        sn=[(12,12),(11,12),(10,12)]; d=(1,0); fd=pf(sn)
                        nd=d; lv=1; iv=150; pts=[]; score=0; run=True; go=False; ps=False; ma=0
                if ev.key==pygame.K_p and run and not go: ps=not ps
                if run and not ps and not go:
                    if ev.key in (pygame.K_UP,pygame.K_w) and d!=(0,1): nd=(0,-1)
                    if ev.key in (pygame.K_DOWN,pygame.K_s) and d!=(0,-1): nd=(0,1)
                    if ev.key in (pygame.K_LEFT,pygame.K_a) and d!=(1,0): nd=(-1,0)
                    if ev.key in (pygame.K_RIGHT,pygame.K_d) and d!=(-1,0): nd=(1,0)
        if run and not ps and not go:
            ma+=dt
            if ma>=iv:
                ma=0; d=nd; hx=(sn[0][0]+d[0])%COLS; hy=(sn[0][1]+d[1])%ROWS
                if (hx,hy) in sn[1:]: go=True; best=max(best,score)
                else:
                    sn.insert(0,(hx,hy))
                    if (hx,hy)==fd:
                        score+=1; best=max(best,score)
                        px=fd[0]*CELL+CELL//2; py=fd[1]*CELL+PANEL+CELL//2
                        for _ in range(18): pts.append(Pt(px,py))
                        fd=pf(sn); lv=score//5+1; iv=max(60,150-(lv-1)*12)
                    else: sn.pop()
        sc.fill(BG)
        for st in stars: st.up(); st.dw()
        dgr(); dfd(fd[0],fd[1],tk); dsn(sn)
        for p in pts[:]:
            p.up(); p.dw()
            if p.l<=0: pts.remove(p)
        dpn(score,best,lv,ps)
        if not run: dov("SNAKE","Press ENTER or SPACE to start")
        elif go: dov("GAME OVER","Press ENTER to play again",score,best)
        pygame.display.flip(); tk+=1

main()
