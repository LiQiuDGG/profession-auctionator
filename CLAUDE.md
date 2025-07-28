# WoW Profession Materials Tracker

This project aggregates materials lists for World of Warcraft profession leveling guides for multiple professions across all expansions, formatted specifically for use with the Auctionator addon.

## Purpose

The main goal is to collect and format profession leveling materials from guides on wow-professions.com into a standardized Auctionator shopping list format for easy in-game reference and tracking.

## Current Status

- **alchemy.txt**: Contains materials lists for Alchemy leveling across expansions (Vanilla through Dragonflight) ✓
- **Python automation**: Complete scraping system with individual profession scripts ✓
- **Enhanced scrapers**: Updated with TradeSkillMaster integration and choice logic ✓
- **Project structure**: Organized with separate folders for scripts and shopping lists ✓

## Recent Updates (Latest Session)

### Enhanced Scraping Features
- **TradeSkillMaster Integration**: Scrapers now detect and parse TSM shopping strings
- **Choice Logic**: Handles alternative materials (like Draenor choices) by selecting historically lowest-cost options
- **Material Priority System**: Ranks materials by availability and cost (common=1, moderate=2, rare=3)
- **Improved Material Detection**: Enhanced parsing to find materials sections by ID and heading text
- **Proper Project Structure**: Updated all scripts to use `../auctionator-shopping-lists/` output path

### Current Scraping Results (Updated)
- **Vanilla**: 15 materials ✅ (Perfect format with ^ separators and quoted items)
- **Outland**: 6 materials ✅ (Choice logic working, selecting Dreamfoil from alternatives)
- **Northrend**: 7 materials ✅ (Has choice items that need cleanup)
- **Cataclysm**: 8 materials ✅ (Choice logic handled)
- **Dragonflight**: 11 materials ✅ (Some duplicate detection issues to resolve)
- **Pandaria, Draenor, Legion**: 0 materials (Different guide structures, no consolidated shopping lists)
- **BFA, Shadowlands, War Within**: 404 errors (guides may not exist or different URLs)

### Format Improvements Made
- ✅ **Correct Auctionator Format**: Shopping list name on same line with ^ separators
- ✅ **Quoted Items**: All items wrapped in quotes for exact search functionality  
- ✅ **Choice Logic**: Handles alternative materials by selecting best priority option
- ✅ **Bold Text Detection**: Finds materials lists under bold headings (like Outland)
- ✅ **Deduplication**: Aggregates quantities for duplicate items

### Outstanding Issues
- Some choice text cleanup needed (Northrend has "Dark Jade, 5xHuge Citrine, 5xEternal Fire)OR")
- Dragonflight has incomplete item name "Awakened" vs "Awakened Order"
- Priority system for choice selection could be refined

### Git Configuration
- **Fixed .gitignore**: Shopping lists are now properly tracked as main deliverables
- **Complete alchemy.txt**: All available expansions included in tracked file
- **Repository Structure**: Both code and output files are version controlled

### Project Structure

```
profession-auctionator/
├── README.md                           # Project documentation
├── CLAUDE.md                          # Development instructions and history
├── auctionator-shopping-lists/        # Ready-to-use shopping lists
│   └── alchemy.txt                    # Alchemy materials (all expansions)
└── python-scripts/                    # Automation tools
    ├── base_scraper.py                # Core scraping functionality
    ├── scrape_alchemy.py              # Alchemy-specific scraper
    ├── scrape_blacksmithing.py        # Blacksmithing scraper
    ├── scrape_engineering.py          # Engineering scraper
    ├── scrape_leatherworking.py       # Leatherworking scraper
    ├── scrape_all.py                  # Master script for all professions
    ├── requirements.txt               # Python dependencies
    └── venv/                          # Virtual environment
```

### Repository Information

- **GitHub**: https://github.com/LiQiuDGG/profession-auctionator
- **SSH Key**: Uses ~/.ssh/liqiud for authentication
- **Git Config**: LiQiuDGG <liqiud@gmail.com>

## Auctionator Format Requirements

Items must be formatted with ^ separators between each item for proper Auctionator import. Item names should be wrapped in quotes for exact search functionality:
```
"Item Name";Category;...;Quantity^"Next Item";Category;...;Quantity^...
```

Key format requirements:
- Use ^ to separate individual items
- Wrap item names in double quotes for exact search
- Semicolon-separated fields within each item entry

## Target Professions

Current focus on these primary crafting professions:
- Alchemy ✓
- Blacksmithing (planned)
- Engineering (planned) 
- Leatherworking (planned)

## Data Sources

Materials are sourced from wow-professions.com:
- **Vanilla**: https://www.wow-professions.com/guides/vanilla-alchemy-leveling
- **Outland**: https://www.wow-professions.com/guides/outland-alchemy-leveling  
- **Northrend**: https://www.wow-professions.com/guides/northrend-alchemy-leveling
- **Cataclysm**: https://www.wow-professions.com/guides/cataclysm-alchemy-leveling
- **Pandaria**: https://www.wow-professions.com/guides/pandaria-alchemy-leveling
- **Legion**: https://www.wow-professions.com/guides/legion-alchemy-leveling
- **BfA**: https://www.wow-professions.com/guides/battle-for-azeroth-alchemy-leveling
- **Shadowlands**: https://www.wow-professions.com/guides/shadowlands-alchemy-leveling
- **Dragonflight**: https://www.wow-professions.com/guides/dragon-isles-alchemy-leveling-guide-dragonflight
- **War Within**: https://www.wow-professions.com/guides/the-war-within-alchemy-leveling

## Usage Instructions

### Virtual Environment Setup
```bash
cd python-scripts
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running Individual Profession Scrapers
```bash
cd python-scripts

# Scrape all expansions for a profession
python scrape_alchemy.py

# Scrape specific expansion
python scrape_alchemy.py --expansion vanilla

# Custom output file and rate limiting
python scrape_alchemy.py --output ../auctionator-shopping-lists/my_alchemy.txt --rate-limit 3.0
```

### Running All Professions
```bash
cd python-scripts

# Scrape all professions, all expansions
python scrape_all.py

# Scrape all professions for specific expansion
python scrape_all.py --expansion vanilla

# Scrape single profession via master script
python scrape_all.py --profession alchemy
```

### Git Operations
```bash
# Git is configured to always use the liqiud SSH key
git add .
git commit -m "Update message"
git push

# Manual SSH key usage (if needed):
GIT_SSH_COMMAND="ssh -i ~/.ssh/liqiud" git push
```

### Development Workflow
```bash
# Always update CLAUDE.md before committing!
# 1. Make changes to code/files
# 2. Update CLAUDE.md with session notes
# 3. Add, commit, and push changes

git add .
git commit -m "Descriptive commit message

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
git push
```

### Available Options
- `--expansion`: Target specific expansion (vanilla, outland, northrend, cataclysm, pandaria, draenor, legion, bfa, shadowlands, dragonflight, war_within)
- `--rate-limit`: Seconds between requests (default: 2.0)
- `--delay`: Seconds between profession scrapers (default: 5.0)
- `--output`: Custom output filename

## Technical Notes

- Format uses semicolon-separated values with ^ separators between items for Auctionator compatibility
- All item names wrapped in quotes for exact search functionality
- Materials categorized by type (Herb, Gem, Elemental, Metal, Leather, etc.)
- Rate limiting (2s default) to respect wow-professions.com servers
- Individual scripts per profession for flexible execution
- Automatic deduplication and quantity aggregation
- Enhanced material extraction with profession-specific patterns