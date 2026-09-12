# Brand Kit - community edition

Give your AI assistant a brand website. Get an organised client folder, a brand-reference PDF and a downloadable asset library.

## Install once

Extract this ZIP. Keep the entire `brand-kit` folder together; it includes helper scripts.

**Claude Code:** place `brand-kit` inside `~/.claude/skills/`. Then use:

```text
/brand-kit https://example.com
```

**Codex:** place `brand-kit` inside `~/.agents/skills/`. Then use:

```text
Use $brand-kit for https://example.com
```

Start a fresh session if the skill does not appear. You can also ask your assistant: “Install the attached brand-kit skill for me,” and provide the extracted folder or ZIP if your app supports attachments.

For other skill-enabled assistants, use their custom-skill import flow if available, or ask the assistant to read `SKILL.md` from the extracted folder. A slash command works only after the host registers the skill; importing a ZIP is not supported by every app. Claude Code's local installation does not automatically install the skill into Cowork or cloud sessions.

## Use it

```text
/brand-kit https://example.com
```

Optional detail:

```text
/brand-kit https://example.com — save under my Clients folder; use the Australian storefront
```

You do not need to prepare a manifest or run scripts yourself. The assistant researches the site, creates those inputs and runs the helpers.

## What you get

```text
Clients/
  Brand Name--example.com/
    2026-09-12/
      01-Brand-Guidelines/
      02-Logos/
      03-Fonts/
      04-Colors/
      05-Copy/
      06-Products/
        Product A/
      07-Collections/
        Collection A/
          Products/
            Product A/
      08-Campaigns/
      09-Lifestyle/
      10-Icons/
      11-Video/
      12-Other/
      13-Sources/
      index.html
```

Names are cleaned for safe file storage. Each run is dated; earlier runs are preserved. Products can appear in more than one collection. Open `index.html` to search the downloaded image library.

## Requirements and limits

An AI assistant with web access, file creation and Python 3.10+ execution. PDF creation uses ReportLab and Pillow; the assistant can use an existing runtime or a project-local environment. No particular paid scraping service or API key is required. Your AI provider and optional tools may still have usage limits or charges.

This is an AI skill, not a standalone desktop app. It adapts to public brand websites but cannot guarantee complete access to blocked, private or very large sites. It records missing items. It retrieves original assets where permitted, sources downloadable fonts with licences, and summarises third-party copy rather than duplicating the entire site. Brand rights and third-party licences are unchanged.

## Share it

Share `brand-kit-skill.zip` with your community. It contains this skill and helpers, not your client files, account keys or any brand-specific assets. You may use, adapt and redistribute the skill package; see `LICENSE.txt`.

Installation references (checked 12 September 2026):
- Codex: https://learn.chatgpt.com/docs/build-skills
- Claude Code: https://code.claude.com/docs/en/skills
