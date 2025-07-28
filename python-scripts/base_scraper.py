#!/usr/bin/env python3
"""
Base scraper class for WoW profession materials from wow-professions.com
Includes rate limiting and common functionality for all profession scrapers
"""

import requests
import time
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Optional
from urllib.parse import urljoin

class WowProfessionScraper:
    """Base class for scraping WoW profession leveling guides"""
    
    BASE_URL = "https://www.wow-professions.com"
    
    # Expansion mapping with their guide URL patterns
    EXPANSIONS = {
        'vanilla': 'vanilla',
        'outland': 'outland', 
        'northrend': 'northrend',
        'cataclysm': 'cataclysm',
        'pandaria': 'pandaria',
        'draenor': 'draenor',
        'legion': 'legion',
        'bfa': 'battle-for-azeroth',
        'shadowlands': 'shadowlands',
        'dragonflight': 'dragon-isles',
        'war_within': 'the-war-within'
    }
    
    def __init__(self, profession: str, rate_limit: float = 2.0):
        """
        Initialize scraper for a specific profession
        
        Args:
            profession: Name of the profession (e.g., 'alchemy', 'blacksmithing')
            rate_limit: Seconds to wait between requests (default 2.0s)
        """
        self.profession = profession
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def _wait(self):
        """Apply rate limiting between requests"""
        time.sleep(self.rate_limit)
        
    def _get_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a webpage with error handling
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            self._wait()
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
            
    def _build_guide_url(self, expansion: str) -> str:
        """
        Build the URL for a specific expansion's profession guide
        
        Args:
            expansion: Expansion key from EXPANSIONS dict
            
        Returns:
            Complete URL to the guide
        """
        expansion_name = self.EXPANSIONS.get(expansion, expansion)
        
        # Special case for dragonflight guide URL pattern
        if expansion == 'dragonflight':
            return f"{self.BASE_URL}/guides/{expansion_name}-{self.profession}-leveling-guide-dragonflight"
        else:
            return f"{self.BASE_URL}/guides/{expansion_name}-{self.profession}-leveling"
            
    def _extract_materials(self, soup: BeautifulSoup) -> List[Dict[str, any]]:
        """
        Extract materials list from a guide page
        This method should be overridden by profession-specific scrapers
        
        Args:
            soup: BeautifulSoup object of the guide page
            
        Returns:
            List of material dictionaries with keys: name, category, quantity
        """
        materials = []
        
        # Look for common material list patterns
        # This is a generic implementation - profession-specific scrapers should override
        
        # Try to find shopping list or materials sections
        sections = soup.find_all(['div', 'section', 'table'], 
                                class_=re.compile(r'material|shopping|ingredient', re.I))
        
        for section in sections:
            # Look for item lists
            items = section.find_all(['li', 'tr', 'div'])
            for item in items:
                text = item.get_text(strip=True)
                
                # Try to extract quantity and item name using regex
                match = re.search(r'(\d+)x?\s*(.+)', text)
                if match:
                    quantity = int(match.group(1))
                    name = match.group(2).strip()
                    
                    # Skip if it looks like a recipe or skill level
                    if any(skip_word in name.lower() for skip_word in ['recipe', 'skill', 'level', 'point']):
                        continue
                        
                    materials.append({
                        'name': name,
                        'category': self._categorize_item(name),
                        'quantity': quantity
                    })
                    
        return materials
        
    def _categorize_item(self, item_name: str) -> str:
        """
        Categorize an item based on its name
        
        Args:
            item_name: Name of the item
            
        Returns:
            Category string (e.g., 'Reagents/Herb', 'Reagents/Gem')
        """
        name_lower = item_name.lower()
        
        # Herb patterns
        herb_keywords = ['leaf', 'bloom', 'blossom', 'weed', 'root', 'kelp', 'grass', 
                        'rose', 'lily', 'cap', 'moss', 'thorn', 'glory', 'vine']
        if any(keyword in name_lower for keyword in herb_keywords):
            return 'Reagents/Herb'
            
        # Gem patterns  
        gem_keywords = ['jade', 'citrine', 'stone', 'gem', 'crystal', 'sapphire', 
                       'ruby', 'emerald', 'diamond', 'topaz']
        if any(keyword in name_lower for keyword in gem_keywords):
            return 'Reagents/Gem'
            
        # Elemental patterns
        elemental_keywords = ['eternal', 'crystallized', 'volatile', 'rousing', 'awakened',
                             'fire', 'air', 'water', 'earth', 'life', 'frost', 'order']
        if any(keyword in name_lower for keyword in elemental_keywords):
            return 'Reagents/Elemental'
            
        # Potion patterns
        potion_keywords = ['potion', 'elixir', 'flask', 'draught']
        if any(keyword in name_lower for keyword in potion_keywords):
            return 'Reagents/Potion'
            
        # Vial patterns
        if 'vial' in name_lower:
            return 'Reagents/Consumable'
            
        # Default category
        return 'Reagents/Other'
        
    def _format_for_auctionator(self, materials: List[Dict[str, any]], expansion_name: str) -> str:
        """
        Format materials list for Auctionator import
        
        Args:
            materials: List of material dictionaries
            expansion_name: Name of the expansion for the header
            
        Returns:
            Formatted string ready for Auctionator import
        """
        if not materials:
            return f"{expansion_name} {self.profession.title()}\n"
            
        # Create the formatted items list
        items = []
        for material in materials:
            # Wrap item name in quotes for exact search
            formatted_item = f'"{material["name"]}";{material["category"]};0;0;0;0;0;0;0;0;;#;0;{material["quantity"]}'
            items.append(formatted_item)
            
        # Join with ^ separator and add header
        items_string = '^'.join(items)
        return f"{expansion_name} {self.profession.title()}\n{items_string}\n"
        
    def scrape_expansion(self, expansion: str) -> str:
        """
        Scrape materials for a specific expansion
        
        Args:
            expansion: Expansion key from EXPANSIONS dict
            
        Returns:
            Formatted materials string for Auctionator
        """
        url = self._build_guide_url(expansion)
        print(f"Scraping {expansion} {self.profession} from: {url}")
        
        soup = self._get_page(url)
        if not soup:
            print(f"Failed to fetch page for {expansion}")
            return f"{expansion.title()} {self.profession.title()}\n"
            
        materials = self._extract_materials(soup)
        expansion_name = expansion.replace('_', ' ').title()
        
        print(f"Found {len(materials)} materials for {expansion} {self.profession}")
        return self._format_for_auctionator(materials, expansion_name)
        
    def scrape_all_expansions(self) -> str:
        """
        Scrape materials for all expansions
        
        Returns:
            Complete formatted materials string for all expansions
        """
        all_materials = []
        
        for expansion in self.EXPANSIONS.keys():
            expansion_materials = self.scrape_expansion(expansion)
            all_materials.append(expansion_materials)
            
        return '\n'.join(all_materials)
        
    def save_to_file(self, content: str, filename: Optional[str] = None):
        """
        Save scraped materials to a file
        
        Args:
            content: Formatted materials content
            filename: Output filename (defaults to {profession}.txt)
        """
        if filename is None:
            filename = f"{self.profession}.txt"
            
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Materials saved to {filename}")


if __name__ == "__main__":
    # Example usage
    scraper = WowProfessionScraper('alchemy')
    materials = scraper.scrape_expansion('vanilla')
    print(materials)