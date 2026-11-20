from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import hashlib
import json
import math

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
SCALE = 4
SIZE = 1024
PAPER = (246, 241, 229)
INK = (23, 35, 59)
NAVY = (22, 50, 79)
RED = (179, 32, 44)
SLATE = (52, 61, 78)
GOLD = (198, 158, 66)
SEA = (203, 221, 228)
TAN = (226, 210, 175)
WHITE = (255, 255, 255)
GREY = (118, 122, 130)
RULE = (188, 182, 168)

FONT_PATHS = {
    "serif_cond_bold": [
        "/usr/share/fonts/truetype/noto/NotoSerifDisplay-CondensedBold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
    ],
    "serif_cond_bitalic": [
        "/usr/share/fonts/truetype/noto/NotoSerifDisplay-CondensedBoldItalic.ttf",
        "/usr/share/fonts/truetype/noto/NotoSerifDisplay-CondensedBold.ttf",
    ],
    "serif_bold": [
        "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSerifDisplay-CondensedBold.ttf",
    ],
    "sans_bold": [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "sans": [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "sans_cond": ["/usr/share/fonts/truetype/noto/NotoSansDisplay-Condensed.ttf"],
    "sans_cond_bold": ["/usr/share/fonts/truetype/noto/NotoSansDisplay-CondensedBold.ttf"],
}


@lru_cache(maxsize=None)
def font(kind, size):
    if size < 9.5:
        raise ValueError(f"Font below 9.5 px: {kind} {size}")
    for candidate in FONT_PATHS[kind]:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, round(size * SCALE))
    raise FileNotFoundError(f"No permitted font available for {kind}")


@dataclass(frozen=True)
class Story:
    number: int
    kicker: str
    headline: str
    deck: str
    source: str
    art: str
    status: str = "REPORTED"


STORIES = [
    Story(1, "ODISHA · STORM", "Akvan comes ashore", "Cyclone Akvan crosses the coast by noon near Gopalpur, winds 90–100 km/h gusting to 110. 300,000 people are out of harm's way, 423 rescue teams deployed, red alerts in 11 districts.", "IMD", "storm"),
    Story(2, "WASHINGTON · IRAN", "Trump puts the Iran decision off to 2027", "Trump says he is in no rush on Iran and will 'see what happens' after 1 January. The Senate rejects a war-powers curb 51–48 as Netanyahu presses for new strikes.", "Reuters", "calendar"),
    Story(3, "RIYADH · ATTACK", "A missile over Riyadh", "A Houthi missile damages the KAFD tower, one of Riyadh's tallest, in the financial district. No casualties are reported as air defences answer the strike.", "Reuters", "riyadh"),
    Story(4, "THE HAGUE · LAW", "The world answers the genocide verdict", "Britain expels Myanmar's defence attaché and seeks an urgent Security Council session. The Gambia presses for reparations after the court's 9–6 ruling.", "BBC · AP", "scales"),
    Story(5, "ANTALYA · CLIMATE", "COP31's final day: fossil fuels cut from the draft", "A revised draft drops the fossil-fuel phase-out pledge as the final plenary meets; delegates push past the Friday deadline. 23 nations back a wildfire plan; oceans stay in the deal.", "UN News", "climate"),
    Story(6, "NEW YORK · MARKETS", "Anthropic's debut can't stop the slide", "The Dow falls 1,100 points, the S&P 2.02%, the Nasdaq 2.25%. Anthropic opens at $111.50 and closes at $97.17.", "Bloomberg", "markets"),
    Story(7, "SHENZHEN · DIPLOMACY", "After the summit: '12 out of 10'", "Trump rates the three-way summit '12 out of 10'. Europe stays wary of a carve-up; Putin may attend the December G20 in Miami.", "AP", "flags"),
    Story(8, "SPACE · SCIENCE", "Voyager 1 crosses one light-day", "NASA confirms the probe is now more than one light-day from Earth — 16 billion miles out, the farthest a human-made object has ever travelled.", "NASA", "voyager"),
    Story(9, "VICE CITY · GAMES", "GTA VI passes $1.84bn", "Launch-day sales top The Odyssey's $1.80bn global run. Reviews land, streams break records, and the network buckles twice.", "Sensor Tower", "vice"),
    Story(10, "KYIV · WAR", "Europe ready to talk to Russia", "European leaders say they are ready for talks on ending the war in Ukraine, the BBC reports, as Kyiv watches Shenzhen and waits.", "BBC", "dove"),
    Story(11, "WELLINGTON · CRICKET", "Day two at the Basin", "New Zealand build on Henry Nicholls' unbeaten 113 as India hunt early wickets in the first Test.", "AP", "cricket"),
    Story(12, "TOKYO · SPACE", "Hayabusa2 gives up its landing", "Engine trouble forces Japan's Hayabusa2 probe to abandon its planned asteroid landing and rewrite its mission.", "JAXA", "asteroid"),
    Story(13, "SEOUL · LAW", "South Korea clears ex-PM Han", "The Supreme Court overturns former prime minister Han Duck-soo's conviction in the case tied to the 2024 martial-law declaration.", "Yonhap", "court"),
]

BRIEFS = [
    (14, "SUVA", "Fiji declares a national disaster over drought and water shortages."),
    (15, "CRIMEA", "A Ukrainian attack on the Crimean Bridge disrupts rail traffic."),
    (16, "CARACAS", "The US and Venezuela sign a deal to restore military cooperation."),
    (17, "CANBERRA", "Australia sanctions Israeli settlers over West Bank expansion."),
    (18, "SOFIA", "An LPG tanker that sank off Bulgaria was hit by projectiles, an official says."),
    (19, "TOKYO", "PM Takaichi calls for continued dialogue with China to ease tensions."),
    (20, "NEW DELHI", "The Sensex gains 700 points on Thursday; the Nifty tops 25,400."),
    (21, "FLORIDA", "The St. Johns River hits 38.3 ft; 100-plus rescued in Broward County."),
    (22, "MIAMI", "GTA VI festival on Saturday; the Heat's Vice City jersey sells out in 90 minutes. [FORECAST]"),
    (23, "ZURICH", "Infantino faces two challengers in the 2027 FIFA presidential race."),
    (24, "SEOUL", "Korea's National Museum draws record crowds ahead of the year-end."),
    (25, "JAMNAGAR", "The Indian Air Force opens exercise Setu 2026."),
    (26, "DUBAI", "An Indian shooter takes bronze at the Dubai Open shooting."),
    (27, "MUMBAI", "The RBI steps in to steady the rupee as foreign funds flow out."),
    (28, "LOS ANGELES", "GTA VI reviews land; Rockstar calls it the highest-rated game ever."),
    (29, "CALIFORNIA", "Snow falls across the Sierra as a storm moves in from the Pacific."),
    (30, "SINGAPORE", "Bitcoin steadies above $93,000 after the IPO drives crypto cash."),
    (31, "NEW DELHI", "Modi meets the Prince and Princess of Wales in Delhi."),
    (32, "KHARTOUM", "Sudan's army says it has broken the two-year siege of El Obeid."),
    (33, "CHAKWAL", "Train services are restored after an accident in Pakistan."),
    (34, "BEIJING", "Xi urges APEC economies to open trade and new technology."),
    (35, "BRUSSELS", "EU Commission hit by cyberattack, Politico reports."),
    (36, "WASHINGTON", "Trump aide floated ceding Guyanese land to Venezuela, Reuters says. [CLAIM]"),
    (37, "AUSTIN", 'Musk: "I\'m not MAGA"; regrets ~$500m spent on midterms. [CLAIM]'),
    (38, "NEW DELHI", "Sensex surges ~1,000 pts to 83,021; Goldman upgrades India."),
    (39, "SHENZHEN", "APEC leaders meet in Shenzhen; trade and the Iran war on the agenda."),
    (40, "WORLDWIDE", "World Children's Day marked around the globe."),
    (41, "BRUSSELS", "Second EU-UK summit opens in Brussels. [Consilium]"),
    (42, "BERLIN", "Kushner: Europe is united on Ukraine after Thursday's Coalition of the Willing meeting; US envoys to brief Moscow. [NewKerala]"),
    (43, "MANILA", "ASEAN+3 leaders adopt pacts on maritime trade, food and energy resilience. [Context.ph]"),
    (44, "MANILA", "Philippine industry urges a reciprocal US trade deal, warns against concessions. [Context.ph]"),
    (45, "MANILA", "PAL seals a Boeing–GE deal for 15 Dreamliners. [Context.ph]"),
    (46, "LONDON", "Gold slides 2.7% to $3,625, lowest in over a year. [MarketIndex]"),
    (47, "SYDNEY", "Asian stocks extend losses; global equities head for longest slide in three years. [MarketIndex]"),
    (48, "CANBERRA", "Australia sheds 43,600 jobs in October; unemployment rises to 4.9%. [MarketIndex]"),
    (49, "CHICAGO", "Fed's Goolsbee does not rule out a bigger December rate rise. [MarketIndex]"),
    (50, "SACRAMENTO", "Nvidia faces a California inquiry over chips reaching China. [MarketIndex]"),
]

STATS = [
    ("300,000", "evacuated ahead of Cyclone Akvan"),
    ("$1.84bn", "GTA VI's first-day sales, Sensor Tower est."),
    ("−1,100", "points the Dow lost on Thursday"),
    ("16bn miles", "Voyager 1 from Earth — one light-day out"),
    ("7.91m", "peak viewers watching GTA VI at once"),
    ("83,021", "Sensex record close as Goldman upgrades India"),
]
REGIONS = [
    ("EUROPE", 10, (41, 87, 152), (105, 174, 252), (4, 5, 10, 15, 18, 23, 35, 41, 42, 46)),
    ("THE AMERICAS", 12, RED, (250, 113, 124), (2, 6, 9, 16, 21, 22, 28, 29, 36, 37, 49, 50)),
    ("ASIA-PACIFIC", 20, (111, 65, 150), (195, 143, 246), (1, 7, 12, 13, 19, 20, 24, 25, 27, 30, 31, 33, 34, 38, 39, 43, 44, 45, 47, 48)),
    ("MIDEAST", 2, (139, 95, 24), (241, 182, 78), (3, 26)),
    ("AFRICA", 1, (47, 107, 74), (128, 209, 120), (32,)),
    ("OCEANIA", 3, (32, 110, 114), (89, 209, 200), (11, 14, 17)),
    ("WORLD", 2, (103, 107, 115), (181, 189, 199), (8, 40)),
]
REGION_COLORS = {number: (color, map_color) for _, _, color, map_color, numbers in REGIONS for number in numbers}
TIMELINE = [
    ("OVERNIGHT", "Crimean Bridge hit a third time"),
    ("~06:00 UTC", "APEC leaders meet in Shenzhen"),
    ("~10:00 UTC", "Trilateral declaration issued"),
    ("~14:00 UTC", "Houthi missile hits Riyadh KAFD"),
    ("EVENING", "Akvan makes landfall in Odisha"),
    ("LATE", "Wall Street slides; Dow −1,101"),
]
DATE_CHECK = "The Shenzhen summit's first meeting · the ICJ's genocide verdict itself · GTA VI's midnight launch in New Zealand · Anthropic's record IPO debut · Henry Nicholls' 113 not out on day one · Modi inaugurating the FICCI centenary · the first COP31 draft · a US court's summonses for Doval and Goel. · the Philippines–Chile trade deal, signed Thursday · US jobless claims at 203,000, released Thursday"
SOURCES = "Sources: Reuters, AP, AFP, BBC, IMD, NASA, Consilium, MarketIndex, NewKerala. Original drawings."
FOOTER = "Every story here happened, or was first reported, on Friday 20 November 2026. Disputed claims are attributed, not stated as fact."


def measure(text, kind, size):
    return font(kind, size).getlength(text) / SCALE


def wrap(text, width, kind, size):
    lines = []
    current = ""
    for word in text.split():
        if measure(word, kind, size) > width:
            raise ValueError(f"Unbreakable word exceeds {width}px: {word}")
        trial = f"{current} {word}" if current else word
        if measure(trial, kind, size) <= width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class Page:
    def __init__(self):
        self.image = Image.new("RGB", (SIZE * SCALE, SIZE * SCALE), PAPER)
        self.draw = ImageDraw.Draw(self.image)
        self.text_blocks = []
        self.art_elements = 0

    def rectangle(self, box, fill=None, outline=None, width=1):
        self.draw.rectangle(tuple(round(value * SCALE) for value in box), fill=fill, outline=outline, width=max(1, round(width * SCALE)))

    def line(self, points, fill=INK, width=1):
        self.draw.line([(round(horizontal * SCALE), round(vertical * SCALE)) for horizontal, vertical in points], fill=fill, width=max(1, round(width * SCALE)))

    def ellipse(self, box, fill, outline=None, width=1):
        self.draw.ellipse(tuple(round(value * SCALE) for value in box), fill=fill, outline=outline, width=max(1, round(width * SCALE)))

    def polygon(self, points, fill):
        self.draw.polygon([(round(horizontal * SCALE), round(vertical * SCALE)) for horizontal, vertical in points], fill=fill)

    def text(self, text, box, kind="sans", size=11, color=INK, leading=None, align="left", max_lines=None):
        left, top, right, bottom = box
        available_width = right - left
        lines = wrap(text, available_width, kind, size)
        if max_lines is not None and len(lines) > max_lines:
            raise ValueError(f"Too many lines ({len(lines)} > {max_lines}): {text}")
        leading = leading or size + 1
        chosen_font = font(kind, size)
        heights = []
        for line in lines:
            bounds = chosen_font.getbbox(line)
            heights.append((bounds[3] - bounds[1]) / SCALE)
        block_height = (len(lines) - 1) * leading + (heights[-1] if heights else 0)
        if block_height > bottom - top + 0.01:
            raise ValueError(f"Text too tall ({block_height:.2f} > {bottom - top:.2f}): {text}")
        for index, line in enumerate(lines):
            bounds = chosen_font.getbbox(line)
            ink_width = (bounds[2] - bounds[0]) / SCALE
            line_width = max(ink_width, measure(line, kind, size))
            if line_width > available_width + 0.01:
                raise ValueError(f"Text too wide ({line_width:.2f} > {available_width:.2f}): {line}")
            horizontal = left
            if align == "center":
                horizontal += (available_width - line_width) / 2
            elif align == "right":
                horizontal = right - line_width
            vertical = top + index * leading
            if index < len(lines) - 1 and heights[index] > leading:
                raise ValueError(f"Text lines overlap: {line}")
            if vertical + heights[index] > bottom + 0.01:
                raise ValueError(f"Text line exceeds its box: {line}")
            if horizontal < 0 or horizontal + ink_width > SIZE or vertical < 0 or vertical + heights[index] > SIZE:
                raise ValueError(f"Text outside page: {line}")
            self.draw.text((round(horizontal * SCALE - bounds[0]), round(vertical * SCALE - bounds[1])), line, font=chosen_font, fill=color)
        self.text_blocks.append({"text": text, "box": list(box), "font": kind, "size": size, "lines": len(lines), "height": block_height})
        return block_height


class Panel:
    def __init__(self, page, box, background):
        self.page = page
        self.box = box
        self.left, self.top, self.right, self.bottom = box
        self.inner = (self.left + 7, self.top + 7, self.right - 7, self.bottom - 7)
        page.rectangle(box, background, INK, 0.8)

    def point(self, horizontal, vertical):
        left, top, right, bottom = self.inner
        return left + horizontal / 1000 * (right - left), top + vertical / 100 * (bottom - top)

    def check(self, points, stroke=0):
        for horizontal, vertical in points:
            if not (self.left + 6 + stroke / 2 <= horizontal <= self.right - 6 - stroke / 2 and self.top + 6 + stroke / 2 <= vertical <= self.bottom - 6 - stroke / 2):
                raise ValueError(f"Illustration violates 6px clearance: {self.box} {(horizontal, vertical)}")
        self.page.art_elements += 1

    def rect(self, box, color, outline=None, stroke=0.7):
        left, top = self.point(box[0], box[1])
        right, bottom = self.point(box[2], box[3])
        self.check([(left, top), (right, bottom)], stroke if outline else 0)
        self.page.rectangle((left, top, right, bottom), color, outline, stroke)

    def oval(self, box, color, outline=None, stroke=0.7):
        left, top = self.point(box[0], box[1])
        right, bottom = self.point(box[2], box[3])
        self.check([(left, top), (right, bottom)], stroke if outline else 0)
        self.page.ellipse((left, top, right, bottom), color, outline, stroke)

    def poly(self, points, color):
        converted = [self.point(*point) for point in points]
        self.check(converted)
        self.page.polygon(converted, color)

    def line(self, points, color=INK, width=0.8):
        converted = [self.point(*point) for point in points]
        self.check(converted, width)
        self.page.line(converted, color, width)

    def label(self, text, box, size=9.5, color=WHITE, kind="sans_bold", align="center"):
        left, top = self.point(box[0], box[1])
        right, bottom = self.point(box[2], box[3])
        self.check([(left, top), (right, bottom)])
        self.page.text(text, (left, top, right, bottom), kind, size, color, align=align, max_lines=1)

    def star(self, horizontal, vertical, radius, color, points=5):
        center_horizontal, center_vertical = self.point(horizontal, vertical)
        coordinates = []
        for index in range(points * 2):
            angle = -math.pi / 2 + index * math.pi / points
            distance = radius if index % 2 == 0 else radius * 0.42
            coordinates.append((center_horizontal + math.cos(angle) * distance, center_vertical + math.sin(angle) * distance))
        self.check(coordinates)
        self.page.polygon(coordinates, color)


def draw_art(page, story, box):
    backgrounds = {"storm": (48, 65, 82), "calendar": SEA, "riyadh": (17, 26, 49), "scales": TAN, "climate": (198, 219, 207), "markets": (31, 47, 60), "flags": SEA, "voyager": (17, 26, 49), "vice": (219, 172, 177), "dove": NAVY, "cricket": (102, 142, 95), "asteroid": (24, 35, 54), "court": TAN}
    panel = Panel(page, box, backgrounds[story.art])
    if story.art == "storm":
        panel.rect((0, 69, 1000, 100), (27, 91, 110))
        for cloud in [(25, 1, 245, 43), (190, 0, 450, 49), (410, 2, 660, 43), (690, 1, 970, 45)]:
            panel.oval(cloud, (28, 43, 60))
        for horizontal in range(55, 980, 70):
            panel.line([(horizontal, 43), (horizontal - 14, 65)], SEA, 0.8)
        panel.poly([(760, 30), (808, 30), (820, 94), (750, 94)], PAPER)
        panel.rect((751, 29, 819, 41), GOLD)
        panel.poly([(744, 28), (785, 13), (827, 28)], RED)
        panel.poly([(812, 33), (974, 13), (974, 48)], (228, 211, 151))
        panel.poly([(915, 88), (938, 75), (959, 77), (978, 89), (959, 83), (944, 87)], SEA)
        panel.rect((12, 62, 471, 100), RED)
        panel.label("LANDFALL · NOON", (22, 67, 463, 99))
    elif story.art == "calendar":
        panel.rect((22, 8, 457, 77), NAVY)
        panel.rect((35, 18, 445, 67), PAPER)
        panel.label("2027", (40, 16, 440, 67), 23, INK, "serif_cond_bold")
        panel.rect((610, 2, 921, 98), PAPER, INK)
        panel.rect((610, 2, 921, 27), RED)
        panel.label("JANUARY", (620, 2, 911, 35), 9.5)
        panel.oval((714, 38, 810, 93), None, RED, 1.2)
        panel.label("1", (705, 39, 820, 99), 17, INK)
        panel.rect((20, 65, 563, 100), RED)
        panel.label("NOT BEFORE JANUARY", (25, 67, 555, 99))
    elif story.art == "riyadh":
        panel.oval((877, 1, 934, 44), (246, 233, 187))
        for horizontal, vertical in [(60, 12), (210, 31), (445, 6), (750, 8)]:
            panel.star(horizontal, vertical, 0.8, WHITE, 4)
        for left, top, right in [(30, 55, 115), (138, 32, 210), (237, 45, 329), (605, 49, 685), (710, 34, 785), (808, 62, 878), (900, 55, 981)]:
            panel.rect((left, top, right, 99), (48, 65, 88))
        panel.poly([(424, 20), (477, 4), (518, 24), (540, 99), (401, 99)], (111, 132, 152))
        for vertical in (32, 48, 64, 80):
            for horizontal in (435, 461, 488):
                panel.rect((horizontal, vertical, horizontal + 9, vertical + 5), GOLD)
        panel.line([(496, 18), (569, 10), (658, 4), (750, 2)], (180, 187, 192), 0.8)
        panel.rect((20, 66, 365, 100), RED)
        panel.label("KAFD · 02:14", (25, 68, 357, 100))
    elif story.art == "scales":
        for left in (46, 837):
            panel.rect((left, 16, left + 105, 28), PAPER)
            panel.rect((left + 25, 29, left + 80, 88), PAPER)
            panel.rect((left - 10, 89, left + 115, 98), INK)
        panel.line([(500, 7), (500, 96)], INK, 1.4)
        panel.line([(285, 25), (713, 25)], INK, 1.1)
        for center in (306, 695):
            panel.line([(center, 26), (center - 97, 65), (center + 97, 65), (center, 26)], INK, 0.8)
            panel.oval((center - 97, 53, center + 97, 79), GOLD)
        panel.rect((384, 92, 614, 99), INK)
    elif story.art == "climate":
        panel.oval((760, 2, 925, 80), GOLD)
        panel.poly([(48, 76), (210, 43), (674, 43), (858, 76)], NAVY)
        panel.rect((105, 76, 815, 99), NAVY)
        panel.rect((180, 9, 744, 67), PAPER)
        panel.label("FOSSIL FUELS", (193, 14, 730, 65), 9.5, INK)
        panel.line([(204, 20), (728, 57)], RED, 1.6)
    elif story.art == "markets":
        for vertical in (20, 52, 84):
            panel.line([(20, vertical), (980, vertical)], (77, 89, 97), 0.4)
        for index, (high, low) in enumerate([(12, 43), (20, 60), (16, 49), (37, 77), (53, 93), (44, 88), (68, 98)]):
            horizontal = 80 + index * 115
            color = (94, 148, 120) if index in (0, 2) else (204, 66, 74)
            panel.line([(horizontal, max(2, high - 8)), (horizontal, min(98, low + 6))], color, 0.8)
            panel.rect((horizontal - 26, high, horizontal + 26, low), color)
        panel.line([(65, 9), (350, 27), (530, 53), (786, 78), (957, 91)], (246, 107, 105), 1.6)
        panel.poly([(947, 64), (974, 96), (861, 94)], (246, 107, 105))
    elif story.art == "flags":
        panel.rect((0, 88, 1000, 100), (66, 116, 132))
        for left, top, right in [(12, 62, 68), (83, 45, 137), (865, 51, 909), (928, 65, 981)]:
            panel.rect((left, top, right, 86), NAVY)
        for left in (170, 430, 690):
            panel.line([(left, 3), (left, 98)], INK, 0.7)
        panel.rect((176, 4, 405, 66), RED)
        panel.star(204, 18, 1.7, GOLD)
        for horizontal, vertical in [(229, 9), (242, 17), (239, 29), (224, 37)]:
            panel.star(horizontal, vertical, 0.7, GOLD)
        panel.rect((436, 4, 665, 66), WHITE)
        for stripe in range(7):
            panel.rect((436, 4 + stripe * 62 / 13 * 2, 665, 4 + (stripe * 2 + 1) * 62 / 13), RED)
        panel.rect((436, 4, 532, 37.4), NAVY)
        for row_index in range(9):
            star_count = 6 if row_index % 2 == 0 else 5
            for column_index in range(star_count):
                panel.star(443 + column_index * 16 + (8 if star_count == 5 else 0), 7 + row_index * 3.4, 0.22, WHITE)
        for stripe, color in enumerate((WHITE, (43, 83, 141), RED)):
            panel.rect((696, 4 + stripe * 62 / 3, 925, 4 + (stripe + 1) * 62 / 3), color)
    elif story.art == "voyager":
        for horizontal, vertical in [(52, 16), (192, 71), (422, 4), (755, 19), (917, 78)]:
            panel.star(horizontal, vertical, 0.65, WHITE, 4)
        for angle in range(0, 360, 17):
            radians = math.radians(angle)
            panel.line([(510 + math.cos(radians) * 260, 51 + math.sin(radians) * 40), (510 + math.cos(radians + 0.055) * 260, 51 + math.sin(radians + 0.055) * 40)], GREY, 0.5)
        panel.poly([(350, 29), (497, 22), (491, 63), (420, 72)], SEA)
        panel.line([(430, 48), (625, 57), (789, 88)], TAN, 1.2)
        panel.rect((580, 45, 654, 70), GOLD)
        panel.line([(602, 47), (680, 8)], PAPER, 0.8)
    elif story.art == "vice":
        panel.oval((367, 2, 606, 92), (247, 204, 116))
        for left, top, right in [(7, 61, 100), (120, 36, 214), (238, 55, 348), (630, 46, 734), (758, 28, 858), (880, 60, 987)]:
            panel.rect((left, top, right, 87), (56, 43, 74))
        for center in (290, 803):
            panel.line([(center, 92), (center - 12, 21)], INK, 1.3)
            panel.poly([(center - 12, 21), (center - 88, 5), (center - 48, 37), (center - 12, 21), (center + 77, 10), (center + 40, 43), (center - 12, 21), (center - 4, 2), (center + 20, 32)], INK)
        panel.rect((0, 89, 1000, 100), INK)
        panel.poly([(420, 86), (453, 72), (548, 72), (580, 85), (625, 87), (627, 98), (388, 98), (390, 90)], RED)
        panel.poly([(462, 76), (532, 76), (549, 84), (445, 84)], SEA)
    elif story.art == "dove":
        for index in range(12):
            angle = index * math.pi / 6
            panel.star(288 + math.cos(angle) * 195, 50 + math.sin(angle) * 41, 1.35, GOLD)
        panel.poly([(555, 59), (614, 39), (665, 4), (692, 42), (771, 28), (737, 57), (814, 56), (757, 76), (642, 76), (606, 91), (610, 68)], PAPER)
        panel.poly([(761, 58), (816, 48), (801, 63)], GOLD)
    elif story.art == "cricket":
        panel.rect((324, 0, 697, 100), TAN)
        for horizontal in (545, 600, 655):
            panel.rect((horizontal, 17, horizontal + 9, 92), PAPER)
        panel.line([(538, 14), (677, 14)], INK, 0.8)
        panel.poly([(198, 92), (266, 98), (481, 39), (421, 21)], (177, 127, 66))
        panel.line([(448, 31), (513, 10)], INK, 1.6)
        panel.oval((733, 60, 805, 99), RED)
        panel.line([(765, 63), (750, 92)], PAPER, 0.6)
    elif story.art == "asteroid":
        for horizontal, vertical in [(60, 17), (195, 73), (608, 8), (945, 86)]:
            panel.star(horizontal, vertical, 0.7, WHITE, 4)
        panel.poly([(698, 4), (820, 8), (917, 45), (872, 87), (752, 98), (644, 70), (620, 34)], (146, 146, 142))
        for crater in [(697, 22, 751, 48), (797, 46, 875, 79), (695, 67, 730, 83)]:
            panel.oval(crater, (108, 110, 111))
        for horizontal in range(332, 600, 57):
            panel.line([(horizontal, 41), (horizontal + 28, 46)], GOLD, 0.8)
        panel.poly([(210, 16), (282, 24), (260, 57), (211, 49)], SEA)
        panel.rect((261, 39, 324, 59), GOLD)
        panel.line([(217, 30), (135, 4)], PAPER, 0.8)
    elif story.art == "court":
        panel.poly([(63, 27), (333, 0), (605, 27)], INK)
        panel.rect((90, 31, 579, 41), PAPER)
        for horizontal in (119, 253, 387, 520):
            panel.rect((horizontal, 44, horizontal + 30, 84), PAPER)
        panel.rect((77, 86, 595, 98), INK)
        panel.poly([(701, 58), (726, 67), (862, 20), (832, 9)], (122, 76, 48))
        panel.poly([(769, 7), (795, 0), (916, 38), (894, 52)], INK)
        panel.rect((671, 85, 960, 98), (122, 76, 48))


def title_height(story):
    lead = story.number <= 3
    width = (984 - 20) / 3 if lead else (984 - 40) / 5
    return len(wrap(story.headline, width, "serif_cond_bold", 26 if lead else 15)) * (26 if lead else 15)


def card_height(story, art_height):
    lead = story.number <= 3
    width = (984 - 20) / 3 if lead else (984 - 40) / 5
    deck_lines = len(wrap(story.deck, width, "sans", 12.5 if lead else 11))
    return art_height + (15 if lead else 12.5) + title_height(story) + (2 if lead else 1.5) + deck_lines * (13 if lead else 11.5) + 13


def status_chip(page, text, left, top):
    chip_width = measure(text, "sans_bold", 9.5) + 7
    page.rectangle((left, top, left + chip_width, top + 12), PAPER, RED, 0.6)
    page.text(text, (left + 3.5, top + 1, left + chip_width - 3.5, top + 11), "sans_bold", 9.5, RED, max_lines=1)


def draw_card(page, story, left, top, width, art_height, row_bottom):
    lead = story.number <= 3
    right = left + width
    draw_art(page, story, (left, top, right, top + art_height))
    cursor = top + art_height + (3 if lead else 2)
    kicker_size = 12 if lead else 10.5
    prefix = f"{story.number} · "
    prefix_width = measure(prefix, "sans_bold", kicker_size)
    page.text(prefix.rstrip(), (left, cursor, left + prefix_width, cursor + 13), "sans_bold", kicker_size, RED, max_lines=1)
    source_width = measure(story.source, "sans", 10) if lead else 0
    page.text(story.kicker, (left + prefix_width, cursor, right - source_width - (8 if lead else 0), cursor + 13), "sans_bold", kicker_size, INK, max_lines=1)
    if lead:
        page.text(story.source, (right - source_width, cursor + 1, right, cursor + 12), "sans", 10, GREY, align="right", max_lines=1)
    cursor = top + art_height + (15 if lead else 12.5)
    headline_height = title_height(story)
    page.text(story.headline, (left, cursor, right, cursor + headline_height), "serif_cond_bold", 26 if lead else 15, INK, 26 if lead else 15, max_lines=3)
    cursor += headline_height + (2 if lead else 1.5)
    deck_size = 12.5 if lead else 11
    deck_leading = 13 if lead else 11.5
    deck_line_count = len(wrap(story.deck, width, "sans", deck_size))
    page.text(story.deck, (left, cursor, right, cursor + deck_line_count * deck_leading), "sans", deck_size, SLATE, deck_leading, max_lines=4 if lead else 5)
    status_chip(page, story.status, left, row_bottom - 12)
    if not lead:
        page.text(story.source, (left + 65, row_bottom - 11, right, row_bottom), "sans", 9.5, GREY, align="right", max_lines=1)


def rich_tokens(number, place, text):
    tokens = [(f"{number} {place}", "sans_cond_bold", INK), ("—", "sans_cond", SLATE)]
    for word in text.split():
        tagged = word in ("[CLAIM]", "[FORECAST]")
        tokens.append((word, "sans_cond_bold" if tagged else "sans_cond", RED if tagged else SLATE))
    return tokens


def rich_lines(tokens, width, size):
    lines = [[]]
    used = 0
    for word, kind, color in tokens:
        word_width = measure(word, kind, size)
        space = measure(" ", kind, size) if lines[-1] else 0
        if used + space + word_width > width:
            lines.append([])
            used = 0
            space = 0
        if word_width > width:
            raise ValueError(f"Brief word wider than column: {word}")
        lines[-1].append((word, kind, color, space, word_width))
        used += space + word_width
    if len(lines) > 2:
        raise ValueError("Brief exceeds two lines")
    return lines


def draw_briefs(page, left, top, width):
    column_width = (width - 12) / 2
    size = 9.5
    leading = 9.5
    entries = [(number, rich_lines(rich_tokens(number, place, text), column_width - 8, size)) for number, place, text in BRIEFS]
    heights = [len(lines) * leading + 0.5 for _, lines in entries]
    split = min(range(1, len(entries)), key=lambda index: abs(sum(heights[:index]) - sum(heights[index:])))
    end_positions = []
    for column_index, column in enumerate((entries[:split], entries[split:])):
        cursor = top
        column_left = left + column_index * (column_width + 12)
        for number, lines in column:
            page.ellipse((column_left, cursor + 3, column_left + 4, cursor + 7), REGION_COLORS[number][0])
            for line_index, line in enumerate(lines):
                horizontal = column_left + 7
                baseline = cursor + line_index * leading + 7.5
                for word, kind, color, space, word_width in line:
                    horizontal += space
                    bounds = font(kind, size).getbbox(word, anchor="ls")
                    ink_top = baseline + bounds[1] / SCALE
                    page.text(word, (horizontal + bounds[0] / SCALE, ink_top, horizontal + word_width + 1, baseline + bounds[3] / SCALE), kind, size, color, max_lines=1)
                    horizontal += word_width
            cursor += len(lines) * leading + 0.5
        end_positions.append(cursor)
    return max(end_positions)


def inside_polygon(horizontal, vertical, polygon):
    inside = False
    previous = len(polygon) - 1
    for current in range(len(polygon)):
        current_horizontal, current_vertical = polygon[current]
        previous_horizontal, previous_vertical = polygon[previous]
        if (current_vertical > vertical) != (previous_vertical > vertical):
            crossing = (previous_horizontal - current_horizontal) * (vertical - current_vertical) / (previous_vertical - current_vertical) + current_horizontal
            if horizontal < crossing:
                inside = not inside
        previous = current
    return inside


def draw_map(page, box):
    left, top, right, bottom = box
    width = right - left
    page.rectangle(box, NAVY)
    page.text("WHERE IT HAPPENED", (left + 9, top + 8, right - 8, top + 22), "sans_bold", 11, WHITE, max_lines=1)
    def project(longitude, latitude):
        return (longitude + 180) / 360 * 100, (85 - latitude) / 150 * 100

    geographic_outlines = [
        [(-168, 71), (-137, 70), (-125, 60), (-110, 70), (-85, 74), (-52, 52), (-62, 44), (-80, 25), (-89, 21), (-100, 17), (-111, 30), (-125, 49), (-168, 60)],
        [(-53, 83), (-20, 80), (-42, 59), (-55, 59)],
        [(-81, 12), (-63, 10), (-35, -6), (-49, -27), (-67, -55), (-75, -39), (-71, -16)],
        [(-10, 36), (-10, 59), (6, 71), (30, 70), (43, 53), (34, 36)],
        [(30, 70), (80, 76), (150, 68), (179, 60), (154, 45), (142, 32), (129, 37), (120, 22), (103, 2), (97, 12), (78, 8), (68, 27), (45, 30), (34, 45)],
        [(-17, 36), (10, 37), (35, 30), (51, 11), (40, -9), (31, -35), (17, -35), (8, -5), (-16, 13)],
        [(112, -12), (134, -10), (153, -27), (141, -39), (116, -34)],
        [(143, 45), (145, 40), (140, 35), (132, 32)],
        [(166, -34), (179, -38), (175, -47), (168, -45)],
    ]
    continents = [[project(*point) for point in outline] for outline in geographic_outlines]
    map_left = left + 8
    map_top = top + 23
    map_width = width - 19
    map_height = min(119, bottom - top - 67)
    for horizontal in range(4, 104, 2):
        for vertical in range(0, 100, 4):
            if any(inside_polygon(horizontal, vertical, continent) for continent in continents):
                center_horizontal = map_left + horizontal / 100 * map_width
                center_vertical = map_top + vertical / 100 * map_height
                page.ellipse((center_horizontal - 1, center_vertical - 1, center_horizontal + 1, center_vertical + 1), TAN)
    brief_locations = [(178, -18), (36, 45), (-67, 10), (149, -35), (23, 43), (140, 36), (77, 29), (-82, 29), (-80, 26), (8.5, 47), (127, 38), (70, 22), (55, 25), (73, 19), (-118, 34), (-120, 39), (104, 1), (77, 29), (33, 16), (73, 33), (116, 40), (4, 51), (-77, 39), (-98, 30), (77, 29), (114, 23), (0, 0), (4, 51), (13.4, 52.5), (121, 14.6), (121, 14.6), (121, 14.6), (-0.1, 51.5), (151.2, -33.9), (149, -35), (-87.6, 41.9), (-121.5, 38.6)]
    for number, (longitude, latitude) in enumerate(brief_locations, start=14):
        horizontal, vertical = project(longitude, latitude)
        center_horizontal = map_left + horizontal / 100 * map_width
        center_vertical = map_top + vertical / 100 * map_height
        radius = 1.6
        if (longitude, latitude) == (149, -35):
            radius = 2.8 if number == 17 else 1.2
        page.ellipse((center_horizontal - radius, center_vertical - radius, center_horizontal + radius, center_vertical + radius), REGION_COLORS[number][1])
    pins = {
        1: ((84.9, 19.3), (75, 63)), 2: ((-77, 38.9), (18, 27)),
        3: ((46.6, 24.7), (64, 62)), 4: ((4.3, 52.1), (46, 12)),
        5: ((30.7, 36.9), (54, 45)), 6: ((-74, 40.7), (36, 18)),
        7: ((114.1, 22.5), (87, 62)), 8: (None, (97, 7)),
        9: ((-80.2, 25.8), (28, 55)), 10: ((30.5, 50.45), (62, 13)),
        11: ((174.8, -41.3), (97, 94)), 12: ((139.7, 35.7), (98, 31)),
        13: ((127, 37.6), (83, 21)),
    }
    for number, (location, label_position) in pins.items():
        horizontal, vertical = label_position
        center_horizontal = map_left + horizontal / 100 * map_width
        center_vertical = map_top + vertical / 100 * map_height
        if location is not None:
            anchor_horizontal, anchor_vertical = project(*location)
            anchor_horizontal = map_left + anchor_horizontal / 100 * map_width
            anchor_vertical = map_top + anchor_vertical / 100 * map_height
            page.line([(center_horizontal, center_vertical), (anchor_horizontal, anchor_vertical)], SEA, 0.45)
            page.ellipse((anchor_horizontal - 1.5, anchor_vertical - 1.5, anchor_horizontal + 1.5, anchor_vertical + 1.5), REGION_COLORS[number][1])
        radius = 8 if number >= 10 else 7
        page.ellipse((center_horizontal - radius, center_vertical - radius, center_horizontal + radius, center_vertical + radius), RED, PAPER, 0.6)
        page.text(str(number), (center_horizontal - radius + 1, center_vertical - 5, center_horizontal + radius - 1, center_vertical + 6), "sans_bold", 9.5, WHITE, align="center", max_lines=1)
    legend_top = map_top + map_height + 11
    page.line([(left + 9, legend_top), (right - 9, legend_top)], SEA, 0.5)
    for index, (name, _, _, color, _) in enumerate(REGIONS):
        row, column = divmod(index, 4)
        horizontal = left + 9 + (0, 52, 109, 183)[column]
        vertical = legend_top + 7 + row * 12
        page.ellipse((horizontal, vertical + 2, horizontal + 4, vertical + 6), color)
        label = name.removeprefix("THE ").title()
        page.text(label, (horizontal + 7, vertical, right - 8, vertical + 10), "sans", 9.5, SEA, max_lines=1)
    page.text("Red numbers mark stories 1–13; dots mark briefs.", (left + 9, legend_top + 34, right - 8, bottom - 6), "sans", 9.5, SEA, max_lines=1)


def render():
    if len(STORIES) != 13 or len(BRIEFS) != 37 or sum(count for _, count, _, _, _ in REGIONS) != 50:
        raise ValueError("Expected 13 cards, 37 briefs, and 50 stories")
    page = Page()
    measurements = {}
    page.text("THE WORLD IN ONE DAY", (20, 12, 350, 27), "sans_bold", 13, RED, max_lines=1)
    page.text("FRIDAY'S NEWS · ONE PAGE · 50 STORIES", (600, 12, 1004, 27), "sans_bold", 13, INK, align="right", max_lines=1)
    page.line([(20, 29), (1004, 29)], INK, 2)
    measurements["brand bottom"] = 30
    page.text("Friday 20 November 2026", (20, 33, 1004, 104), "serif_cond_bold", 70, INK, align="center", max_lines=1)
    page.text("Akvan comes ashore · Trump puts Iran off to 2027 · A missile over Riyadh", (20, 104, 1004, 118), "serif_cond_bitalic", 11, RED, align="center", max_lines=1)
    for index, (label, event) in enumerate(TIMELINE):
        slot_left = 20 + index * 164
        if index:
            page.line([(slot_left, 120), (slot_left, 139)], RULE, 0.5)
        page.text(label, (slot_left + 3, 120, slot_left + 161, 129), "sans_cond_bold", 9.5, RED, max_lines=1)
        page.text(event, (slot_left + 3, 130, slot_left + 161, 140), "sans_cond", 9.5, INK, max_lines=1)
    measurements["masthead bottom"] = 140
    region_widths = [160, 191, 230, 113, 88, 117, 85]
    horizontal = 20
    for (name, count, color, _, _), tab_width in zip(REGIONS, region_widths):
        page.rectangle((horizontal, 141, horizontal + tab_width, 158), color)
        page.text(f"{name} {count}", (horizontal + 3, 143, horizontal + tab_width - 3, 156), "sans_bold", 12, WHITE, align="center", max_lines=1)
        horizontal += tab_width
    page.text("50 STORIES FROM 7 REGIONS", (20, 160, 1004, 170), "sans_bold", 9.5, GREY, align="center", max_lines=1)
    stat_width = 984 / 6
    for index, (number, caption) in enumerate(STATS):
        left = 20 + index * stat_width
        if index:
            page.line([(left, 173), (left, 221)], RULE, 0.6)
        page.text(number, (left + 4, 172, left + stat_width - 4, 199), "sans_bold", 26, RED, align="center", max_lines=1)
        page.text(caption, (left + 6, 200, left + stat_width - 6, 222), "sans", 10.5, GREY, 11, align="center", max_lines=2)
    page.line([(20, 223), (1004, 223)], INK, 0.8)
    measurements["stat band bottom"] = 224
    cursor = 227
    art_height = 55
    lead_bottom = cursor + max(card_height(story, art_height) for story in STORIES[:3])
    for index, story in enumerate(STORIES[:3]):
        draw_card(page, story, 20 + index * (984 + 10) / 3, cursor, (984 - 20) / 3, art_height, lead_bottom)
    measurements["lead row bottom"] = lead_bottom
    cursor = lead_bottom + 4
    page.line([(20, cursor - 2), (1004, cursor - 2)], RULE, 0.7)
    for row_index in range(2):
        stories = STORIES[3 + row_index * 5:8 + row_index * 5]
        row_bottom = cursor + max(card_height(story, 28) for story in stories)
        for column_index, story in enumerate(stories):
            draw_card(page, story, 20 + column_index * (984 + 10) / 5, cursor, (984 - 40) / 5, 28, row_bottom)
        cursor = row_bottom + 4
    measurements["grid bottom"] = cursor - 7
    bottom_top = cursor
    map_width = 250
    brief_left = 20 + map_width + 10
    page.text("ALSO ON FRIDAY 20 NOVEMBER — 37 BRIEFS", (brief_left, bottom_top, 1004, bottom_top + 14), "sans_bold", 11, RED, max_lines=1)
    briefs_end = draw_briefs(page, brief_left, bottom_top + 16, 1004 - brief_left)
    bottom_end = max(briefs_end, bottom_top + 205)
    draw_map(page, (20, bottom_top, 20 + map_width, bottom_end))
    measurements["bottom-zone bottom"] = bottom_end
    legend_top = bottom_end + 3
    label = "HOW SURE ARE WE?"
    label_width = measure(label, "sans_bold", 10)
    page.text(label, (20, legend_top, 20 + label_width + 1, legend_top + 11), "sans_bold", 10, GREY, max_lines=1)
    page.text("REPORTED confirmed by wires · CLAIM one side's claim, attributed · FORECAST expected, not yet happened", (29 + label_width, legend_top, 1004, legend_top + 11), "sans", 10, GREY, max_lines=1)
    date_top = legend_top + 13
    page.rectangle((20, date_top, 1004, date_top + 29), None, RED, 0.9)
    date_label = "DATE CHECK"
    date_label_width = measure(date_label, "sans_bold", 11)
    page.text(date_label, (26, date_top + 4, 27 + date_label_width, date_top + 16), "sans_bold", 11, RED, max_lines=1)
    prefix = "FIRST REPORTED THURSDAY 19 NOV — "
    date_lines = wrap(prefix + DATE_CHECK, 950 - date_label_width - 10, "sans_cond", 9.5)
    if len(date_lines) > 2:
        raise ValueError("DATE CHECK must occupy at most two lines")
    for index, line in enumerate(date_lines):
        left = 36 + date_label_width if index == 0 else 26
        page.text(line, (left, date_top + 3 + index * 11, 997, date_top + 14 + index * 11), "sans_cond", 9.5, INK, max_lines=1)
    footer_top = date_top + 32
    page.text(SOURCES, (20, footer_top, 1004, footer_top + 11), "sans", 10, GREY, max_lines=1)
    page.text(FOOTER, (20, footer_top + 12, 1004, footer_top + 23), "sans", 10, GREY, max_lines=1)
    measurements["footer end"] = footer_top + 23
    budgets = {"brand bottom": 30, "masthead bottom": 140, "stat band bottom": 224, "lead row bottom": 440, "grid bottom": 752, "bottom-zone bottom": 941, "footer end": 1012}
    for name, position in measurements.items():
        if position > budgets[name]:
            raise ValueError(f"Layout budget exceeded: {name} {position} > {budgets[name]}")
    image = page.image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    image.save(ROOT / "entry.png", optimize=True, compress_level=9)
    content = (ROOT / "entry.png").read_bytes()
    if len(content) > 1048576:
        raise ValueError(f"Image exceeds 1 MiB: {len(content)}")
    report = {"measurements": measurements, "budgets": budgets, "text_blocks": len(page.text_blocks), "minimum_font_px": min(block["size"] for block in page.text_blocks), "checked_art_elements": page.art_elements, "dimensions": [SIZE, SIZE], "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
    (ROOT / "layout.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    render()
