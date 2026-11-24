#!/usr/bin/env python3
"""Sum up Tuesday 24 November 2026's world news in one 1024x1024 image.

Standard library only: no Pillow, no fonts from disk, no network.
Draws a newspaper front page into a raw RGB framebuffer with a
hand-written 5x7 bitmap font, then encodes the PNG by hand
(struct + zlib). Deterministic: two runs are byte-identical.

Lead story: Nvidia reinstates Jensen Huang as CEO (+31%); plus
NATO AWACS to Poland, Ukraine sinking a Russian corvette off Libya,
Iran v the US naval blockade, the Ulleung evacuation alert, COP31,
the Women's World Cup hosts and the West Bank.

Writes entry.png into $MAKEFUN_OUTPUT_DIR (default /output).
"""
import os
import struct
import zlib

W, H = 1024, 1024
BG = (13, 24, 40)        # deep navy paper
PANEL = (22, 36, 58)     # card navy
GOLD = (232, 184, 74)    # headline gold
CREAM = (244, 238, 222)  # body cream
MUTED = (168, 183, 201)  # muted blue-grey
GREEN = (74, 222, 128)   # market green
RED = (248, 113, 113)    # alert red
RULE = (58, 84, 120)


# ---------------------------------------------------------------- PNG output

def _chunk(kind, data):
    body = kind + data
    return (struct.pack(">I", len(data)) + body
            + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))


def write_png(path, pixels):
    """pixels: bytes/bytearray of W*H*3 RGB. Writes a valid PNG."""
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)  # filter: none
        raw += pixels[y * stride:(y + 1) * stride]
    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


# ------------------------------------------------------------------ canvas

class Canvas:
    def __init__(self):
        self.px = bytearray(bytes(BG) * (W * H))

    def _off(self, x, y):
        return (y * W + x) * 3

    def set(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            o = self._off(x, y)
            self.px[o:o + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + w), min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            o = self._off(x0, yy)
            self.px[o:o + len(row)] = row

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def border(self, x, y, w, h, color, thick=2):
        self.fill_rect(x, y, w, thick, color)
        self.fill_rect(x, y + h - thick, w, thick, color)
        self.fill_rect(x, y, thick, h, color)
        self.fill_rect(x + w - thick, y, thick, h, color)


def text_width(text, scale):
    return len(text) * 6 * scale


def draw_text(cv, x, y, text, scale, color):
    """Draw uppercase text with the 5x7 bitmap font (see FONT below)."""
    cx = x
    for ch in text:
        glyph = FONT.get(ch)
        if glyph is None:
            glyph = FONT["?"]
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    cv.fill_rect(cx + col * scale, y + row * scale,
                                 scale, scale, color)
        cx += 6 * scale
    return cx


def wrap(text, scale, max_w):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------- 5x7 bitmap font
# Each glyph is 7 rows of 5 bits ("1" = ink). Written from scratch
# for this entry; every glyph below is my own drawing of the letter.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}


# ------------------------------------------------------------------ layout

def card(cv, x, y, w, h, kick, kick_color, head, deck):
    cv.fill_rect(x, y, w, h, PANEL)
    cv.border(x, y, w, h, RULE, 2)
    draw_text(cv, x + 22, y + 16, kick, 3, kick_color)
    yy = y + 52
    for line in wrap(head, 3, w - 44):
        draw_text(cv, x + 22, yy, line, 3, CREAM)
        yy += 7 * 3 + 6
    yy += 6
    for line in wrap(deck, 2, w - 44):
        draw_text(cv, x + 22, yy, line, 2, MUTED)
        yy += 7 * 2 + 5
    return yy


def main():
    cv = Canvas()

    # Masthead
    draw_text(cv, 32, 22, "THE WORLD IN ONE PAGE", 5, CREAM)
    draw_text(cv, 32, 78, "TUESDAY 24 NOVEMBER 2026", 3, GOLD)
    cv.hline(32, 122, 960, RULE, 3)

    # Lead story: Nvidia
    cv.fill_rect(32, 140, 960, 232, PANEL)
    cv.border(32, 140, 960, 232, RULE, 2)
    draw_text(cv, 56, 158, "MARKETS | LEAD STORY", 3, GREEN)
    draw_text(cv, 56, 186, "HUANG IS BACK", 6, CREAM)
    draw_text(cv, 742, 168, "+31%", 8, GREEN)
    lead = ("NVIDIA REINSTATES JENSEN HUANG AS CEO, 11 DAYS AFTER HIS "
            "EXIT - SHARES SOAR 31% AND NASDAQ JUMPS 6.5% IN THE BIGGEST "
            "ONE-DAY GAIN IN MARKET VALUE EVER.")
    yy = 268
    for line in wrap(lead, 3, 900):
        draw_text(cv, 56, yy, line, 3, MUTED)
        yy += 7 * 3 + 6

    # 2 x 2 grid of stories
    gx, gy, gw, gh, gap = 32, 392, 468, 218, 24
    card(cv, gx, gy, gw, gh, "NATO | EUROPE", GOLD,
         "AWACS TO POLAND",
         "ALLIANCE SENDS ITS EARLY-WARNING JET AFTER RUSSIAN MISSILES "
         "LAND IN POLAND.")
    card(cv, gx + gw + gap, gy, gw, gh, "WAR | LIBYA", RED,
         "UKRAINE SINKS CORVETTE",
         "SEA DRONES SINK RUSSIA'S MERKURY OFF LIBYA; CARGO SHIP "
         "ANGARA HIT TOO.")
    card(cv, gx, gy + gh + gap, gw, gh, "GULF | STANDOFF", GOLD,
         "IRAN V THE BLOCKADE",
         "TEHRAN VOWS TO BREAK THE US NAVAL BLOCKADE; 14 TANKERS "
         "MASS AT KHARG.")
    card(cv, gx + gw + gap, gy + gh + gap, gw, gh, "KOREA | SCARE", RED,
         "ULLEUNG: 3-MINUTE ALERT",
         "SOUTH KOREA'S EVACUATION WARNING AS RUSSIAN JETS ENTER "
         "ITS ZONE.")

    # Bottom strip: three briefs
    y0 = 864
    cv.hline(32, y0, 960, RULE, 3)
    draw_text(cv, 32, y0 + 12, "ALSO TODAY", 3, GOLD)
    briefs = [
        ("COP31 COLLAPSES", "NO CLIMATE DEAL IN ANTALYA - TALKS END WITHOUT AGREEMENT."),
        ("WOMEN'S WORLD CUP", "2031: USA AND CO-HOSTS. 2035: UNITED KINGDOM."),
        ("WEST BANK", "ARSON ATTACKS HIT FIVE PALESTINIAN VILLAGES OVERNIGHT."),
    ]
    yy = y0 + 44
    for head, deck in briefs:
        draw_text(cv, 32, yy, head + " - ", 2, CREAM)
        tw = text_width(head + " - ", 2)
        draw_text(cv, 32 + tw, yy, deck, 2, MUTED)
        yy += 7 * 2 + 5

    draw_text(cv, 32, 994, "SOURCES: REUTERS, CNN, FIFA, UN NEWS", 2, MUTED)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    write_png(os.path.join(out_dir, "entry.png"), cv.px)


if __name__ == "__main__":
    main()
