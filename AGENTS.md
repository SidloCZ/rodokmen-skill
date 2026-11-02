# Správa a vývoj repozitáře rodokmen-skill (Antigravity)

Tento workspace je propojen s forkem `https://github.com/SidloCZ/rodokmen-skill` (upstream: `https://github.com/sarsonj/rodokmen-skill`).

- Samotný skill je ve složce `skills/rodokmen/` (`SKILL.md`, `tools/`, `reference/`, `template/`, `VERZE`) a je v Antigravity registrován přes `.agents/skills.json`.
- Při zakládání nového projektu rodokmenu spouštěj `python -I -X utf8 skills/rodokmen/tools/novy_projekt.py <cilova_slozka>`.
- **Pravidla pro Windows a Antigravity terminál (`run_command`):**
  - Python spouštěj vždy jako `python -I -X utf8` (ne `python3`).
  - V příkazech používej vždy dopředná lomítka (`/`) a relativní cesty z kořene workspace (žádná zpětná lomítka `\`, žádné zbytečné roury `|`, středníky `;` ani bloky `{ ... }`).
  - Zpracování obrázků (`vyrez.py`, `ramecek.py`, `overit.py`, `aron_img.py` aj.) funguje automaticky přes Python knihovnu `Pillow` (`PIL`) nebo `ImageMagick` (`magick`). Nikdy nepoužívej příkaz `convert`.
- **Vydání nové verze:** zvedni číslo ve třech místech najednou – `.claude-plugin/plugin.json` (`version`), `skills/rodokmen/VERZE` a `README.md`. Do `CHANGELOG.md` přidej nahoru sekci `## X.Y.Z – D. M. RRRR`.
