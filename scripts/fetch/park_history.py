"""Short, sourced establishment histories for the 63 national parks.

Sources (cached in data/raw/history/, treated as untrusted data):
  1. The National Parks: Index 2012-2016 (NPS). This is the newest edition NPS
     posts on its publications page.
  2. NPS "Recent Changes to the National Park System", for changes after the
     Index (2018 to 2020 redesignations).
  3. NPS Land Resources Division "Listing of Acreage" for 09/30/2026, gross
     area acres.

Run from the project root:
  UV_PROJECT_ENVIRONMENT=.uvenv uv run python -I scripts/fetch/park_history.py [--refresh] [--dump]

The event list for each park is picked by hand below (EVENTS). The script
checks that every `text` appears word for word in that park's own Index entry
(or in one Recent Changes table row), ignoring only spaces and hyphens, which
the PDF text layer does not keep reliably. Every date is parsed from that text.
Any mismatch, missing park or missing acreage row stops the script.
"""
import html
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

import requests
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/history"
OUT = ROOT / "config/park_history.json"

INDEX_URL = "https://www.nps.gov/aboutus/upload/npindex2012-2016.pdf"
INDEX_PDF = RAW / "npindex2012-2016.pdf"
RECENT_URL = "https://www.nps.gov/aboutus/recent-changes.htm"
RECENT_HTM = RAW / "recent-changes.htm"
ACRES_PAGE = "https://www.nps.gov/subjects/lwcf/acreagereports.htm"
ACRES_URL = "https://www.nps.gov/subjects/lwcf/upload/NPS-Acreage-09-30-2026.xlsx"
ACRES_XLSX = RAW / "NPS-Acreage-09-30-2026.xlsx"
ACRES_AS_OF = "2026-09-30"

# Other official NPS documents, used only where the Index leaves a gap.
EXTRA_DOCS = {
    "ISRO": ("https://www.nps.gov/isro/learn/management/upload/ISRO_Web_Accessible_Foundation_Document_Overview_2016.pdf",
             RAW / "ISRO_Foundation_Document_Overview_2016.pdf", 4),
}

UA = {"User-Agent": "Mozilla/5.0 (Data 4 The People research; park history)"}
refresh = "--refresh" in sys.argv


def fetch(url, path):
    if refresh or not path.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=120)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


# ---------------------------------------------------------------- Index (PDF)

def norm(s):
    """Join the PDF text layer into one line. Words split across lines by a
    soft hyphen are rejoined; nothing else about the wording is changed."""
    s = s.replace("\r", "")
    s = re.sub(r"­[ \t]*\n\s*", "", s)
    s = s.replace("­", "-")  # the PDF encodes every hyphen as U+00AD
    s = re.sub(r"\s*\n\s*", " ", s)
    s = re.sub(r"\b([TVWYPF]) (?=[a-z]{2})", r"\1", s)
    s = re.sub(r" (?=[.,;])", "", s)
    return re.sub(r"\s{2,}", " ", s).strip()


def key(s):
    """Comparison form: drop spaces and hyphens, which the PDF text layer
    adds or loses at random (e.g. 'establis hed', 'Nov . 10')."""
    return re.sub(r"[\s­\-]", "", s)


def index_entries():
    fetch(INDEX_URL, INDEX_PDF)
    pages = [p.extract_text() or "" for p in PdfReader(str(INDEX_PDF)).pages]
    out = {}
    for i, txt in enumerate(pages):
        for m in re.finditer(r"www\.nps\.gov/([a-z]{4})\b", txt):
            rest = txt[m.end():]
            j = rest.find("Acreage")
            if j < 0 and i + 1 < len(pages):
                rest += "\n" + pages[i + 1]
                j = rest.find("Acreage")
            if j < 0:
                continue
            out.setdefault(m.group(1).upper(), []).append((i + 1, norm(rest[:j])))
    return out


# --------------------------------------------------------- Recent Changes page

def recent_rows():
    fetch(RECENT_URL, RECENT_HTM)
    t = RECENT_HTM.read_text(encoding="utf-8")
    m = re.search(r"Last updated:\s*([A-Z][a-z]+ \d{1,2}, \d{4})", re.sub(r"<[^>]+>", " ", t))
    rows = []
    for tr in re.findall(r"(?s)<tr.*?</tr>", t):
        cells = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip().replace(" ,", ",")
                 for c in re.findall(r"(?s)<t[dh][^>]*>(.*?)</t[dh]>", tr)]
        if cells:
            rows.append(cells)
    return rows, (m.group(1) if m else None)


# ------------------------------------------------------------ Acreage (xlsx)

def acreage_rows():
    fetch(ACRES_URL, ACRES_XLSX)
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    z = zipfile.ZipFile(ACRES_XLSX)
    ss = ["".join(t.text or "" for t in si.iter(f"{{{ns['m']}}}t"))
          for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns)]
    sh = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    rows = []
    for r in sh.iter(f"{{{ns['m']}}}row"):
        d = {}
        for c in r.findall("m:c", ns):
            v = c.find("m:v", ns)
            if v is None:
                continue
            col = re.match(r"[A-Z]+", c.get("r")).group(0)
            d[col] = ss[int(v.text)] if c.get("t") == "s" else v.text
        rows.append(d)
    title = rows[0].get("A", "")
    if "09/30/2026" not in title or rows[1].get("K") != "Gross Area Acres" or rows[1].get("A") != "Area Name":
        raise SystemExit(f"Acreage workbook layout changed: {title!r} {rows[1]}")
    out = {}
    for d in rows[2:]:
        name = (d.get("A") or "").strip()
        if name and d.get("K"):
            if name in out:
                raise SystemExit(f"Duplicate acreage row {name}")
            out[name] = round(float(d["K"]), 2)
    return out


# Acreage row names: (national park row, preserve row or None, rows to add).
ACRE_ROWS = {
    "ACAD": "ACADIA NP", "ARCH": "ARCHES NP", "BADL": "BADLANDS NP", "BIBE": "BIG BEND NP",
    "BISC": "BISCAYNE NP", "BLCA": "BLACK CANYON OF GUNNISON", "BRCA": "BRYCE CANYON NP",
    "CANY": "CANYONLANDS NP", "CARE": "CAPITOL REEF NP", "CAVE": "CARLSBAD CAVERNS NP",
    "CHIS": "CHANNEL ISLANDS NP", "CONG": "CONGAREE NP", "CRLA": "CRATER LAKE NP",
    "CUVA": "CUYAHOGA VALLEY NP", "DEVA": "DEATH VALLEY NP",
    "DENA": ("DENALI NP", "DENALI N PRESERVE"), "DRTO": "DRY TORTUGAS NP",
    "EVER": ("EVERGLADES NP", None, ["EVERGLADES EXPANSION"]),
    "GAAR": ("GATES OF THE ARCTIC NP", "GATES OF ARCTIC N PRES"), "JEFF": "GATEWAY ARCH NP",
    "GLBA": ("GLACIER BAY NP", "GLACIER BAY N PRESERVE"), "GLAC": "GLACIER NP",
    "GRCA": "GRAND CANYON NP", "GRTE": "GRAND TETON NP", "GRBA": "GREAT BASIN NP",
    "GRSA": ("GREAT SAND DUNES NP", "GREAT SAND DUNES N PRES"), "GRSM": "GREAT SMOKY MTS NP",
    "GUMO": "GUADALUPE MTS NP", "HALE": "HALEAKALA NP", "HAVO": "HAWAII VOLCANOES NP",
    "HOSP": "HOT SPRINGS NP", "INDU": "INDIANA DUNES NP", "ISRO": "ISLE ROYALE NP",
    "JOTR": "JOSHUA TREE NP", "KATM": ("KATMAI NP", "KATMAI N PRESERVE"),
    "KEFJ": "KENAI FJORDS NP", "KICA": "KINGS CANYON NP", "KOVA": "KOBUK VALLEY NP",
    "LACL": ("LAKE CLARK NP", "LAKE CLARK N PRESERVE"), "LAVO": "LASSEN VOLCANIC NP",
    "MACA": "MAMMOTH CAVE NP", "MEVE": "MESA VERDE NP", "MORA": "MT RAINIER NP",
    "NPSA": "NP OF AMERICAN SAMOA", "NERI": "NEW RIVER GORGE NP & PRES",
    "NOCA": "NORTH CASCADES NP", "OLYM": "OLYMPIC NP", "PEFO": "PETRIFIED FOREST NP",
    "PINN": "PINNACLES NP", "REDW": "REDWOOD NP", "ROMO": "ROCKY MT NP", "SAGU": "SAGUARO NP",
    "SEQU": "SEQUOIA NP", "SHEN": "SHENANDOAH NP", "THRO": "T ROOSEVELT NP",
    "VIIS": "VIRGIN ISLANDS NP", "VOYA": "VOYAGEURS NP", "WHSA": "WHITE SANDS NP",
    "WICA": "WIND CAVE NP", "WRST": ("WRANGELL-ST ELIAS NP", "WRANGELL-ST ELIAS N PRES"),
    "YELL": "YELLOWSTONE NP", "YOSE": "YOSEMITE NP", "ZION": "ZION NP",
}

# Which Index entry to use when the URL code is shared or differs.
# (url code on the page, PDF page, first words of the history that pick the entry)
INDEX_PICK = {
    "SEQU": ("SEKI", 36, "Great groves of giant sequoias"),
    "KICA": ("SEKI", 33, "Two enormous canyons"),
    "GRTE": ("GRTE", 113, "Grand Teton features"),
    "NOCA": ("NOCA", 110, "In this wilderness park"),
}

# Index entry headings that differ from the name in config/parks.json.
INDEX_HEADING = {
    "JEFF": "Jefferson National Expansion Memorial",
    "INDU": "Indiana Dunes National Lakeshore",
    "NERI": "New River Gorge National River",
    "WHSA": "White Sands National Monument",
    "HALE": "Haleakalā National Park",
    "DENA": "Denali National Park and Denali National Preserve",
    "GAAR": "Gates of the Arctic National Park and Gates of the Arctic National Preserve",
    "GLBA": "Glacier Bay National Park and Glacier Bay National Preserve",
    "GRSA": "Great Sand Dunes National Park and Great Sand Dunes National Preserve",
    "KATM": "Katmai National Park and Katmai National Preserve",
    "LACL": "Lake Clark National Park and Lake Clark National Preserve",
    "WRST": "Wrangell-St. Elias National Park and Wrangell-St. Elias National Preserve",
}

# ------------------------------------------------------------------ Events
# (kind, name, text[, date_text])
# `name_stated` in the output is True when the name is written in the event
# text, elsewhere in the same Index entry, or is the heading of the entry. It is False when the source gives
# only the unit type ("a national monument") and the name is the park's name
# joined with that type, or when the spelling is ours (see notes).
I = "index"
EVENTS = {
    "ACAD": [("proclaimed", "Sieur de Monts National Monument", "Proclaimed Sieur de Monts National Monument July 8, 1916"),
             ("established", "Lafayette National Park", "established as Lafayette National Park Feb. 26, 1919"),
             ("renamed", "Acadia National Park", "renamed Acadia National Park Jan. 19, 1929"),
             ("other", "Acadia National Park", "Permanent boundary established Sept. 25, 1986.")],
    "ARCH": [("proclaimed", "Arches National Monument", "Proclaimed a national monument April 12, 1929"),
             ("redesignated", "Arches National Park", "redesignated Nov. 12, 1971")],
    "BADL": [("authorized", "Badlands National Monument", "Authorized as a national monument March 4, 1929"),
             ("established", "Badlands National Monument", "established Jan. 24, 1939"),
             ("redesignated", "Badlands National Park", "redesignated a national park Nov. 10, 1978")],
    "BIBE": [("authorized", "Big Bend National Park", "Authorized June 20, 1935"),
             ("established", "Big Bend National Park", "established June 12, 1944")],
    "BISC": [("authorized", "Biscayne National Monument", "Authorized as a national monument Oct. 18, 1968"),
             ("redesignated", "Biscayne National Park", "redesignated as a national park and enlarged June 28, 1980")],
    "BLCA": [("proclaimed", "Black Canyon of the Gunnison National Monument", "Proclaimed a national monument March 2, 1933"),
             ("redesignated", "Black Canyon of the Gunnison National Park", "redesignated as a national park Oct. 21, 1999")],
    "BRCA": [("proclaimed", "Bryce Canyon National Monument", "Proclaimed a national monument June 8, 1923"),
             ("redesignated", "Utah National Park", "renamed and redesignated Utah National Park June 7, 1924"),
             ("renamed", "Bryce Canyon National Park", "renamed Bryce Canyon National Park Feb. 25, 1928")],
    "CANY": [("established", "Canyonlands National Park", "Established Sept. 12, 1964.")],
    "CARE": [("proclaimed", "Capitol Reef National Monument", "Proclaimed a national monument Aug. 2, 1937"),
             ("redesignated", "Capitol Reef National Park", "redesignated a national park Dec. 18, 1971")],
    "CAVE": [("proclaimed", "Carlsbad Cave National Monument", "Proclaimed Carlsbad Cave National Monument Oct. 25, 1923"),
             ("established", "Carlsbad Caverns National Park", "established as Carlsbad Caverns National Park May 14, 1930")],
    "CHIS": [("proclaimed", "Channel Islands National Monument", "Proclaimed a national monument April 26, 1938"),
             ("redesignated", "Channel Islands National Park", "redesignated March 5, 1980")],
    "CONG": [("authorized", "Congaree Swamp National Monument", "Authorized Oct. 18, 1976 as Congaree Swamp National Monument"),
             ("redesignated", "Congaree National Park", "redesignated Nov. 10, 2003")],
    "CRLA": [("established", "Crater Lake National Park", "Established May 22, 1902.")],
    "CUVA": [("authorized", "Cuyahoga Valley National Recreation Area", "Authorized Dec. 27, 1974"),
             ("established", "Cuyahoga Valley National Recreation Area", "established June 26, 1975"),
             ("redesignated", "Cuyahoga Valley National Park", "redesignated Oct. 11, 2000")],
    "DEVA": [("proclaimed", "Death Valley National Monument", "Proclaimed a national monument Feb. 11, 1933"),
             ("redesignated", "Death Valley National Park", "redesignated as a national park Oct. 31, 1994")],
    "DENA": [("established", "Mt. McKinley National Park", "Established as Mt. McKinley National Park Feb. 26, 1917."),
             ("proclaimed", "Denali National Monument", "Separate Denali National Monument proclaimed Dec. 1, 1978."),
             ("established", "Denali National Park and Denali National Preserve",
              "Both incorporated into and established as Denali National Park and Denali National Preserve Dec. 2, 1980.")],
    "DRTO": [("proclaimed", "Fort Jefferson National Monument", "Proclaimed Fort Jefferson National Monument Jan. 4, 1935"),
             ("redesignated", "Dry Tortugas National Park", "renamed and redesignated as a national park Oct. 26, 1992")],
    "EVER": [("authorized", "Everglades National Park", "Authorized May 30, 1934"),
             ("established", "Everglades National Park", "established Dec. 6, 1947")],
    "GAAR": [("proclaimed", "Gates of the Arctic National Monument", "Proclaimed Gates of the Arctic National Monument Dec. 1, 1978"),
             ("established", "Gates of the Arctic National Park and Gates of the Arctic National Preserve",
              "established as a national park and national preserve Dec. 2, 1980")],
    "JEFF": [("other", "Jefferson National Expansion Memorial", "Designated Dec. 21, 1935"),
             ("authorized", "Jefferson National Expansion Memorial", "Gateway Arch authorized May 17, 1954"),
             ("redesignated", "Gateway Arch National Park", ("recent", "February 22, 2018"))],
    "GLBA": [("proclaimed", "Glacier Bay National Monument", "Proclaimed Glacier Bay National Monument Feb. 26, 1925"),
             ("established", "Glacier Bay National Park and Glacier Bay National Preserve",
              "established as a national park and national preserve Dec. 2, 1980")],
    "GLAC": [("established", "Glacier National Park", "Established May 11, 1910."),
             ("other", "Glacier National Park", "Authorized as part of Waterton-Glacier International Peace Park May 2, 1932"),
             ("other", "Glacier National Park", "proclaimed June 30, 1932.")],
    "GRCA": [("proclaimed", "Grand Canyon Forest Reserve", "Proclaimed as Grand Canyon Forest Reserve Feb. 20, 1893"),
             ("proclaimed", "Grand Canyon Game Preserve", "Grand Canyon Game Preserve proclaimed Nov. 28, 1906"),
             ("proclaimed", "Grand Canyon National Monument", "Grand Canyon National Monument proclaimed Jan. 11, 1908"),
             ("established", "Grand Canyon National Park", "national park established Feb. 26, 1919"),
             ("other", "Grand Canyon National Park", "transferred from U.S. Forest Service, Aug. 15, 1919."),
             ("proclaimed", "Grand Canyon National Monument", "A separate Grand Canyon National Monument proclaimed Dec. 22, 1932."),
             ("proclaimed", "Marble Canyon National Monument", "Marble Canyon National Monument proclaimed Jan. 20, 1969."),
             ("enlarged", "Grand Canyon National Park",
              "Three units and portions of Glen Canyon and Lake Mead national recreation areas combined with additional lands as a national park Jan. 3, 1975.")],
    "GRTE": [("established", "Grand Teton National Park", "Established Feb. 26, 1929."),
             ("proclaimed", "Jackson Hole National Monument",
              "Enlarged by Congress Sept. 14, 1950, through a boundary change that incorporated much of the Jackson Hole National Monument, proclaimed March 15, 1943.",
              "March 15, 1943"),
             ("enlarged", "Grand Teton National Park",
              "Enlarged by Congress Sept. 14, 1950, through a boundary change that incorporated much of the Jackson Hole National Monument, proclaimed March 15, 1943.",
              "Sept. 14, 1950")],
    "GRBA": [("proclaimed", "Lehman Caves National Monument", "Proclaimed as Lehman Caves National Monument Jan. 24, 1922"),
             ("other", "Lehman Caves National Monument", "transferred from the U.S. Forest Service, Aug. 10, 1933"),
             ("established", "Great Basin National Park", "made part of Great Basin National Park when established Oct. 27, 1986")],
    "GRSA": [("proclaimed", "Great Sand Dunes National Monument", "Proclaimed a national monument March 17, 1932."),
             ("redesignated", "Great Sand Dunes National Park and Great Sand Dunes National Preserve",
              "Boundary change/redesignation as a national park and national preserve Nov. 22, 2000."),
             ("established", "Great Sand Dunes National Park and Great Sand Dunes National Preserve", "Established Sept. 24, 2004.")],
    "GRSM": [("authorized", "Great Smoky Mountains National Park", "Authorized May 22, 1926"),
             ("established", "Great Smoky Mountains National Park", "established for administration and protection only Feb. 6, 1930"),
             ("established", "Great Smoky Mountains National Park", "established for full development June 15, 1934")],
    "GUMO": [("authorized", "Guadalupe Mountains National Park", "Authorized Oct. 15, 1966"),
             ("established", "Guadalupe Mountains National Park", "established Sept. 30, 1972")],
    "HALE": [("established", "Hawaii National Park", "Established as a part of Hawaii National Park Aug. 1, 1916"),
             ("renamed", "Haleakalā National Park", "renamed Sept. 13, 1960")],
    "HAVO": [("established", "Hawaii National Park", "Established as part of Hawaii National Park Aug. 1, 1916"),
             ("renamed", "Hawaii Volcanoes National Park", "renamed Sept. 22, 1961")],
    "HOSP": [("established", "Hot Springs Reservation", "Established as Hot Springs Reservation April 20, 1832"),
             ("other", "Hot Springs Reservation", "dedicated to public use as a park June 16, 1880"),
             ("redesignated", "Hot Springs National Park", "redesignated March 4, 1921")],
    "INDU": [("authorized", "Indiana Dunes National Lakeshore", "Authorized Nov. 5, 1966."),
             ("redesignated", "Indiana Dunes National Park", ("recent", "February 15, 2019"))],
    "ISRO": [("authorized", "Isle Royale National Park", "Authorized March 3, 1931."),
             ("established", "Isle Royale National Park",
              ("doc", "The park was formally authorized on March 3, 1931, and was officially established on April 3, 1940."),
              "April 3, 1940")],
    "JOTR": [("proclaimed", "Joshua Tree National Monument", "Proclaimed a national monument Aug. 10, 1936"),
             ("redesignated", "Joshua Tree National Park", "redesignated Oct. 31, 1994")],
    "KATM": [("proclaimed", "Katmai National Monument", "Proclaimed Katmai National Monument Sept. 24, 1918"),
             ("established", "Katmai National Park and Katmai National Preserve", "established as national park and national preserve Dec. 2, 1980")],
    "KEFJ": [("proclaimed", "Kenai Fjords National Monument", "Proclaimed a national monument Dec. 1, 1978"),
             ("established", "Kenai Fjords National Park", "established as a national park Dec. 2, 1980")],
    "KICA": [("established", "General Grant National Park", "Established as General Grant National Park Oct. 1, 1890"),
             ("renamed", "Kings Canyon National Park", "renamed and enlarged March 4, 1940")],
    "KOVA": [("proclaimed", "Kobuk Valley National Monument", "Proclaimed a national monument Dec. 1, 1978"),
             ("established", "Kobuk Valley National Park", "established as a national park Dec. 2, 1980")],
    "LACL": [("proclaimed", "Lake Clark National Monument", "Proclaimed Lake Clark National Monument Dec. 1, 1978"),
             ("established", "Lake Clark National Park and Lake Clark National Preserve",
              "established as a national park and national preserve Dec. 2, 1980")],
    "LAVO": [("proclaimed", "Lassen Peak and Cinder Cone National Monuments", "Proclaimed as Lassen Peak and Cinder Cone National Monuments May 6, 1907"),
             ("established", "Lassen Volcanic National Park", "made part of Lassen Volcanic National Park when established Aug. 9, 1916")],
    "MACA": [("authorized", "Mammoth Cave National Park", "Authorized May 25, 1926"),
             ("established", "Mammoth Cave National Park", "established July 1, 1941")],
    "MEVE": [("established", "Mesa Verde National Park", "Established June 29, 1906.")],
    "MORA": [("established", "Mount Rainier National Park", "Established March 2, 1899.")],
    "NPSA": [("authorized", "National Park of American Samoa", "Authorized Oct. 31, 1988"),
             ("other", "National Park of American Samoa", "50-year lease signed Sept. 9, 1993.")],
    "NERI": [("authorized", "New River Gorge National River", "Authorized Nov. 10, 1978."),
             ("redesignated", "New River Gorge National Park and Preserve", ("recent", "December 27, 2020"))],
    "NOCA": [("established", "North Cascades National Park", "Established Oct. 2, 1968.")],
    "OLYM": [("proclaimed", "Mount Olympus National Monument", "Proclaimed Mount Olympus National Monument March 2, 1909"),
             ("other", "Mount Olympus National Monument", "transferred from U.S. Forest Service Aug. 10, 1933"),
             ("redesignated", "Olympic National Park", "renamed and redesignated national park June 29, 1938")],
    "PEFO": [("proclaimed", "Petrified Forest National Monument", "Proclaimed a national monument Dec. 8, 1906"),
             ("redesignated", "Petrified Forest National Park", "redesignated Dec. 9, 1962")],
    "PINN": [("proclaimed", "Pinnacles National Monument", "Proclaimed a national monument Jan. 16, 1908"),
             ("redesignated", "Pinnacles National Park", "redesignated as national park Jan. 10, 2013")],
    "REDW": [("established", "Redwood National Park", "Established Oct. 2, 1968.")],
    "ROMO": [("established", "Rocky Mountain National Park", "Established Jan. 26, 1915.")],
    "SAGU": [("proclaimed", "Saguaro National Monument", "Proclaimed a national monument March 1, 1933"),
             ("other", "Saguaro National Monument", "transferred from U.S. Forest Service, Aug. 10, 1933"),
             ("redesignated", "Saguaro National Park", "redesignated Oct. 4, 1994")],
    "SEQU": [("established", "Sequoia National Park", "Established Sept. 25, 1890.")],
    "SHEN": [("authorized", "Shenandoah National Park", "Authorized May 22, 1926"),
             ("established", "Shenandoah National Park", "fully established Dec. 26, 1935"),
             ("other", "Shenandoah National Park", "dedicated July 3, 1936.")],
    "THRO": [("established", "Theodore Roosevelt National Memorial Park", "Established as Theodore Roosevelt National Memorial Park April 25, 1947"),
             ("redesignated", "Theodore Roosevelt National Park", "redesignated Nov. 10, 1978.")],
    "VIIS": [("authorized", "Virgin Islands National Park", "Authorized Aug. 2, 1956.")],
    "VOYA": [("authorized", "Voyageurs National Park", "Authorized Jan. 8, 1971"),
             ("established", "Voyageurs National Park", "established April 8, 1975.")],
    "WHSA": [("proclaimed", "White Sands National Monument", "Proclaimed Jan. 18, 1933."),
             ("redesignated", "White Sands National Park", ("recent", "December 20, 2019"))],
    "WICA": [("established", "Wind Cave National Park", "Established Jan. 9, 1903."),
             ("enlarged", "Wind Cave National Park",
              "Wind Cave National Game Preserve, established Aug. 10, 1912, added to park June 15, 1935.", "June 15, 1935")],
    "WRST": [("proclaimed", "Wrangell-St. Elias National Monument", "Proclaimed Wrangell-St. Elias National Monument Dec. 1, 1978"),
             ("established", "Wrangell-St. Elias National Park and Wrangell-St. Elias National Preserve",
              "established as a national park and national preserve Dec. 2, 1980")],
    "YELL": [("established", "Yellowstone National Park", "Established March 1, 1872.")],
    "YOSE": [("other", "Yosemite Valley and Mariposa Big Tree Grove",
              "Yosemite Valley and Mariposa Big Tree Grove granted to State of California June 30, 1864"),
             ("established", "Yosemite National Park", "established as a national park Oct. 1, 1890"),
             ("other", "Yosemite National Park", "Federal government accepted lands returned by state June 11, 1906.")],
    "ZION": [("proclaimed", "Mukuntuweap National Monument", "Mukuntuweap National Monument proclaimed July 31, 1909"),
             ("renamed", "Zion National Monument", "incorporated in Zion National Monument by proclamation March 18, 1918."),
             ("established", "Zion National Park", "Established as a national park Nov. 19, 1919."),
             ("proclaimed", "Zion National Monument", "Separate Zion National Monument proclaimed Jan. 22, 1937"),
             ("enlarged", "Zion National Park", "incorporated in park July 11, 1956.")],
}

NOTES = {
    "ACAD": "The Index lists 14 boundary changes from 1929 to 1982; only the 1986 permanent boundary is listed here.",
    "BRCA": "The Index says the monument was 'renamed and redesignated Utah National Park June 7, 1924' and 'renamed Bryce Canyon National Park Feb. 25, 1928.'",
    "CONG": "Recent Changes lists Nov. 10, 2003 with the wording 'incorporated Congaree Swamp National Monument' (P.L. 108-108). Same date as the Index.",
    "CUVA": "The Index does not name the unit before 2000. Recent Changes says it was 'redesignated from a national recreation area' on Oct. 11, 2000 (P.L. 106-291), so the earlier name is given as Cuyahoga Valley National Recreation Area.",
    "BLCA": "Recent Changes also lists Oct. 21, 1999 (P.L. 106-076), 'redesignated from a national monument.' Same date as the Index.",
    "DEVA": "Recent Changes lists Oct. 31, 1994, 'incorporated Death Valley National Monument' (P.L. 103-433). Same date as the Index.",
    "DENA": "Park and preserve are separate rows in the acreage report: 'acres' is the national park, 'acres_preserve' the national preserve. The Index spells the first name 'Mt. McKinley National Park.'",
    "EVER": "The acreage report lists 'EVERGLADES NP' and 'EVERGLADES EXPANSION' on separate rows. Its endnote 6 says: 'FOR TOTAL ACREAGE OF EVERGLADES NATIONAL PARK - ADD THE ACREAGE FOR EVERGLADES NATIONAL PARK AND EVERGLADES EXPANSION.' 'acres' is that sum.",
    "GAAR": "Park and preserve are separate rows in the acreage report: 'acres' is the national park, 'acres_preserve' the national preserve.",
    "JEFF": "The Index entry is 'Jefferson National Expansion Memorial' (2012-2016). The 2018 change comes from Recent Changes, which names the old unit 'Jefferson Expansion Memorial' (sic) and cites 'S. 1438' rather than a public law number. The Index does not say which designation the 1935 date is; it says only 'Designated Dec. 21, 1935.'",
    "GLBA": "Park and preserve are separate rows in the acreage report: 'acres' is the national park, 'acres_preserve' the national preserve.",
    "GLAC": "The two 1932 events are the Waterton-Glacier International Peace Park designation. The Index lists them after the boundary changes.",
    "GRCA": "The Index lists a forest reserve, a game preserve, two separate units named Grand Canyon National Monument (1908 and 1932) and Marble Canyon National Monument before the 1975 combined park.",
    "GRTE": "The Jackson Hole National Monument (proclaimed March 15, 1943) and the 1950 enlargement come from one Index sentence; both events quote it. The Index entry under the same web address that follows is John D. Rockefeller, Jr. Memorial Parkway, which is not used here.",
    "GRSA": "Park and preserve are separate rows in the acreage report: 'acres' is the national park, 'acres_preserve' the national preserve. The Index lists the 'redesignation as a national park and national preserve' on Nov. 22, 2000 and 'Established Sept. 24, 2004.' Recent Changes lists the redesignation on September 24, 2004 (P.L. 106-530). The event list follows the Index.",
    "HALE": "The Index lists both Haleakalā and Hawai'i Volcanoes as 'established as part of Hawaii National Park Aug. 1, 1916'; Haleakalā was renamed Sept. 13, 1960. The Index prints the name 'Haleakalā' with a macron; the acreage report uses 'HALEAKALA NP.'",
    "HAVO": "Established in 1916 as part of Hawaii National Park; renamed Sept. 22, 1961. The Index heading spells the name 'Hawai'i Volcanoes' with an okina but writes 'Hawaii National Park' for the 1916 unit. The Index does not spell out the 1961 name; 'Hawaii Volcanoes National Park' here is our spelling, without the okina. The acreage report uses 'HAWAII VOLCANOES NP.'",
    "HOSP": "The Index lists 15 boundary changes, left out here.",
    "INDU": "The Index entry is 'Indiana Dunes National Lakeshore' (2012-2016). The 2019 change comes from Recent Changes, which cites 'P.L. 166-6' (as printed).",
    "ISRO": "The Index gives only the authorization date (March 3, 1931) and no establishment date. The 1940 establishment date comes from the park's 2016 Foundation Document Overview (NPS), page 4.",
    "JOTR": "Recent Changes lists Oct. 31, 1994, 'incorporated Joshua Tree National Monument' (P.L. 103-433). Same date as the Index.",
    "KATM": "Park and preserve are separate rows in the acreage report: 'acres' is the national park, 'acres_preserve' the national preserve.",
    "KICA": "Kings Canyon has its own Index entry, separate from Sequoia, but both list the shared web address www.nps.gov/seki. The 1940 event is both a renaming and an enlargement in the Index wording.",
    "LACL": "Park and preserve are separate rows in the acreage report: 'acres' is the national park, 'acres_preserve' the national preserve.",
    "LAVO": "Two national monuments (Lassen Peak and Cinder Cone) were combined into the park in 1916.",
    "MACA": "The 09/30/2026 acreage report gives 72,041.73 gross acres, of which 20,034.11 are non-federal. The Index (2012-2016) gave 52,830.19. The acreage reports do not explain the change.",
    "NPSA": "The acreage report lists all 8,256.67 acres as 'Other Public Acres' (none federal); the Index says 'all Nonfederal.' The land is leased (the 1993 50-year lease in the event list).",
    "NERI": "The Index entry is 'New River Gorge National River' (2012-2016). The 2020 change comes from Recent Changes, which says 'renamed from New River Gorge National River' (P.L. 116-260); it is listed here as a redesignation because the unit type changed. The acreage report has one combined row, 'NEW RIVER GORGE NP & PRES', so the park and preserve parts cannot be split from it.",
    "NOCA": "The Index lists three entries under www.nps.gov/noca: North Cascades National Park, Lake Chelan National Recreation Area and Ross Lake National Recreation Area. Only the park entry is used, and the acreage is the park row only.",
    "OLYM": "The Index lists nine boundary changes, left out here.",
    "PINN": "Recent Changes also lists January 10, 2013 (P.L. 112-245). Same date as the Index.",
    "REDW": "The acreage report's gross area includes non-federal land inside the boundary; the Index lists 61,252.91 non-federal acres for 2012-2016.",
    "SAGU": "Dates disagree. The Index says 'redesignated Oct. 4, 1994.' Recent Changes lists October 14, 1994, 'incorporated Saguaro National Monument' (P.L. 103-364). The event list follows the Index.",
    "SEQU": "Sequoia has its own Index entry, separate from Kings Canyon, but both list the shared web address www.nps.gov/seki. The Index lists Oct. 1, 1890 as Sequoia's first boundary change, the same day General Grant National Park was established.",
    "SHEN": "The Index lists three dates: authorized 1926, 'fully established' 1935, 'dedicated' 1936.",
    "THRO": "The acreage report spells the name 'T ROOSEVELT NP.'",
    "VIIS": "The Index gives only the authorization date (Aug. 2, 1956) and no separate establishment date.",
    "WHSA": "The Index entry is 'White Sands National Monument' (2012-2016) and gives only 'Proclaimed Jan. 18, 1933.' The 2019 change comes from Recent Changes (P.L. 116-92).",
    "WRST": "Park and preserve are separate rows in the acreage report: 'acres' is the national park, 'acres_preserve' the national preserve. The Index prints 'WrangellSt. Elias' without a hyphen in the text layer.",
    "YELL": "parks.json lists the state as ID; the Index lists Yellowstone under Wyoming, '(Also in Montana and Idaho).'",
    "YOSE": "The Index acreage 'does not include 1,397.99 acres composing El Portal administrative site, adjacent to park.' The acreage report does not say whether its Yosemite row includes El Portal. The Index also lists 'El Portal site authorized Sept. 2, 1958,' left out here.",
    "ZION": "The Index lists two different units called Zion National Monument: the renamed Mukuntuweap monument (1918), which became the park in 1919, and a separate one proclaimed in 1937 and added to the park in 1956.",
}

MONTHS = {"Jan": 1, "Feb": 2, "March": 3, "Mar": 3, "April": 4, "May": 5, "June": 6, "July": 7,
          "Aug": 8, "Sept": 9, "Oct": 10, "Nov": 11, "Dec": 12,
          "January": 1, "February": 2, "August": 8, "September": 9, "October": 10,
          "November": 11, "December": 12}
DATE_RE = re.compile(r"\b(Jan|Feb|March|Mar|April|May|June|July|Aug|Sept|Oct|Nov|Dec|January|February|"
                     r"August|September|October|November|December)\.? (\d{1,2}), (\d{4})")


def parse_date(s):
    m = DATE_RE.search(s)
    if not m:
        raise SystemExit(f"No date in {s!r}")
    return date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2))).isoformat(), m.group(0)


def main():
    parks = json.loads((ROOT / "config/parks.json").read_text())
    codes = [p["code"] for p in parks]
    names = {p["code"]: p["name"] for p in parks}
    ents = index_entries()
    rows, recent_updated = recent_rows()
    acres = acreage_rows()
    problems = []
    out = {}
    for code in codes:
        if code not in EVENTS:
            problems.append(f"{code}: no event list")
            continue
        url_code, page, start = INDEX_PICK.get(code, (code, None, None))
        cands = [(pg, body) for pg, body in ents.get(url_code, [])
                 if (page is None or pg == page) and (start is None or body.startswith(start))]
        if len(cands) != 1:
            problems.append(f"{code}: {len(cands)} Index entries found under www.nps.gov/{url_code.lower()}")
            continue
        page, body = cands[0]
        heading = INDEX_HEADING.get(code, names[code])
        evs = []
        for spec in EVENTS[code]:
            kind, name, text = spec[:3]
            want = spec[3] if len(spec) > 3 else None
            if isinstance(text, tuple) and text[0] == "doc":  # other NPS document
                url, path, dpage = EXTRA_DOCS[code]
                fetch(url, path)
                dtext = norm(PdfReader(str(path)).pages[dpage - 1].extract_text() or "")
                text = text[1]
                if key(text) not in key(dtext) or want not in text:
                    problems.append(f"{code}: text not in {url} p{dpage}: {text!r}")
                    continue
                d, dt = parse_date(want)
                source = f"{url}#page={dpage}"
            elif isinstance(text, tuple):  # Recent Changes row, picked by date + new name
                _, dtext = text
                hit = [r for r in rows if r and r[0] == dtext and len(r) > 2 and key(name) in key(r[1])]
                if len(hit) != 1:
                    problems.append(f"{code}: Recent Changes row for {dtext} {name}: {len(hit)} found")
                    continue
                r = hit[0]
                text = f"{r[0]} | {r[1]} | {r[2]}"
                d, dt = parse_date(r[0])
                source = RECENT_URL
            else:
                if key(text) not in key(body):
                    problems.append(f"{code}: text not in Index entry p{page}: {text!r}")
                    continue
                if want:
                    if want not in text:
                        problems.append(f"{code}: {want!r} not in {text!r}")
                        continue
                    d, dt = parse_date(want)
                else:
                    d, dt = parse_date(text)
                source = f"{INDEX_URL}#page={page}"
            stated = key(name) in key(text) or key(name) in key(body) or name == heading
            evs.append({"date": d, "date_text": dt, "kind": kind, "name": name,
                        "name_stated": stated, "text": text, "source": source})
        evs.sort(key=lambda e: e["date"])
        spec = ACRE_ROWS[code]
        spec = (spec, None, []) if isinstance(spec, str) else (tuple(spec) + ([],))[:3]
        park_row, pres_row, extra = spec
        missing = [n for n in [park_row, pres_row, *extra] if n and n not in acres]
        if missing:
            problems.append(f"{code}: acreage rows missing {missing}")
            continue
        rec = {"events": evs,
               "acres": round(acres[park_row] + sum(acres[n] for n in extra), 2),
               "acres_as_of": ACRES_AS_OF,
               "acres_source": ACRES_URL}
        if pres_row:
            rec["acres_preserve"] = acres[pres_row]
            rec["acres_park_and_preserve"] = round(rec["acres"] + acres[pres_row], 2)
        rec["notes"] = NOTES.get(code, "")
        out[code] = rec
    if problems:
        raise SystemExit("FAILED:\n  " + "\n  ".join(problems))
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(out)} parks, "
          f"{sum(len(v['events']) for v in out.values())} events. Recent Changes last updated {recent_updated}.")


if __name__ == "__main__":
    if "--dump" in sys.argv:
        for c, lst in sorted(index_entries().items()):
            for pg, body in lst:
                print(f"### {c} p{pg}\n{body}\n")
    else:
        main()
