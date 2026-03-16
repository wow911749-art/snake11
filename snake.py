import pygame, random, sys, math

pygame.init()

# ── Константы ──────────────────────────────────────────────────────────────
COLS, ROWS = 25, 25
PANEL      = 64
FULLSCREEN = False

def make_screen(fs):
    if fs:
        return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        return pygame.display.set_mode((700, 764))

screen = make_screen(FULLSCREEN)
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

# ── Цвета ──────────────────────────────────────────────────────────────────
BG       = (10,  12,  20)
GC       = (18,  22,  38)
PB       = (14,  18,  32)
TM       = (220, 220, 220)
TD       = (80,  90,  120)
AC       = (80,  230, 160)
DG       = (230,  60,  80)

# Змейка — зелёный градиент
S_HEAD   = (120, 255, 180)
S_HEAD2  = (80,  210, 140)
S_BODY1  = (60,  200, 120)
S_BODY2  = (30,  140,  80)
S_OUT    = (20,   90,  55)
S_EYE    = (10,   15,  25)
S_PUPIL  = (255, 255, 255)

# Яблоко
A_RED    = (235,  55,  75)
A_RED2   = (200,  30,  50)
A_SHINE  = (255, 160, 160)
A_STEM   = (100, 170,  60)
A_LEAF   = (80,  200,  80)

# Частицы
P_COLS   = [(235,55,75),(255,120,100),(255,200,100),(80,230,160)]

# ── Шрифты ─────────────────────────────────────────────────────────────────
fb = pygame.font.SysFont("consolas", 38, bold=True)
fm = pygame.font.SysFont("consolas", 24, bold=True)
fs = pygame.font.SysFont("consolas", 15)

# ── Звёзды ─────────────────────────────────────────────────────────────────
class Star:
    def __init__(self): self.rs(random.randint(0, 900))
    def rs(self, y=None):
        self.x  = random.randint(0, 800)
        self.y  = y if y is not None else 0
        self.r  = random.uniform(.4, 1.8)
        self.sp = random.uniform(.03, .2)
        self.a  = random.randint(40, 180)
    def up(self, H):
        self.y += self.sp
        if self.y > H: self.rs()
    def dw(self, sc):
        pygame.draw.circle(sc, (self.a,self.a,self.a), (int(self.x), int(self.y)), max(1,int(self.r)))

stars = [Star() for _ in range(140)]

# ── Частицы ────────────────────────────────────────────────────────────────
class Pt:
    def __init__(self, x, y):
        a = random.uniform(0, math.tau); sp = random.uniform(2.5, 7)
        self.x=x; self.y=y; self.vx=math.cos(a)*sp; self.vy=math.sin(a)*sp
        self.l=1.; self.r=random.uniform(3,8)
        self.c=random.choice(P_COLS)
    def up(self):
        self.x+=self.vx; self.y+=self.vy; self.vy+=.18
        self.l-=.035; self.r=max(1,self.r-.12)
    def dw(self, sc):
        if self.l>0: pygame.draw.circle(sc,self.c,(int(self.x),int(self.y)),int(self.r))

pts = []

# ── Вспомогательные ────────────────────────────────────────────────────────
def rnd_rect(sc, color, rect, r=6, bc=None, bw=2):
    pygame.draw.rect(sc, color, rect, border_radius=r)
    if bc: pygame.draw.rect(sc, bc, rect, bw, border_radius=r)

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

# ── Рисование сетки ────────────────────────────────────────────────────────
def draw_grid(sc, W, H, CELL):
    for x in range(0, W, CELL):
        pygame.draw.line(sc, GC, (x, PANEL), (x, PANEL+H))
    for y in range(PANEL, PANEL+H+1, CELL):
        pygame.draw.line(sc, GC, (0, y), (W, y))

# ── Рисование панели ───────────────────────────────────────────────────────
def draw_panel(sc, W, score, best, lv, ps):
    pygame.draw.rect(sc, PB, (0, 0, W, PANEL))
    pygame.draw.line(sc, (30,38,65), (0, PANEL), (W, PANEL), 2)

    # Score
    sc.blit(fs.render("SCORE", True, TD), (24, 8))
    sc.blit(fm.render(str(score), True, AC), (24, 28))
    # Best
    sc.blit(fs.render("BEST",  True, TD), (160, 8))
    sc.blit(fm.render(str(best),  True, TM), (160, 28))
    # Level
    sc.blit(fs.render("LEVEL", True, TD), (296, 8))
    sc.blit(fm.render(str(lv),    True, TM), (296, 28))
    # Hint
    hint = fs.render("F=fullscreen  P=pause  ESC=quit", True, TD)
    sc.blit(hint, (W - hint.get_width() - 16, 26))

    if ps:
        p = fm.render("[ PAUSE ]", True, DG)
        sc.blit(p, (W//2 - p.get_width()//2, 20))

# ── Рисование змейки ───────────────────────────────────────────────────────
def draw_snake(sc, sn, CELL):
    n = len(sn)
    for i, (cx, cy) in enumerate(sn):
        x = cx*CELL; y = cy*CELL + PANEL
        t = i / max(n-1, 1)

        pad = 2 if i > 0 else 1
        rect = pygame.Rect(x+pad, y+pad, CELL-pad*2, CELL-pad*2)

        if i == 0:
            # Голова
            col  = S_HEAD
            col2 = S_HEAD2
            rnd_rect(sc, col,  rect, r=9)
            # Блик на голове
            shine = pygame.Rect(x+pad+2, y+pad+2, CELL//3, CELL//4)
            pygame.draw.ellipse(sc, (180,255,220), shine)
            # Контур
            pygame.draw.rect(sc, S_OUT, rect, 2, border_radius=9)

            # Глаза
            nd = (sn[1][0]-cx, sn[1][1]-cy) if n > 1 else (0,0)
            eye_map = {
                (1,0):  [(CELL-9, 6),  (CELL-9, CELL-10)],
                (-1,0): [(5, 6),       (5, CELL-10)],
                (0,1):  [(5, CELL-9),  (CELL-10, CELL-9)],
                (0,-1): [(5, 5),       (CELL-10, 5)],
            }
            eyes = eye_map.get((-nd[0],-nd[1]), [(6,6),(CELL-10,6)])
            for ex, ey in eyes:
                pygame.draw.circle(sc, S_EYE,   (x+ex, y+ey), 4)
                pygame.draw.circle(sc, S_PUPIL, (x+ex+1, y+ey-1), 1)
        else:
            # Тело — плавный градиент от зелёного к тёмному
            col = lerp_color(S_BODY1, S_BODY2, t)
            r   = max(3, 7 - int(t*3))
            rnd_rect(sc, col, rect, r=r)
            # Тонкий контур
            out = lerp_color(S_OUT, (10,50,30), t)
            pygame.draw.rect(sc, out, rect, 1, border_radius=r)
            # Блик на теле (только первые сегменты)
            if i < n*0.4:
                bx = x + pad + 2
                by = y + pad + 2
                bw2 = max(2, CELL//4)
                bh  = max(1, CELL//6)
                shine_s = pygame.Rect(bx, by, bw2, bh)
                pygame.draw.ellipse(sc, (160,255,200,80), shine_s)

# ── Рисование яблока ───────────────────────────────────────────────────────
def draw_food(sc, fx, fy, tick, CELL):
    # Центр клетки
    cx = fx * CELL + CELL // 2
    cy = fy * CELL + PANEL + CELL // 2

    # Пульс
    pulse = math.sin(tick * 0.08) * 0.12 + 0.88
    R = int((CELL // 2 - 3) * pulse)

    # Свечение (мягкое, в пределах одной клетки)
    glow_r = min(R + 5, CELL // 2 - 1)
    gsurf = pygame.Surface((glow_r*2+2, glow_r*2+2), pygame.SRCALPHA)
    pygame.draw.circle(gsurf, (*A_RED, 45), (glow_r+1, glow_r+1), glow_r)
    sc.blit(gsurf, (cx - glow_r - 1, cy - glow_r - 1))

    # Тело яблока
    pygame.draw.circle(sc, A_RED,  (cx, cy), R)
    pygame.draw.circle(sc, A_RED2, (cx, cy), R, 2)

    # Блик
    shine_x = cx - R//3
    shine_y = cy - R//3
    pygame.draw.circle(sc, A_SHINE, (shine_x, shine_y), max(2, R//4))

    # Стебель
    stem_x = cx
    stem_y = cy - R
    pygame.draw.line(sc, A_STEM, (stem_x, stem_y), (stem_x+2, stem_y-5), 2)

    # Листик
    leaf_pts = [
        (stem_x+2, stem_y-3),
        (stem_x+7, stem_y-6),
        (stem_x+4, stem_y-1),
    ]
    pygame.draw.polygon(sc, A_LEAF, leaf_pts)

# ── Оверлей ────────────────────────────────────────────────────────────────
def draw_overlay(sc, W, H, ti, su, score=None, best=None):
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 165))
    sc.blit(ov, (0, 0))
    t1 = fb.render(ti, True, AC)
    sc.blit(t1, (W//2 - t1.get_width()//2, H//2 - 70))
    t2 = fm.render(su, True, TD)
    sc.blit(t2, (W//2 - t2.get_width()//2, H//2))
    if score is not None:
        s2 = fm.render(f"Score: {score}    Best: {best}", True, TM)
        sc.blit(s2, (W//2 - s2.get_width()//2, H//2 + 44))

# ── Еда ────────────────────────────────────────────────────────────────────
def place_food(sn, COLS, ROWS):
    while True:
        fx = random.randint(0, COLS-1)
        fy = random.randint(0, ROWS-1)
        if (fx, fy) not in sn: return fx, fy

# ── Главный цикл ───────────────────────────────────────────────────────────
def main():
    global screen, FULLSCREEN, pts, stars

    sn = [(12,12),(11,12),(10,12)]; d=(1,0); fd=place_food(sn,COLS,ROWS)
    best=0; lv=1; tk=0; ma=0.; iv=150; nd=d
    score=0; run=False; ps=False; go=False; pts=[]

    while True:
        dt = clock.tick(60)

        W = screen.get_width()
        H = screen.get_height()
        GAME_H = H - PANEL
        CELL = min(GAME_H // ROWS, W // COLS)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

                # Полный экран
                if ev.key == pygame.K_f:
                    FULLSCREEN = not FULLSCREEN
                    screen = make_screen(FULLSCREEN)

                if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if not run or go:
                        sn=[(12,12),(11,12),(10,12)]; d=(1,0)
                        fd=place_food(sn,COLS,ROWS); nd=d
                        lv=1; iv=150; pts=[]; score=0
                        run=True; go=False; ps=False; ma=0

                if ev.key == pygame.K_p and run and not go:
                    ps = not ps

                if run and not ps and not go:
                    if ev.key in (pygame.K_UP,   pygame.K_w) and d!=(0, 1): nd=(0,-1)
                    if ev.key in (pygame.K_DOWN,  pygame.K_s) and d!=(0,-1): nd=(0, 1)
                    if ev.key in (pygame.K_LEFT,  pygame.K_a) and d!=(1, 0): nd=(-1,0)
                    if ev.key in (pygame.K_RIGHT, pygame.K_d) and d!=(-1,0): nd=(1, 0)

        # Логика
        if run and not ps and not go:
            ma += dt
            if ma >= iv:
                ma = 0; d = nd
                hx = (sn[0][0]+d[0]) % COLS
                hy = (sn[0][1]+d[1]) % ROWS
                if (hx,hy) in sn[1:]:
                    go=True; best=max(best,score)
                else:
                    sn.insert(0,(hx,hy))
                    if (hx,hy) == fd:
                        score+=1; best=max(best,score)
                        px = fd[0]*CELL + CELL//2
                        py = fd[1]*CELL + PANEL + CELL//2
                        for _ in range(22): pts.append(Pt(px,py))
                        fd=place_food(sn,COLS,ROWS)
                        lv=score//5+1; iv=max(55,150-(lv-1)*12)
                    else:
                        sn.pop()

        # Рисование
        screen.fill(BG)

        for st in stars: st.up(H); st.dw(screen)

        draw_grid(screen, W, GAME_H, CELL)
        draw_food(screen, fd[0], fd[1], tk, CELL)
        draw_snake(screen, sn, CELL)

        for p in pts[:]:
            p.up(); p.dw(screen)
            if p.l <= 0: pts.remove(p)

        draw_panel(screen, W, score, best, lv, ps)

        if not run:
            draw_overlay(screen, W, H, "SNAKE", "Press ENTER or SPACE to start")
        elif go:
            draw_overlay(screen, W, H, "GAME OVER", "Press ENTER to play again", score, best)

        pygame.display.flip()
        tk += 1

main()

