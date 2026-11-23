# Bundled System Design Starter skill

This folder is the copy of [Surya760/system-design-starter](https://github.com/Surya760/system-design-starter) used by the design agent. The agent loads `SKILL.md` for every model stage and loads the relevant reference guides by stage.

The bundled copy lets the application work without fetching prompts at runtime. When the upstream skill changes, sync `SKILL.md` and `references/` from the upstream repository and review the prompts and artifact exporter for compatibility.
