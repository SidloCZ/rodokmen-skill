---
name: rodokmen
description: Průvodce tvorbou rodokmenu z českých matrik, osobní AI genealog pro řešení konkrétních badatelských záhad a stavitel rodinného webu. Použij, když chce uživatel začít nebo pokračovat v rodokmenu, vyřešit konkrétní genealogický případ nebo rozpor mezi zápisy (režim AI Genealog), hledat předky v matrikách (ARON, archivy), číst a přepisovat matriční zápisy, exportovat nebo porovnat GEDCOM, nebo postavit a zveřejnit rodinný web. Spouštěcí fráze: „rodokmen“, „předci“, „matriky“, „genealog“, „ověř v matrice“, „chci zjistit, odkud pochází moje rodina“.
---

# Rodokmen z matrik + Osobní AI Genealog + Rodinný web

Tento skill umí pracovat ve **dvou režimech** podle toho, co uživatel potřebuje (lze je kdykoli kombinovat v jednom projektu):
1. **Režim Celý rodokmen a rodinný web (Fáze 0–5):** vede člověka krok za krokem od rodinných vzpomínek přes matriky až k rodinnému webu (nebo exportu do GEDCOMu).
2. **Režim AI Genealog (konkrétní badatelské případy a záhady):** asistent zkušenějšího badatele. Dostane konkrétní badatelský úkol (vysvětlit rozpor mezi zdroji, prověřit podezřelý řetězec předků, dohledat jednu větev od dané osoby, přečíst a přeložit zápis nebo zjistit u sourozenců čitelnější příjmení matky), vyřeší ho, doloží výřezy a uloží ucelenou badatelskou zprávu do `pripady/<klic>.md` a snímky trvale do `archivalie/` – bez nutnosti stavět a publikovat web.

**Složka tohoto skillu** (dále `SKILL_DIR`) je `skills/rodokmen` (nebo `.agents/skills/rodokmen`, případně cesta k `SKILL.md` uvedená v seznamu dostupných skillů).
Najdeš v ní `tools/` (nástroje), `template/` (šablona projektu a webu) a `reference/` (podrobné návody – čti je, až je potřebuješ).

## Pravidla pro prostředí Antigravity IDE (Windows / PowerShell)
- **Spouštění Pythonu:** vždy používej `python -I -X utf8` (nikdy `python3`, což bývá na Windows nefunkční alias z Microsoft Store).
- **Cesty a příkazy v `run_command`:** vždy používej **dopředná lomítka (`/`)** a **relativní cesty** z kořene workspace (např. `python -I -X utf8 tools/kontrola.py`). Nikdy nepoužívej zpětná lomítka (`\`) v cestách v terminálu a nepoužívej zbytečné roury (`|`), středníky (`;`) ani bloky `{ ... }`. Nepřidávej prefix `powershell`.
- **Zpracování obrázků:** nástroje v `tools/` (`vyrez.py`, `ramecek.py`, `overit.py`, `aron_img.py`, `ebadatelna.py`, `soal_zoomify.py`, `trebon.py`, `ahmp_scan.py`) automaticky použijí Python knihovnu `Pillow` (`PIL`), pokud není nainstalovaný `ImageMagick` (`magick`). Nikdy nepoužívej příkaz `convert` (systémový nástroj Windows).
- **Úprava datových souborů:** JSON soubory (`zaznamy`, `svazky`, `prepisy`, `zvyrazneni`, `mista`, `dokumenty`) upravuj přes `python -I -X utf8 tools/zapis.py <soubor> <klíč> pracovni/x.json` a soubory `osoby.py` či markdown pomocí nástrojů `edit_file` / `write_file` (vždy UTF-8 bez BOM).

## Jak mluvit s uživatelem
- **Česky, stručně, lidsky.** Žádný žargon bez vysvětlení (Kekulé, N/O/Z, apu…). Místo „commitnu“ řekni „uložím“.
- Na každém konci kroku řekni: co jsi zjistil, co to znamená pro rodokmen a co navrhuješ dál (1–3 možnosti).
- Ptej se jen na věci, které víš jen on (rodina, rozhodnutí, souhlas). Technické volby udělej sám.
- Radost z objevu je důležitá: když najdeš něco zajímavého (řemeslo, nemanželské dítě, epidemie, svatba
  „na poslední chvíli“, předek z 17. století), řekni to jako příběh, ne jako tabulku.
- Buď poctivý: „nenašel jsem“ a „nejsem si jistý“ jsou plnohodnotné výsledky.
- **Pozor na formulace u smrti a hrobů** – mluvíš s lidmi o jejich mrtvých. Ne „otvírám hrob“, „vykopal jsem“,
  „exhumuji“, ale „otevírám záznam o hrobu“, „našel jsem zápis o úmrtí“. Žádné vtipy na úmrtí a nemoci předků.
- Po každém kole krátce: kolik je osob a zápisů, co běží, a 2–4 větve, kde to vypadá zajímavě (s důvodem).
- Dnešní datum (do deníku, STAV.md) ber z metadat konverzace nebo příkazu `Get-Date -Format "yyyy-MM-dd"`, ne z hlavy.

## Na začátku každé konverzace
1. Jsi ve složce projektu? (`data/STAV.md` existuje.) → Přečti `data/STAV.md`, konec `data/research_log.md`
   a pokračuj podle sekce „Rozpracováno“. Krátce uživateli shrň, kde jste skončili.
   **Verze:** porovnej soubor `.skill_verze` v projektu se `SKILL_DIR/VERZE`. Chybí-li, nebo se liší, řekni jednou větou,
   že je nová verze skillu, a nabídni aktualizaci projektu: `python -I -X utf8 SKILL_DIR/tools/novy_projekt.py <složka projektu>`
   (data zůstanou, změněné soubory webu se zazálohují do `pracovni/`), pak ve `web/` `npm install`. Po souhlasu ji udělej
   a podle výpisu převezmi ze zálohy případné úpravy vzhledu (viz `reference/web.md`). Odmítne-li, připomeň to až příště.
2. Projekt ještě není → **Fáze 0**.

## Fáze 0 – Příprava (jednou)
1. Zkontroluj nástroje: `python --version` (≥ 3.9), `node --version` (≥ 20), `git --version` a přítomnost knihovny `Pillow` (`python -I -c "import PIL"`) nebo `ImageMagick` (`magick -version`).
   Co chybí, pomoz nainstalovat (Windows: `winget install --id <balík> --source winget --accept-source-agreements --accept-package-agreements` pro `Python.Python.3.12`, `OpenJS.NodeJS.LTS`, `ImageMagick.ImageMagick`, `Git.Git`, případně `pip install Pillow`). Instalace systémových věcí nech uživatele potvrdit.
   Skripty `.sh` spouštěj přes Git Bash (`bash tools/…`). Delší jednorázové skripty v Pythonu zapiš do souboru v `pracovni/` a spusť.
2. Zeptej se, kde má projekt být (navrhni `~/Rodokmen` nebo podsložku), a založ ho:
   `python -I -X utf8 SKILL_DIR/tools/novy_projekt.py <složka>`
   Chce-li uživatel nejdřív vidět, jak web vypadá, založ ukázku (`--ukazka`), pak ve složce `web` spusť `npm install` a `npm run nahled` (jako daemon úlohu na pozadí) a pošli mu odkaz http://localhost:4321.
   Pak se zeptej, jestli zapnout **hlídač sítě** (`python -I -X utf8 SKILL_DIR/tools/novy_projekt.py <složka> --hlidac`, vypnutí `--bez-hlidace`).
   Vysvětli jednou větou: archivy blokují IP adresu po sérii rychlých dotazů. Hlídač je malý skript v projektu
   (`tools/hlidac_site.py`, hook `PreToolUse` v `.agents/hooks.json`), který před každým příkazem zkontroluje, že stahování jde přes brzdu, a jinak ho zamítne.
   Sám nic nestahuje.
3. V projektu `git init` a první uložení (git = historie změn, kdyby se něco pokazilo). Soubor `AGENTS.md` v kořeni workspace zajistí, že příště plynule navážeš.
4. Vyplň v `data/STAV.md` sekci „Pro koho“ a v `data/web.json` název webu („Rodokmen Novákových“),
   jakmile znáš příjmení výchozí osoby (šablona je prázdná).

## Fáze 1 – Rozhovor s rodinou (nejcennější hodina celého projektu)
Cíl: znát co nejvíc o 3–4 generacích nazpět, než sáhneš do matrik.
- Ptej se postupně (ne dotazníkem naráz): výchozí osoba (pro koho rodokmen je – on sám, partner, dítě?), rodiče,
  prarodiče, pradědečci: **jména, rodná příjmení žen, roky a místa narození, sňatky, úmrtí (a kde jsou pohřbeni), řemesla, domy (čísla popisná!)**.
- Požádej o dokumenty: rodné a oddací listy, domovské listy, parte, fotky (i náhrobků), rodinné kroniky, paměti, staré dopisy,
  výpisy z MyHeritage/Geni od příbuzných. Ať je dá do `dokumenty/`. Přečti je celé (PDF/fotky) a vytěž.
- Doporuč zeptat se nejstarších žijících příbuzných – teď, dokud to jde. Nabídni seznam otázek.
- **Příbuzenství ber doslova, jak ho rodina řekla** („pradědeček babičky“ ≠ „otec babičky“) – nikdy ho neopravuj podle
  toho, co se ti hodí do dat. Při nejasnosti se zeptej. Ztotožnění jen podle křestního jména veď jako `prob` s poznámkou.
- Vše zapiš: `data/udaje_od_rodiny.md` (kdo co řekl), osoby do `data/osoby.py` se stavem `fam`
  (formát v hlavičce souboru a v `reference/data.md`). Žijící lidé jen jméno a rok narození.
- **Rodinný strom jako soubor GEDCOM** (`.ged`, export z MyHeritage/Geni/FamilySearch): `python -I -X utf8 tools/ged_import.py
  dokumenty/strom.ged "Jméno Příjmení"` vypíše předky s čísly, všechny události a poznámky a **frontu zápisů**
  (nejmladší známá událost u každého předka, a jestli už je v archivu). `--osoby` dá kostru pro `osoby.py`.
  Poznámky ve stromu bývají plné rodinných historek. Přečti je a vytěž do `udaje_od_rodiny.md`.
  Starší strom z **Brother's Keeper** (kódování ANSI a česká data „SRPEN 1945“ nástroj převede sám): místa tam bývají
  v 6. pádě („Táboře“) – do `osoby.py` je přepiš do 1. pádu. Kořenem takového stromu často nejsou uživatel, ale jeho děti
  (oba rody) – výchozí osobu proto vyber jménem.
- **Záloha stromu z MyHeritage** (ZIP se souborem `<strom>.ftb` a složkou `Photos/` – to není GEDCOM, ale databáze):
  rozbal do vlastní složky v `dokumenty/` (bývá velká – dej ji do `.gitignore`), pak
  `python -I -X utf8 tools/ftb_export.py <strom.ftb> dokumenty/strom.ged "Jméno Příjmení" <rok narození> pracovni/prima_linie.md <složka Photos>`.
  Vznikne GEDCOM pro `ged_import.py` (bez adres, e-mailů a telefonů) a přehled přímé linie s **původem údajů** – u každé
  osoby, ze kterých cizích stromů (Smart Match) či zdrojů její údaje přišly. Do `osoby.py`: osoba bez cizí citace = `fam`,
  doložená jen cizími stromy = `mh`. Údaje ze stromů (i Smart Match) jsou jen vodítko k zápisu – datum a číslo domu tě
  dovedou na stránku, ale **jména vždy ověř v zápisu** (skutečná chyba: „sňatek“ ze Smart Match byl jiný pár ze stejného domu). V přehledu jsou i připojené skeny (opisy matrik, parte, domovské listy) – přečti je,
  bývají to nejcennější rodinné doklady.
- Strom, který si rodina vede sama, má stav `fam`. Cizí stromy z internetu (stromy jiných lidí na MyHeritage, Geni,
  FamilySearch) jsou **jen vodítko**, stav `mh`, nikdy `doc`.

## Fáze 2 – Matriky, generace po generaci
Podrobný postup čtení: `reference/matriky.md`. Portály archivů: `reference/portaly.md`. Metodika: `reference/playbook.md` (EN).

Základní smyčka pro každou osobu:
1. **Vyber cíl a začni od nejmladšího zápisu.** Vezmi nejmladšího předka bez dokladu a hledej jeho **nejmladší
   známou událost**: úmrtí (online po 30 letech; ve 20. století uvádí datum a místo narození i rodiče), pak sňatek
   (uvádí rodiče a bydliště obou snoubenců, otevírá další generaci), a teprve z nich křest. **Nikdy nehledej křest
   naslepo** po stovkách snímků bez rejstříku, když je známé úmrtí nebo sňatek. (Skutečná chyba: křest ve velkoměstě
   hledaný naslepo, přitom datum a místo úmrtí byly známé.)
   Není-li nejmladší událost online (na venkově bývají svazky po ~1905 nenaskenované), začni nejmladším svazkem, který
   online je: křty sourozenců, sňatek rodičů, rejstříky – a chybějící zápis dej do `archivni_dotazy.md`.
2. **Ověř přístupnost**: matriky jsou v archivu až po uplynutí lhůty od *posledního* zápisu ve svazku
   (narození 100 let, sňatky 75, úmrtí 30). Mladší údaje jsou na matričním úřadě (žádost s doložením příbuzenství) –
   zapiš do `data/archivni_dotazy.md` a jdi dál.
3. **Najdi svazek**: podle obce → farnost → archiv. ARON: `python -I -X utf8 tools/aron_search.py "Obec"`, SOA Třeboň:
   `tools/trebon.py`, SOA Plzeň: `tools/portafontium.py`, SOA Praha (střední Čechy): `tools/ebadatelna.py`,
   Praha: `tools/ahmp_search.sh`; ostatní a Rakousko viz `reference/portaly.md`. Sňatek hledej nejdřív ve farnosti nevěsty.
   Je-li ke svazku index (rejstřík), začni jím – **hustý kurentový rejstřík vždy stáhni v plném rozlišení a rozřež na překrývající se pásy** (`python -I -X utf8 tools/overit.py pracovni/rejstrik.jpg rejstrik pracovni/rej`), nikdy neříkej „v rejstříku není“ jen z pohledu na celou stránku v prohlížeči! Starší matriky (před ~1784) bývají ve faře sousedního města.
4. **Stáhni snímek** do `pracovni/<svazek>/` a nech ho tam – před dalším stažením se podívej, jestli ho už nemáš
   (šetří čas, archiv i CAPTCHY). U chráněných archivů bez přímého stahování (MZA Brno – Acta Publica, ZA Opava při CAPTCHe) najdi snímek v prohlížeči a požádej uživatele o uložení snímku v plném rozlišení strukturovanou výzvou (viz `reference/portaly.md`). Najdi zápis, **přečti ho sám ze snímku v plném rozlišení**.
5. **Zapiš nález** (vždy všech 6 kroků, i když to zdržuje):
   1. svazek do `data/svazky.json` (ARON: `python -I -X utf8 tools/aron_img.py <apu> svazek`),
   2. zápis do `data/zaznamy.json` (klíč = popisný název, např. `holice_krest_jan_novak_1890`; odkaz na snímek) přes `tools/zapis.py`,
   3. výřez: `python -I -X utf8 tools/vyrez.py pracovni/<stránka>.jpg <klíč> x0,y0,x1,y1` (velkoryse – celý zápis s hlavičkou sloupců a okrajovými poznámkami),
   4. rámeček čteného místa: `python -I -X utf8 tools/ramecek.py <klíč> x0,y0,x1,y1` a **prohlédni si** `pracovni/ramecek_<klíč>.jpg`,
   5. přepis originálu a český překlad do `data/prepisy.json` (nejistá místa „(?)“, nečitelná „[…]“),
   6. osobu/osoby do `data/osoby.py` (`f` fakta, `r` klíč zápisu, `st="doc"`), sourozence a kmotry-příbuzné do `SIDE`.
6. **Zapiš hledání do deníku** `data/research_log.md` – i neúspěšné, s rozsahem (které roky / snímky jsi prošel).
   Narazíš-li po cestě na **zjevně související výskyt** (vzácné příjmení rodu, stejný dům, jméno z rodinného
   vyprávění), zapiš ho do výsledku v deníku se snímkem – je to jen stopa, ne doklad. Když se hledání zasekne,
   projdi deník právě kvůli takovým stopám.
7. Spusť `python -I -X utf8 tools/kontrola.py` a oprav chyby.

Pravidla, která chrání kvalitu (naučená na skutečném projektu):
- **Než něco ohlásíš jako nové, prohledej** `data/osoby.py`, `data/zaznamy.json` a `data/research_log.md`
  (jméno, místo, rok). Snadno „objevíš“ něco, co už v datech je.
- **Zápis do dat:** `zaznamy`, `svazky`, `prepisy`, `dokumenty` přes `python -I -X utf8 tools/zapis.py <soubor> <klíč> pracovni/x.json`
  (objekt napiš do `pracovni/x.json`, nástroj změní jen tu položku), `osoby.py` a markdown nástrojem pro úpravu souborů.
  Nikdy `sed -i` ani skript, který soubor přepíše celý – rozbije formát a v historii je pak změněný celý soubor.
- **`doc` jen to, co jsi četl přímo na snímku.** Shoda jména a doby bez přímého dokladu = `prob` + poznámka proč.
- **Pravidlo 4 kotev proti záměně jmenovců v obci (anti-homonymní protokol):** V jedné obci často žilo více rodin téhož příjmení i křestního jména (*Jan Novák + Anna*). Než spojíš dva zápisy k jedné osobě (`doc`), ověř: (1) **číslo popisné (čp.)**, (2) **rodné příjmení a rodiče matky/manželky**, (3) **povolání/stav a okruh kmotrů**, (4) **vyloučení dětského úmrtí (nekronyma)** – zkontroluj následujících 5–8 let, zda nalezené dítě nezemřelo a nenarodil se mladší sourozenec téhož jména! Žije-li v obci více rodin stejného příjmení, veď si přehled párů podle čp. v `pracovni/rodiny_<obec>_<prijmeni>.md` (viz `reference/matriky.md`).
- **Normalizace příjmení vs. dobový zápis:** V `prepisy.json` (`orig`) piš doslovný dobový pravopis (`Foytik`, `Tomschu`), ale v `osoby.py` (`n`) a `LINES` drž sjednocenou novodobou českou podobu (`Foytik` → `Fojtík`, ne `Foitík`; moravská rodová příjmení na `-ů` jako `Tomšů` u žen nepřechyluj na `Tomšíková` – viz `reference/matriky.md`).
- **Nic nedomýšlej.** Nejisté čtení „(?)“, rozpory zapiš do `ISSUES`. Písaři se pletli (jména sourozenců, věk, Anna/Františka, Marie/Terezie v úmrtním zápisu).
- **Čti celý zápis včetně okrajů** – pozdější poznámky o úmrtí, sňatku, legitimaci bývají nejcennější.
- **Rodina přes čísla domů**: stejné číslo popisné a řemeslo přes generace je silná stopa; v knize hledej celé domácnosti.
- **Ztotožnění míst ověř** podle panství/kraje v zápisu (německé „Langenau“ je v Čechách několikrát – rozhodne „bey Hohenelbe“ = u Vrchlabí).
- **U úředníků, vojáků, lékařů, učitelů, farářů** zkus noviny a ročenky (`reference/portaly.md` → Noviny): ukážou
  kariéru, tedy kde člověk kdy žil, a dají výstřižky na web. U sedláků a řemeslníků na vsi se nevyplatí.
- Matriky před ~1650 skoro nejsou. Pro 17. století: soupis poddaných 1651, berní rula 1654, gruntovní knihy (`reference/portaly.md`).
- Najdeš-li **spornou věc**, kterou nerozhodneš (dvě možná čtení, dva kandidáti), napiš to uživateli s výřezem
  a nech ho rozhodnout; do té doby `prob`.
- **Hodně sporných čtení najednou** (desítky po velkém kole) nedávej do chatu po jednom. Sesbírej je do
  `pracovni/sporna_cteni.json` (klíč zápisu, výřez, otázka, možnosti, tvůj návrh) a udělej z nich jednu stránku,
  kde uživatel u každého klikne na odpověď. Když to jde, použij artefakt s ukládáním odpovědí, jinak HTML soubor
  s tlačítkem „stáhnout odpovědi“. Odpovědi pak zapracuj a zapiš do deníku.
- **Správa kontextu a úspora tokenů (`/compact`):** Dlouhé konverzace s desítkami načtených snímků matrik spotřebují až 80 % tokenů na opakované čtení cache. Jakmile dokončíš ucelený krok (např. jednu generaci nebo větev) a vše zapíšeš do `data/osoby.py`, `data/STAV.md` a `data/research_log.md`, **doporuč uživateli příkaz `/compact`** (případně novou konverzaci), aby se z kontextu uvolnily staré snímky.

### Šetrně k archivům – brzda `tools/slusne.py`
Archivy blokují IP adresu po sérii rychlých dotazů (MZA i celou síť na hodiny, ZA Opava na 30 minut). Blokaci
nezpůsobují nástroje, ale rychlé dočasné skripty a smyčky `curl`. Nástroje v `tools/` mají brzdu samy: společný limit
pro každý web (dotaz 1 za 2 s, obrázky a dlaždice nejvýš 1 za 0,15 s) pro všechny procesy na počítači.
- **Síť jen přes brzdu, i u pomocníků:** vlastní skript `python -I -X utf8 tools/slusne.py pracovni/x.py …`, curl
  `python -I -X utf8 tools/slusne.py curl …`, shellový skript `python -I -X utf8 tools/slusne.py bash pracovni/x.sh`.
  I místní náhled webu zkoušej přes `slusne.py curl`.
- **Hláška „slusne: … je zastavený“ (kód 3)** = archiv dal najevo, že ho zatěžujeme (429/503/403, stránka
  „zablokováno“, spojení odmítnuto). Nezkoušej to znovu, neobcházej to (jiný nástroj, prohlížeč), řekni to uživateli
  a dělej jinou práci. Stav: `python -I -X utf8 tools/slusne.py stav`. `slusne.py odblokuj` jen když víš, že šlo o tvou chybu (špatná adresa).
- **V prohlížeči brzda neplatí:** nejvýš 1 dotaz za 2 s, žádné smyčky `fetch` ani `Promise.all`.
- **Na jeden archiv nejvýš jeden pomocník.** Víc projektů na jednom počítači má jednu IP adresu.

### Pomocníci (subagenti v Antigravity) – šetrně
Na velké kolo (např. „projdi 5 svazků a najdi všechny Nováky“) můžeš pustit 2–4 pomocníky paralelně pomocí nástroje `invoke_subagent` (`TypeName: "self"`, `Workspace: "inherit"`).
Každému dej přesné zadání (`Prompt`: svazek, snímky, koho hledat, formát výsledku: klíč, snímek, souřadnice zápisu, přepis)
a pravidla výše. Pomocník píše jen do `pracovni/pom_<větev>/`, **do `data/` nikdy**. Zapisuješ ty.
Po spuštění pomocníků přes `invoke_subagent` na ně **nečekej ve smyčce (nepolluj)** – systém tě sám probudí, až pošlou výsledek.
Ať zmíní i zjevně související výskyty (viz krok 6 výše). Výstupy pomocníků v `pracovni/` nemaž, dokud nejsou vytěžené.
**Jejich čtení vždy ověř sám na snímku** (`python -I -X utf8 tools/overit.py <snímek> x0,y0,x1,y1 pracovni/over`, souřadnice jako zlomky 0–1 šířky a výšky, ne pixely, rozdělí zápis
na dvě čitelné poloviny), než ho zapíšeš jako `doc`. Uživateli to vysvětli správně: jde o princip čtyř očí a pomocník nemá kontext (dvě rodiny stejného jména ve vsi, dva Janové na statku).
Prohlížeč (`chrome-devtools` / `/browser`) může mít najednou jen jeden pomocník, proto dávej přednost nástrojům bez prohlížeče.
**Pomocníky spouštěj na úspornějším modelu** (`Model: "flash"` v `invoke_subagent`, případně `"inherit"`): hledání a první čtení zvládnou rychleji a levněji. Ověření na snímku a zápis do dat dělá hlavní model (ty).
Osvědčilo se 3–4 pomocníci na různé větve a archivy současně, jedno kolo ≈ 15–25 nových předků.
Před velkým kolem řekni uživateli, co plánuješ a proč, a nech si to schválit.
Do zadání jim napiš technické pasti z `reference/matriky.md` (Windows PowerShell: `python -I -X utf8`, dopředná lomítka `/`, žádné roury a zpětná lomítka)
a pravidla brzdy výše (síť jen přes `tools/slusne.py`, při hlášce „zastavený“ skončit a ohlásit).
**V zadání chtěj u každého prošlého snímku, co na něm skutečně přečetl** (rok, první jméno), ne jen „prošel jsem
sn. 20–40“ – pomocník jinak přehlédne, že se mu část snímků nenačetla. Na špatně čitelné knihy (kurent 1. poloviny
19. století, vybledlé snímky) pomocníky nepouštěj, nebo jim dej přesný snímek; ARON a Porta fontium zvládají dobře.

### Kdy přestat
Linie končí, když matriky mlčí (nemanželské dítě bez otce, shořelé knihy, chybějící svazky) nebo když jsi
v 17. století. Zapiš to do `ISSUES`/`archivni_dotazy.md` a jdi na jinou větev. Průběžně aktualizuj `data/STAV.md`
(„Rozpracováno“), aby šlo kdykoli navázat.

## Fáze 3 – Zajímavosti a Příběh hlavního rodu
Podrobně `reference/pribehy.md`. Tohle je to, co rodina na webu čte nejradši, takže na to nezapomínej a nenechávej to na konec.
- **Zajímavosti** („fun facts“) sbírej **průběžně**: co najdeš při čtení, hned zapiš do `data/zajimavosti.md`
  a řekni uživateli. Po každém kole spusť `python -I -X utf8 tools/napady.py`. Najde v datech svatby krátce před porodem,
  rod v jednom domě, sňatky příbuzných, dlouhověkost, epidemie… Ověř a napiš jako krátké příběhy.
- **„Příběh <hlavního rodu>“** (Příběh Novákových): jakmile má hlavní rod ~5 doložených generací, nabídni ho.
  Koncept napiš **do chatu** ke schválení, pak `data/pribeh.md` a v `web.json` menu, tlačítko a úvod.
  Je hlavní věcí na úvodní stránce webu.

## Fáze 4 – Web
Podrobně `reference/web.md`. Ve zkratce:
1. `cd web && npm install` (jednou), pak `npm run nahled` → http://localhost:4321 – ukaž uživateli. V cloudovém prostředí
   (claude.ai) localhost neuvidí – pošli mu snímky stránek (headless prohlížeč) nebo nasaď náhled.
2. Nastav `data/web.json`: název, úvod, kontakt a **přihlašovací otázku a odpověď** (web je jen pro rodinu).
3. Po každé změně dat: `npm run data && npm run build` (nebo znovu `npm run nahled`). Hlášky `POZOR: nefunkční odkaz`
   oprav hned (adresa osoby se mění, když se jí doplní rok narození).
   Po každém větším kole hledání zkontroluj i texty úvodu ve `web.json` (`uvod`, `zajimavosti_na_uvodu`) –
   zastarávají („nejstarší předek je…“, počty generací).
4. Před zveřejněním si vezmi `reference/soukromi.md` a projdi s uživatelem, co na webu bude (žijící lidé!).
   Na web jde i „Co hledáme“ (`ISSUES`), poznámky osob a deník. Hlášky `CITLIVÉ` z `kontrola.py` vyřeš s uživatelem;
   co na webu nechat smí, zapiš úryvkem textu do `web.json` → `citlive_schvaleno` (pak se už nehlásí).

## Fáze 5 – Zveřejnění nebo Export do GEDCOMu (volitelné, jen se souhlasem)
- **Export do genealogických programů (GEDCOM 5.5.1):** Chce-li uživatel rodokmen otevřít v programu (MacFamilyTree, MyHeritage, Gramps, Ancestral Quest…) nebo ho porovnat se svým dosavadním výzkumem:
  - Export celého stromu (nebo podstromu od konkrétní osoby, např. dědy `--vychozi 4`):
    `python -I -X utf8 tools/ged_export.py vystupy/rodokmen.ged [--vychozi <kekule_cislo>]`
  - Porovnání nalezených předků s uživatelovým referenčním GEDCOMem po generacích:
    `python -I -X utf8 tools/ged_porovnej.py dokumenty/referencni.ged ["Jméno výchozí osoby"] [--vychozi <kekule_cislo>]`
- **Zveřejnění webu:** Výchozí cesta je **Netlify** (zdarma): `npm run nasadit`. Přihlášení k Netlify a první propojení webu jsou interaktivní –
  dej je uživateli jako `! npx netlify-cli login` atd. (postup v `reference/web.md`). Pokročilá varianta: vlastní server (Docker/CapRover).
  Nic nezveřejňuj bez výslovného souhlasu uživatele.

## Režim AI Genealog – řešení jednotlivých badatelských případů a záhad
Když uživatel nechce procházet celý průvodce stavbou rodinného webu, ale zadá **konkrétní badatelský úkol** (např. *„vysvětli rozpor mezi jmény Terezie a Marie v zápisech“*, *„ověř tuhle hypotézu“*, *„zjisti u sourozenců čitelnější rodné příjmení matky“*, *„dohledej jen předky této osoby ze snímku“*), postupuj takto:
1. **Nerozšiřuj zadání a nestav web:** soustřeď se čistě na zadanou otázku. „Nenašel jsem“ nebo „záznamy si odporují“ je plnohodnotný výsledek – nic nedomýšlej.
2. **Trvalý archiv snímků v `archivalie/`:**
   - Každý stažený celý snímek matriky ukládej trvale do `archivalie/<archiv>_<obec>_<kniha>/snimek_<N>.jpg` (jedna složka na svazek, např. `archivalie/mza_vizovice_4926/snimek_051.jpg`) a do `archivalie/<archiv>_<obec>_<kniha>/zdroj.json` ulož název svazku a trvalé odkazy na snímky.
   - **Před každým stažením se nejdřív podívej do `archivalie/` a `pracovni/`**, jestli už snímek nemáš na disku. Mezivýsledky a pokusy patří do `pracovni/`.
3. **Evidence nálezů v `data/`:** Doložené matriční zápisy (`zaznamy.json`), svazky (`svazky.json`), přepisy (`prepisy.json`) a výřezy (`vyrezy/`, `zdroje/`) ukládej standardně přes `tools/zapis.py`, `vyrez.py` a `ramecek.py`, aby se mezi případy nikdy nehledalo totéž dvakrát. Do samotného stromu předků (`data/osoby.py`) zapisuj jen tehdy, když si to uživatel přeje (jinak si nálezy přenáší do svého genealogického programu sám).
4. **Výstup = samostatná zpráva v `pripady/<klic_pripadu>.md` + řádek v `pripady/PREHLED.md`:**
   - Piš česky, **nejdřív jasný závěr s mírou jistoty** (`doloženo` / `pravděpodobné` / `vyvráceno` / `zatím nevyřešeno`), **pak důkazy** (vložené výřezy zápisů `![…](../vyrezy/<klic>.jpg)`, doslovný přepis, překlad, odkazy na snímky a vysvětlení souvislostí – např. jak chyba v úmrtním zápisu vznikla nebo proč dvě zdánlivé sestry narozené 8 měsíců po sobě jsou tatáž osoba) a na konec **další doporučené kroky**.
   - Zprávu v `pripady/<klic_pripadu>.md` si uživatel může přímo otevřít s vloženými obrázky matrik nebo vytisknout do PDF.

## Poznámky pro správce skillu
Skill se zlepšuje podle zkušeností lidí, kteří ho používají. Proto **průběžně zapisuj do `poznamky_pro_skill.md`**
(v kořeni projektu), co by se mělo ve skillu zlepšit:
- chyby nástrojů a webu (příkaz, co se stalo, co jsi čekal, jak jsi to obešel),
- nový archiv nebo portál a postup, který fungoval (adresy, pasti, omezení), nástroje, které sis musel napsat sám,
- místa, kde návod mlčel nebo radil špatně, a co uživatel chtěl, ale skill to neuměl (nápady na web apod.).

Piš obecně a stručně. Zapisuj technický postup, ne údaje o rodině (žádní žijící lidé, žádné citlivé věci).
**Ve vhodnou chvíli připomeň uživateli, že může poznámky poslat správci skillu**: po zveřejnění webu, na konci velkého
kola nebo sezení, když je v poznámkách něco podstatného (chyba, nový archiv), a pak zhruba jednou za pár sezení.
Nedělej to pořád. Postup:
1. Projdi poznámky a odstraň nebo zobecni osobní údaje.
2. Vypiš je do chatu celé, jako jeden blok k zkopírování.
3. Požádej uživatele, ať je zkopíruje a pošle e-mailem na **sarsonj@gmail.com** (předmět třeba „Rodokmen skill – poznámky“).
   Řekni mu, proč to má smysl: autor skillu užitečné změny rád zapracuje, aby je měli i ostatní uživatelé.
   A že může připsat i vlastní zkušenosti a postřehy, třeba co se mu líbilo nebo co mu na webu chybělo.
**Nic sám neposílej** (žádný e-mail, formulář ani issue). Rozhoduje uživatel. Až řekne, že poslal, zapiš do
`poznamky_pro_skill.md` „odesláno <datum>“ a další poznámky piš pod tuto čáru.

## Co nikdy
- Nestahuj hromadně z placených služeb (MyHeritage, Ancestry, Geni…) a neobcházej jejich ochranu –
  automatické procházení stovek záznamů vede k **zablokování účtu**. Čti jen to, co uživatel otevře, nebo co potřebuješ jednotlivě.
- Nezadávej za uživatele hesla, platební údaje, neřeš CAPTCHA, nekupuj předplatné.
- Neobcházej brzdu `tools/slusne.py` ani blokaci archivu.
- Nedávej na web podrobnosti o žijících lidech bez jejich souhlasu.
- Nepřepisuj data bez zálohy v gitu; po větším kroku navrhni uložení (`git add -A && git commit -m "…"`).

## Mapa souborů projektu
| Cesta | K čemu |
|---|---|
| `data/STAV.md` | vstupní bod: pro koho, pravidla, rozpracované věci |
| `data/osoby.py` | předci (Kekulého čísla), rody `LINES`, boční příbuzní `SIDE`, otázky `ISSUES`, `HYPOTEZY`, `SAME` |
| `data/zaznamy.json`, `data/svazky.json` | zápisy z matrik a svazky, ze kterých jsou |
| `data/prepisy.json`, `data/zvyrazneni.json` | přepisy s překlady, rámečky čteného místa |
| `data/research_log.md` | deník všech hledání |
| `data/udaje_od_rodiny.md`, `data/archivni_dotazy.md` | co víme od rodiny; co jen v archivu |
| `data/zajimavosti.md`, `data/pribeh.md`, `data/web.json`, `data/dokumenty.json`, `data/mista.json` | texty a nastavení webu, rodinné fotky, místa na mapě |
| `vyrezy/`, `zdroje/` | výřezy zápisů a dokumentů (web / plné rozlišení), název = klíč + `.jpg` |
| `archivalie/` | trvale uložené celé snímky matrik po svazcích (`<archiv>_<obec>_<kniha>/snimek_<N>.jpg` + `zdroj.json`) |
| `pripady/` | badatelské zprávy jednotlivých případů v režimu AI Genealog (`<klic>.md` + `PREHLED.md`) |
| `dokumenty/`, `pracovni/` | originály od rodiny; pracovní soubory a mezivýsledky (nejdou na web) |
| `poznamky_pro_skill.md` | poznámky pro správce skillu (chyby, nové archivy, nápady) – posílá je uživatel ručně |
| `tools/` | nástroje (kopie ze skillu; aktualizace celého projektu: znovu spustit `novy_projekt.py` na stejnou složku, viz `reference/web.md`) |
| `web/` | web (Astro); data do něj jdou jen přes `npm run data` |

## Nástroje (`tools/`, spouštět z kořene projektu `python -I -X utf8 tools/<nástroj>`)
| Nástroj | Co dělá |
|---|---|
| `aron_search.py "Obec"` | najde svazky matrik na ARON (SOA Zámrsk); `"Obec,Fara"` zúží stejnojmenné obce |
| `aron_img.py <apu> info / <snímek> 1 pracovni/x.jpg / link <n> / svazek` | stáhne snímek, dá odkaz, zapíše svazek |
| `trebon.py misto / svazky / rejstrik / snimek / svazek` | matriky SOA Třeboň (jižní Čechy) bez prohlížeče, i rejstříky |
| `portafontium.py fara / info / snimek / link / svazek` | matriky SOA Plzeň (západní Čechy, Porta fontium) bez prohlížeče (faru zjisti na portálu) |
| `ebadatelna.py hledat / matriky / info / snimek / link / svazek`, `a-…` | matriky a archiválie (urbáře, gruntovní knihy) SOA Praha (střední Čechy) |
| `ahmp_search.sh "dotaz"`, `ahmp_scan.py XID snímek out.jpg` | matriky Prahy (AHMP) |
| `policie_prihlasky.py Příjmení [Jméno] [od] [do]`, `karta <pořadí> out.jpg …` | pražské policejní přihlášky 1850–1914 (rodiny s dětmi a adresami), stažení karty |
| `soal_zoomify.py <cesta nebo adresa> 0 out.jpg` | snímek SOA Litoměřice nebo ZA Opava (knihu najdi v prohlížeči; pozor na blokování) |
| `matricula_dl.sh`, `matricula_batch.sh` | snímky z Matriculy (Rakousko…), URL se bere z prohlížeče |
| `anno.py`, `anno_snap.py`, `kramerius.py` | noviny: ANNO (rakouské), Kramerius (české) |
| `ged_import.py strom.ged "Jméno"` | předci z rodinného stromu (GEDCOM) + fronta zápisů |
| `ged_export.py [vystupy/rodokmen.ged] [--vychozi <k>]` | export rodokmenu z `data/osoby.py` do formátu GEDCOM 5.5.1 (`.ged`) |
| `ged_porovnej.py <ref.ged> ["Jméno"] [--vychozi <k>]` | porovná předky v `data/osoby.py` s referenčním GEDCOMem po generacích |
| `ftb_export.py strom.ftb out.ged ["Jméno" rok linie.md [Photos/]]` | záloha z MyHeritage (.ftb) → GEDCOM + přímá linie s původem údajů |
| `overit.py <snímek> x0,y0,x1,y1 / rejstrik <prefix>` | zápis na dvě poloviny (zlomky 0–1) nebo stránka rejstříku na 5 překrývajících se pásů |
| `napady.py` | náměty na zajímavosti z dat |
| `vyrez.py <stránka.jpg> <klíč> x0,y0,x1,y1` | výřez do `zdroje/` a `vyrezy/` |
| `ramecek.py <klíč> x0,y0,x1,y1` | rámeček čteného místa + kontrolní obrázek |
| `mista.py pridej "Obec"` / `mista.py` | místa pro mapu (souřadnice z OpenStreetMap) |
| `zapis.py <soubor> <klíč> <vstup.json> [--sloucit]` | přidá / změní položku v `zaznamy`, `svazky`, `prepisy`… beze změny formátu |
| `slusne.py <skript.py> / curl … / bash x.sh / stav` | brzda proti zablokování archivem – vlastní skripty a curl spouštěj přes ni |
| `kontrola.py` | kontrola dat; hlásí i citlivé údaje na webu a kdy psát příběh |
| `export_web.py` | data → web (volá ho `npm run data`) |
| `fan_chart.py vystupy/` | vějíř předků jako plakát k tisku |
