#!/usr/bin/env python3

import sys
sys.path.append('.')
from base_scraper import WowProfessionScraper

# Create scraper instance
scraper = WowProfessionScraper('alchemy')

# Debug the full scraping process
print("=== DEBUG: Full Shadowlands Alchemy Scraping Process ===")

expansion = 'shadowlands'
url = scraper._build_guide_url(expansion)
print(f"URL: {url}")

soup = scraper._get_page(url)
if not soup:
    print("❌ Failed to get page")
    exit(1)

print("✅ Got page successfully")

# Extract materials
materials = scraper._extract_materials(soup)
print(f"✅ Extracted {len(materials)} materials:")
for material in materials:
    print(f"  - {material['name']} ({material['quantity']}) - {material['category']}")

# Get expansion info
expansion_info = scraper.EXPANSIONS.get(expansion, {'name': expansion.title(), 'number': 0})
expansion_name = scraper._get_expansion_display_name(expansion)
expansion_number = expansion_info['number']

print(f"Expansion name: {expansion_name}")
print(f"Expansion number: {expansion_number}")

# Format for auctionator
formatted = scraper._format_for_auctionator(materials, expansion_name, expansion_number)
print(f"Formatted result length: {len(formatted)}")
print(f"Formatted result: {formatted[:200]}..." if len(formatted) > 200 else f"Formatted result: {formatted}")
