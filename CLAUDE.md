# WoW Profession Materials Tracker

This project aggregates materials lists for World of Warcraft profession leveling guides for multiple professions across all expansions, formatted specifically for use with the Auctionator addon.

## Purpose

The main goal is to collect and format profession leveling materials from guides on wow-professions.com into a standardized Auctionator shopping list format for easy in-game reference and tracking.

## Current Status

- **alchemy.txt**: Contains materials lists for Alchemy leveling across expansions (Vanilla through Dragonflight) ✓
- **Python automation**: Complete scraping system with individual profession scripts ✓

### Python Scripts

- **base_scraper.py**: Core scraping functionality with rate limiting and Auctionator formatting
- **scrape_alchemy.py**: Alchemy-specific scraper with enhanced material extraction
- **scrape_blacksmithing.py**: Blacksmithing materials scraper  
- **scrape_engineering.py**: Engineering materials scraper
- **scrape_leatherworking.py**: Leatherworking materials scraper
- **scrape_all.py**: Master script to run all profession scrapers with delays
- **requirements.txt**: Python dependencies (requests, beautifulsoup4, lxml)
- **venv/**: Virtual environment for isolated dependencies

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
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running Individual Profession Scrapers
```bash
# Scrape all expansions for a profession
python scrape_alchemy.py

# Scrape specific expansion
python scrape_alchemy.py --expansion vanilla

# Custom output file and rate limiting
python scrape_alchemy.py --output my_alchemy.txt --rate-limit 3.0
```

### Running All Professions
```bash
# Scrape all professions, all expansions
python scrape_all.py

# Scrape all professions for specific expansion
python scrape_all.py --expansion vanilla

# Scrape single profession via master script
python scrape_all.py --profession alchemy
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