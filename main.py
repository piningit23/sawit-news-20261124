#!/usr/bin/env python3
"""Sum up Tuesday 24 November 2026's world news in one 1024x1024 image.

Draws a newspaper front page with PIL (stdlib + Pillow, no network):
lead story on Nvidia's rebound, plus NATO, Ukraine, Iran, Ulleung,
COP31, the Women's World Cup and the West Bank. Writes /output/entry.png.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BG = (13, 24, 40)        # deep navy paper
PANEL = (22, 36, 58)     # card navy
GOLD = (232, 184, 74)    # headline gold
CREAM = (244, 238, 222)  # body cream
MUTED = (168, 183, 201)  # muted blue-grey
GREEN = (74, 222, 128)   # market green
RED = (248, 113, 113)    # alert red
RULE = (58, 84, 120)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_TITLE = font("DejaVuSerif-Bold.ttf", 46)
F_KICK = font("DejaVuSans-Bold.ttf", 24)
F_HEAD = font("DejaVuSans-Bold.ttf", 34)
F_DECK = font("DejaVuSans.ttf", 23)
F_SMALL = font("DejaVuSans.ttf", 20)
F_BIG = font("DejaVuSans-Bold.ttf", 84)
F_FOOT = font("DejaVuSans.ttf", 18)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def card(draw, x, y, w, h, kick, kick_color, head, deck):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=PANEL)
    draw.text((x + 22, y + 16), kick, font=F_KICK, fill=kick_color)
    yy = y + 52
    for line in wrap(draw, head, F_HEAD, w - 44):
        draw.text((x + 22, yy), line, font=F_HEAD, fill=CREAM)
        yy += 40
    yy += 6
    for line in wrap(draw, deck, F_DECK, w - 44):
        draw.text((x + 22, yy), line, font=F_DECK, fill=MUTED)
        yy += 30
    return yy


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Masthead
    d.text((32, 22), "THE WORLD IN ONE PAGE", font=F_TITLE, fill=CREAM)
    d.text((32, 78), "TUESDAY  24  NOVEMBER  2026", font=F_KICK, fill=GOLD)
    d.line([(32, 122), (992, 122)], fill=RULE, width=3)

    # Lead story: Nvidia
    d.rounded_rectangle([32, 140, 992, 372], radius=16, fill=PANEL)
    d.text((56, 158), "MARKETS  •  LEAD STORY", font=F_KICK, fill=GREEN)
    d.text((56, 186), "HUANG IS BACK", font=font("DejaVuSans-Bold.ttf", 62), fill=CREAM)
    d.text((742, 168), "+31%", font=F_BIG, fill=GREEN)
    lead = ("Nvidia reinstates Jensen Huang as CEO, 11 days after his "
            "exit — shares soar 31% and Nasdaq jumps 6.5% in the biggest "
            "one-day gain in market value ever.")
    yy = 268
    for line in wrap(d, lead, F_DECK, 900):
        d.text((56, yy), line, font=F_DECK, fill=MUTED)
        yy += 30

    # 2 x 2 grid of stories
    gx, gy, gw, gh, gap = 32, 392, 468, 218, 24
    card(d, gx, gy, gw, gh, "NATO  •  EUROPE", GOLD,
         "AWACS TO POLAND",
         "Alliance sends its early-warning jet after Russian missiles "
         "land in Poland.")
    card(d, gx + gw + gap, gy, gw, gh, "WAR  •  LIBYA", RED,
         "UKRAINE SINKS CORVETTE",
         "Sea drones sink Russia's Merkury off Libya; cargo ship "
         "Angara hit too.")
    card(d, gx, gy + gh + gap, gw, gh, "GULF  •  STANDOFF", GOLD,
         "IRAN v THE BLOCKADE",
         "Tehran vows to break the US naval blockade; 14 tankers "
         "mass at Kharg.")
    card(d, gx + gw + gap, gy + gh + gap, gw, gh, "KOREA  •  SCARE", RED,
         "ULLEUNG: 3-MINUTE ALERT",
         "South Korea's evacuation warning as Russian jets enter "
         "its zone.")

    # Bottom strip: three briefs
    y0 = 864
    d.line([(32, y0), (992, y0)], fill=RULE, width=3)
    d.text((32, y0 + 12), "ALSO TODAY", font=F_KICK, fill=GOLD)
    briefs = [
        ("COP31 COLLAPSES", "No climate deal in Antalya — talks end without agreement."),
        ("WOMEN'S WORLD CUP", "2031: USA & co-hosts. 2035: United Kingdom."),
        ("WEST BANK", "Arson attacks hit five Palestinian villages overnight."),
    ]
    yy = y0 + 44
    for head, deck in briefs:
        d.text((32, yy), head + "  —  ", font=F_SMALL, fill=CREAM)
        tw = d.textlength(head + "  —  ", font=F_SMALL)
        d.text((32 + tw, yy), deck, font=F_SMALL, fill=MUTED)
        yy += 26

    d.text((32, 994), "Sources: Reuters · CNN · FIFA · UN News", font=F_FOOT, fill=MUTED)

    os.makedirs("/output", exist_ok=True)
    img.save("/output/entry.png", "PNG", optimize=True)


if __name__ == "__main__":
    main()
