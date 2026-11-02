# Přehled badatelských případů (Režim AI Genealog)

Tento přehled slouží pro **Režim AI Genealog** – řešení konkrétních genealogických záhad, ověřování hypotéz, vysvětlování rozporů mezi zdroji a cílené dohledávání jednotlivých větví bez nutnosti stavět celý web.

| # | Datum | Případ (soubor) | Otázka / Zadání | Závěr | Jistota |
|---|---|---|---|---|---|

---

## Šablona pro jednotlivý případ (`pripady/<klic_pripadu>.md`)

Každý případ má vlastní soubor v `pripady/<klic_pripadu>.md` s touto strukturou (nejdřív jasný závěr, pak důkazy):

```markdown
# <Název případu>

**Datum řešení:** RRRR-MM-DD
**Zadání:** <Co přesně bylo úkolem vyřešit nebo ověřit>
**Závěr:** <Stručná a jednoznačná odpověď na 1–3 věty>
**Míra jistoty:** doloženo / pravděpodobné / vyvráceno / zatím nevyřešeno

## Rozbor a důkazy
1. **<Název zápisu 1> (<datum>, <místo čp.>)**
   - **Zdroj:** <archiv, svazek, snímek, trvalý odkaz>
   - **Snímek v archivu projektu:** `archivalie/<archiv>_<obec>_<kniha>/snimek_<N>.jpg`
   - **Výřez:** `![<popis>](../vyrezy/<klic>.jpg)`
   - **Přepis originálu:** …
   - **Překlad a význam pro případ:** …

## Další kroky / Otevřené otázky
- …
```

