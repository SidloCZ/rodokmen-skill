#!/usr/bin/env python3
"""Exportuje rodokmen z data/osoby.py do standardního formátu GEDCOM 5.5.1 (.ged, UTF-8).

Použití (z kořene projektu):
  python -I -X utf8 tools/ged_export.py [vystupy/rodokmen.ged] [--vychozi <kekule_cislo>]
    vystupy/rodokmen.ged   cílový soubor (výchozí: vystupy/rodokmen.ged)
    --vychozi <číslo>      exportovat jen podstrom předků počínaje osobou s tímto Kekulého číslem
                           (např. --vychozi 4 vyexportuje dědu a jeho přímé předky jako kořen stromu)

Převede předky z P (včetně vazeb rodič–dítě, sňatků, dat a míst narození/sňatku/úmrtí, povolání,
poznámek a citací zápisů ze zaznamy.json) a boční příbuzné ze SIDE do platného souboru GEDCOM 5.5.1.
"""
import datetime, json, os, re, sys
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
MONTHS_EN = {i: m for i, m in enumerate("JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split(), 1)}


def ged_date(cz):
    """Převede české datum ('14. 2. 1890', 'asi 1756', 'před 1785', 'po 1810') na GEDCOM datum."""
    s = (cz or "").strip()
    if not s:
        return ""
    pre = ""
    for k, g in (("asi ", "ABT "), ("≈", "ABT "), ("kolem ", "ABT "), ("před ", "BEF "), ("po ", "AFT ")):
        if s.lower().startswith(k):
            pre = g
            s = s[len(k):].strip()
            break
    m = re.match(r"^(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})$", s)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), m.group(3)
        if 1 <= mo <= 12:
            return f"{pre}{d} {MONTHS_EN[mo]} {y}"
    m = re.match(r"^(\d{1,2})[./]\s*(\d{4})$", s)
    if m:
        mo, y = int(m.group(1)), m.group(2)
        if 1 <= mo <= 12:
            return f"{pre}{MONTHS_EN[mo]} {y}"
    m = re.search(r"\b(1[4-9]\d\d|20\d\d)\b", s)
    if m:
        return f"{pre}{m.group(1)}"
    return s


def parse_fact(fact):
    """Rozebere řetězec faktu ('* 14. 2. 1890 Holice čp. 112') na (druh, datum_cz, misto, zbytek)."""
    s = fact.strip()
    for sym, tag in (("*", "BIRT"), ("×", "MARR"), ("†", "DEAT")):
        if s.startswith(sym):
            rest = s[len(sym):].strip()
            m = re.match(
                r"^((?:(?:asi|před|po|kolem)\s+|≈\s*)?(?:\d{1,2}\.\s*\d{1,2}\.\s*\d{4}|\d{1,2}[./]\s*\d{4}|\d{4}))\s*(.*)$",
                rest, re.I
            )
            if m:
                return tag, m.group(1).strip(), m.group(2).strip()
            return tag, "", rest
    return "OCCU", "", s


def split_name(full_name):
    """Rozdělí 'Jan František Novák' na ('Jan František', 'Novák') pro GEDCOM 'Jan František /Novák/'."""
    n = (full_name or "").strip()
    if not n or n.startswith("otec neuveden"):
        return "", ""
    parts = n.split()
    if len(parts) == 1:
        return parts[0], ""
    return " ".join(parts[:-1]), parts[-1]


def main():
    args = sys.argv[1:]
    root_k = 1
    if "--vychozi" in args:
        i = args.index("--vychozi")
        root_k = int(args[i + 1])
        args = args[:i] + args[i + 2:]
    out_path = os.path.abspath(args[0]) if args else os.path.join(ROOT, "vystupy", "rodokmen.ged")

    ns = {}
    osoby_p = os.path.join(DATA, "osoby.py")
    if not os.path.exists(osoby_p):
        sys.exit(f"Soubor {osoby_p} neexistuje.")
    exec(open(osoby_p, encoding="utf-8").read(), ns)
    P, SAME = ns.get("P", {}), ns.get("SAME", {})
    zaz_p = os.path.join(DATA, "zaznamy.json")
    zaznamy = {z["klic"]: z for z in json.load(open(zaz_p, encoding="utf-8"))} if os.path.exists(zaz_p) else {}

    def je_podstrom(k, r):
        while k >= r:
            if k == r:
                return True
            k //= 2
        return False

    vybrane = sorted(k for k in P if je_podstrom(k, root_k) and not P[k].get("n", "").startswith("otec neuveden"))
    if not vybrane:
        sys.exit(f"Pro výchozí osobu {root_k} nebyl v data/osoby.py nalezen žádný předek.")

    def canon(k):
        return SAME.get(k, k)

    lines = [
        "0 HEAD",
        "1 SOUR rodokmen-skill",
        "2 NAME Rodokmen Skill (Antigravity)",
        f"1 DATE {datetime.date.today().strftime('%d %b %Y').upper()}",
        "1 GEDC",
        "2 VERS 5.5.1",
        "2 FORM LINEAGE-LINKED",
        "1 CHAR UTF-8",
    ]

    fams = {}
    for k in vybrane:
        fk, mk = 2 * k, 2 * k + 1
        has_f = fk in P and not P[fk].get("n", "").startswith("otec neuveden")
        has_m = mk in P and not P[mk].get("n", "").startswith("otec neuveden")
        if has_f or has_m:
            fams[k] = (canon(fk) if has_f else None, canon(mk) if has_m else None)

    vydane_indi = set()
    for k in vybrane:
        ck = canon(k)
        if ck in vydane_indi:
            continue
        vydane_indi.add(ck)
        p = P[ck]
        givn, surn = split_name(p.get("n", ""))
        sex = p.get("sex") or ("M" if ck == 1 else ("M" if ck % 2 == 0 else "F"))
        lines.append(f"0 @I{ck}@ INDI")
        lines.append(f"1 NAME {givn} /{surn}/".strip())
        if givn:
            lines.append(f"2 GIVN {givn}")
        if surn:
            lines.append(f"2 SURN {surn}")
        lines.append(f"1 SEX {sex}")

        birt_written = deat_written = False
        for f in p.get("f", []):
            tag, d_cz, plac = parse_fact(f)
            if tag in ("BIRT", "DEAT"):
                if tag == "BIRT":
                    birt_written = True
                if tag == "DEAT":
                    deat_written = True
                lines.append(f"1 {tag}")
                if d_cz:
                    lines.append(f"2 DATE {ged_date(d_cz)}")
                if plac:
                    lines.append(f"2 PLAC {plac}")
            elif tag == "OCCU" and plac:
                lines.append(f"1 OCCU {plac}")

        y = p.get("y", "")
        if not birt_written and y:
            m = re.match(r"^(?:(asi|před|po)\s+|≈\s*|\*\s*)?(1[4-9]\d\d|20\d\d)", y.strip())
            if m:
                lines.append("1 BIRT")
                lines.append(f"2 DATE {ged_date((m.group(1) or '') + ' ' + m.group(2))}")
        if not deat_written and y:
            m = re.search(r"(?:–|†)\s*((?:asi|před|po)\s+|≈\s*)?(1[4-9]\d\d|20\d\d)", y)
            if m:
                lines.append("1 DEAT")
                lines.append(f"2 DATE {ged_date((m.group(1) or '') + ' ' + m.group(2))}")

        if k in fams:
            lines.append(f"1 FAMC @F{k}@")
        for child_k, (h_id, w_id) in fams.items():
            if ck in (h_id, w_id):
                lines.append(f"1 FAMS @F{child_k}@")

        note_parts = []
        if p.get("st"):
            note_parts.append(f"Stav doložení: {p['st']}")
        if p.get("note"):
            note_parts.append(p["note"])
        for rk in p.get("r", []):
            z = zaznamy.get(rk)
            if z:
                note_parts.append(f"Zápis [{rk}]: {z.get('nazev', '')} ({z.get('datum', '')}) – {z.get('odkaz', '')}".strip())
        if note_parts:
            full_note = " | ".join(note_parts).replace("\n", " ")
            lines.append(f"1 NOTE {full_note[:240]}")
            for i in range(240, len(full_note), 240):
                lines.append(f"2 CONC {full_note[i:i + 240]}")

    for child_k, (h_id, w_id) in sorted(fams.items()):
        lines.append(f"0 @F{child_k}@ FAM")
        if h_id:
            lines.append(f"1 HUSB @I{h_id}@")
        if w_id:
            lines.append(f"1 WIFE @I{w_id}@")
        lines.append(f"1 CHIL @I{canon(child_k)}@")
        marr_src = P.get(h_id or w_id, {})
        for f in marr_src.get("f", []):
            tag, d_cz, plac = parse_fact(f)
            if tag == "MARR":
                lines.append("1 MARR")
                if d_cz:
                    lines.append(f"2 DATE {ged_date(d_cz)}")
                if plac:
                    lines.append(f"2 PLAC {plac}")
                break

    lines.append("0 TRLR")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"GEDCOM uložen: {out_path} ({len(vydane_indi)} osob, {len(fams)} rodin)")


if __name__ == "__main__":
    main()

