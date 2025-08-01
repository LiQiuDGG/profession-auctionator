#!/usr/bin/env python3
"""
Base scraper class for WoW profession materials from wow-professions.com
Includes rate limiting and common functionality for all profession scrapers
"""

import requests
import time
import re
import json
import os
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Optional
from urllib.parse import urljoin

class WowProfessionScraper:
    """Base class for scraping WoW profession leveling guides"""
    
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
        
        # Load profession guides configuration
        self._load_config()
        
    def _load_config(self):
        """Load profession guides configuration from JSON file"""
        config_path = os.path.join(os.path.dirname(__file__), 'profession_guides_config.json')
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            self.BASE_URL = self.config['base_url']
            self.EXPANSIONS = {exp: info for exp, info in self.config['expansion_info'].items()}
        except FileNotFoundError:
            print(f"Warning: Config file not found at {config_path}. Using fallback configuration.")
            # Fallback to old configuration
            self.BASE_URL = "https://www.wow-professions.com"
            self.EXPANSIONS = {
                'vanilla': {'name': 'Vanilla (Classic)', 'number': 0},
                'outland': {'name': 'Burning Crusade (Outland)', 'number': 1}, 
                'northrend': {'name': 'Wrath of the Lich King (Northrend)', 'number': 2},
                'cataclysm': {'name': 'Cataclysm', 'number': 3},
                'pandaria': {'name': 'Mists of Pandaria', 'number': 4},
                'draenor': {'name': 'Warlords of Draenor', 'number': 5},
                'legion': {'name': 'Legion', 'number': 6},
                'bfa': {'name': 'Battle for Azeroth', 'number': 7},
                'shadowlands': {'name': 'Shadowlands', 'number': 8},
                'dragonflight': {'name': 'Dragonflight', 'number': 9},
                'tww': {'name': 'The War Within', 'number': 10}
            }
            self.config = {'professions': {}}
    
    def _get_expansion_display_name(self, expansion: str) -> str:
        """
        Get the proper display name for an expansion
        
        Args:
            expansion: Expansion key
            
        Returns:
            Properly formatted expansion name
        """
        # Special case for TWW - should be all caps
        if expansion == 'tww':
            return 'TWW'
            
        # Use config name if available
        expansion_info = self.EXPANSIONS.get(expansion)
        if expansion_info and 'name' in expansion_info:
            return expansion_info['name']
            
        # Fallback to title case
        return expansion.replace('_', ' ').title()
        
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
        Build the URL for a specific expansion's profession guide using config file
        
        Args:
            expansion: Expansion key from config
            
        Returns:
            Complete URL to the guide
        """
        # Check if we have the profession in config
        if self.profession in self.config.get('professions', {}):
            profession_urls = self.config['professions'][self.profession]
            if expansion in profession_urls and profession_urls[expansion] is not None:
                return f"{self.BASE_URL}{profession_urls[expansion]}"
        
        # Fallback to old URL construction if config is missing
        print(f"Warning: No config URL found for {expansion} {self.profession}, using fallback URL construction")
        expansion_info = self.EXPANSIONS.get(expansion, {'name': expansion.title(), 'number': 0})
        
        # Try some common URL patterns as fallback
        if expansion == 'dragonflight':
            return f"{self.BASE_URL}/guides/dragon-isles-{self.profession}-leveling-guide-dragonflight"
        elif expansion == 'bfa':
            return f"{self.BASE_URL}/guides/zandalari-kul-tiran-bfa-{self.profession}-leveling-guide"
        elif expansion in ['shadowlands']:
            return f"{self.BASE_URL}/guides/{expansion}-{self.profession}-leveling-guide"
        else:
            return f"{self.BASE_URL}/guides/{expansion}-{self.profession}-leveling"
            
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
        
        # First, look for the standard "Approximate Materials Required" section
        materials_section = self._find_materials_section(soup)
        if materials_section:
            section_materials = self._parse_materials_section(materials_section)
            materials.extend(section_materials)
            if section_materials:  # If we found materials in the standard section, return them
                return materials
        
        # Look for TradeSkillMaster shopping list as fallback
        tsm_materials = self._extract_tsm_shopping_list(soup)
        if tsm_materials:
            materials.extend(tsm_materials)
            
        # Look for common material list patterns - cast a wide net as final fallback
        sections = soup.find_all(['div', 'section', 'table', 'article', 'main', 'content'], 
                                class_=re.compile(r'material|shopping|ingredient|guide|content|post|article', re.I))
        
        # If no specific sections found, search the entire body
        if not sections:
            sections = [soup.find('body')] if soup.find('body') else [soup]
            
        for section in sections:
            if not section:
                continue
                
            # Handle choice sections (like Draenor)
            choice_materials = self._handle_choice_section(section)
            if choice_materials:
                materials.extend(choice_materials)
                continue
                
            # Look for item lists in various elements
            items = section.find_all(['li', 'tr', 'div', 'p', 'span', 'strong', 'b'])
            
            # Also parse all text content line by line
            full_text = section.get_text()
            text_lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            
            all_text_sources = []
            for item in items:
                item_text = item.get_text(strip=True)
                if item_text:
                    all_text_sources.append(item_text)
            all_text_sources.extend(text_lines)
            
            for text in all_text_sources:
                if not text or len(text) < 5:
                    continue
                    
                # Try to extract quantity and item name using regex
                patterns = [
                    r'(\d+)x?\s*(.+)',  # "60x Peacebloom" or "60 Peacebloom"
                    r'(.+)\s*[x×]\s*(\d+)',  # "Peacebloom x 60"
                    r'(.+)\s*[-–]\s*(\d+)',  # "Peacebloom - 60"
                    r'(.+)\s*:\s*(\d+)',  # "Peacebloom: 60"
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
                        name = re.sub(r'\([^)]*\)', '', name)  # Remove parentheses
                        name = re.sub(r'\[[^\]]*\]', '', name)  # Remove brackets
                        name = re.sub(r'\s+', ' ', name).strip()  # Normalize whitespace
                        
                        # Skip if it looks like a recipe or skill level
                        if self._is_valid_material(name):
                            materials.append({
                                'name': name,
                                'category': self._categorize_item(name),
                                'quantity': quantity
                            })
                        break
                    
        return materials
    
    def _find_materials_section(self, soup: BeautifulSoup):
        """
        Find the standard "Approximate Materials Required" section or similar
        
        Args:
            soup: BeautifulSoup object of the guide page
            
        Returns:
            BeautifulSoup section containing materials list or None
        """
        # Look for common materials section headings
        materials_headings = [
            'approximate materials required',
            'materials required',
            'shopping list',
            'materials needed',
            'reagents needed'
        ]
        
        # Find headings that might contain materials
        for heading_text in materials_headings:
            # Look for various heading tags
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b']:
                headings = soup.find_all(tag, string=re.compile(heading_text, re.I))
                for heading in headings:
                    # Find the next sibling or parent that contains the materials list
                    section = self._find_materials_content_after_heading(heading)
                    if section:
                        return section
                        
        return None
    
    def _find_materials_content_after_heading(self, heading):
        """
        Find the content section after a materials heading
        
        Args:
            heading: BeautifulSoup element containing the heading
            
        Returns:
            BeautifulSoup section with materials content or None
        """
        # Try to find the next sibling that contains a list
        current = heading
        for _ in range(10):  # Look at next 10 siblings
            current = current.find_next_sibling()
            if not current:
                break
                
            # Check if this sibling contains list items or structured content
            if current.find_all(['li', 'tr', 'div']):
                # Verify it contains material-like content
                text = current.get_text().lower()
                if any(keyword in text for keyword in ['x ', 'ore', 'herb', 'leather', 'cloth', 'stone']):
                    return current
                    
        # If no sibling found, try looking in the parent's next sibling
        parent = heading.find_parent()
        if parent:
            next_section = parent.find_next_sibling()
            if next_section and next_section.find_all(['li', 'tr', 'div']):
                return next_section
                
        return None
    
    def _parse_materials_section(self, section) -> List[Dict[str, any]]:
        """
        Parse materials from a standard materials section
        
        Args:
            section: BeautifulSoup section containing materials
            
        Returns:
            List of material dictionaries
        """
        materials = []
        
        # Look for list items first (most common format)
        list_items = section.find_all('li')
        if list_items:
            for item in list_items:
                material = self._parse_material_text(item.get_text(strip=True))
                if material:
                    materials.append(material)
        else:
            # Look for table rows
            rows = section.find_all('tr')
            if rows:
                for row in rows:
                    # Skip header rows
                    if row.find('th'):
                        continue
                    material = self._parse_material_text(row.get_text(strip=True))
                    if material:
                        materials.append(material)
            else:
                # Parse plain text line by line
                text_lines = section.get_text().split('\n')
                for line in text_lines:
                    line = line.strip()
                    if line:
                        material = self._parse_material_text(line)
                        if material:
                            materials.append(material)
                            
        return materials
    
    def _parse_material_text(self, text: str) -> Optional[Dict[str, any]]:
        """
        Parse a single line of text to extract material information
        
        Args:
            text: Text line that might contain material info
            
        Returns:
            Material dictionary or None if no valid material found
        """
        if not text or len(text) < 5:
            return None
            
        # Try to extract quantity and item name using regex
        patterns = [
            r'(\d+)\s*x\s*(.+)',  # "60x Peacebloom" or "60 x Peacebloom"
            r'(\d+)\s+(.+)',      # "60 Peacebloom"
            r'(.+)\s*[x×]\s*(\d+)',  # "Peacebloom x 60"
            r'(.+)\s*[-–]\s*(\d+)',  # "Peacebloom - 60"
            r'(.+)\s*:\s*(\d+)',     # "Peacebloom: 60"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if pattern in patterns[:2]:  # First two patterns (quantity first)
                    quantity = int(match.group(1))
                    name = match.group(2).strip()
                else:  # Other patterns (name first)
                    name = match.group(1).strip()
                    quantity = int(match.group(2))
                
                # Clean up the name
                name = re.sub(r'\([^)]*\)', '', name)  # Remove parentheses
                name = re.sub(r'\[[^\]]*\]', '', name)  # Remove brackets
                name = re.sub(r'\s+', ' ', name).strip()  # Normalize whitespace
                
                # Skip if it looks like a recipe or skill level
                if self._is_valid_material(name) and quantity > 0:
                    return {
                        'name': name,
                        'category': self._categorize_item(name),
                        'quantity': quantity
                    }
                break
                
        return None
        
    def _extract_tsm_shopping_list(self, soup: BeautifulSoup) -> List[Dict[str, any]]:
        """
        Extract TradeSkillMaster shopping list if available
        
        Args:
            soup: BeautifulSoup object of the guide page
            
        Returns:
            List of material dictionaries from TSM list
        """
        materials = []
        
        # Look for TSM shopping list sections
        tsm_sections = soup.find_all(['div', 'section', 'pre', 'code'], 
                                    class_=re.compile(r'tsm|tradeskill|shopping', re.I))
        
        for section in tsm_sections:
            text = section.get_text()
            
            # Look for TSM string patterns
            if '/tsm' in text.lower() or 'tradeskillmaster' in text.lower():
                # Extract items from TSM string
                lines = text.split('\n')
                for line in lines:
                    if '/' in line and any(char.isdigit() for char in line):
                        # Parse TSM item strings like "item:765/50" (item ID / quantity)
                        tsm_match = re.search(r'item:(\d+)/(\d+)', line)
                        if tsm_match:
                            item_id = tsm_match.group(1)
                            quantity = int(tsm_match.group(2))
                            
                            # Try to find item name in the same section
                            item_name = self._resolve_item_name(item_id, soup)
                            if item_name:
                                materials.append({
                                    'name': item_name,
                                    'category': self._categorize_item(item_name),
                                    'quantity': quantity
                                })
                                
        return materials
        
    def _handle_choice_section(self, section) -> List[Dict[str, any]]:
        """
        Handle sections with multiple material choices (like Draenor alternatives)
        Always choose the most available but historically lowest cost option
        
        Args:
            section: BeautifulSoup section containing choices
            
        Returns:
            List of selected materials
        """
        materials = []
        text = section.get_text().lower()
        
        # Look for choice indicators
        choice_indicators = ['choose', 'alternative', 'option', 'either', 'or', 'cheapest']
        if not any(indicator in text for indicator in choice_indicators):
            return materials
            
        # Extract all potential choices
        choices = []
        lines = section.get_text().split('\n')
        
        for line in lines:
            match = re.search(r'(\d+)x?\s*(.+)', line.strip())
            if match:
                quantity = int(match.group(1))
                name = match.group(2).strip()
                
                # Clean up choice text
                name = re.sub(r'\(.*?\)', '', name)  # Remove parenthetical notes
                name = re.sub(r'or\s+', '', name, flags=re.I)  # Remove "or"
                name = name.strip()
                
                if self._is_valid_material(name):
                    choices.append({
                        'name': name,
                        'category': self._categorize_item(name),
                        'quantity': quantity,
                        'priority': self._get_material_priority(name)
                    })
        
        # Select best choice based on priority (lower is better)
        if choices:
            best_choice = min(choices, key=lambda x: x['priority'])
            materials.append(best_choice)
            
        return materials
        
    def _get_material_priority(self, item_name: str) -> int:
        """
        Get priority for material selection (lower = better choice)
        Based on historical availability and cost
        
        Args:
            item_name: Name of the material
            
        Returns:
            Priority score (lower is better)
        """
        name_lower = item_name.lower()
        
        # Highly available, low-cost materials (priority 1)
        common_materials = [
            'copper', 'tin', 'iron', 'light leather', 'medium leather',
            'peacebloom', 'silverleaf', 'earthroot', 'mageroyal',
            'linen cloth', 'wool cloth', 'rough stone', 'coarse stone',
            'golden sansam'  # Add Golden Sansam as common since it appears frequently
        ]
        
        # Moderately available materials (priority 2)
        moderate_materials = [
            'silver', 'gold', 'mithril', 'heavy leather', 'thick leather',
            'briarthorn', 'stranglekelp', 'bruiseweed', 'wild steelbloom',
            'silk cloth', 'mageweave cloth', 'heavy stone', 'solid stone'
        ]
        
        # Less common, higher cost materials (priority 3)
        uncommon_materials = [
            'thorium', 'rugged leather', 'black lotus', 'ghost mushroom',
            'gromsblood', 'blindweed', 'runecloth', 'dense stone'
        ]
        
        # Check priority levels
        for material in common_materials:
            if material in name_lower:
                return 1
                
        for material in moderate_materials:
            if material in name_lower:
                return 2
                
        for material in uncommon_materials:
            if material in name_lower:
                return 3
                
        # Default priority for unknown materials
        return 2
        
    def _resolve_item_name(self, item_id: str, soup: BeautifulSoup) -> Optional[str]:
        """
        Try to resolve item ID to item name from the page context
        
        Args:
            item_id: WoW item ID
            soup: BeautifulSoup object to search for item names
            
        Returns:
            Item name if found, None otherwise
        """
        # This is a simplified implementation
        # In a full implementation, you might query WoW API or maintain an item database
        
        # Look for item names in the same section as the TSM string
        text = soup.get_text()
        lines = text.split('\n')
        
        # Try to find lines that might contain item names near the item ID
        for i, line in enumerate(lines):
            if item_id in line:
                # Check nearby lines for item names
                for j in range(max(0, i-3), min(len(lines), i+4)):
                    potential_name = lines[j].strip()
                    if potential_name and not any(char.isdigit() for char in potential_name[:3]):
                        # Clean potential name
                        potential_name = re.sub(r'[^\w\s\'-]', '', potential_name)
                        if len(potential_name) > 3 and len(potential_name) < 50:
                            return potential_name
                            
        return None
        
    def _is_valid_material(self, name: str) -> bool:
        """
        Enhanced validation for material names
        """
        if not name or len(name) < 3:
            return False
            
        # Skip obvious non-materials
        skip_words = ['recipe', 'skill', 'level', 'point', 'guide', 'section', 
                     'total', 'cost', 'gold', 'silver', 'copper', 'requires',
                     'choose', 'option', 'alternative', 'either', 'cheapest']
        
        name_lower = name.lower()
        return not any(skip_word in name_lower for skip_word in skip_words)
        
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
                        'rose', 'lily', 'cap', 'moss', 'thorn', 'glory', 'vine', 'poppy',
                        'dreamfoil', 'ragveil', 'azshara', 'veil', 'jasmine', 'whiptail', 'sansam']  # Add specific herb names that were miscategorized
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
        
    def _format_for_auctionator(self, materials: List[Dict[str, any]], expansion_name: str, expansion_number: int) -> str:
        """
        Format materials list for Auctionator import
        
        Args:
            materials: List of material dictionaries
            expansion_name: Name of the expansion for the header
            expansion_number: WoW expansion number (unused, kept for compatibility)
            
        Returns:
            Formatted string ready for Auctionator import
        """
        shopping_list_name = f"{expansion_name} {self.profession.title()}"
        
        if not materials:
            return f"{shopping_list_name}\n"
            
        # Create the formatted items list
        items = []
        for material in materials:
            # Wrap item name in quotes for exact search, remove expansion field entirely
            formatted_item = f'"{material["name"]}";{material["category"]};0;0;0;0;0;0;0;0;;#;;{material["quantity"]}'
            items.append(formatted_item)
            
        # Format: Shopping List Name^Item1^Item2^Item3...
        items_string = '^'.join(items)
        return f"{shopping_list_name}^{items_string}\n"
        
    def scrape_expansion(self, expansion: str) -> str:
        """
        Scrape materials for a specific expansion

        Args:
            expansion: Expansion key from EXPANSIONS dict
            
        Returns:
            Formatted materials string for Auctionator
        """
        # Skip problematic expansions that don't have proper material sections
        if expansion in ['draenor', 'legion']:
            print(f"Skipping {expansion} {self.profession} - guide structure not compatible with scraper")
            return ""  # Return empty string to exclude from output entirely
            
        url = self._build_guide_url(expansion)
        print(f"Scraping {expansion} {self.profession} from: {url}")
        
        soup = self._get_page(url)
        if not soup:
            print(f"Failed to fetch page for {expansion}")
            expansion_name = self._get_expansion_display_name(expansion)
            return f"{expansion_name} {self.profession.title()}\n"
            
        materials = self._extract_materials(soup)
        expansion_info = self.EXPANSIONS.get(expansion, {'name': expansion.title(), 'number': 0})
        expansion_name = self._get_expansion_display_name(expansion)
        expansion_number = expansion_info['number']
        
        print(f"Found {len(materials)} materials for {expansion} {self.profession}")
        return self._format_for_auctionator(materials, expansion_name, expansion_number)
        
    def scrape_all_expansions(self) -> str:
        """
        Scrape materials for all expansions
        
        Returns:
            Complete formatted materials string for all expansions
        """
        all_materials = []
        
        for expansion in self.EXPANSIONS.keys():
            expansion_materials = self.scrape_expansion(expansion)
            if expansion_materials.strip():  # Only add non-empty results
                all_materials.append(expansion_materials)
            
        return '\n'.join(all_materials)
        
    def save_to_file(self, content: str, filename: Optional[str] = None):
        """
        Save scraped materials to a file
        
        Args:
            content: Formatted materials content
            filename: Output filename (defaults to ../auctionator-shopping-lists/{profession}.txt)
        """
        if filename is None:
            filename = f"../auctionator-shopping-lists/{self.profession}.txt"
            
        # Ensure the directory exists
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
            
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Materials saved to {filename}")


if __name__ == "__main__":
    # Example usage
    scraper = WowProfessionScraper('alchemy')
    materials = scraper.scrape_expansion('vanilla')
    print(materials)