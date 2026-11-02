# AGENTS.md – Pravidla projektu rodokmenu a instrukce pro AI asistenta

Tento soubor slouží jako centrální a závazná sada instrukcí pro AI asistenta v prostředí IDE (Antigravity, Cursor, Windsurf, VS Code, Gemini).

---

# ČÁST I: PRAVIDLA TOHOTO PROJEKTU (Project-Specific)

## 1. Postup na začátku každé konverzace
Tohle je projekt rodokmenu vedený skillem **rodokmen** (`.agents/skills/rodokmen/SKILL.md`). Na začátku každé konverzace:
1. Načti skill `rodokmen` (`.agents/skills/rodokmen/SKILL.md`), pokud ještě není načtený.
2. Přečti `data/STAV.md` – stav, pravidla a co je rozpracované – a konec `data/research_log.md` (v Režimu AI Genealog i `pripady/PREHLED.md`).
3. Pokračuj tam, kde se skončilo. Komunikuj česky, stručně a srozumitelně pro člověka bez zkušeností s genealogií a programováním.
4. Po dokončení každé ucelené větve nebo generace (po uložení do `data/STAV.md` a `data/research_log.md`) doporuč uživateli příkaz `/compact`, aby se z kontextu uvolnily staré snímky matrik a šetřily se tokeny.
5. Co by šlo ve skillu zlepšit (chyby nástrojů, nové archivy, nápady), zapisuj do `poznamky_pro_skill.md` – viz skill, sekce „Poznámky pro správce skillu“.

## 2. Specifikace a příkazy projektu
- **Tech stack:** Python 3 (`Pillow` / `PIL`, volitelně `ImageMagick`), Astro 7, Pagefind, Leaflet / OpenStreetMap, Netlify Edge Functions.
- **Spouštěcí a kontrolní příkazy:**
  - Kontrola dat a konzistence: `python -I -X utf8 tools/kontrola.py`
  - Úprava položky v JSON datech: `python -I -X utf8 tools/zapis.py <soubor.json> <akce> ...`
  - Export do GEDCOM 5.5.1: `python -I -X utf8 tools/ged_export.py vystupy/rodokmen.ged`
  - Porovnání s referenčním GEDCOMem: `python -I -X utf8 tools/ged_porovnej.py <referencni.ged>`
  - Převod dat do webu (ve složce `web/`): `npm run data`
  - Vývojový server / náhled webu (ve složce `web/`): `npm run dev` / `npm run nahled`
- **Pravidla pro Windows a Antigravity terminál (`run_command`):**
  - Python spouštěj vždy jako `python -I -X utf8 tools/<nastroj>.py` (ne `python3`).
  - V příkazech používej vždy dopředná lomítka (`/`) a relativní cesty z kořene projektu (žádná zpětná lomítka `\`, žádné zbytečné roury `|`, středníky `;` ani bloky `{ ... }`).
  - Zpracování obrázků (`vyrez.py`, `ramecek.py`, `overit.py`, `aron_img.py` aj.) funguje automaticky přes Python knihovnu `Pillow` (`PIL`) nebo `ImageMagick` (`magick`). Nikdy nepoužívej příkaz `convert`.
- **Pravidla pro síť a data:**
  - Síť na weby archivů smí chodit jen přes brzdu `tools/slusne.py` (vlastní skripty, curl), i v zadání pomocníků (`invoke_subagent`) – viz skill, „Šetrně k archivům“.
  - Nikdy ručně needituj `web/src/data/site.json`; jediným zdrojem pravdy je složka `data/`.

---

# ČÁST II: UNIVERZÁLNÍ GLOBÁLNÍ STANDARDY (Global Core)

## 1. Komunikace, minimalismus a kontrola nad změnami
- **Méně je někdy více:** Preferuj jednoduchá, čistá, funkční a věcná řešení.
- **Audit a transparentnost nepožádaných změn kódu:** Pokud v kódu provedeš jakoukoliv změnu, refaktoring nebo optimalizaci, o kterou uživatel v zadání výslovně nežádal, VŽDY tuto změnu v odpovědi zřetelně zdůrazni a vysvětli její důvod.
- **Striktní zákaz emoji:** V celém projektu (uživatelské rozhraní, kód, komentáře, commit zprávy, texty i odpovědi asistenta) je **přísně zakázáno používat emoji**. Místo emotikonů používej výhradně minimalistické jednobarevné inline SVG.
- **Faktická přesnost bez domýšlení:** Nikdy si nevymýšlej neověřené parametry, čísla nebo fakta. V rodokmenu označuj nedoložené hypotézy jako `st="prob"` nebo `st="unk"`.

## 2. Nástroje IDE, Git a verzování
- **Nativní IDE nástroje:** K vyhledávání, čtení a inspekci souborů používej nativní workspace nástroje (`read_file`, vyhledávání).
- **Commit message (Conventional Commits):** Na konci každé zprávy v chatu připrav výstižný návrh commit zprávy v angličtině podle konvence (`feat(...)`, `fix(...)`, `chore(...)`, `docs(...)`, `refactor(...)`, `style(...)`) jako čistý text bez `git commit -m` a bez uvozovek. Nikdy nespouštěj commit ani push automaticky.

## 3. Jazyková pravidla a česká mikrotypografie
- **České uvozovky:** V českých textech používej výhradně uvozovky 99–66: dole `„` (U+201E) a nahoře `“` (U+201C).
- **Pomlčka vs. spojovník:** Půlčtverčíková pomlčka (`–`, en-dash) pro číselné rozsahy bez mezer (*1890–1944*) a jako větná pomlčka oddělená mezerami; spojovník (`-`) pouze pro složená slova.
- **Pevné mezery (`&nbsp;` / `\u00A0`):** Jednopísmenné předložky a spojky (*k, s, v, z, o, u, a, i*) a mezery mezi číslem a jednotkou navaž pevnou mezerou.
