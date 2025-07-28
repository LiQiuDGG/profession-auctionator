#!/usr/bin/env python3
"""
Blacksmithing-specific scraper for WoW profession materials
Extends the base scraper with blacksmithing-specific material extraction logic
"""

import sys
import argparse
from base_scraper import WowProfessionScraper
from bs4 import BeautifulSoup
import re
from typing import List, Dict

class BlacksmithingScraper(WowProfessionScraper):
    """Blacksmithing-specific scraper with enhanced material extraction"""
    
    def __init__(self, rate_limit: float = 2.0):
        super().__init__('blacksmithing', rate_limit)
        
    def _extract_materials(self, soup: BeautifulSoup) -> List[Dict[str, any]]:
        """
        Extract materials from blacksmithing guide pages
        Enhanced for blacksmithing-specific patterns
        """
        materials = []
        
        # Look for "Approximate Materials Required" section (blacksmithing-specific)
        materials_section = self._parse_materials_required_section(soup)
        if materials_section:
            materials.extend(materials_section)
            
        # If no materials found, fall back to base scraper logic
        if not materials:
            materials = super()._extract_materials(soup)
            
        # Deduplicate and aggregate quantities
        return self._deduplicate_materials(materials)
        
    def _parse_materials_required_section(self, soup: BeautifulSoup) -> List[Dict[str, any]]:
        """
        Parse the "Approximate Materials Required" section specific to blacksmithing guides
        """
        materials = []
        
        # Look for text containing "Approximate Materials Required"
        text_content = soup.get_text()
        
        # Find the materials section
        materials_start = text_content.find("Approximate Materials Required")
        if materials_start == -1:
            return materials
            
        # Extract the section after "Approximate Materials Required"
        materials_text = text_content[materials_start:materials_start + 2000]  # Reasonable limit
        
        # Split into lines and parse each line
        lines = materials_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue
                
            # Handle choice materials first (like "72x Rugged Leather or 9x Star Ruby")
            choice_match = re.search(r'(\d+)x\s*([A-Za-z\s\']+)\s+or\s+(\d+)x\s*([A-Za-z\s\']+)', line)
            if choice_match:
                # Take the first option (usually more common/cheaper)
                quantity = int(choice_match.group(1))
                name = choice_match.group(2).strip()
                name = self._clean_item_name(name)
                
                if self._is_valid_blacksmithing_material(name):
                    materials.append({
                        'name': name,
                        'category': self._categorize_item(name),
                        'quantity': quantity
                    })
                continue  # Skip the basic pattern check for this line
                
            # Look for basic pattern: "133x Rough Stone" or "210x Copper Bar"
            match = re.search(r'(\d+)x\s*([A-Za-z\s\']+(?:Bar|Stone|Ore|Cloth|Leather|Dye|Ruby|Coal))', line)
            if match:
                quantity = int(match.group(1))
                name = match.group(2).strip()
                
                # Clean up the name
                name = self._clean_item_name(name)
                
                if self._is_valid_blacksmithing_material(name):
                    materials.append({
                        'name': name,
                        'category': self._categorize_item(name),
                        'quantity': quantity
                    })
                    
        return materials
        
    def _clean_item_name(self, name: str) -> str:
        """
        Clean up blacksmithing material names
        """
        # Remove common unwanted patterns
        name = re.sub(r'\([^)]*\)', '', name)  # Remove parentheses content
        name = re.sub(r'\[[^\]]*\]', '', name)  # Remove brackets content
        name = re.sub(r'\s+', ' ', name).strip()  # Normalize whitespace
        
        return name
        
    def _is_valid_blacksmithing_material(self, name: str) -> bool:
        """
        Check if an item name represents a valid blacksmithing material
        """
        if not name or len(name) < 3:
            return False
            
        # Skip obvious non-materials
        skip_words = ['recipe', 'skill', 'level', 'point', 'guide', 'section', 
                     'total', 'cost', 'gold', 'silver', 'copper', 'requires',
                     'plans', 'blueprint', 'schematic', '-']
        
        name_lower = name.lower()
        return not any(skip_word in name_lower for skip_word in skip_words)
        
    def _deduplicate_materials(self, materials: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Remove duplicates and aggregate quantities
        """
        material_dict = {}
        
        for material in materials:
            name = material['name']
            if name in material_dict:
                # Add quantities if same item appears multiple times
                material_dict[name]['quantity'] += material['quantity']
            else:
                material_dict[name] = material.copy()
                
        return list(material_dict.values())
        
    def _categorize_item(self, item_name: str) -> str:
        """
        Categorize blacksmithing materials
        """
        name_lower = item_name.lower()
        
        # Ore and metal patterns
        ore_keywords = ['ore', 'metal', 'bar', 'ingot', 'copper', 'tin', 'iron', 
                       'silver', 'gold', 'mithril', 'thorium', 'adamantite', 
                       'cobalt', 'saronite', 'titanium', 'obsidium', 'elementium',
                       'pyrite', 'ghost', 'kyparite', 'trillium', 'draenor',
                       'leystone', 'felslate', 'storm', 'monelite', 'platinum',
                       'laestrite', 'solenium', 'oxxein', 'phaedrum', 'sinvyr',
                       'serevite', 'draconium', 'khaz', 'bismuth']
        if any(keyword in name_lower for keyword in ore_keywords):
            return 'Reagents/Metal'
            
        # Gem patterns  
        gem_keywords = ['jade', 'citrine', 'stone', 'gem', 'crystal', 'sapphire', 
                       'ruby', 'emerald', 'diamond', 'topaz', 'agate', 'bloodstone',
                       'chalcedony', 'shadow', 'sun', 'huge', 'perfect']
        if any(keyword in name_lower for keyword in gem_keywords):
            return 'Reagents/Gem'
            
        # Leather patterns (for some blacksmithing items)
        leather_keywords = ['leather', 'hide', 'skin', 'scale']
        if any(keyword in name_lower for keyword in leather_keywords):
            return 'Reagents/Leather'
            
        # Cloth patterns (for some recipes)
        cloth_keywords = ['cloth', 'linen', 'wool', 'silk', 'mageweave', 'runecloth',
                         'netherweave', 'frostweave', 'embersilk', 'windwool',
                         'sumptuous', 'hexweave', 'shal', 'lightless', 'shrouded']
        if any(keyword in name_lower for keyword in cloth_keywords):
            return 'Reagents/Cloth'
            
        # Flux and enhancement materials
        flux_keywords = ['flux', 'coal', 'grindstone', 'weightstone', 'sharpening',
                        'whetstone', 'grinding', 'rough', 'coarse', 'heavy']
        if any(keyword in name_lower for keyword in flux_keywords):
            return 'Reagents/Enhancement'
            
        # Elemental patterns
        elemental_keywords = ['eternal', 'crystallized', 'volatile', 'rousing', 'awakened',
                             'fire', 'air', 'water', 'earth', 'life', 'frost', 'order',
                             'essence', 'spirit', 'primal']
        if any(keyword in name_lower for keyword in elemental_keywords):
            return 'Reagents/Elemental'
            
        # Default category
        return 'Reagents/Other'


def main():
    parser = argparse.ArgumentParser(description='Scrape WoW Blacksmithing materials from wow-professions.com')
    parser.add_argument('--expansion', '-e', type=str, 
                       help='Specific expansion to scrape (e.g., vanilla, outland, northrend)')
    parser.add_argument('--output', '-o', type=str, default='../auctionator-shopping-lists/blacksmithing.txt',
                       help='Output filename (default: ../auctionator-shopping-lists/blacksmithing.txt)')
    parser.add_argument('--rate-limit', '-r', type=float, default=2.0,
                       help='Rate limit between requests in seconds (default: 2.0)')
    
    args = parser.parse_args()
    
    scraper = BlacksmithingScraper(rate_limit=args.rate_limit)
    
    if args.expansion:
        # Scrape specific expansion
        if args.expansion not in scraper.EXPANSIONS:
            print(f"Invalid expansion: {args.expansion}")
            print(f"Available expansions: {', '.join(scraper.EXPANSIONS.keys())}")
            sys.exit(1)
            
        content = scraper.scrape_expansion(args.expansion)
    else:
        # Scrape all expansions
        print("Scraping all expansions for Blacksmithing...")
        content = scraper.scrape_all_expansions()
        
    scraper.save_to_file(content, args.output)
    print(f"Blacksmithing materials saved to {args.output}")


if __name__ == "__main__":
    main()