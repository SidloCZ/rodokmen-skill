# AGENTS.md – Pravidla projektu a instrukce pro AI asistenta

Tento soubor slouží jako centrální a závazná sada instrukcí pro AI asistenta v prostředí IDE (Antigravity, Cursor, Windsurf, VS Code, Gemini).

---

# ČÁST I: PRAVIDLA TOHOTO PROJEKTU (Project-Specific)

## 1. Specifikace a technologický stack
- **Název projektu / repozitáře:** `rodokmen-skill` (fork `https://github.com/SidloCZ/rodokmen-skill`, upstream `https://github.com/sarsonj/rodokmen-skill`)
- **Hlavní účel:** AI skill a sada nástrojů pro tvorbu rodokmenu z českých, moravských a rakouských digitalizovaných matrik, řešení badatelských záhad v režimu AI Genealog a generování statického rodinného webu.
- **Tech stack:** Python 3 (`Pillow` / `PIL`, volitelně `ImageMagick`), Astro 7, Pagefind, Leaflet / OpenStreetMap, Netlify Edge Functions.
- **Spouštěcí a testovací příkazy:**
  - Založení / aktualizace projektu rodokmenu: `python -I -X utf8 skills/rodokmen/tools/novy_projekt.py <cilova_slozka>`
  - Založení ukázkového projektu: `python -I -X utf8 skills/rodokmen/tools/novy_projekt.py <cilova_slozka> --ukazka`
  - Kontrola dat v projektu rodokmenu: `python -I -X utf8 tools/kontrola.py`
  - Export dat do webu (ve složce `web/` projektu): `npm run data`
  - Vývojový server / náhled webu (ve složce `web/` projektu): `npm run dev` / `npm run nahled`
  - Kontrola syntaxe nástrojů: `python -I -X utf8 -m py_compile skills/rodokmen/tools/<skript>.py`

## 2. Architektura a specifické konvence projektu
- **Klíčové složky a soubory:**
  - `skills/rodokmen/SKILL.md` – hlavní metodický průvodce pro agenta (fáze 0–5, Režim AI Genealog, ochrana proti jmenovcům). Registrován v Antigravity přes `.agents/skills.json`.
  - `skills/rodokmen/tools/` – Python skripty pro stahování z archivů (`aron_img.py`, `trebon.py`, `portafontium.py`, `ebadatelna.py`, `ahmp_scan.py`, `soal_zoomify.py`, `matricula_fetch.py`), výřezy a rejstříkové pásy (`vyrez.py`, `ramecek.py`, `overit.py`), brzdu a hlídače sítě (`slusne.py`, `hlidac_site.py`), kontrolu dat (`kontrola.py`, `zapis.py`), GEDCOM (`ged_import.py`, `ged_export.py`, `ged_porovnej.py`, `ftb_export.py`) a web (`export_web.py`, `fan_chart.py`, `mista.py`).
  - `skills/rodokmen/reference/` – podrobné metodické příručky (`matriky.md`, `portaly.md`, `data.md`, `web.md`, `pribehy.md`, `soukromi.md`, `playbook.md`).
  - `skills/rodokmen/template/` – šablona zakládaného projektu rodokmenu (`data/`, `pripady/PREHLED.md`, `ukazka/`, `web/`, `.agents/launch.json`, `AGENTS.md`).
  - `skills/rodokmen/VERZE` – číslo aktuální verze skillu.
- **Pravidla pro Windows a Antigravity terminál (`run_command`):**
  - Python spouštěj vždy jako `python -I -X utf8` (nikdy `python3`).
  - V příkazech používej vždy dopředná lomítka (`/`) a relativní cesty z kořene workspace (žádná zpětná lomítka `\`, žádné zbytečné roury `|`, středníky `;` ani bloky `{ ... }`).
  - Zpracování obrázků (`vyrez.py`, `ramecek.py`, `overit.py`, `aron_img.py` aj.) funguje automaticky přes Python knihovnu `Pillow` (`PIL`) nebo `ImageMagick` (`magick`). Nikdy nepoužívej příkaz `convert`.
- **Specifická pravidla pro data, síť a stav:**
  - Síťové dotazy na weby archivů smí chodit výhradně přes brzdu `tools/slusne.py` (stránky max. 1 za `2,0 s`, obrázky/dlaždice max. 1 za `0,15 s`; po HTTP 429/503 nebo varování archivu se doména na 30 minut zastaví).
  - Ve vygenerovaném projektu rodokmenu se nikdy ručně needituje `web/src/data/site.json`; jediným zdrojem pravdy je složka `data/` (`osoby.py`, `zaznamy.json`, `svazky.json`, `prepisy.json`, `zvyrazneni.json`, `mista.json`, `web.json`).
  - Všechny zápisy z `tools/` musí ukládat soubory s konci řádků LF (`newline="\n"`).
- **Vydání nové verze a větvení:**
  - Repozitář je napojen na `origin` (`https://github.com/SidloCZ/rodokmen-skill`) a `upstream` (`https://github.com/sarsonj/rodokmen-skill.git`).
  - Při vydání nové verze zvedni číslo v `skills/rodokmen/VERZE` a `README.md`. Do `CHANGELOG.md` přidej nahoru sekci `## X.Y.Z – D. M. RRRR`.

---

# ČÁST II: UNIVERZÁLNÍ GLOBÁLNÍ STANDARDY (Global Core)

## 1. Komunikace, minimalismus a kontrola nad změnami

- **Méně je někdy více:**
  - Preferuj jednoduchá, čistá, funkční a věcná řešení.
  - Vyvaruj se překombinovaných návrhů a zbytečného kódu navíc.
- **Audit a transparentnost nepožádaných změn kódu:**
  - Pokud v kódu provedeš jakoukoliv změnu, refaktoring nebo optimalizaci, **o kterou uživatel v zadání výslovně nežádal**, VŽDY tuto změnu v odpovědi zřetelně zdůrazni a vysvětli její důvod.
  - Nápady a návrhy nad rámec původního zadání neimplementuj svévolně – popiš je v chatu jako dotaz či doporučení.
- **Striktní zákaz emoji:**
  - V celém projektu (uživatelské rozhraní, dialogy, toast zprávy, kód, komentáře, commit zprávy, texty i odpovědi asistenta) je **přísně zakázáno používat emoji**.
  - Místo emotikonů používej výhradně **pěkné, minimalistické, jednobarevné inline SVG**.
  - Zákaz Unicode vlaječek států (na Windows se vykreslují jako textová písmena) – vždy nahradit inline SVG vlajkou.
- **Faktická přesnost bez domýšlení:**
  - Nikdy si nevymýšlej neověřené parametry, čísla nebo fakta. Pokud chybí přesný zdroj či data, zeptej se uživatele nebo nastav prvek do stavu konceptu / nejistoty (`st="prob"` nebo `st="unk"`).

---

## 2. Nástroje IDE, Git a verzování

- **Nativní IDE nástroje:**
  - K vyhledávání, čtení a inspekci souborů používej nativní workspace nástroje (`read_file`, vyhledávání).
  - Nepoužívej terminálové zkratky typu `node -e` ani ad-hoc bash skripty pro inspekci souborů.
- **Commit message (Conventional Commits):**
  - Na konci každé zprávy v chatu připrav výstižný návrh commit zprávy v angličtině podle konvence (`feat(...)`, `fix(...)`, `chore(...)`, `docs(...)`, `refactor(...)`, `style(...)`).
  - Vypiš **pouze čistý text zprávy** bez balení do `git commit -m` a bez uvozovek.
  - Asistent **nikdy nespouští commit ani push automaticky**, pouze navrhne zprávu a čeká na potvrzení uživatelem.
- **Sémantické verzování (SemVer):**
  - Při aktualizaci verzí (`skills/rodokmen/VERZE`, `package.json` apod.) dodržuj:
    - **PATCH (`x.y.Z+1`):** Opravy chyb, drobný refaktoring, styly, textové úpravy.
    - **MINOR (`x.Y+1.0`):** Nové funkce, nové nástroje, nové UI komponenty, rozšíření API.
    - **MAJOR (`X+1.0.0`):** Zlomové změny architektury, nekompatibilní přepracování.
- **Udržování dokumentace:**
  - Při zásadní změně struktury kódu nebo novém nástroji adekvátně aktualizuj soubory dokumentace (`README.md`, `CHANGELOG.md`, `skills/rodokmen/SKILL.md`).

---

## 3. UI, UX a frontendový design

- **Jednoduchost UI prvků:**
  - Tlačítka, položky navigace a nadpisy formuluj stručně a výstižně (ideálně 1–2 slova).
  - Do UI nepřidávej svévolné dekorativní štítky a odznaky (badges jako „Novinka“, „Báze znalostí“), pokud nebyly vyžádány.
- **Parita světlého a tmavého režimu (Dark / Light mode):**
  - Při jakékoliv úpravě barev nebo motivů zajisti adekvátní kontrast a funkčnost v obou režimech současně.
- **Staging a produkční synchronizace:**
  - Pokud projekt využívá trvalé testovací či staging stránky (`temp-*`), udržuj jejich kód v synchronizovaném stavu s odpovídajícími ostrými verzemi.

---

## 4. Jazyková pravidla a česká mikrotypografie

- **Výchozí jazyk:** Řiď se jazykem promptu (typicky čeština; u webových projektů s `/en/` verzí udržuj překladovou paritu).
- **Zásady české mikrotypografie:**
  - **Pevné mezery (`&nbsp;` / `\u00A0`):** Neslabičné a jednopísmenné předložky a spojky (*k, s, v, z, o, u, a, i*) nesmí zůstávat na konci řádku. Vždy je navaž pevnou mezerou k následujícímu slovu.
  - **České uvozovky:** V českých textech používej výhradně uvozovky 99–66: dole `„` (U+201E) a nahoře `“` (U+201C). Zákaz rovných `""` i anglických `“...”`.
  - **Pomlčka vs. spojovník:**
    - Půlčtverčíková pomlčka (`–`, en-dash): Pro číselné rozsahy bez mezer (*1890–1944*, *10–15 mm*, *20–25 °C*) a jako větná pomlčka oddělená mezerami po obou stranách.
    - Spojovník (`-`, hyphen): Pouze pro těsně vázaná složená slova (*česko-slovenský*) nebo dělení slov.
  - **Jednotky a procenta:** Mezi číslem a jednotkou je vždy pevná mezera (`12&nbsp;mm`, `24&nbsp;°C`). U procent: `10 %` = deset procent (podstatné jméno), `10%` = desetiprocentní (přídavné jméno).
  - **Desetinná čísla a řády:** V českém textu piš desetinnou čárku (*1,5 mm*), v anglickém tečku (*1.5 mm*). Tisíce a vyšší řády odděluj mezerou (*10 000*).
- **Japonský jazyk (pokud je v projektu použit):**
  - Přepis do latinky uváděj vždy **českým přepisem** (vhodně doplněný o Hepburn). U kandži vždy doplň přepis do kany.

---

# ČÁST III: SPECIALIZOVANÝ MODUL – GENEALOGIE, MATRIKY A PALEOGRAFIE
<!-- Tento modul je aktivní při práci s matričními zápisy, rodokmenem a historickými prameny -->

## 1. Ochrana proti záměně jmenovců (Anti-Homonym Protocol)
- Před přiřazením narození/křtu k ženichovi nebo nevěstě vždy ověř **4 kotvy**:
  1. **Číslo popisné (*čp.*):** Návaznost domu mezi narozením, sňatkem a narozením sourozenců.
  2. **Rodné příjmení a původ matky:** Shoda rodného příjmení matky (a jejích rodičů) mezi zápisem o sňatku a zápisem o narození.
  3. **Povolání / stav a kmotři (*patrini*):** Kontinuita sociálního stavu (*sedlák/Bauer*, *chalupník/Chaluppner*, *domkář/Häusler*, *podruh/Inwohner*) a okruhu kmotrů.
  4. **Kontrola úmrtí dítěte a nekronym:** Vždy prověř matriku zemřelých (a narozených 5–8 let po křtu), zda nalezené dítě nezemřelo v dětském věku a zda se nenarodil mladší sourozenec téhož jména.

## 2. Paleografie kurentu a normalizace jmen
- **Rejstříky (indexy):** Nikdy neuzavírej hustě psaný rejstřík jako „nenalezeno“ z celostránkového náhledu; vždy jej rozřež přes `python -I -X utf8 tools/overit.py <snimek.jpg> rejstrik <prefix>` na 5 vodorovných pásů v šířce 2000 px.
- **Sjednocení příjmení v `osoby.py`:** Převáděj archaické spřežky (`cz` → `č`, `sz` → `š`, `rz` → `ř`, `w` → `v`, `au` → `ou`, `ay/ey/oy/uy` → `aj/ej/oj/uj`) na dnešní český tvar větve; původní zápis ponech v `prepisy.json` (`orig`).
- **Moravská příjmení na `-ů`:** Příjmení typu *Tomšů, Fojtů, Janů, Petrů, Ševců, Kovářů* jsou uvízlý genitiv plurálu a **nikdy se nepřechylují** koncovkou `-ová` u žen.

---

# ČÁST IV: SPECIALIZOVANÝ MODUL – BIOLOGIE A MYRMEKOLOGIE
<!-- Tento modul je aktivní při tvorbě biologického, taxonomického a chovatelského obsahu -->

## 1. Binomická nomenklatura (Vědecké názvosloví)
- **Rod (Genus):** První písmeno velké, formátováno kurzívou (*Camponotus*, *Odontomachus*, *Lasius*, *Formica*).
- **Druhový přívlastek:** Všechna písmena malá, formátováno kurzívou (*ligniperda*, *tyrannicus*, *niger*).
- **Skupina druhů (Species group):** Pouze druhové jméno kurzívou, slovo „group“ nebo „skupina druhů“ normálním písmem bez kurzívy (*tyrannicus* group, skupina druhů *rufa*).
- **Vyšší taxony (Tribus, Podčeleď, Čeleď):** Velké počáteční písmeno, **normální písmo bez kurzívy** (Camponotini, Formicinae, Formicidae).
- **Zákaz CSS capitalize:** Nikdy nepoužívat CSS vlastnost `capitalize` ani automatické kapitálky na druhy (nepřípustné: *Camponotus Ligniperda*).

## 2. Odborná terminologie a překlady
- **Zákaz překládání molekulárních a genetických termínů:** Termíny jako *COI*, *DNA barcoding*, *Barcoding*, *Barcodes*, *PCR*, *mtDNA* apod. se **NIKDY NEPŘEKLÁDAJÍ** do češtiny (např. nepoužívat výrazy „čárové kódy DNA“). Ponechat standardní vědecké označení.
- **Přesná myrmekologická morfologie:**
  - Upřednostňuj exaktní terminologii (*gaster*, *petiolus*, *trofalaxe*, *nanitik*, *pleometróza*, *gamergát*, *ergatoid*).
  - Nepřidávat české názvy do závorek za odborné termíny, které se běžně nepřekládají.
  - **Diapauza:** Mravenci mají diapauzu; nepoužívat paušálně termíny „hibernace“ či „zimování“, pokud to není přesně fyziologicky podloženo.
  - **Subkasty a kasty:** Major je subkasta dělnice, voják (soldier) je samostatná kasta s unikátními morfologickými znaky (fragmotická hlava, šavlovitá kusadla). Množné číslo: majoři, minoři, medie (nikoliv „majory“, „minora“).
