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