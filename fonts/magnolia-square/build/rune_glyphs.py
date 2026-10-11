"""Glyph definitions for Magnolia Rune full charset.
Each function returns a list of shapely Polygons (clean, pre-distress).
Coordinate system: y-up, BASE=1, CAP=761.
"""
from rune_lib import *

CAPT = 761
BASE = 1

# ---------------- UPPERCASE ----------------
def g_B():
    s = stem(0)
    up = ring(330, 590, 200, 175, 125)
    lo = ring(350, 250, 215, 195, 125)
    return U(s, *up, *lo)

def g_C():
    r = ring(350, 381, 290, 300, 135)
    cut = rect(470, -60, 820, 860)
    body = [g.difference(cut) for g in r]
    # angled terminals
    return U(*[g for g in body if not g.is_empty])

def g_D():
    s = stem(0)
    r = ring(330, 381, 300, 300, 135)
    half = [g.intersection(rect(130, -50, 700, 860)) for g in r]
    return U(s, *[g for g in half if not g.is_empty])

def g_E():
    s = stem(0)
    t = hbar(0, 660, CAPT-125)
    m = hbar(0, 500, 320)
    b = hbar(0, 660, BASE)
    return U(s, *t, *m, *b)

def g_F():
    s = stem(0)
    t = hbar(0, 660, CAPT-125)
    m = hbar(0, 500, 320)
    return U(s, *t, *m)

def g_H():
    a = stem(0); b = stem(660)
    m = hbar(0, 800, 320)
    return U(a, b, *m)

def g_J():
    # right-side hook
    v = stem(320, y0=180, y1=CAPT)
    # remove bottom serif of that stem by rebuilding: use plain bar + top serif
    v = U(rect(320, 180, 460, CAPT), rect(320-42, CAPT-60, 460+42, CAPT-18),
          P([(320-42,CAPT-60),(460+42,CAPT-60),(460+42-18,CAPT),(320-42+18,CAPT)]))
    hook = ring(250, 250, 190, 190, 120)
    hook = [g.intersection(rect(40, -60, 440, 260)) for g in hook]
    hook = [g for g in hook if not g.is_empty]
    return U(v, *hook)

def g_K():
    s = stem(0)
    arm = diag(140, 360, 660, CAPT, 125)
    leg = diag(170, 400, 680, BASE, 135)
    return U(s, *arm, *leg)

def g_P():
    s = stem(0)
    b = ring(340, 555, 205, 205, 125)
    return U(s, *b)

def g_T():
    t = hbar(0, 780, CAPT-130)
    s = stem(320, y0=BASE, y1=CAPT-130)
    return U(*t, s)

def g_V():
    a = diag(10, CAPT, 320, BASE, 150)
    b = diag(630, CAPT, 320, BASE, 150)
    return U(*a, *b)

def g_W():
    a = diag(10, CAPT, 280, BASE, 140)
    b = diag(550, CAPT, 280, BASE, 140)
    c = diag(550, CAPT, 820, BASE, 140)
    d = diag(1090, CAPT, 820, BASE, 140)
    return U(*a, *b, *c, *d)

def g_X():
    a = diag(10, CAPT, 610, BASE, 145)
    b = diag(610, CAPT, 10, BASE, 145)
    return U(*a, *b)

def g_Y():
    a = diag(10, CAPT, 300, 400, 140)
    b = diag(590, CAPT, 300, 400, 140)
    s = stem(230, y0=BASE, y1=400)
    return U(*a, *b, s)

def g_Z():
    t = hbar(0, 720, CAPT-130)
    d = diag(590, CAPT-130, 130, 131, 130)
    b = hbar(0, 720, BASE)
    return U(*t, *d, *b)

UPPER = {
    'B': g_B, 'C': g_C, 'D': g_D, 'E': g_E, 'F': g_F,
    'H': g_H, 'J': g_J, 'K': g_K, 'P': g_P, 'T': g_T,
    'V': g_V, 'W': g_W, 'X': g_X, 'Y': g_Y, 'Z': g_Z,
}

# ---------------- LOWERCASE ----------------
LX = XH  # 470

def _stem(x, w=115, y0=BASE, y1=LX):
    return stem(x, w=w, y0=y0, y1=y1, serif=48, flare=36)

def g_a():
    b = ring(210, 235, 160, 175, 110)
    s = _stem(290, y1=LX)
    return U(*b, s)

def g_b():
    s = _stem(0, y0=BASE, y1=ASC)
    b = ring(280, 235, 175, 175, 110)
    return U(s, *b)

def g_c():
    r = ring(260, 235, 195, 175, 110)
    cut = rect(360, -60, 600, 600)
    return U(*[g.difference(cut) for g in r if not g.difference(cut).is_empty])

def g_d():
    b = ring(190, 235, 175, 175, 110)
    s = _stem(310, y0=BASE, y1=ASC)
    return U(*b, s)

def g_e():
    r = ring(260, 235, 185, 175, 110)
    bar = hbar(95, 425, 235, 95)
    return U(*r, *bar)

def g_f():
    s = _stem(160, y0=BASE, y1=ASC)
    hook = diag(160, ASC, 300, ASC-110, 105)
    cross = hbar(50, 400, 400, 90)
    return U(s, *hook, *cross)

def g_g():
    up = ring(240, 310, 175, 160, 110)
    lo = ring(240, -10, 160, 150, 105)
    link = rect(300, -60, 400, 200)
    return U(*up, *lo, link)

def g_h():
    s = _stem(0, y0=BASE, y1=ASC)
    arch = ring(300, 235, 185, 235, 135)
    arch = [g.intersection(rect(100, 235, 500, 500)) for g in arch]
    leg = rect(380, BASE, 510, 310)
    return U(s, *[g for g in arch if not g.is_empty], leg)

def g_i():
    s = _stem(140, y0=BASE, y1=LX)
    d = diamond(197, 610, 58)
    return U(s, *d)

def g_j():
    s = _stem(140, w=115, y0=DESC, y1=LX)
    hook = ring(170, -40, 130, 140, 100)
    hook = [g.intersection(rect(20, -220, 300, 40)) for g in hook]
    d = diamond(197, 610, 58)
    return U(s, *[g for g in hook if not g.is_empty], *d)

def g_k():
    s = _stem(0, y0=BASE, y1=ASC)
    arm = diag(115, 210, 360, LX, 100)
    leg = diag(140, 230, 380, BASE, 100)
    return U(s, *arm, *leg)

def g_l():
    return [_stem(140, y0=BASE, y1=ASC)][0:1] if False else U(_stem(140, y0=BASE, y1=ASC))

def g_m():
    s1 = _stem(0, y0=BASE, y1=LX)
    a1 = ring(300, 235, 165, 235, 130)
    a1 = [g.intersection(rect(130, 235, 475, 500)) for g in a1]
    a2 = ring(590, 235, 165, 235, 130)
    a2 = [g.intersection(rect(420, 235, 765, 500)) for g in a2]
    leg1 = rect(370, BASE, 480, 310)
    leg2 = rect(660, BASE, 770, 310)
    return U(s1, *[g for g in a1+a2 if not g.is_empty], leg1, leg2)

def g_n():
    s = _stem(0, y0=BASE, y1=LX)
    arch = ring(300, 235, 185, 235, 135)
    arch = [g.intersection(rect(100, 235, 500, 500)) for g in arch]
    leg = rect(380, BASE, 510, 310)
    return U(s, *[g for g in arch if not g.is_empty], leg)

def g_o():
    return ring(230, 235, 180, 175, 112)

def g_p():
    s = _stem(0, y0=DESC, y1=LX)
    b = ring(285, 235, 175, 175, 110)
    return U(s, *b)

def g_q():
    b = ring(195, 235, 175, 175, 110)
    s = _stem(320, y0=DESC, y1=LX)
    return U(*b, s)

def g_r():
    s = _stem(0, y0=BASE, y1=LX)
    fl = diag(115, 370, 300, LX, 95)
    return U(s, *fl)

def g_s():
    # angular s: top hook + bottom hook
    top = ring(220, 330, 150, 130, 100)
    top = [g.intersection(rect(60, 280, 400, 480)) for g in top]
    bot = ring(220, 140, 150, 130, 100)
    bot = [g.intersection(rect(40, -20, 380, 200)) for g in bot]
    mid = hbar(90, 350, 200, 95)
    parts = [g for g in top+bot if not g.is_empty]
    return U(*parts, *mid)

def g_t():
    s = _stem(150, y0=BASE, y1=620)
    cross = hbar(50, 390, 380, 90)
    foot = diag(150, 120, 300, BASE, 100)
    return U(s, *cross, *foot)

def g_u():
    a = _stem(0, y0=120, y1=LX)
    b = _stem(310, y0=120, y1=LX)
    bot = hbar(0, 425, BASE, 120)
    return U(a, b, *bot)

def g_v():
    a = diag(10, LX, 175, BASE, 115)
    b = diag(340, LX, 175, BASE, 115)
    return U(*a, *b)

def g_w():
    a = diag(10, LX, 160, BASE, 105)
    b = diag(310, LX, 160, BASE, 105)
    c = diag(310, LX, 460, BASE, 105)
    d = diag(610, LX, 460, BASE, 105)
    return U(*a, *b, *c, *d)

def g_x():
    a = diag(10, LX, 320, BASE, 110)
    b = diag(320, LX, 10, BASE, 110)
    return U(*a, *b)

def g_y():
    a = diag(10, LX, 175, 130, 110)
    b = diag(340, LX, 175, 130, 110)
    t = diag(175, 130, 60, DESC, 105)
    return U(*a, *b, *t)

def g_z():
    t = hbar(0, 360, 360, 110)
    d = diag(250, 360, 110, 111, 105)
    b = hbar(0, 360, BASE, 110)
    return U(*t, *d, *b)

LOWER = {
    'a': g_a, 'b': g_b, 'c': g_c, 'd': g_d, 'e': g_e, 'f': g_f,
    'g': g_g, 'h': g_h, 'i': g_i, 'j': g_j, 'k': g_k, 'l': g_l,
    'm': g_m, 'n': g_n, 'o': g_o, 'p': g_p, 'q': g_q, 'r': g_r,
    's': g_s, 't': g_t, 'u': g_u, 'v': g_v, 'w': g_w, 'x': g_x,
    'y': g_y, 'z': g_z,
}

# ---------------- DIGITS ----------------
DH = 701
def g_zero():
    return ring(230, 351, 195, 300, 128)
def g_one():
    s = stem(190, w=135, y0=BASE, y1=DH)
    fl = diag(190, DH, 70, DH-120, 95)
    ft = hbar(90, 420, BASE, 95)
    return U(s, *fl, *ft)
def g_two():
    # stroked 2: top curve sweeping into diagonal
    path = [(130,600),(200,668),(300,690),(390,650),(420,560),
            (400,470),(300,380),(180,260),(120,180)]
    body = stroke(path, 125)
    b = hbar(50, 480, BASE, 120)
    return U(*body, *b)
def g_three():
    # stroked 3: two open arcs
    path = [(170,620),(260,672),(350,650),(390,580),(360,510),
            (280,470),(200,450),(280,420),(360,380),(390,300),
            (350,210),(260,160),(170,190)]
    return stroke(path, 120)
def g_four():
    d = diag(330, DH, 70, 260, 115)
    m = hbar(70, 430, 260, 105)
    s = stem(320, w=125, y0=BASE, y1=DH)
    return U(*d, *m, s)
def g_five():
    t = hbar(70, 450, DH-120, 120)
    v = rect(70, 300, 190, DH)
    b = ring(250, 210, 195, 185, 118)
    return U(*t, v, *b)
def g_six():
    b = ring(235, 230, 195, 205, 120)
    curl = ring(235, 490, 175, 185, 112)
    curl = [g.intersection(rect(40, 420, 440, 720)) for g in curl]
    link = rect(60, 280, 170, 480)
    return U(*b, *[g for g in curl if not g.is_empty], link)
def g_seven():
    t = hbar(50, 470, DH-120, 120)
    d = diag(420, DH-120, 190, BASE, 125)
    return U(*t, *d)
def g_eight():
    t = ring(225, 525, 180, 165, 112)
    b = ring(225, 195, 195, 180, 118)
    return U(*t, *b)
def g_nine():
    t = ring(235, 490, 190, 195, 118)
    s = stem(330, w=125, y0=BASE, y1=490)
    return U(*t, s)

DIGITS = {
    'zero': g_zero, 'one': g_one, 'two': g_two, 'three': g_three,
    'four': g_four, 'five': g_five, 'six': g_six, 'seven': g_seven,
    'eight': g_eight, 'nine': g_nine,
}
DIGIT_CODEPOINTS = {'zero':48,'one':49,'two':50,'three':51,'four':52,'five':53,
                    'six':54,'seven':55,'eight':56,'nine':57}

# ---------------- PUNCTUATION ----------------
def g_period():
    return [rect(60, BASE, 185, 126)]
def g_comma():
    dot = rect(60, BASE, 185, 126)
    tail = P([(60,126),(185,126),(150,1),(95,-110),(35,-110),(70,1)])
    return U(dot, tail)
def g_exclam():
    bar = stem(150, w=125, y0=200, y1=DH)
    dot = rect(150, BASE, 275, 126)
    return U(bar, dot)
def g_question():
    hook = ring(215, 510, 175, 180, 112)
    hook = [g.intersection(rect(40, 380, 420, 720)) for g in hook]
    neck = diag(300, 400, 215, 230, 110)
    dot = rect(152, BASE, 277, 126)
    parts = [g for g in hook if not g.is_empty]
    return U(*parts, *neck, dot)
def g_quote():  # apostrophe
    return [P([(190,CAPT),(300,CAPT),(255,540),(165,540)])]
def g_hyphen():
    return hbar(90, 400, 270, 105)
def g_colon():
    return U(rect(60, BASE, 185, 126), rect(60, 350, 185, 476))
def g_semicolon():
    d = rect(60, 350, 185, 476)
    c = g_comma()
    return U(d, *c)

PUNCT = {
    'period': g_period, 'comma': g_comma, 'exclam': g_exclam,
    'question': g_question, 'quotesingle': g_quote, 'hyphen': g_hyphen,
    'colon': g_colon, 'semicolon': g_semicolon,
}
PUNCT_CODEPOINTS = {'period':46,'comma':44,'exclam':33,'question':63,
                    'quotesingle':39,'hyphen':45,'colon':58,'semicolon':59}

# ---------------- SYMBOLS ----------------
def g_at():
    outer = ring(310, 380, 265, 300, 130)
    inner = ring(310, 330, 125, 145, 92)
    inner = [g.intersection(rect(180, 180, 440, 480)) for g in inner]
    tail = diag(430, 480, 310, 200, 95)
    parts = [g for g in inner if not g.is_empty]
    return U(*outer, *parts, *tail)
def g_numbersign():
    v1 = rect(170, 100, 290, 660)
    v2 = rect(420, 100, 540, 660)
    h1 = hbar(90, 620, 440, 95)
    h2 = hbar(90, 620, 220, 95)
    return U(v1, v2, *h1, *h2)
def g_dollar():
    s = g_s()
    bar = rect(235, -90, 325, 790)
    return U(*s, bar)
def g_percent():
    t = ring(150, 560, 115, 115, 88)
    b = ring(370, 160, 115, 115, 88)
    d = diag(100, 660, 420, 60, 95)
    return U(*t, *b, *d)
def g_ampersand():
    up = ring(255, 545, 135, 135, 100)
    mid = hbar(110, 420, 380, 140)
    lo = ring(255, 215, 165, 155, 108)
    d = diag(140, 640, 390, 60, 115)
    return U(*up, *mid, *lo, *d)
def g_asterisk():
    c = hbar(120, 480, 400, 100)
    d1 = diag(180, 620, 420, 220, 100)
    d2 = diag(420, 620, 180, 220, 100)
    return U(*c, *d1, *d2)
def g_plus():
    return U(*hbar(140, 460, 290, 115), rect(242, 90, 357, 605))
def g_equal():
    return U(*hbar(100, 500, 440, 110), *hbar(100, 500, 220, 110))
def g_slash():
    return U(*diag(90, BASE, 430, CAPT, 115))
def g_backslash():
    return U(*diag(90, CAPT, 430, BASE, 115))
def g_bar():
    return [rect(195, BASE, 305, CAPT)]
def g_less():
    a = diag(410, 610, 130, 380, 115)
    b = diag(130, 380, 410, 150, 115)
    return U(*a, *b)
def g_greater():
    a = diag(130, 610, 410, 380, 115)
    b = diag(410, 380, 130, 150, 115)
    return U(*a, *b)
def g_tilde():
    pts = [(60,360),(170,430),(280,360),(390,430),(500,360),(500,270),
           (390,340),(280,270),(170,340),(60,270)]
    return [P(pts)]
def g_circum():
    a = diag(90, 300, 250, 490, 105)
    b = diag(410, 300, 250, 490, 105)
    return U(*a, *b)
def g_copyright():
    o = ring(310, 381, 265, 280, 122)
    c = ring(310, 381, 145, 155, 85)
    c = [g.difference(rect(310, 150, 500, 620)) for g in c]
    return U(*o, *[g for g in c if not g.is_empty])
def g_registered():
    o = ring(310, 381, 265, 280, 122)
    s = rect(230, 280, 320, 500)
    b = ring(360, 430, 90, 85, 62)
    leg = diag(320, 350, 430, 280, 60)
    inner = [g for g in U(s, *b, *leg)]
    return U(*o, *inner)
def g_trademark():
    t = hbar(80, 300, 560, 70)
    ts = rect(165, 380, 215, 630)
    m1 = rect(330, 380, 380, 630)
    m2 = diag(380, 630, 480, 430, 50)
    m3 = diag(580, 630, 480, 430, 50)
    m4 = rect(530, 380, 580, 630)
    return U(*t, ts, m1, *m2, *m3, m4)

SYMBOLS = {
    'at': g_at, 'numbersign': g_numbersign, 'dollar': g_dollar,
    'percent': g_percent, 'ampersand': g_ampersand, 'asterisk': g_asterisk,
    'plus': g_plus, 'equal': g_equal, 'slash': g_slash,
    'backslash': g_backslash, 'bar': g_bar, 'less': g_less,
    'greater': g_greater, 'asciitilde': g_tilde, 'asciicircum': g_circum,
    'copyright': g_copyright, 'registered': g_registered,
    'trademark': g_trademark,
}
SYMBOL_CODEPOINTS = {'at':64,'numbersign':35,'dollar':36,'percent':37,
    'ampersand':38,'asterisk':42,'plus':43,'equal':61,'slash':47,
    'backslash':92,'bar':124,'less':60,'greater':62,'asciitilde':126,
    'asciicircum':94,'copyright':169,'registered':174,'trademark':8482}
