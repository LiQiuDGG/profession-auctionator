# WoW Profession Materials Tracker for Auctionator

A complete automation system to scrape World of Warcraft profession leveling materials from [wow-professions.com](https://www.wow-professions.com) and format them as Auctionator shopping lists for easy in-game purchasing.

## 🎯 Purpose

This project transforms profession leveling guides into ready-to-use Auctionator shopping lists, allowing WoW players to:
- Quickly buy all materials needed for profession leveling
- Use exact search functionality to avoid buying wrong items
- Level professions across all expansions efficiently
- Save time on manual material list creation

## 📁 Project Structure

```
profession-auctionator/
├── README.md                           # This file
├── CLAUDE.md                          # Project documentation and instructions
├── auctionator-shopping-lists/        # Ready-to-use shopping lists
│   └── alchemy.txt                    # Alchemy materials (Vanilla-Dragonflight)
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

## 🚀 Quick Start

### Using Pre-Generated Shopping Lists

1. Download the shopping list file for your profession from `auctionator-shopping-lists/`
2. In WoW, open Auctionator
3. Go to the Shopping Lists tab
4. Import the contents of the `.txt` file
5. Start shopping!

### Generating New Shopping Lists

#### Setup
```bash
cd python-scripts
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Scrape Individual Profession
```bash
# All expansions
python scrape_alchemy.py

# Specific expansion
python scrape_alchemy.py --expansion vanilla

# Custom settings
python scrape_alchemy.py --output my_list.txt --rate-limit 3.0
```

#### Scrape All Professions
```bash
# All professions, all expansions
python scrape_all.py

# All professions, specific expansion  
python scrape_all.py --expansion dragonflight

# Single profession via master script
python scrape_all.py --profession blacksmithing
```

## 🛠️ Available Professions

- ✅ **Alchemy** - Complete (Vanilla through Dragonflight)
- 🔄 **Blacksmithing** - Automation ready
- 🔄 **Engineering** - Automation ready  
- 🔄 **Leatherworking** - Automation ready

## 📋 Supported Expansions

| Expansion | Status | Guide URL Pattern |
|-----------|--------|-------------------|
| Vanilla | ✅ | `/guides/vanilla-{profession}-leveling` |
| Outland | ✅ | `/guides/outland-{profession}-leveling` |
| Northrend | ✅ | `/guides/northrend-{profession}-leveling` |
| Cataclysm | ✅ | `/guides/cataclysm-{profession}-leveling` |
| Pandaria | ✅ | `/guides/pandaria-{profession}-leveling` |
| Draenor | ✅ | `/guides/draenor-{profession}-leveling` |
| Legion | ✅ | `/guides/legion-{profession}-leveling` |
| BfA | ✅ | `/guides/battle-for-azeroth-{profession}-leveling` |
| Shadowlands | ✅ | `/guides/shadowlands-{profession}-leveling` |
| Dragonflight | ✅ | `/guides/dragon-isles-{profession}-leveling-guide-dragonflight` |
| War Within | ✅ | `/guides/the-war-within-{profession}-leveling` |

## 🎮 Auctionator Format

Shopping lists use the Auctionator format with these key features:

- **Exact Search**: Item names wrapped in quotes (`"Peacebloom"`) for precise matching
- **Item Separation**: Items separated by `^` character
- **Structured Data**: Semicolon-separated fields for each item
- **Categories**: Materials categorized (Herb, Gem, Elemental, Metal, etc.)

Example format:
```
Vanilla Alchemy
"Peacebloom";Reagents/Herb;0;0;0;0;0;0;0;0;;#;0;60^"Silverleaf";Reagents/Herb;0;0;0;0;0;0;0;0;;#;0;60
```

## ⚙️ Script Options

| Option | Description | Default |
|--------|-------------|---------|
| `--expansion` | Target specific expansion | All expansions |
| `--profession` | Target specific profession (scrape_all.py only) | All professions |
| `--output` | Custom output filename | `{profession}.txt` |
| `--rate-limit` | Seconds between requests | 2.0 |
| `--delay` | Seconds between professions (scrape_all.py) | 5.0 |

## 🔧 Technical Features

- **Rate Limiting**: Respectful 2-second delays between requests
- **Error Handling**: Robust error handling and retry logic
- **Deduplication**: Automatic quantity aggregation for duplicate items
- **Categorization**: Smart material categorization by profession
- **Extensible**: Easy to add new professions and expansions

## 📊 Data Sources

All materials sourced from [wow-professions.com](https://www.wow-professions.com) leveling guides:
- High-quality, maintained profession guides
- Accurate material quantities and recommendations
- Covers all expansions and professions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add new profession scrapers or improve existing ones
4. Test with rate limiting to respect wow-professions.com
5. Submit a pull request

## 📄 License

This project is for educational and personal use. Please respect wow-professions.com's terms of service and use appropriate rate limiting when scraping.

## 🙏 Acknowledgments

- [wow-professions.com](https://www.wow-professions.com) for comprehensive leveling guides
- [Auctionator](https://www.curseforge.com/wow/addons/auctionator) addon for shopping list functionality
- World of Warcraft community for profession knowledge

---

**Happy leveling!** 🎉