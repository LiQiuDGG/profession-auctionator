#!/usr/bin/env python3

import sys
sys.path.append('.')
from base_scraper import WowProfessionScraper

# Create scraper instance
scraper = WowProfessionScraper('alchemy')

# Get the page
url = "https://www.wow-professions.com/guides/shadowlands-alchemy-leveling-guide"
soup = scraper._get_page(url)

if soup:
    print("=== DEBUG: Shadowlands Alchemy Materials Detection ===")
    
    # Check if we can find the materials section
    materials_section = scraper._find_materials_section(soup)
    if materials_section:
        print(f"✅ Found materials section: {materials_section.name}")
        print(f"Section text preview: {materials_section.get_text()[:200]}...")
        
        # Try parsing the section
        materials = scraper._parse_materials_section(materials_section)
        print(f"✅ Parsed {len(materials)} materials:")
        for material in materials:
            print(f"  - {material['name']} ({material['quantity']}) - {material['category']}")
    else:
        print("❌ No materials section found")
        
        # Let's check what headings exist
        print("\n=== Available headings ===")
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            headings = soup.find_all(tag)
            for heading in headings:
                text = heading.get_text().strip()
                if 'material' in text.lower() or 'required' in text.lower():
                    print(f"{tag}: {text}")
    
    # Try the fallback extraction method
    print("\n=== Trying fallback extraction ===")
    fallback_materials = scraper._extract_materials(soup)
    print(f"Fallback found {len(fallback_materials)} materials:")
    for material in fallback_materials:
        print(f"  - {material['name']} ({material['quantity']}) - {material['category']}")
        
else:
    print("❌ Failed to fetch page")
