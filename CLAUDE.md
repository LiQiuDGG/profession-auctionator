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
- **Pandaria**: 5 materials ✅ (Special inline parsing implemented for discovery-based guides)
- **Draenor**: 2 materials ✅ (Frostweed, Fireweed - basic parsing working)
- **Dragonflight**: 11 materials ✅ (Some duplicate detection issues to resolve)
- **Legion**: 0 materials (Different guide structure, no consolidated shopping lists)
- **BFA, Shadowlands, TWW**: 404 errors (guides may not exist or have different URLs)

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

### Recent Session Progress (Latest)

#### Completed Fixes:
- ✅ **Fixed Dreamfoil and Ragveil categorization**: Now properly categorized as Reagents/Herb
- ✅ **Fixed Cataclysm herbs**: Azshara's Veil, Twilight Jasmine, Whiptail now correctly categorized
- ✅ **Removed expansion field**: Auctionator format now uses `;;#;;` instead of expansion numbers
- ✅ **Enhanced choice logic**: Improved consistent material selection across expansions
- ✅ **Fixed Outland materials**: Added missing Golden Sansam (10) and corrected quantities
- ✅ **Fixed Pandaria parsing**: Updated logic to correctly parse inline herb mentions and prioritize order
- ✅ **Corrected Rain Poppy**: Correctly categorized as Reagents/Herb

#### Still Outstanding:
- 🔧 **Fix Northrend malformed text**: "Dark Jade, 5xHuge Citrine, 5xEternal Fire)OR" needs cleanup
- 🔧 **Fix Dragonflight incomplete item**: "Awakened" should be "Awakened Order" or similar
- 📝 **Review remaining categorizations**: Ensure all herbs are properly categorized
- 🔄 **Legion expansion**: Still shows 0 materials (different guide structure)
- ❌ **BfA, Shadowlands, TWW**: 404 errors (guides may not exist or have different URLs)

#### Investigation Results:
- ✅ **Dreaming Glory duplication**: No actual duplication found - only 1 entry with quantity 80 in Outland
- ✅ **Pandaria structure**: Successfully implemented special parsing for discovery-based guides with inline herb mentions
- ✅ **Draenor materials**: Found 2 materials (Frostweed, Fireweed) using existing parsing logic

### Current Work: Blacksmithing Implementation

#### Reference Guide:
- **Overall Guide Index**: https://www.wow-professions.com/profession-leveling-guides#the-war-within
- **Vanilla Blacksmithing**: https://www.wow-professions.com/guides/vanilla-blacksmithing-leveling

#### Blacksmithing Guide Structure Analysis:
The vanilla blacksmithing guide has a clear "Approximate Materials Required for 1-300" section with quantities:
```
133x Rough Stone
210x Copper Bar  
80x Coarse Stone
7x Silver Bar
180x Bronze Bar
105x Heavy Stone
35x Green Dye
230x Iron Bar
50x Steel Bar
20x Solid Stone
150x Mageweave Cloth
320x Mithril Bar
20x Dense Stone
420x Thorium Bar
72x Rugged Leather or 9x Star Ruby
```

#### Current Status:
- ✅ **Vanilla Blacksmithing**: Successfully implemented - found 12 materials with proper categorization
- ✅ **Enhanced Parser**: Added `_parse_materials_required_section()` to target blacksmithing-specific format
- ✅ **Material Results**: Successfully extracted all key materials (stones, bars, cloth, leather)
- 📝 **Next Steps**: Test Outland blacksmithing and verify accuracy

#### Vanilla Blacksmithing Results (12 materials):
```
Rough Stone (133), Coarse Stone (80), Bronze Bar (180), Heavy Stone (105),
Iron Bar (230), Steel Bar (50), Solid Stone (20), Mageweave Cloth (150),
Mithril Bar (320), Dense Stone (20), Thorium Bar (420), Rugged Leather (72)
```

#### Recent Fix:
- ✅ **Fixed Duplicate Rugged Leather**: Was showing 144 (72x2) due to both regex patterns matching the same line
- ✅ **Pattern Priority**: Rearranged choice pattern to be checked first, then skip basic pattern for that line
- ✅ **Correct Quantities**: Now shows accurate 72 for Rugged Leather as per guide specification

#### Final Fix - Complete Material Extraction:
- ✅ **Debug Logging Added**: Added detailed logging to identify parsing issues
- ✅ **Fixed Material Validation**: Removed "copper" and "silver" from skip_words since they appear in valid material names (Copper Bar, Silver Bar)
- ✅ **Enhanced Regex Pattern**: Updated from `(\d+)x\s*` to `(\d+)\s*x\s*` to handle both "35x" and "35 x" formats (for Green Dye)
- ✅ **Complete Material Set**: Now finds all 15 expected materials from "Approximate Materials Required" section:
  - Rough Stone (133), Copper Bar (210), Coarse Stone (80), Silver Bar (7), Bronze Bar (180)
  - Heavy Stone (105), Green Dye (35), Iron Bar (230), Steel Bar (50), Solid Stone (20) 
  - Mageweave Cloth (150), Mithril Bar (320), Dense Stone (20), Thorium Bar (420), Rugged Leather (72)
- ✅ **Additional Materials**: Also captures materials from recipe sections (19 total)
- ✅ **Proper Categorization**: All materials correctly categorized (Metal, Gem, Cloth, Leather, Other)
- ✅ **Clean Output**: Removed debug logging for production use

#### Summary Section Only Validation:
- ✅ **Confirmed Issue**: User correctly identified that the scraper was parsing detailed recipe sections in addition to summary
- ✅ **Enhanced Stop Indicators**: Added comprehensive section detection to limit parsing to "Approximate Materials Required" section only
- ✅ **Malformed Entry Filtering**: Added regex patterns to filter out malformed text like "-300", "OR" endings, and bracket entries
- ✅ **Final Results Validated**:
  - **Vanilla**: Exactly 15 materials (perfect match to expected list)
  - **Outland**: Clean 3 materials (Fel Iron Bar 102, Netherweave Cloth 100, Adamantite Bar 180)
  - **No recipe inflation**: Materials only from summary sections, not detailed step-by-step recipes
- ✅ **Production File**: Created clean blacksmithing.txt with only vanilla and outland expansions
- ✅ **Blacksmithing Complete**: First profession successfully parsing summary-only materials ✅

### URL Configuration System Implementation

#### Problem Identified:
- **Dynamic URL Construction Issues**: The scrapers were using dynamic URL construction which led to 404 errors for expansions like BfA, Shadowlands, and TWW
- **Inconsistent URL Patterns**: Different expansions use different URL patterns (e.g., BfA uses "zandalari-kul-tiran-bfa-{profession}-leveling-guide")
- **Site Structure Changes**: URL patterns changed over time and the dynamic construction couldn't keep up

#### Solution Implemented:
- ✅ **Created Config File**: `profession_guides_config.json` with all actual profession guide URLs scraped from the main index page
- ✅ **Updated Base Scraper**: Modified `base_scraper.py` to use config file URLs instead of dynamic construction
- ✅ **Fallback System**: Maintains fallback URL construction for missing config entries
- ✅ **Verified All URLs**: Scraped the main profession guides index to get exact URLs for all professions/expansions

#### Config File Structure:
```json
{
  "base_url": "https://www.wow-professions.com",
  "professions": {
    "alchemy": {
      "vanilla": "/guides/vanilla-alchemy-leveling",
      "bfa": "/guides/zandalari-kul-tiran-bfa-alchemy-leveling-guide",
      ...
    }
  },
  "expansion_info": {...}
}
```

#### Results:
- ✅ **Fixed BfA**: Now correctly uses `/guides/zandalari-kul-tiran-bfa-{profession}-leveling-guide`
- ✅ **Fixed Shadowlands**: Now correctly uses `/guides/shadowlands-{profession}-leveling-guide`  
- ✅ **Maintained Compatibility**: All existing functionality preserved with fallback system
- ✅ **Future-Proof**: Easy to add new profession guides by updating config file instead of code
- ✅ **Reliable URLs**: No more guessing URL patterns, uses exact URLs from the site

### Git Configuration
- **Fixed .gitignore**: Shopping lists are now properly tracked as main deliverables
- **Complete alchemy.txt**: All available expansions included in tracked file
- **Repository Structure**: Both code and output files are version controlled

### Recent Fixes (Current Session)
- **Corrected Expansion Numbers**: Fixed Auctionator format to use proper WoW expansion numbering
  - Vanilla (Classic) = 0
  - Burning Crusade (Outland) = 1
  - Wrath of the Lich King (Northrend) = 2
  - Cataclysm = 3
  - Mists of Pandaria = 4
  - Warlords of Draenor = 5
  - Legion = 6
  - Battle for Azeroth = 7
  - Shadowlands = 8
  - Dragonflight = 9
  - The War Within (TWW) = 10
- **Updated Naming**: Changed "war_within" to "tww" for consistency
- **Enhanced Base Scraper**: Updated expansion mapping with both URL patterns and correct numbers

### Project Structure

```
profession-auctionator/
├── README.md                           # Project documentation
├── CLAUDE.md                          # Development instructions and history
├── auctionator-shopping-lists/        # Ready-to-use shopping lists
│   ├── alchemy.txt                    # Alchemy materials (all expansions)
│   └── blacksmithing.txt              # Blacksmithing materials
└── python-scripts/                    # Automation tools
    ├── base_scraper.py                # Core scraping functionality
    ├── profession_guides_config.json  # Profession guide URLs configuration
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
- Alchemy ✅ (Complete - all expansions)
- Blacksmithing 🔄 (In Progress - working on Vanilla)
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