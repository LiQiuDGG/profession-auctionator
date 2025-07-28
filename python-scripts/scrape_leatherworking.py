#!/usr/bin/env python3
"""
Leatherworking-specific scraper for WoW profession materials
Extends the base scraper with leatherworking-specific material extraction logic
"""

import sys
import argparse
from base_scraper import WowProfessionScraper
from bs4 import BeautifulSoup
import re
from typing import List, Dict

class LeatherworkingScraper(WowProfessionScraper):
    """Leatherworking-specific scraper with enhanced material extraction"""
    
    def __init__(self, rate_limit: float = 2.0):
        super().__init__('leatherworking', rate_limit)
        
    def _categorize_item(self, item_name: str) -> str:
        """
        Categorize leatherworking materials
        """
        name_lower = item_name.lower()
        
        # Leather and hide patterns
        leather_keywords = ['leather', 'hide', 'skin', 'pelt', 'fur', 'rawhide',
                           'light', 'medium', 'heavy', 'thick', 'rugged', 'knothide',
                           'heavy clefthoof', 'cobra', 'wind scales', 'arctic', 'nerubian',
                           'icy dragonscale', 'jormungar', 'savage', 'blackened dragonscale',
                           'pristine', 'exotic', 'magnificent', 'sha-touched', 'yak',
                           'kyparite', 'sha', 'ghost', 'sumptuous', 'burnished',
                           'stonehide', 'gorebound', 'felscale', 'stormscale', 'silkweave',
                           'dreadleather', 'fiendish', 'lightless', 'shadow', 'deep sea',
                           'bone', 'desolate', 'pallid', 'heavy callous', 'lightless silk',
                           'heavy desolate', 'shrouded']
        if any(keyword in name_lower for keyword in leather_keywords):
            return 'Reagents/Leather'
            
        # Scale patterns
        scale_keywords = ['scale', 'dragonscale', 'prismatic', 'iridescent', 'brilliant',
                         'gleaming', 'pristine', 'resplendent', 'storm', 'wind']
        if any(keyword in name_lower for keyword in scale_keywords):
            return 'Reagents/Scale'
            
        # Thread and binding patterns
        thread_keywords = ['thread', 'sinew', 'gut', 'string', 'cord', 'binding',
                          'rune', 'enchanted', 'heavy silken', 'silken', 'enchanting']
        if any(keyword in name_lower for keyword in thread_keywords):
            return 'Reagents/Thread'
            
        # Cloth patterns (for some leatherworking items)
        cloth_keywords = ['cloth', 'linen', 'wool', 'silk', 'mageweave', 'runecloth',
                         'netherweave', 'frostweave', 'embersilk', 'windwool',
                         'sumptuous', 'hexweave', 'shal', 'lightless', 'shrouded']
        if any(keyword in name_lower for keyword in cloth_keywords):
            return 'Reagents/Cloth'
            
        # Salt and curing materials
        salt_keywords = ['salt', 'curing', 'tanning', 'alum', 'lime', 'potash']
        if any(keyword in name_lower for keyword in salt_keywords):
            return 'Reagents/Chemical'
            
        # Dye patterns
        dye_keywords = ['dye', 'pigment', 'ink', 'paint', 'stain', 'tint']
        if any(keyword in name_lower for keyword in dye_keywords):
            return 'Reagents/Dye'
            
        # Elemental patterns
        elemental_keywords = ['eternal', 'crystallized', 'volatile', 'rousing', 'awakened',
                             'fire', 'air', 'water', 'earth', 'life', 'frost', 'order',
                             'essence', 'spirit', 'primal']
        if any(keyword in name_lower for keyword in elemental_keywords):
            return 'Reagents/Elemental'
            
        # Gem patterns (for some leatherworking enhancements)
        gem_keywords = ['jade', 'citrine', 'stone', 'gem', 'crystal', 'sapphire', 
                       'ruby', 'emerald', 'diamond', 'topaz', 'agate', 'bloodstone',
                       'chalcedony', 'shadow', 'sun', 'huge', 'perfect']
        if any(keyword in name_lower for keyword in gem_keywords):
            return 'Reagents/Gem'
            
        # Default category
        return 'Reagents/Other'


def main():
    parser = argparse.ArgumentParser(description='Scrape WoW Leatherworking materials from wow-professions.com')
    parser.add_argument('--expansion', '-e', type=str, 
                       help='Specific expansion to scrape (e.g., vanilla, outland, northrend)')
    parser.add_argument('--output', '-o', type=str, default='../auctionator-shopping-lists/leatherworking.txt',
                       help='Output filename (default: ../auctionator-shopping-lists/leatherworking.txt)')
    parser.add_argument('--rate-limit', '-r', type=float, default=2.0,
                       help='Rate limit between requests in seconds (default: 2.0)')
    
    args = parser.parse_args()
    
    scraper = LeatherworkingScraper(rate_limit=args.rate_limit)
    
    if args.expansion:
        # Scrape specific expansion
        if args.expansion not in scraper.EXPANSIONS:
            print(f"Invalid expansion: {args.expansion}")
            print(f"Available expansions: {', '.join(scraper.EXPANSIONS.keys())}")
            sys.exit(1)
            
        content = scraper.scrape_expansion(args.expansion)
    else:
        # Scrape all expansions
        print("Scraping all expansions for Leatherworking...")
        content = scraper.scrape_all_expansions()
        
    scraper.save_to_file(content, args.output)
    print(f"Leatherworking materials saved to {args.output}")


if __name__ == "__main__":
    main()