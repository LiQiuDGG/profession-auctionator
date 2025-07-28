#!/usr/bin/env python3

import sys
sys.path.append('.')
from base_scraper import WowProfessionScraper

# Test the actual problem directly
scraper = WowProfessionScraper('alchemy')
expansion = 'shadowlands'

url = scraper._build_guide_url(expansion)
soup = scraper._get_page(url)

print("=== Testing the exact issue ===")

# Test the materials section finding
materials_section = scraper._find_materials_section(soup)
print(f"Materials section found: {materials_section is not None}")

if materials_section:
    section_materials = scraper._parse_materials_section(materials_section)
    print(f"Section materials count: {len(section_materials)}")
    print(f"Section materials bool evaluation: {bool(section_materials)}")
    
    materials = []
    materials.extend(section_materials)
    print(f"Materials after extend: {len(materials)}")
    
    if section_materials:
        print("✅ Would return section_materials")
        print(f"Returning: {len(materials)} materials")
    else:
        print("❌ section_materials evaluated to False")
        
    # Test each individual material
    for i, material in enumerate(section_materials):
        print(f"Material {i+1}: {material}")
        print(f"  Valid material check: {scraper._is_valid_material(material['name'])}")
