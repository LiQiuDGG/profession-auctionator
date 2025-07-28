#!/usr/bin/env python3
"""
Alchemy-specific scraper for WoW profession materials
Extends the base scraper with alchemy-specific material extraction logic
"""

import sys
import argparse
from base_scraper import WowProfessionScraper
from bs4 import BeautifulSoup
import re
from typing import List, Dict

class AlchemyScraper(WowProfessionScraper):
    """Alchemy-specific scraper with enhanced material extraction"""
    
    def __init__(self, rate_limit: float = 2.0):
        super().__init__('alchemy', rate_limit)
        
    def _extract_materials(self, soup: BeautifulSoup) -> List[Dict[str, any]]:
        """
        Extract materials from alchemy guide pages
        Enhanced for alchemy-specific patterns
        """
        materials = []
        
        # Look for shopping list sections first
        shopping_sections = soup.find_all(['div', 'section'], 
                                        class_=re.compile(r'shopping|material', re.I))
        
        if shopping_sections:
            for section in shopping_sections:
                materials.extend(self._parse_shopping_section(section))
                
        # If no shopping section found, look for recipe sections
        if not materials:
            recipe_sections = soup.find_all(['div', 'section'], 
                                          class_=re.compile(r'recipe|guide', re.I))
            for section in recipe_sections:
                materials.extend(self._parse_recipe_section(section))
                
        # Look for table-based material lists
        tables = soup.find_all('table')
        for table in tables:
            materials.extend(self._parse_material_table(table))
            
        # Deduplicate and aggregate quantities
        return self._deduplicate_materials(materials)
        
    def _parse_shopping_section(self, section) -> List[Dict[str, any]]:
        """Parse a shopping list section"""
        materials = []
        
        # Look for list items
        items = section.find_all(['li', 'p', 'div'])
        for item in items:
            text = item.get_text(strip=True)
            
            # Try multiple regex patterns for quantity extraction
            patterns = [
                r'(\d+)x?\s*(.+)',  # "60x Peacebloom" or "60 Peacebloom"
                r'(.+)\s*[x×]\s*(\d+)',  # "Peacebloom x 60"
                r'(.+)\s*[-–]\s*(\d+)',  # "Peacebloom - 60"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    if pattern == patterns[0]:  # First pattern
                        quantity = int(match.group(1))
                        name = match.group(2).strip()
                    else:  # Other patterns
                        name = match.group(1).strip()
                        quantity = int(match.group(2))
                        
                    # Clean up the name
                    name = self._clean_item_name(name)
                    
                    if self._is_valid_material(name):
                        materials.append({
                            'name': name,
                            'category': self._categorize_item(name),
                            'quantity': quantity
                        })
                    break
                    
        return materials
        
    def _parse_recipe_section(self, section) -> List[Dict[str, any]]:
        """Parse recipe sections to extract required materials"""
        materials = []
        
        # Look for ingredient lists in recipes
        recipe_blocks = section.find_all(['div', 'p'], class_=re.compile(r'recipe|ingredient', re.I))
        
        for block in recipe_blocks:
            text = block.get_text()
            
            # Look for "Requires:" or "Materials:" patterns
            if re.search(r'(requires?|materials?|ingredients?):', text, re.I):
                lines = text.split('\n')
                for line in lines:
                    match = re.search(r'(\d+)x?\s*(.+)', line.strip())
                    if match:
                        quantity = int(match.group(1))
                        name = self._clean_item_name(match.group(2))
                        
                        if self._is_valid_material(name):
                            materials.append({
                                'name': name,
                                'category': self._categorize_item(name),
                                'quantity': quantity
                            })
                            
        return materials
        
    def _parse_material_table(self, table) -> List[Dict[str, any]]:
        """Parse material information from tables"""
        materials = []
        
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                # Try to find quantity and item name in cells
                for i, cell in enumerate(cells):
                    text = cell.get_text(strip=True)
                    match = re.search(r'(\d+)x?\s*(.+)', text)
                    if match:
                        quantity = int(match.group(1))
                        name = self._clean_item_name(match.group(2))
                        
                        if self._is_valid_material(name):
                            materials.append({
                                'name': name,
                                'category': self._categorize_item(name),
                                'quantity': quantity
                            })
                            
        return materials
        
    def _clean_item_name(self, name: str) -> str:
        """Clean up item names by removing unwanted text"""
        # Remove common unwanted patterns
        name = re.sub(r'\([^)]*\)', '', name)  # Remove parentheses content
        name = re.sub(r'\[[^\]]*\]', '', name)  # Remove brackets content
        name = re.sub(r'(recipe|skill|level|point).*', '', name, flags=re.I)  # Remove recipe info
        name = re.sub(r'x\d+$', '', name)  # Remove trailing x numbers
        name = re.sub(r'\s+', ' ', name)  # Normalize whitespace
        
        return name.strip()
        
    def _is_valid_material(self, name: str) -> bool:
        """Check if an item name represents a valid crafting material"""
        if not name or len(name) < 3:
            return False
            
        # Skip obvious non-materials
        skip_words = ['recipe', 'skill', 'level', 'point', 'guide', 'section', 
                     'total', 'cost', 'gold', 'silver', 'copper', 'requires']
        
        name_lower = name.lower()
        return not any(skip_word in name_lower for skip_word in skip_words)
        
    def _deduplicate_materials(self, materials: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """Remove duplicates and aggregate quantities"""
        material_dict = {}
        
        for material in materials:
            name = material['name']
            if name in material_dict:
                # Add quantities if same item appears multiple times
                material_dict[name]['quantity'] += material['quantity']
            else:
                material_dict[name] = material.copy()
                
        return list(material_dict.values())


def main():
    parser = argparse.ArgumentParser(description='Scrape WoW Alchemy materials from wow-professions.com')
    parser.add_argument('--expansion', '-e', type=str, 
                       help='Specific expansion to scrape (e.g., vanilla, outland, northrend)')
    parser.add_argument('--output', '-o', type=str, default='alchemy.txt',
                       help='Output filename (default: alchemy.txt)')
    parser.add_argument('--rate-limit', '-r', type=float, default=2.0,
                       help='Rate limit between requests in seconds (default: 2.0)')
    
    args = parser.parse_args()
    
    scraper = AlchemyScraper(rate_limit=args.rate_limit)
    
    if args.expansion:
        # Scrape specific expansion
        if args.expansion not in scraper.EXPANSIONS:
            print(f"Invalid expansion: {args.expansion}")
            print(f"Available expansions: {', '.join(scraper.EXPANSIONS.keys())}")
            sys.exit(1)
            
        content = scraper.scrape_expansion(args.expansion)
    else:
        # Scrape all expansions
        print("Scraping all expansions for Alchemy...")
        content = scraper.scrape_all_expansions()
        
    scraper.save_to_file(content, args.output)
    print(f"Alchemy materials saved to {args.output}")


if __name__ == "__main__":
    main()