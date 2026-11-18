#!/usr/bin/env python3
"""Draw the 18 November 2026 front page and save it as frontpage.png.

A dense one-page newspaper front page: masthead, three lead stories,
a by-the-numbers strip, then 29 more stories grouped by region and
topic in three columns. All 32 stories and every number come from the
verified story list for Wednesday 18 November 2026. No network use.
Layout flows top to bottom with a running y cursor, so no block can
collide with the one below it; column ends are printed for checking.
Run: python3 generate_frontpage.py
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (253, 252, 246)
INK = (17, 17, 17)
GREY = (90, 90, 90)
RULE = (180, 175, 160)
RED = (185, 28, 28)
NAVY = (30, 58, 95)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
SERIF_BOLD = FONT_DIR + "DejaVuSerif-Bold.ttf"
SANS = FONT_DIR + "DejaVuSans.ttf"
SANS_BOLD = FONT_DIR + "DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block_height(draw, lines, leading):
    return len(lines) * leading


# --- Story data: (headline, deck) ---------------------------------------
LEADS = [
    ("TRUMP IN MANILA",
     "US President Donald Trump arrives in Manila for Quad talks, ahead of a China visit."),
    ("UKRAINE HITS CRIMEAN BRIDGE",
     "Ukraine strikes the Crimean bridge for a second day as Russia pounds bridges in Kyiv."),
    ("IRAN DRONES OVER BAHRAIN",
     "Iran attacks a US military radar system in Bahrain with drones; Bahrain gives the all-clear; Kuwait reports interceptions."),
]

# Columns: each is a list of (section title, colour, [(headline, deck), ...])
COLUMNS = [
    [
        ("ASIA-PACIFIC", (14, 116, 144), [
            ("Modi Presses Peaceful Indo-Pacific",
             "Proposes free e-visas and maritime cooperation with ASEAN at the East Asia Summit."),
            ("Cyclone Akvan Set to Intensify",
             "Severe cyclonic storm over the Bay of Bengal; Chennai\u2013Yangon flights cancelled."),
            ("India Condemns Tanker Attack",
             "Panama-flagged LPG tanker MT TARA GAS hit in the Strait of Hormuz; 21 of 24 Indian crew evacuated at Khasab."),
            ("India Re-elected to ITU Council",
             "India re-elected to the International Telecommunication Union Council for 2027\u20132030."),
            ("India, Philippines Deepen Ties",
             "Deeper defence, security and trade ties; Modi meets Marcos in Manila."),
            ("ASEAN Backs AI Growth for Small Firms",
             "ASEAN leaders adopt a declaration for AI-powered growth among small businesses."),
            ("Canada, China Extend Trade Deals",
             "Xi meets Carney ahead of the APEC summit."),
        ]),
        ("OCEANIA", (109, 40, 217), [
            ("Australia Sanctions Israeli Settlements",
             "Australia targets Israeli settlements with fresh sanctions, says Foreign Minister Penny Wong."),
            ("Trump Praises \u2018Friend\u2019 Albanese",
             "Trump praises \u2018friend\u2019 Albanese at the Quad summit."),
            ("Australia Gender Pay Gap Below 20%",
             "Australia\u2019s gender pay gap falls below 20% for the first time."),
        ]),
    ],
    [
        ("EUROPE", (29, 78, 216), [
            ("Britain Sanctions Settlement Firms",
             "Sanctions on Israeli settlement firms in a push to protect the two-state solution."),
            ("Latvia Approves Kulbergs Government",
             "Parliament approves the Kulbergs government in a confidence vote."),
            ("US Presses UN Agency Over Taiwan",
             "US presses a UN agency over Taiwan flight restrictions; China hits back."),
            ("372 Civilians Killed in Ukraine in October",
             "The United Nations reports the toll for October."),
        ]),
        ("MIDDLE EAST & AFRICA", (146, 64, 14), [
            ("Gaza: One Hot Meal Every Two Days",
             "The World Food Programme now provides one hot meal every two days."),
            ("Sudan: Over 2,230 Civilian Deaths",
             "UN confirms over 2,230 civilian deaths; 1,630 killed by drones in January\u2013October 2026."),
        ]),
        ("AMERICAS", (22, 101, 52), [
            ("Asif Merchant Jailed for 27.5 Years",
             "Sentenced in the US over a plot against US officials."),
            ("Trump Deposition Deadline Extended",
             "Judge extends Trump\u2019s deposition deadline in the $10bn BBC lawsuit to 22 January."),
            ("EU Postpones Brazil Poultry Vote",
             "Vote on resuming Brazilian poultry and honey exports postponed to 7\u20138 December."),
            ("Eight Killed in Colombian Air Strike",
             "Air strike targeting the Gulf Clan gang kills eight."),
        ]),
    ],
    [
        ("BUSINESS & MARKETS", (153, 27, 27), [
            ("Nvidia Revenue Doubles to $115.8bn",
             "First report since CEO Jensen Huang\u2019s ouster; board will not reinstate him; Trump backs reinstatement."),
            ("Amazon Invests $7bn in India Renewables",
             "Amazon announces a $7bn investment in India\u2019s renewable energy."),
            ("India GDP Growth Seen at 7.5%",
             "India\u2019s GDP growth expected at 7.5% in the July\u2013September quarter."),
            ("Deutsche Bank Dismissed Warnings",
             "Deutsche Bank dismissed warnings about risky clients, leaked files show."),
            ("St Kitts Winds Down Citizenship Scheme",
             "St Kitts and Nevis winds down its citizenship-by-investment programme after EU threats."),
            ("Costco Gains as Shoppers Stock Up",
             "Costco gains as shoppers stock up amid \u2018apocalyptic concerns\u2019, analysts say."),
        ]),
        ("SPORT & CULTURE", (194, 65, 12), [
            ("Dhoni Retires from the IPL",
             "MS Dhoni announces retirement from the IPL, to become Chennai Super Kings mentor."),
            ("Jay Shah Re-elected ICC Chairman",
             "Jay Shah re-elected ICC chairman for a second term."),
            ("India Win Record 10th SAFF Title",
             "India beat Pakistan 2\u20131 to win a record 10th SAFF Championship in Dhaka."),
        ]),
    ],
]

NUMBERS = [
    ("$115.8bn", "Nvidia quarterly revenue"),
    ("372", "Ukraine deaths, Oct (UN)"),
    ("2,230", "Sudan civilian deaths"),
    ("7.5%", "India GDP, Jul\u2013Sep"),
    ("27.5 years", "Merchant sentence"),
    ("21 of 24", "Indian crew evacuated"),
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    margin = 24
    content_w = W - 2 * margin
    y = 0

    # --- Masthead (compact, so the body gets the room) -------------------
    d.rectangle([0, 0, W, 4], fill=NAVY)
    d.text((W // 2, 8), "THE WORLD IN ONE DAY",
           font=font(SERIF_BOLD, 46), fill=INK, anchor="ma")
    d.text((W // 2, 60), "Wednesday 18 November 2026",
           font=font(SANS_BOLD, 26), fill=RED, anchor="ma")
    d.text((W // 2, 90), "32 stories  \u00b7  6 continents  \u00b7  One front page",
           font=font(SANS, 16), fill=GREY, anchor="ma")
    y = 112
    d.line([margin, y, W - margin, y], fill=INK, width=2)
    d.line([margin, y + 4, W - margin, y + 4], fill=INK, width=1)
    y += 10

    # --- Lead banner: measure first, then draw to the tallest column ----
    lead_head = font(SANS_BOLD, 20)
    lead_deck = font(SANS, 13)
    lead_kick = font(SANS_BOLD, 12)
    col_w = (content_w - 2 * 14) // 3
    measured = []
    for head, deck in LEADS:
        h_lines = wrap(d, head, lead_head, col_w)[:2]
        dk_lines = wrap(d, deck, lead_deck, col_w)[:3]
        height = 16 + len(h_lines) * 23 + 3 + len(dk_lines) * 16
        measured.append((h_lines, dk_lines, height))
    lead_h = max(m[2] for m in measured)
    lead_y = y
    for i, (h_lines, dk_lines, _) in enumerate(measured):
        x = margin + i * (col_w + 14)
        yy = lead_y
        d.text((x, yy), "LEAD", font=lead_kick, fill=RED)
        yy += 16
        for line in h_lines:
            d.text((x, yy), line, font=lead_head, fill=INK)
            yy += 23
        yy += 3
        for line in dk_lines:
            d.text((x, yy), line, font=lead_deck, fill=(60, 60, 60))
            yy += 16
        if i < 2:
            d.line([x + col_w + 7, lead_y, x + col_w + 7, lead_y + lead_h],
                   fill=RULE, width=1)
    y = lead_y + lead_h + 8
    d.line([margin, y, W - margin, y], fill=INK, width=2)
    y += 8

    # --- By the numbers: one short label line per figure -----------------
    d.text((margin, y), "BY THE NUMBERS",
           font=font(SANS_BOLD, 13), fill=NAVY)
    y += 18
    cell_w = content_w // 6
    for i, (num, label) in enumerate(NUMBERS):
        x = margin + i * cell_w
        d.text((x + 4, y), num, font=font(SANS_BOLD, 19), fill=RED)
        d.text((x + 4, y + 24), label, font=font(SANS, 11), fill=GREY)
    y += 40
    d.line([margin, y, W - margin, y], fill=INK, width=2)
    y += 8

    # --- Body: three columns of sections --------------------------------
    body_bottom = 1010
    head_f = font(SANS_BOLD, 16)
    deck_f = font(SANS, 12)
    sect_f = font(SANS_BOLD, 13)
    col_ends = []
    for ci, sections in enumerate(COLUMNS):
        x = margin + ci * (col_w + 14)
        yy = y
        for title, colour, stories in sections:
            d.rectangle([x, yy, x + col_w, yy + 22], fill=colour)
            d.text((x + 8, yy + 3), title, font=sect_f, fill=(255, 255, 255))
            yy += 27
            for headline, deck in stories:
                h_lines = wrap(d, headline, head_f, col_w)[:2]
                for line in h_lines:
                    d.text((x, yy), line, font=head_f, fill=INK)
                    yy += 18
                deck_lines = wrap(d, deck, deck_f, col_w)[:2]
                for line in deck_lines:
                    d.text((x, yy), line, font=deck_f, fill=(60, 60, 60))
                    yy += 13
                yy += 3
                d.line([x, yy, x + col_w, yy], fill=(225, 220, 205), width=1)
                yy += 5
            yy += 1
        col_ends.append(yy)
        if yy > body_bottom:
            print(f"WARNING column {ci} overflows by {yy - body_bottom}px")
    print("column ends:", col_ends, "body bottom:", body_bottom)

    # No footer text: the date is already in the masthead, and the
    # longest column ends just above the bottom edge, leaving no room
    # for a footer line that would not clip.
    img.save("frontpage.png", optimize=True)
    print("saved frontpage.png", img.size)


if __name__ == "__main__":
    main()
