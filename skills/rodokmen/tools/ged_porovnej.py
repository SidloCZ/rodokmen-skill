#!/usr/bin/env python3
"""Porovná předky v data/osoby.py s referenčním GEDCOM souborem po generacích.

Použití (z kořene projektu):
  python -I -X utf8 tools/ged_porovnej.py <referencni.ged> ["Jméno výchozí osoby v GEDCOMu"] [--vychozi <kekule_v_osoby_py>]

Vypíše přehledovou tabulku po generacích:
  Generace | Osoby ref. | Osoby AI | Osoby AI správně
a podrobný seznam odchylek (pravopisné varianty jako Foitík × Fojtík, chybějící předci, rozdílné osoby).
"""
import os, re, sys, unicodedata
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import ged_import  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

KRESTNI_SYNONYMA = {
    "johann": "jan", "joannes": "jan", "jan": "jan", "hans": "jan",
    "wenzel": "vaclav", "wenceslaus": "vaclav", "vaclav": "vaclav",
    "franz": "frantisek", "franciscus": "frantisek", "frantisek": "frantisek",
    "joseph": "josef", "josephus": "josef", "josef": "josef",
    "georg": "jiri", "georgius": "jiri", "jiri": "jiri", "juraj": "jiri",
    "matthias": "matej", "mathes": "matej", "matej": "matej", "matous": "matej",
    "adalbert": "vojtech", "vojtech": "vojtech",
    "laurenz": "vavrinec", "laurentius": "vavrinec", "vavrinec": "vavrinec",
    "maria": "marie", "marie": "marie", "marianna": "marie", "marina": "marie",
    "katharina": "katerina", "catharina": "katerina", "katerina": "katerina",
    "theresia": "terezie", "terezia": "terezie", "terezie": "terezie", "tereza": "terezie",
    "barbara": "barbora", "barbora": "barbora",
    "magdalena": "magdalena", "majdalena": "magdalena",
    "dorothea": "dorota", "dorota": "dorota",
    "ludmilla": "lidmila", "ludmila": "lidmila", "lidmila": "lidmila",
    "apollonia": "apolena", "apolena": "apolena",
    "rosina": "ruzena", "rosalia": "ruzena", "ruzena": "ruzena",
    "elisabeth": "alzbeta", "alzbeta": "alzbeta", "betka": "alzbeta",
}


def bez_diakritiky(s):
    return "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if not unicodedata.combining(c))


def norm_jmeno(full):
    """Vrátí (norm_krestni, norm_prijmeni, volne_prijmeni) pro porovnání."""
    s = bez_diakritiky(re.sub(r"\([^)]*\)|\?", " ", full or "")).strip()
    parts = [p for p in s.split() if p not in ("ml.", "st.", "mladsi", "starsi")]
    if not parts:
        return "", "", ""
    if len(parts) == 1:
        krest = KRESTNI_SYNONYMA.get(parts[0], parts[0])
        return krest, "", ""
    krest = KRESTNI_SYNONYMA.get(parts[0], parts[0])
    prijm = parts[-1]
    for konc in ("ova", "ov", "ych", "u"):
        if len(prijm) > len(konc) + 2 and prijm.endswith(konc):
            prijm = prijm[:-len(konc)]
            break
    if len(prijm) > 3 and prijm.endswith(("y", "a", "i", "e")):
        prijm = prijm[:-1]
    volne = re.sub(r"[ijy]", "i", prijm).replace("w", "v").replace("cz", "c").replace("sz", "s").replace("au", "ou")
    return krest, prijm, volne


def porovnej_osoby(jmeno_ref, jmeno_ai):
    """Vrátí ('presne' | 'varianta' | 'neshoda')."""
    kr1, pr1, vl1 = norm_jmeno(jmeno_ref)
    kr2, pr2, vl2 = norm_jmeno(jmeno_ai)
    if not kr2:
        return "neshoda"
    kr_ok = (kr1 == kr2) or (kr1 in kr2) or (kr2 in kr1)
    if not kr_ok:
        return "neshoda"
    if not pr1 or not pr2:
        return "varianta"
    if pr1 == pr2:
        return "presne"
    if vl1 == vl2 or pr1.startswith(pr2[:3]) or pr2.startswith(pr1[:3]):
        return "varianta"
    return "neshoda"


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    root_k = 1
    max_depth = None
    if "--vychozi" in args:
        i = args.index("--vychozi")
        root_k = int(args[i + 1])
        args = args[:i] + args[i + 2:]
    if "--hloubka" in args:
        i = args.index("--hloubka")
        max_depth = int(args[i + 1])
        args = args[:i] + args[i + 2:]

    ged_path = args[0]
    recs = ged_import.read(ged_path)

    ged2_path = None
    if len(args) > 1 and args[1].lower().endswith(".ged") and os.path.isfile(args[1]):
        ged2_path = args[1]
        args = [args[0]] + args[2:]

    ns = {}
    osoby_path = os.path.join(DATA, "osoby.py")
    if os.path.isfile(osoby_path):
        exec(open(osoby_path, encoding="utf-8").read(), ns)
    P, SAME = ns.get("P", {}), ns.get("SAME", {})

    def ai_osoba_from_py(rel_k):
        # mapuje relativní Kekulého číslo (1 = root_k) na číslo v P
        g = rel_k.bit_length() - 1
        real_k = (root_k << g) + (rel_k - (1 << g))
        real_k = SAME.get(real_k, real_k)
        p = P.get(real_k)
        if not p or p.get("n", "").startswith("otec neuveden") or p.get("st") == "unk":
            return None
        return p

    start_query = args[1] if len(args) > 1 else (ai_osoba_from_py(1) or {}).get("n", "")
    if not start_query and recs:
        first_ind = next((r for k, r in recs.items() if r.get("tag") == "INDI"), None)
        start_query = ged_import.name(first_ind) if first_ind else ""
    if not start_query:
        sys.exit("Zadej jméno výchozí osoby v GEDCOMu jako 2. parametr.")
    start_ind = recs.get(start_query) or ged_import.find(recs, start_query)

    if ged2_path:
        recs2 = ged_import.read(ged2_path)
        start_ind2 = recs2.get(start_query) or ged_import.find(recs2, start_query)
        ai_tree, todo2 = {1: start_ind2}, [1]
        while todo2:
            k = todo2.pop(0)
            f, m = ged_import.parents(ai_tree[k], recs2)
            for kk, p in ((2 * k, f), (2 * k + 1, m)):
                if p:
                    ai_tree[kk] = p
                    todo2.append(kk)
        def ai_osoba(rel_k):
            ind = ai_tree.get(rel_k)
            return {"n": ged_import.name(ind)} if ind else None
    else:
        ai_osoba = ai_osoba_from_py

    ref_tree, todo = {1: start_ind}, [1]
    while todo:
        k = todo.pop(0)
        f, m = ged_import.parents(ref_tree[k], recs)
        for kk, p in ((2 * k, f), (2 * k + 1, m)):
            if p:
                ref_tree[kk] = p
                todo.append(kk)

    max_gen = max((k.bit_length() for k in ref_tree), default=1)
    if max_depth:
        max_gen = min(max_gen, max_depth)
    print(f"{'Generace':<14} {'Osoby ref.':>12} {'Osoby AI':>12} {'Osoby AI správně':>18}")
    print("-" * 60)
    tot_ref = tot_ai = tot_ok = 0
    varianty, neshody, chybi = [], [], []

    for g in range(1, max_gen + 1):
        lo, hi = 1 << (g - 1), (1 << g) - 1
        g_ref = g_ai = g_ok = 0
        for k in range(lo, hi + 1):
            r_ind = ref_tree.get(k)
            a_p = ai_osoba(k)
            r_name = ged_import.name(r_ind) if r_ind else None
            a_name = a_p.get("n") if a_p else None
            if r_name:
                g_ref += 1
            if a_name:
                g_ai += 1
            if r_name and a_name:
                st = porovnej_osoby(r_name, a_name)
                if st in ("presne", "varianta"):
                    g_ok += 1
                    if st == "varianta" and bez_diakritiky(r_name) != bez_diakritiky(a_name):
                        varianty.append((g, k, r_name, a_name))
                else:
                    neshody.append((g, k, r_name, a_name))
            elif r_name and not a_name:
                chybi.append((g, k, r_name))
        tot_ref += g_ref
        tot_ai += g_ai
        tot_ok += g_ok
        if g_ref or g_ai:
            print(f"{g}. generace    {g_ref:>12} {g_ai:>12} {g_ok:>18}")

    print("-" * 60)
    print(f"{'Celkem':<14} {tot_ref:>12} {tot_ai:>12} {tot_ok:>18}")

    if varianty:
        print("\nPravopisné varianty / částečné přepisy (uznáno jako správná osoba):")
        for g, k, rn, an in varianty:
            print(f"  gen {g} (#{k}): ref „{rn}“ × AI „{an}“")
    if neshody:
        print("\nRozdílné osoby (možná záměna jmenovce nebo chyba v jednom z rodokmenů):")
        for g, k, rn, an in neshody:
            print(f"  gen {g} (#{k}): ref „{rn}“ × AI „{an}“")
    if chybi:
        print(f"\nChybějící osoby v AI rodokmenu ({len(chybi)}):")
        for g, k, rn in chybi[:20]:
            print(f"  gen {g} (#{k}): {rn}")


if __name__ == "__main__":
    main()
