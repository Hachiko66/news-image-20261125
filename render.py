#!/usr/bin/env python3
"""Draw the 25 November 2026 world-news summary image (1024x1024 PNG).

Build-time tool only: run locally with Pillow. The graded entry (main.py)
just copies the finished entry.png into the output directory, so the
program that runs in the sandbox needs no fonts and no network.

Stories verified against wire reports published on Wednesday 25 November
2026 (events that happened, or were first reported, that day in some time
zone; the NATO card covers the alliance's response announced earlier in
the week, phrased as the deployment it ordered).
"""
from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
NAVY = (13, 32, 54)
PAPER = (255, 255, 255)
INK = (18, 26, 40)
MUTED = (74, 82, 96)
CRIMSON = (176, 38, 28)
GOLD = (214, 158, 58)
CARD = (240, 243, 247)
CARD_EDGE = (208, 216, 226)
SKY = (219, 232, 244)

BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
PLAIN_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def face(path, size):
    return ImageFont.truetype(path, size)


def fit_lines(text, fnt, width, limit):
    """Greedy word wrap, capped at `limit` lines."""
    words = text.split()
    out, current = [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if fnt.getlength(trial) <= width:
            current = trial
        else:
            if current:
                out.append(current)
            current = word
    if current:
        out.append(current)
    return out[:limit]


def globe(d, cx, cy, r, colour, w=4):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=colour, width=w)
    d.ellipse([cx - int(r * 0.42), cy - r, cx + int(r * 0.42), cy + r],
              outline=colour, width=w)
    d.line([cx - r, cy, cx + r, cy], fill=colour, width=w)
    d.arc([cx - r, cy - int(r * 0.6), cx + r, cy + int(r * 0.6)],
          205, 335, fill=colour, width=w)
    d.arc([cx - r, cy - int(r * 0.6), cx + r, cy + int(r * 0.6)],
          25, 155, fill=colour, width=w)


def tower(d, cx, cy, s, colour):
    """A tall skyscraper with a flame licking its crown."""
    d.rectangle([cx - int(s * 0.32), cy - s, cx + int(s * 0.32), cy + int(s * 0.8)],
                fill=colour)
    for row in range(5):
        yy = cy - int(s * 0.8) + row * int(s * 0.32)
        for col in (-1, 1):
            xx = cx + col * int(s * 0.14)
            d.rectangle([xx - 3, yy, xx + 3, yy + 10], fill=PAPER)
    d.polygon([(cx, cy - int(s * 1.45)), (cx - int(s * 0.3), cy - int(s * 0.95)),
               (cx + int(s * 0.3), cy - int(s * 0.95))], fill=CRIMSON)
    d.ellipse([cx - int(s * 0.3), cy - int(s * 1.15), cx + int(s * 0.3),
               cy - int(s * 0.55)], fill=CRIMSON)


def ship(d, cx, cy, s, colour):
    d.polygon([(cx - s, cy - int(s * 0.1)), (cx + s, cy - int(s * 0.1)),
               (cx + int(s * 0.65), cy + int(s * 0.4)),
               (cx - int(s * 0.65), cy + int(s * 0.4))], fill=colour)
    d.rectangle([cx - int(s * 0.4), cy - int(s * 0.45), cx + int(s * 0.4),
                 cy - int(s * 0.1)], fill=colour)
    d.line([cx, cy - int(s * 0.45), cx, cy - s], fill=colour, width=4)
    d.polygon([(cx, cy - s), (cx + int(s * 0.4), cy - int(s * 0.8)),
               (cx, cy - int(s * 0.62))], fill=colour)
    for dx in (-1, 0, 1):
        d.arc([cx + dx * int(s * 0.75) - int(s * 0.3), cy + int(s * 0.55),
               cx + dx * int(s * 0.75) + int(s * 0.3), cy + int(s * 0.9)],
              180, 360, fill=colour, width=3)


def scales(d, cx, cy, s, colour):
    d.line([cx, cy - s, cx, cy + int(s * 0.8)], fill=colour, width=4)
    d.line([cx - int(s * 0.8), cy - int(s * 0.6), cx + int(s * 0.8),
            cy - int(s * 0.6)], fill=colour, width=4)
    for side in (-1, 1):
        px = cx + side * int(s * 0.8)
        d.line([px, cy - int(s * 0.6), px, cy - int(s * 0.1)], fill=colour, width=3)
        d.polygon([(px - int(s * 0.32), cy - int(s * 0.1)),
                   (px + int(s * 0.32), cy - int(s * 0.1)),
                   (px, cy + int(s * 0.35))], outline=colour, width=3)
    d.rectangle([cx - int(s * 0.55), cy + int(s * 0.8), cx + int(s * 0.55),
                 cy + int(s * 0.95)], fill=colour)


def medal(d, cx, cy, s, colour):
    d.ellipse([cx - int(s * 0.55), cy - int(s * 0.55), cx + int(s * 0.55),
               cy + int(s * 0.55)], fill=colour)
    d.ellipse([cx - int(s * 0.22), cy - int(s * 0.22), cx + int(s * 0.22),
               cy + int(s * 0.22)], fill=PAPER)
    d.polygon([(cx - int(s * 0.45), cy - int(s * 0.5)),
               (cx - int(s * 0.15), cy - s),
               (cx + int(s * 0.15), cy - s),
               (cx + int(s * 0.45), cy - int(s * 0.5))], fill=NAVY)


def radar(d, cx, cy, s, colour):
    """AWACS-style jet seen from above, radar dome on its back."""
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=colour)
    d.rounded_rectangle([cx - 5, cy - s, cx + 5, cy + s], radius=5, fill=colour)
    d.polygon([(cx - s, cy - 4), (cx + s, cy - 4), (cx + 7, cy + 10),
               (cx - 7, cy + 10)], fill=colour)
    d.polygon([(cx - int(s * 0.5), cy + int(s * 0.7)),
               (cx + int(s * 0.5), cy + int(s * 0.7)),
               (cx + 5, cy + s), (cx - 5, cy + s)], fill=colour)


def ballot(d, cx, cy, s, colour):
    """A ballot box with a paper slip going in."""
    d.polygon([(cx - int(s * 0.25), cy - int(s * 0.9)),
               (cx + int(s * 0.35), cy - int(s * 0.9)),
               (cx + int(s * 0.15), cy - int(s * 0.35)),
               (cx - int(s * 0.45), cy - int(s * 0.35))], fill=colour)
    d.rectangle([cx - int(s * 0.8), cy - int(s * 0.35), cx + int(s * 0.8),
                 cy + int(s * 0.7)], fill=colour)
    d.line([cx - int(s * 0.5), cy - int(s * 0.35), cx + int(s * 0.5),
            cy - int(s * 0.35)], fill=PAPER, width=4)
    d.line([cx - int(s * 0.4), cy + int(s * 0.15), cx - int(s * 0.1),
            cy + int(s * 0.45)], fill=PAPER, width=4)
    d.line([cx - int(s * 0.1), cy + int(s * 0.45), cx + int(s * 0.45),
            cy - int(s * 0.05)], fill=PAPER, width=4)


def bat(d, cx, cy, s, colour):
    """A cricket bat striking a ball."""
    d.line([cx - int(s * 0.7), cy + int(s * 0.7), cx + int(s * 0.3),
            cy - int(s * 0.3)], fill=colour, width=7)
    d.rounded_rectangle([cx - int(s * 0.15), cy - int(s * 0.85),
                         cx + int(s * 0.45), cy - int(s * 0.25)],
                        radius=6, fill=colour)
    d.ellipse([cx + int(s * 0.5), cy - int(s * 0.75), cx + int(s * 0.85),
               cy - int(s * 0.4)], fill=CRIMSON)


ICONS = {
    "tower": tower,
    "ship": ship,
    "scales": scales,
    "medal": medal,
    "radar": radar,
    "ballot": ballot,
    "bat": bat,
}

LEAD_KICKER = "MIDDLE EAST  \u2014  RIYADH"
LEAD_HEADLINE = "HOUTHI DRONE HITS RIYADH\u2019S TALLEST TOWER"
LEAD_BODY = ("A drone strike on the PIF Tower wounds 11 people \u2014 the "
             "second hit on the capital\u2019s tallest tower in under a "
             "week, Saudi civil defence says.")

# (kicker, headline, summary, icon, accent)
GRID = [
    ("WAR AT SEA", "Kyiv confirms ship strike",
     "Zelenskiy says Ukraine hit the Russian ship Sparta II; Norway "
     "urges caution.",
     "ship", (46, 94, 140)),
    ("LAW", "Huawei guilty on 10 counts",
     "Guilty of trade-secret theft and bank fraud; cleared of "
     "racketeering.",
     "scales", (120, 60, 140)),
    ("USA", "Medal of Freedom for Giuliani",
     "Trump honours the former New York mayor, 82, in a private Oval "
     "Office ceremony.",
     "medal", (176, 38, 28)),
    ("EUROPE", "NATO radar jet for Poland",
     "An AWACS radar jet heads to Poland after Russian missiles landed "
     "there.",
     "radar", (14, 124, 123)),
    ("INDIA", "BJP and Akali Dal reunite",
     "The old allies revive their pact for the 2027 Punjab polls, six "
     "years after splitting.",
     "ballot", (185, 122, 15)),
    ("SPORT", "15-year-old smashes 204 off 53",
     "Sooryavanshi hits a record 28 sixes as India A chase down 250 "
     "against UAE in Doha.",
     "bat", (34, 120, 60)),
]

TICKER = [
    "CHESS  \u2022  Gukesh holds Sindarov in Game 1 of the World "
    "Championship \u2014 0.5\u20130.5",
    "USA  \u2022  Trump spares turkeys Freedom and Feathers  \u2022  "
    "MARKETS  \u2022  Anthropic below its $83 IPO price",
    "25 NOV  \u2022  International Day for the Elimination of Violence "
    "against Women",
]


def build():
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead ----
    d.rectangle([0, 0, SIZE, 146], fill=NAVY)
    d.text((34, 16), "THE WORLD IN ONE DAY",
           font=face(BOLD_PATH, 62), fill=PAPER)
    d.text((36, 100), "WEDNESDAY 25 NOVEMBER 2026",
           font=face(BOLD_PATH, 27), fill=GOLD)
    globe(d, 938, 73, 46, (126, 164, 205), w=5)
    d.rectangle([0, 146, SIZE, 154], fill=CRIMSON)

    # ---- Lead story ----
    d.text((36, 176), LEAD_KICKER, font=face(BOLD_PATH, 22), fill=CRIMSON)
    hy = 206
    for line in fit_lines(LEAD_HEADLINE, face(BOLD_PATH, 44), 700, 2):
        d.text((36, hy), line, font=face(BOLD_PATH, 44), fill=NAVY)
        hy += 52
    sy = hy + 8
    for line in fit_lines(LEAD_BODY, face(PLAIN_PATH, 25), 700, 3):
        d.text((36, sy), line, font=face(PLAIN_PATH, 25), fill=MUTED)
        sy += 32
    d.ellipse([812, 190, 988, 366], fill=SKY)
    tower(d, 900, 288, 52, NAVY)

    d.line([36, 416, SIZE - 36, 416], fill=CARD_EDGE, width=2)

    # ---- Story grid: 3 columns x 2 rows ----
    cw, ch, gap = 318, 232, 16
    x0, y0 = 14, 430
    for i, (kicker, headline, summary, icon, accent) in enumerate(GRID):
        x = x0 + (i % 3) * (cw + gap)
        y = y0 + (i // 3) * (ch + 14)
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=14,
                            fill=CARD, outline=CARD_EDGE, width=2)
        cx, cy, r = x + 46, y + 46, 30
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=accent)
        ICONS[icon](d, cx, cy, 21, PAPER)
        d.text((x + 88, y + 32), kicker, font=face(BOLD_PATH, 18), fill=accent)
        hy = y + 88
        for line in fit_lines(headline, face(BOLD_PATH, 25), cw - 30, 2):
            d.text((x + 15, hy), line, font=face(BOLD_PATH, 25), fill=INK)
            hy += 29
        sy = hy + 4
        for line in fit_lines(summary, face(PLAIN_PATH, 19), cw - 30, 3):
            d.text((x + 15, sy), line, font=face(PLAIN_PATH, 19), fill=MUTED)
            sy += 23

    # ---- Footer ticker ----
    d.rectangle([0, 924, SIZE, SIZE], fill=NAVY)
    ty = 938
    for line in TICKER:
        d.text((36, ty), line, font=face(PLAIN_PATH, 18), fill=PAPER)
        ty += 24

    img.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    build()
