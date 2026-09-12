# Brand Kit

Turn a brand website into an organised client asset library and a brand-reference PDF.

```text
/brand-kit https://example.com
```

## Download and install

[Download the skill ZIP](brand-kit-skill.zip?raw=true), extract it, and keep the whole `brand-kit` folder together.

- **Claude Code:** copy the folder to `~/.claude/skills/brand-kit/`, then run `/brand-kit https://example.com`.
- **Codex:** copy the folder to `~/.agents/skills/brand-kit/`, then ask `Use $brand-kit for https://example.com`.

[Read the full setup guide](brand-kit/START-HERE.md).

## What it creates

A dated folder under `Clients/<brand-name>--<domain>/` containing:

- Brand-reference PDF and editable Markdown
- Original logos, downloadable fonts and licence references
- Colour palettes and sourced copy summaries
- Product images grouped by product and collection
- Campaigns, lifestyle images, icons and available videos
- Searchable asset directory, source records and coverage report
- A ZIP of the complete client run

Products can belong to several collections. Repeat runs preserve earlier folders. Missing files and conflicting claims are recorded rather than invented.

## Requirements

A skill-enabled AI assistant with web access, file creation and Python 3.10+. PDF generation uses ReportLab and Pillow. No particular paid scraping plugin or API key is required; AI-provider and optional-tool usage charges may apply.

This is an agent workflow, not a standalone application or unattended crawler. The assistant researches the website and prepares the inputs for the included organiser and PDF helpers. Access depends on the site and the tools available in your assistant.

## Scope

Public third-party copy is summarised rather than archived wholesale. Original assets are collected where permitted. Font licences and all third-party rights remain with their owners. This creates an independent reference, not an official brand manual. Blocked pages, private assets and unsupported downloads are reported as gaps.

## Package contents

- `brand-kit/SKILL.md` - agent workflow
- `brand-kit/scripts/brandkit.py` - folder organisation, indexing and ZIP packaging
- `brand-kit/scripts/render_guidelines.py` - PDF and Markdown rendering
- `brand-kit/references/` - research guidance and input schemas
- `brand-kit/START-HERE.md` - installation and usage

The helper workflow was checked with synthetic fixtures for deduplication, collection membership, filename collisions, repeat runs, invalid downloads and path handling. PDF output and archive integrity were also checked. These checks do not guarantee complete extraction from every website.

## Sharing

You may use, adapt and redistribute this skill and its original helper code. See [LICENSE.txt](LICENSE.txt). No client assets, account credentials or private research are included.
