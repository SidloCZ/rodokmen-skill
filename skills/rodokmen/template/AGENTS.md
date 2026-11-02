# Projekt rodokmenu (Antigravity)

Tohle je projekt rodokmenu vedený skillem **rodokmen** (`.agents/skills/rodokmen/SKILL.md`). Na začátku každé konverzace:
1. Načti skill `rodokmen` (`.agents/skills/rodokmen/SKILL.md`), pokud ještě není načtený.
2. Přečti `data/STAV.md` – stav, pravidla a co je rozpracované – a konec `data/research_log.md`.
3. Pokračuj tam, kde se skončilo. Komunikuj česky, stručně a srozumitelně pro člověka bez zkušeností s genealogií a programováním.
4. **Pravidla pro Windows a Antigravity terminál (`run_command`):**
   - Python spouštěj vždy jako `python -I -X utf8 tools/<nastroj>.py` (ne `python3`).
   - V příkazech používej vždy dopředná lomítka (`/`) a relativní cesty z kořene projektu (žádná zpětná lomítka `\`, žádné zbytečné roury `|`, středníky `;` ani bloky `{ ... }`).
   - Zpracování obrázků (`vyrez.py`, `ramecek.py`, `overit.py`, `aron_img.py` aj.) funguje automaticky přes Python knihovnu `Pillow` (`PIL`) nebo `ImageMagick` (`magick`). Nikdy nepoužívej příkaz `convert`.
5. Síť na weby archivů jen přes brzdu `tools/slusne.py` (vlastní skripty, curl), i v zadání pomocníků (`invoke_subagent`) – viz skill, „Šetrně k archivům“.
6. Co by šlo ve skillu zlepšit (chyby nástrojů, nové archivy, nápady), zapisuj do `poznamky_pro_skill.md` – viz skill, sekce „Poznámky pro správce skillu“.

