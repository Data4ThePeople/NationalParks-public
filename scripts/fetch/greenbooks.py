"""Park base budgets and FTE for the 63 national parks, from the NPS budget
justifications ("Green Books"), FY 2010 through FY 2025.

Each book has a "Park and Program Summary" (later "Park and Program Table")
under Operation of the National Park System. Each row is a park or program.
The book for FY N reports park base FTE, total FTE and the FY N-2 final or
actual park base amount, then the later years' enacted, CR and request figures.

The script finds the table pages, reads each book's column headers, parses the
rows and keeps the 63 parks. It writes data/processed/budget.csv,
config/budget_units.json and research/budget_overlap.md.

Run: UV_PROJECT_ENVIRONMENT=.uvenv uv run python -I scripts/fetch/greenbooks.py [--refresh]
"""
import csv
import io
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

import requests
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/greenbooks"
OUT_CSV = ROOT / "data/processed/budget.csv"
OUT_UNITS = ROOT / "config/budget_units.json"
OUT_OVERLAP = ROOT / "research/budget_overlap.md"
PARKS = ROOT / "config/parks.json"

# Book fiscal year -> URL as linked from https://www.nps.gov/aboutus/budget.htm
# (checked 2026-10-22). FY 2019 is a zip holding one PDF. No FY 2026 book is
# linked. FY 2027 is linked but has no park table (see research/availability).
BOOKS = {
    2010: "https://www.nps.gov/aboutus/upload/FY_2010_NPS_Greenbook_508.pdf",
    2011: "https://www.nps.gov/aboutus/upload/FY_2011_NPS_Greenbook_508.pdf",
    2012: "https://www.nps.gov/aboutus/upload/FY_2012_NPS_Greenbook_508.pdf",
    2013: "https://www.nps.gov/aboutus/upload/FY_2013_NPS_Greenbook_508.pdf",
    2014: "https://www.nps.gov/aboutus/upload/FY_2014_NPS_Greenbook_508.pdf",
    2015: "https://www.nps.gov/aboutus/upload/FY_2015_NPS_Greenbook_508.pdf",
    2016: "https://www.nps.gov/aboutus/upload/FY_2016_NPS_Greenbook_508-2.pdf",
    2017: "https://www.nps.gov/aboutus/upload/FY_2017_NPS_Greenbook_508.pdf",
    2018: "https://www.nps.gov/aboutus/upload/FY_2018_NPS_Greenbook_508.pdf",
    2019: "https://www.nps.gov/aboutus/upload/FY_2019_NPS_Greenbook_508-1-1.zip",
    2020: "https://www.doi.gov/sites/doi.gov/files/uploads/fy2020-budget-justification-nps.pdf",
    2021: "https://www.doi.gov/sites/doi.gov/files/uploads/fy2021-budget-justification-nps.pdf",
    2022: "https://www.doi.gov/sites/doi.gov/files/fy2022-nps-budget-justification.pdf",
    2023: "https://www.doi.gov/sites/doi.gov/files/fy2023-nps-greenbook.pdf",
    2024: "https://www.doi.gov/sites/doi.gov/files/fy2024-nps-greenbook.pdf-508.pdf",
    2025: "https://www.doi.gov/sites/default/files/documents/2024-03/fy2025-508-nps-greenbook_2.pdf",
}

# Budget lines that cover more than one unit. Members are NPS unit codes; only
# the members in config/parks.json are national parks.
COMBINED = {
    "SEKI": ["SEQU", "KICA"],                  # Sequoia and Kings Canyon NPs
    # Western Arctic National Parklands. Bering Land Bridge has its own line
    # from the FY 2022 book on, so the group changes and gets a new code.
    "BELA_CAKR_KOVA_NOAT": ["BELA", "CAKR", "KOVA", "NOAT"],
    "CAKR_KOVA_NOAT": ["CAKR", "KOVA", "NOAT"],
    "KATM_ANIA_ALAG": ["KATM", "ANIA", "ALAG"],  # Katmai NP&Pres, Aniakchak NM&Pres, Alagnak WR
    "NOCA_LACH_ROLA": ["NOCA", "LACH", "ROLA"],  # North Cascades NP, Lake Chelan NRA, Ross Lake NRA
}

# Row names as printed, by budget unit. Matching ignores case, spaces and
# punctuation, so "Y ellowstone NP" matches "Yellowstone NP". A row matches when
# its name (with any wrapped lines before it) ends with one of these.
ALIASES = {
    "ACAD": ["Acadia NP"],
    "ARCH": ["Arches NP"],
    "BADL": ["Badlands NP"],
    "BIBE": ["Big Bend NP"],
    "BISC": ["Biscayne NP"],
    "BLCA": ["Black Canyon of the Gunnison NP"],
    "BRCA": ["Bryce Canyon NP"],
    "CANY": ["Canyonlands NP"],
    "CARE": ["Capitol Reef NP"],
    "CAVE": ["Carlsbad Caverns NP"],
    "CHIS": ["Channel Islands NP"],
    "CONG": ["Congaree NP"],
    "CRLA": ["Crater Lake NP"],
    "CUVA": ["Cuyahoga Valley NP"],
    "DEVA": ["Death Valley NP"],
    "DENA": ["Denali NP&Pres", "Denali NP & Preserve", "Denali NP and Preserve"],
    "DRTO": ["Dry Tortugas NP"],
    "EVER": ["Everglades NP"],
    "GAAR": ["Gates of the Arctic NP&Pres", "Gates of the Arctic NP & Preserve",
             "Gates of the Arctic NP and Preserve"],
    "JEFF": ["Jefferson National Expansion Memorial", "Jefferson National Expansion NMem",
             "Gateway Arch NP"],
    "GLBA": ["Glacier Bay NP&Pres", "Glacier Bay NP & Preserve", "Glacier Bay NP and Preserve"],
    "GLAC": ["Glacier NP"],
    "GRCA": ["Grand Canyon NP"],
    "GRTE": ["Grand Teton NP"],
    "GRBA": ["Great Basin NP"],
    "GRSA": ["Great Sand Dunes NP&Pres", "Great Sand Dunes NP & Preserve",
             "Great Sand Dunes NP and Preserve"],
    "GRSM": ["Great Smoky Mountains NP"],
    "GUMO": ["Guadalupe Mountains NP"],
    "HALE": ["Haleakala NP"],
    "HAVO": ["Hawaii Volcanoes NP", "Hawai'i Volcanoes NP"],
    "HOSP": ["Hot Springs NP"],
    "INDU": ["Indiana Dunes NL", "Indiana Dunes NP"],
    "ISRO": ["Isle Royale NP"],
    "JOTR": ["Joshua Tree NP"],
    "KATM": [],  # inside KATM_ANIA_ALAG
    "KATM_ANIA_ALAG": ["Katmai NP&Pres, Aniakchak NM&Pres, & Alagna",
                       "Katmai NP&Pres, Aniakchak NM&Pres, & Alagnak",
                       "Katmai NP&Pres, Aniakchak NM&Pres & Alagnak WR"],
    "KEFJ": ["Kenai Fjords NP"],
    "KOVA": [],  # inside WEAR
    "KICA": [],  # inside SEKI
    "SEQU": [],  # inside SEKI
    "SEKI": ["Sequoia NP & Kings Canyon NP", "Sequoia and Kings Canyon NPs", "Sequoia and Kings Canyon NP",
             "Sequoia & Kings Canyon NPs", "Sequoia & Kings Canyon NP"],
    "BELA_CAKR_KOVA_NOAT": ["Bering Land Bridge NPres, Noatak NPres, Cape Krusenstern NM, Kobuk Valley NP"],
    "CAKR_KOVA_NOAT": ["West. Arctic Parklands - Noatak NPres, Cape Krusenstern NM, Kobuk Valley NP"],
    "NOCA_LACH_ROLA": ["North Cascades NP, Lake Chelan NRA, Ross La",
                       "North Cascades NP, Lake Chelan NRA, Ross Lake",
                       "North Cascades NP, Lake Chelan NRA, Ross Lake NRA"],
    "LACL": ["Lake Clark NP&Pres", "Lake Clark NP & Preserve", "Lake Clark NP and Preserve"],
    "LAVO": ["Lassen Volcanic NP"],
    "MACA": ["Mammoth Cave NP"],
    "MEVE": ["Mesa Verde NP"],
    "MORA": ["Mount Rainier NP"],
    "NPSA": ["National Park of American Samoa", "NP of American Samoa"],
    "NERI": ["New River Gorge NR", "New River Gorge National River", "New River Gorge NP&Pres", "New River Gorge NP & Preserve",
             "New River Gorge NP and Preserve"],
    "NOCA": [],  # inside NOCA_LACH_ROLA
    "OLYM": ["Olympic NP"],
    "PEFO": ["Petrified Forest NP"],
    "PINN": ["Pinnacles NM", "Pinnacles NP"],
    "REDW": ["Redwood NP", "Redwood NP & SP", "Redwood National and State Parks"],
    "ROMO": ["Rocky Mountain NP", "Rocky Mountain NP & Cache La Poudre",
             "Rocky Mountain NP (& Cache La Pourdre Herita"],
    "SAGU": ["Saguaro NP"],
    "SHEN": ["Shenandoah NP"],
    "THRO": ["Theodore Roosevelt NP", "Theodore Roosevelt NP & International Peace Garden",
             "Theodore Roosevelt NP and International Peace Garden"],
    "VIIS": ["Virgin Islands NP"],
    "VOYA": ["Voyageurs NP"],
    "WHSA": ["White Sands NM", "White Sands NP"],
    "WICA": ["Wind Cave NP"],
    "WRST": ["Wrangell-Saint Elias NP&Pres", "Wrangell-Saint Elias NP & Preserve",
             "Wrangell-St. Elias NP&Pres", "Wrangell-St Elias NP & Preserve"],
    "YELL": ["Yellowstone NP"],
    "YOSE": ["Yosemite NP"],
    "ZION": ["Zion NP"],
}

# Parks that may be absent from a book, with the documented reason. None so far.
ALLOWED_MISSING = {}

# Header words that close a column, in the order they appear across a header
# row. Each column header ends in exactly one of these.
COL_END = re.compile(
    r"^(FTE|Final|FINAL|Actual|Enacted|CR|Request|Changes|Transfers|Absorptions|"
    r"Efficiencies|Savings|Use|Gross|Federal)\W*\d*\W*$")
NUM = re.compile(r"^\[?[-+]?\d{1,3}(?:,\d{3})*\]?$")
NUMISH = re.compile(r"^(\[?[-+]?\d[\d,.]*\]?|-+|-+\d/|\d/)$")


def norm(s):
    s = re.sub(r"[^a-z0-9]", "", s.lower().replace("&", "and"))
    return s.replace("saint", "st")


def fetch(fy, refresh):
    pdf = RAW / f"fy{fy}.pdf"
    if pdf.exists() and not refresh:
        return pdf
    url = BOOKS[fy]
    print(f"downloading FY {fy}: {url}")
    r = requests.get(url, timeout=300, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    data = r.content
    if url.endswith(".zip"):
        (RAW / f"fy{fy}.zip").write_bytes(data)
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            names = [n for n in z.namelist() if n.lower().endswith(".pdf")]
            if len(names) != 1:
                raise SystemExit(f"FY {fy} zip: expected one PDF, found {names}")
            data = z.read(names[0])
    if not data.startswith(b"%PDF"):
        raise SystemExit(f"FY {fy}: download is not a PDF ({url})")
    pdf.write_bytes(data)
    return pdf


YEAR = re.compile(r"^(FY)?(20)?\d\d\W*\d?$")


def page_items(page):
    """Text pieces on the page as (text, col, line, char_width): col grows left
    to right along the reading direction, line grows down the page. Works on
    rotated pages."""
    items = []

    def visit(text, cm, tm, fd, fs):
        if not text.strip():
            return
        m = [tm[0] * cm[0] + tm[1] * cm[2], tm[0] * cm[1] + tm[1] * cm[3],
             tm[2] * cm[0] + tm[3] * cm[2], tm[2] * cm[1] + tm[3] * cm[3],
             tm[4] * cm[0] + tm[5] * cm[2] + cm[4], tm[4] * cm[1] + tm[5] * cm[3] + cm[5]]
        n = (m[0] ** 2 + m[1] ** 2) ** 0.5 or 1
        d = (m[0] / n, m[1] / n)
        col = m[4] * d[0] + m[5] * d[1]
        line = m[4] * d[1] - m[5] * d[0]
        items.append((text.replace("\n", " "), col, line, 0.5 * fs * n))

    page.extract_text(visitor_text=visit)
    return items


def header_words(page):
    """Words as (text, col, line). Letters split by stray spaces ("Trans fe
    rs") are joined back when the joined word is a known header word."""
    out = []
    for text, col0, line, cw in page_items(page):
        ws = [(w.group(), w.start()) for w in re.finditer(r"\S+", text)]
        i = 0
        while i < len(ws):
            take = 1
            for j in range(min(len(ws), i + 4), i + 1, -1):
                if COL_END.match("".join(w for w, _ in ws[i:j])):
                    take = j - i
                    break
            word = "".join(w for w, _ in ws[i:i + take])
            start = ws[i][1]
            end = ws[i + take - 1][1] + len(ws[i + take - 1][0])
            out.append((word, col0 + (start + end) / 2 * cw, line))
            i += take
    return out


def page_lines(page):
    """Rebuild the page's text lines from positions. The plain text extractor
    sometimes reads a block of cells column by column; positions do not."""
    items = sorted(page_items(page), key=lambda t: (t[2], t[1]))
    lines = []
    for it in items:
        if lines and abs(it[2] - lines[-1][0][2]) <= 2.5:
            lines[-1].append(it)
        else:
            lines.append([it])
    out = []
    for ln in lines:
        ln.sort(key=lambda t: t[1])
        s, end = "", None
        for text, col, line, cw in ln:
            t = text.strip()
            t = re.sub(r"(?<=\d) ,(?=\d{3})|(?<=\d,) (?=\d{3})", lambda m: m.group().strip(), t)
            if end is not None and col - end < 0.6 * cw and re.match(r"[-\d,]", t) \
                    and re.search(r"[-\d,]$", s):
                s += t
            else:
                s = f"{s} {t}" if s else t
            end = col + len(text.rstrip()) * cw
        out.append(s)
    return "\n".join(out)


def detect_columns(page, fy):
    """Return the ordered column labels [(year, word), ...] of a table page."""
    words = header_words(page)
    fte = [w for w in words if re.match(r"^FTE", w[0])]
    if not fte:
        raise SystemExit(f"FY {fy}: no FTE header on table page")
    lo = min(w[2] for w in fte) - 40
    hi = max(w[2] for w in fte) + 2
    hdr = [w for w in words if lo <= w[2] <= hi]
    # Drop title lines that sit inside the header zone.
    title = {round(w[2]) for w in hdr if re.search(
        r"SUMMARY|Summary|\(\$000\)|Greenbook|Justifications|Thousands|Table|Addendum", w[0])}
    hdr = [w for w in hdr if round(w[2]) not in title]
    ends = sorted([w for w in hdr if COL_END.match(w[0])], key=lambda w: w[1])
    # One column can hold two closing words, e.g. "Enacted/ FY 2011 CR".
    cols = []
    for w in ends:
        if cols and abs(w[1] - cols[-1][-1][1]) < 14:
            cols[-1].append(w)
        else:
            cols.append([w])
    years = [w for w in hdr if YEAR.match(w[0])]
    labels = []
    for col in cols:
        cx = sum(w[1] for w in col) / len(col)
        cl = min(w[2] for w in col)
        above = [y for y in years if y[2] <= cl + 1]
        yr = min(above, key=lambda y: abs(y[1] - cx)) if above else None
        yr_val = None
        if yr and abs(yr[1] - cx) < 30:
            dgt = re.search(r"\d\d+", yr[0]).group()
            yr_val = int(dgt) + 2000 if len(dgt) == 2 else int(dgt[:4])
        labels.append((yr_val, " ".join(re.sub(r"\W*\d*\W*$", "", w[0]) for w in col)))
    return labels


def actual_column(labels, fy):
    want = fy - 2
    for i, (yr, kw) in enumerate(labels):
        if yr == want and re.search(r"Final|FINAL|Actual", kw):
            return i, f"FY {yr} {kw}"
    # FY 2014 book: no Final column. Footnote 3 says the FY 2012 Enacted
    # amounts are "in effect, the FY 2012 Final numbers."
    for i, (yr, kw) in enumerate(labels):
        if yr == want and kw == "Enacted":
            return i, f"FY {yr} {kw}"
    raise SystemExit(f"FY {fy}: no FY {want} Final/Actual column in {labels}")


def is_table_page(text):
    t = norm(text)
    return ("parkbase" in t or "pkbase" in t) and "fte" in t \
        and numeric_rows(text) >= 5


def table_pages(reader, fy):
    hits = []
    for i, p in enumerate(reader.pages):
        t = p.extract_text() or ""
        if is_table_page(t):
            hits.append((i, t))
    # Join qualifying pages into runs. A gap of one or two pages is filled when
    # the gap pages also hold table rows (a continuation page can lack the
    # "Park Base" header text). Keep the longest run.
    runs, cur = [], []
    for i, t in hits:
        if cur and i - cur[-1][0] > 1:
            gap = [(j, reader.pages[j].extract_text() or "") for j in range(cur[-1][0] + 1, i)]
            if len(gap) <= 2 and all(numeric_rows(g) >= 5 for _, g in gap):
                cur.extend(gap)
            else:
                runs.append(cur)
                cur = []
        cur.append((i, t))
    if cur:
        runs.append(cur)
    if not runs:
        raise SystemExit(f"FY {fy}: no park table pages found")
    return max(runs, key=len)


def numeric_rows(text):
    return len(re.findall(r"\n[^\n]*[A-Za-z][^\n]* -?\d[\d,]* -?\d[\d,]* -?\d[\d,]*", text))


def split_row(line):
    toks = line.split()
    k = len(toks)
    while k > 0 and NUMISH.match(toks[k - 1]):
        k -= 1
    return " ".join(toks[:k]), toks[k:]


CONT_END = re.compile(r"([,\-&/]|\band|\bNational|\bthe|\bof)$")


def rows_of_page(text):
    """Yield (name, numbers, raw) for each row, joining wrapped names. A name
    can wrap above its numbers or below them; a fragment that ends in a comma,
    dash or "&" continues on the next line."""
    pending, open_row = [], None
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue
        name, nums = split_row(line)
        if open_row and not nums:
            open_row[0] += " " + name
            if not CONT_END.search(name.rstrip()):
                yield tuple(open_row)
                open_row = None
            continue
        if open_row:
            yield tuple(open_row)
            open_row = None
        if not nums:
            pending.append(name)
            continue
        if not name:
            # Numbers on their own line belong to the pending name fragments up
            # to the first one that does not end mid-name.
            take = []
            while pending:
                frag = pending.pop(0)
                take.append(frag)
                if not CONT_END.search(frag.rstrip()):
                    break
            yield " ".join(take), nums, line
            continue
        full = " ".join(pending + [name])
        pending = []
        if CONT_END.search(name.rstrip()):
            open_row = [full, nums, line]
        else:
            yield full, nums, line
    if open_row:
        yield tuple(open_row)


def val(tok):
    return int(tok.strip("[]").replace(",", "").replace("+", ""))


def balances(nums, req_i):
    """The request column equals the column-4 base plus the change columns
    between them (bracketed amounts are non-adds)."""
    if not all(NUM.match(t) for t in nums[:req_i + 1]):
        return False
    adds = [val(t) for t in nums[4:req_i] if not t.startswith("[")]
    return val(nums[req_i]) == val(nums[3]) + sum(adds)


def repair(nums, ncols, req_i):
    """Undo stray spaces inside numbers. "4, 821" -> "4,821" always. When a row
    still has too many tokens ("-9 3", "- 129"), try joining neighbors and keep
    the one join set that makes the row balance. Joins in the first three
    columns (FTE and the actual) are never guessed."""
    out = []
    for t in nums:
        if out and out[-1].endswith(",") and re.match(r"^\d{3}\]?$", t):
            out[-1] += t
        else:
            out.append(t)
    extra = len(out) - ncols
    if extra <= 0:
        return out, []
    if extra > 2:
        return out, ["too many tokens"]
    from itertools import combinations
    fixes = []
    for joins in combinations(range(3, len(out) - 1), extra):
        if any(j2 - j1 < 2 for j1, j2 in zip(joins, joins[1:])):
            continue
        cand, i = [], 0
        while i < len(out):
            if i in joins:
                cand.append(out[i] + out[i + 1])
                i += 2
            else:
                cand.append(out[i])
                i += 1
        if balances(cand, req_i):
            fixes.append(cand)
    if len(fixes) == 1:
        return fixes[0], [f"joined split number tokens: {' '.join(nums)}"]
    return out, [f"{len(fixes)} ways to join tokens"]


def parse_num(tok, fy, where):
    t = tok.strip("[]")
    if not NUM.match(tok):
        raise SystemExit(f"FY {fy}: unparseable number {tok!r} in {where}")
    return int(t.replace(",", "").replace("+", ""))


def parse_book(fy, path, alias_index):
    reader = PdfReader(path)
    pages = table_pages(reader, fy)
    labels = detect_columns(reader.pages[pages[0][0]], fy)
    ncols = len(labels)
    act_i, act_label = actual_column(labels, fy)
    fte_cols = [i for i, (yr, kw) in enumerate(labels) if kw == "FTE"]
    if fte_cols != [0, 1]:
        raise SystemExit(f"FY {fy}: expected FTE in columns 1 and 2, got {labels}")
    req_i = [i for i, (yr, kw) in enumerate(labels) if kw == "Request"][0]
    counts = Counter()
    found = {}
    unbalanced = []
    for pidx, _ in pages:
        text = page_lines(reader.pages[pidx])
        for name, nums, raw in rows_of_page(text):
            counts[len(nums)] += 1
            key = norm(name)
            key = re.sub(r"\d+$", "", key)
            hits = [a for a in alias_index if key.endswith(a)]
            if not hits:
                continue
            a = max(hits, key=len)
            code, line_name = alias_index[a]
            where = f"page {pidx + 1}: {raw!r}"
            nums, notes = repair(nums, ncols, req_i)
            if len(nums) != ncols:
                raise SystemExit(f"FY {fy}: {code} row has {len(nums)} numbers, "
                                 f"expected {ncols} ({notes}): {where}")
            for n in notes:
                print(f"  FY {fy} {code}: {n}")
            if not balances(nums, req_i):
                print(f"  FY {fy} {code}: request does not equal base plus changes: {where}")
                unbalanced.append((fy, code))
            if code in found:
                raise SystemExit(f"FY {fy}: duplicate row for {code}: {found[code]['raw']} / {where}")
            vals = [parse_num(nums[i], fy, where) for i in (0, 1, act_i)]
            found[code] = {"budget_unit": code, "fy": fy - 2, "park_base_k": vals[2],
                           "park_base_fte": vals[0], "total_fte": vals[1],
                           "line_name": line_name, "source_book": fy,
                           "source_page": pidx + 1, "raw": where}
    modal = counts.most_common(1)[0][0]
    if modal != ncols:
        raise SystemExit(f"FY {fy}: headers give {ncols} columns but rows mostly have {modal}: {labels}")
    return found, labels, act_label, [p[0] + 1 for p in pages]


def main():
    refresh = "--refresh" in sys.argv
    RAW.mkdir(parents=True, exist_ok=True)
    parks = {p["code"] for p in json.loads(PARKS.read_text())}
    if len(parks) != 63:
        raise SystemExit(f"config/parks.json has {len(parks)} parks, expected 63")
    alias_index = {}
    for code, names in ALIASES.items():
        if code not in parks and code not in COMBINED:
            raise SystemExit(f"alias for unknown unit {code}")
        for n in names:
            k = norm(n)
            if k in alias_index:
                if alias_index[k][0] != code:
                    raise SystemExit(f"alias {n!r} maps to two units")
                continue  # keep the first spelling, which is the printed one
            alias_index[k] = (code, n)
    covers = {c: {c} for c in parks} | {k: set(m) for k, m in COMBINED.items()}

    rows, layout, fte_mislabel = [], [], []
    for fy in sorted(BOOKS):
        path = fetch(fy, refresh)
        found, labels, act_label, pages = parse_book(fy, path, alias_index)
        covered = Counter(p for u in found for p in covers[u] if p in parks)
        twice = [p for p, n in covered.items() if n > 1]
        if twice:
            raise SystemExit(f"FY {fy} book: parks on more than one line: {twice}")
        miss = parks - covered.keys()
        for code in sorted(miss):
            if (fy, code) not in ALLOWED_MISSING:
                raise SystemExit(f"FY {fy} book: no row for {code}")
        layout.append((fy, pages, labels, act_label))
        fte_year = labels[0][0]
        if fte_year != fy - 2:
            print(f"  FY {fy} book: FTE columns are labeled FY {fte_year}, "
                  f"the amount column FY {fy - 2}")
            fte_mislabel.append((fy, fte_year, found))
        print(f"FY {fy} book: pages {pages[0]}-{pages[-1]}, {len(found)} units, "
              f"actual from '{act_label}', columns: "
              + "; ".join(f"{y or ''} {k}".strip() for y, k in labels))
        rows.extend(found.values())

    # Overlap: keep the later book for any (unit, fy) that appears twice.
    by_key, diffs = {}, []
    for r in sorted(rows, key=lambda r: r["source_book"]):
        k = (r["budget_unit"], r["fy"])
        if k in by_key:
            old = by_key[k]
            for f in ("park_base_k", "park_base_fte", "total_fte"):
                if old[f] != r[f]:
                    diffs.append((k, f, old["source_book"], old[f], r["source_book"], r[f]))
        by_key[k] = r
    out = sorted(by_key.values(), key=lambda r: (r["budget_unit"], r["fy"]))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    cols = ["budget_unit", "fy", "park_base_k", "park_base_fte", "total_fte",
            "line_name", "source_book", "source_page"]
    with OUT_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)
    used = {r["budget_unit"] for r in out}
    OUT_UNITS.write_text(json.dumps({k: v for k, v in COMBINED.items() if k in used},
                                    indent=1) + "\n")

    lines = ["# Budget overlap check", "",
             "Generated by `scripts/fetch/greenbooks.py`. Each book reports one",
             "final or actual year (FY N-2 for the FY N book), so a (unit, fy) pair",
             "appears twice only if two books report the same year as final or actual.", ""]
    dup = len(rows) - len(out)
    lines.append(f"Rows parsed: {len(rows)}. Rows kept: {len(out)}. Repeated (unit, fy) pairs: {dup}.")
    lines.append("")
    if diffs:
        lines += ["| unit | fy | field | earlier book | value | later book (kept) | value |",
                  "|---|---|---|---|---|---|---|"]
        for (u, y), f, b1, v1, b2, v2 in diffs:
            lines.append(f"| {u} | {y} | {f} | FY {b1} | {v1} | FY {b2} | {v2} |")
    else:
        lines.append("No differences found.")
    for fy, fte_year, found in fte_mislabel:
        other = {r["budget_unit"]: r for r in rows if r["fy"] == fte_year}
        same = sum(1 for u, r in found.items() if u in other and
                   (r["park_base_fte"], r["total_fte"]) ==
                   (other[u]["park_base_fte"], other[u]["total_fte"]))
        src = next(iter(other.values()))["source_book"]
        lines += ["", f"## FTE label check: FY {fy} book", "",
                  f"The FY {fy} book labels its FTE columns FY {fte_year}, but its amount",
                  f"column is FY {fy - 2}. Its FTE are stored under fy {fy - 2}. Compared with",
                  f"the FY {fte_year} FTE in the FY {src} book, {same} of {len(found)} lines match",
                  "on both park base FTE and total FTE.", "",
                  "| unit | FY %d book park base FTE | FY %d book park base FTE | FY %d book total FTE | FY %d book total FTE |" % (fy, src, fy, src),
                  "|---|---|---|---|---|"]
        for u in sorted(found):
            if u in other:
                a, b = found[u], other[u]
                lines.append(f"| {u} | {a['park_base_fte']} | {b['park_base_fte']} | "
                             f"{a['total_fte']} | {b['total_fte']} |")
    OUT_OVERLAP.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_CSV} ({len(out)} rows), {OUT_UNITS}, {OUT_OVERLAP}")


if __name__ == "__main__":
    main()
