#!/usr/bin/env python3

import sys
sys.path.append('.')
from base_scraper import WowProfessionScraper

# Create scraper instance
scraper = WowProfessionScraper('alchemy')

# Debug the exact scrape_expansion method 
print("=== DEBUG: scrape_expansion method for shadowlands ===")

expansion = 'shadowlands'

# Check if expansion is being skipped
if expansion in ['draenor', 'legion']:
    print(f"❌ {expansion} would be skipped")
else:
    print(f"✅ {expansion} is not in skip list")

url = scraper._build_guide_url(expansion)
print(f"Built URL: {url}")

soup = scraper._get_page(url)
if not soup:
    print("❌ Failed to get page")
else:
    print("✅ Got page")
    
    materials = scraper._extract_materials(soup)
    print(f"Extracted materials count: {len(materials)}")
    
    expansion_info = scraper.EXPANSIONS.get(expansion, {'name': expansion.title(), 'number': 0})
    expansion_name = scraper._get_expansion_display_name(expansion)
    expansion_number = expansion_info['number']
    
    print(f"Found {len(materials)} materials for {expansion} {scraper.profession}")
    result = scraper._format_for_auctionator(materials, expansion_name, expansion_number)
    print(f"Final result length: {len(result)}")
    print(f"Result starts with: {result[:100]}...")
