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
        self.chosen_materials = {}  # Track materials chosen in choice scenarios
        
    def _extract_materials(self, soup: BeautifulSoup) -> List[Dict[str, any]]:
        """
        Extract materials from alchemy guide pages
        Enhanced for alchemy-specific patterns
        """
        materials = []
        
        # First, look for the specific materials section with id="materials"
        materials_section = soup.find('h2', id='materials')
        if materials_section:
            # Find the next ul element after the materials heading
            materials_list = materials_section.find_next('ul')
            if materials_list:
                materials.extend(self._parse_materials_list(materials_list))
        
        # Also look for any other materials lists in the document
        # Look for headings that indicate material lists
        all_headings = soup.find_all(['h1', 'h2', 'h3'])
        
        for heading in all_headings:
            heading_text_lower = heading.get_text(strip=True).lower()
            
            # Look for various material list indicators  
            material_indicators = [
                'material', 'shopping', 'ingredient', 'required', 
                'approximate', 'needed', 'reagent', 'herb', 'components'
            ]
            
            if any(indicator in heading_text_lower for indicator in material_indicators):
                # Find the next ul after each heading
                materials_list = heading.find_next('ul')
                if materials_list:
                    new_materials = self._parse_materials_list(materials_list)
                    materials.extend(new_materials)
        
        # Also look for bold text that indicates materials lists (like Outland)
        bold_elements = soup.find_all(['strong', 'b'])
        
        for bold in bold_elements:
            bold_text_lower = bold.get_text(strip=True).lower()
            
            material_indicators = [
                'material', 'shopping', 'ingredient', 'required', 
                'approximate', 'needed', 'reagent', 'herb', 'components'
            ]
            
            if any(indicator in bold_text_lower for indicator in material_indicators):
                # Find the next ul after this bold text
                materials_list = bold.find_next('ul')
                if materials_list:
                    new_materials = self._parse_materials_list(materials_list)
                    materials.extend(new_materials)
        
        # Look for shopping list sections
        shopping_sections = soup.find_all(['div', 'section'], 
                                        class_=re.compile(r'shopping|material', re.I))
        
        for section in shopping_sections:
            materials.extend(self._parse_shopping_section(section))
                
        # Look for recipe sections if still no materials
        if not materials:
            recipe_sections = soup.find_all(['div', 'section'], 
                                          class_=re.compile(r'recipe|guide', re.I))
            for section in recipe_sections:
                materials.extend(self._parse_recipe_section(section))
                
        # Look for table-based material lists
        tables = soup.find_all('table')
        for table in tables:
            materials.extend(self._parse_material_table(table))
            
        # Special handling for Pandaria-style inline herb mentions
        if not materials:
            materials.extend(self._parse_pandaria_style(soup))
            
        # Deduplicate and aggregate quantities
        return self._deduplicate_materials(materials)
        
    def _parse_materials_list(self, materials_list) -> List[Dict[str, any]]:
        """Parse a <ul> element containing materials"""
        materials = []
        
        list_items = materials_list.find_all('li')
        for item in list_items:
            # Get text content, which should be in format like "60x Peacebloom"  
            text = item.get_text(strip=True)
            
            # Check if this item contains choice alternatives (like Outland's choice item)
            if '/' in text and ('only need' in text.lower() or 'you need' in text.lower()):
                # This is a choice item, extract all alternatives
                choice_materials = self._parse_choice_item(text)
                materials.extend(choice_materials)
            else:
                # Parse the format: "60x Peacebloom"
                match = re.search(r'(\d+)x\s*(.+)', text)
                if match:
                    quantity = int(match.group(1))
                    name = match.group(2).strip()
                    
                    # Clean up the name (remove any extra whitespace or artifacts)
                    name = self._clean_item_name(name)
                    
                    if self._is_valid_material(name):
                        materials.append({
                            'name': name,
                            'category': self._categorize_item(name),
                            'quantity': quantity
                        })
                    
        return materials
        
    def _parse_choice_item(self, text: str) -> List[Dict[str, any]]:
        """Parse a choice item like '14x Golden Sansam / 14x Dreamfoil / 14x Mountain Silversage (you only need 14 from one)'"""
        materials = []
        
        # Split on the explanatory text first
        if '(' in text:
            choices_text = text.split('(')[0]
        else:
            choices_text = text
            
        # Split on / to get individual choices  
        choices = choices_text.split('/')
        
        choice_materials = []
        for choice in choices:
            choice = choice.strip()
            # Parse each choice: "14x Golden Sansam"
            match = re.search(r'(\d+)x\s*(.+)', choice)
            if match:
                quantity = int(match.group(1))
                name = match.group(2).strip()
                name = self._clean_item_name(name)
                
                if self._is_valid_material(name):
                    choice_materials.append({
                        'name': name,
                        'category': self._categorize_item(name),
                        'quantity': quantity,
                        'priority': self._get_material_priority(name)
                    })
        
        # Select the best choice, preferring materials we've already chosen
        if choice_materials:
            # First, check if we've already chosen any of these materials
            already_chosen = [mat for mat in choice_materials if mat['name'] in self.chosen_materials]
            
            if already_chosen:
                # Use a material we've already chosen, prefer the one we've used most
                best_choice = max(already_chosen, key=lambda x: self.chosen_materials[x['name']])
            else:
                # No previous choice, use priority-based selection
                best_choice = min(choice_materials, key=lambda x: x['priority'])
            
            # Track this choice for future consistency
            if best_choice['name'] not in self.chosen_materials:
                self.chosen_materials[best_choice['name']] = 0
            self.chosen_materials[best_choice['name']] += best_choice['quantity']
            
            # Remove priority key before returning
            del best_choice['priority']
            materials.append(best_choice)
                    
        return materials
        
    def _parse_shopping_section(self, section) -> List[Dict[str, any]]:
        """Parse a shopping list section"""
        materials = []
        
        # Look for list items and text content
        items = section.find_all(['li', 'p', 'div', 'strong', 'b'])
        
        # Also parse the raw text for cases where items aren't in structured elements
        full_text = section.get_text()
        text_lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        
        # Combine structured items with text lines
        all_text_sources = []
        for item in items:
            all_text_sources.append(item.get_text(strip=True))
        all_text_sources.extend(text_lines)
        
        for text in all_text_sources:
            if not text or len(text) < 5:
                continue
                
            # Try multiple regex patterns for quantity extraction
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
        
    def _parse_pandaria_style(self, soup: BeautifulSoup) -> List[Dict[str, any]]:
        """Parse Pandaria-style guides with inline herb mentions and priority lists"""
        materials = []
        
        # Get all text content
        full_text = soup.get_text()
        
        # Look for inline herb mentions like "20 x Green Tea Leaf"
        inline_patterns = [
            r'(\d+)\s*x\s*([A-Z][a-zA-Z\s\']+(?:Leaf|Cap|Poppy|Lily|weed))',
            r'(\d+)\s*([A-Z][a-zA-Z\s\']+(?:Leaf|Cap|Poppy|Lily|weed))'
        ]
        
        found_herbs = {}
        
        for pattern in inline_patterns:
            matches = re.finditer(pattern, full_text)
            for match in matches:
                quantity = int(match.group(1))
                name = match.group(2).strip()
                
                # Clean up the name
                name = self._clean_item_name(name)
                
                if self._is_valid_material(name) and 'herb' in name.lower() or any(suffix in name.lower() for suffix in ['leaf', 'cap', 'poppy', 'lily', 'weed']):
                    if name in found_herbs:
                        found_herbs[name] += quantity
                    else:
                        found_herbs[name] = quantity
        
        # Look for priority order mentions like "Green Tea Leaf > Silkweed > Rain Poppy > Snow Lily > Fool's Cap"
        priority_pattern = r'([A-Z][a-zA-Z\s\']+(?:Leaf|Cap|Poppy|Lily|weed))\s*>\s*([A-Z][a-zA-Z\s\']+(?:Leaf|Cap|Poppy|Lily|weed))'
        priority_matches = re.finditer(priority_pattern, full_text)
        
        # Extract herbs from priority list
        priority_herbs = []
        priority_text_matches = re.findall(r'([A-Z][a-zA-Z\s\']+(?:Leaf|Cap|Poppy|Lily|weed))', full_text)
        
        for herb_name in priority_text_matches:
            clean_name = self._clean_item_name(herb_name)
            if self._is_valid_material(clean_name) and clean_name not in priority_herbs:
                # Add to priority herbs if it looks like a Pandaria herb
                pandaria_herbs = ['green tea leaf', 'silkweed', 'rain poppy', 'snow lily', "fool's cap"]
                if any(pandaria_herb in clean_name.lower() for pandaria_herb in pandaria_herbs):
                    priority_herbs.append(clean_name)
        
        # Create materials from found herbs
        for name, quantity in found_herbs.items():
            materials.append({
                'name': name,
                'category': self._categorize_item(name),
                'quantity': quantity
            })
        
        # Add priority herbs with estimated quantities if not already found
        estimated_quantities = {
            'Green Tea Leaf': 100,  # Most commonly used
            'Silkweed': 50,
            'Rain Poppy': 30,
            'Snow Lily': 20,
            "Fool's Cap": 20
        }
        
        for herb in priority_herbs:
            if herb not in found_herbs:
                # Estimate quantity based on herb type
                estimated_qty = 50  # Default
                for est_herb, qty in estimated_quantities.items():
                    if est_herb.lower() in herb.lower():
                        estimated_qty = qty
                        break
                        
                materials.append({
                    'name': herb,
                    'category': self._categorize_item(herb),
                    'quantity': estimated_qty
                })
                
        return materials
        
    def _clean_item_name(self, name: str) -> str:
        """Clean up item names by removing unwanted text"""
        # Remove common unwanted patterns
        name = re.sub(r'\([^)]*\)', '', name)  # Remove parentheses content
        name = re.sub(r'\[[^\]]*\]', '', name)  # Remove brackets content
        name = re.sub(r'(recipe|skill|level|point).*', '', name, flags=re.I)  # Remove recipe info
        name = re.sub(r'x\d+$', '', name)  # Remove trailing x numbers
        
        # Handle choice text patterns more comprehensively
        # Look for patterns like "Golden Sansam / 14x Dreamfoil / 14x Mountain Silversage (you only need 14 from one)"
        if '/' in name and ('only need' in name.lower() or 'choose' in name.lower() or 'one' in name.lower()):
            # Split on / and take the first option, clean up quantity
            first_choice = name.split('/')[0].strip()
            # Extract just the item name if it has quantity info
            choice_match = re.search(r'(\d+x\s*)?(.+)', first_choice)
            if choice_match:
                name = choice_match.group(2).strip()
            else:
                name = first_choice
        
        # Handle choice text like "and 15xAzshara's VeilOR15xNightstoneand 15xTwilight Jasmine"
        elif 'OR' in name or ' or ' in name.lower():
            name = re.split(r'\s+OR\s+|\s+or\s+', name, flags=re.I)[0]
            
        # Remove "and XXx" patterns that indicate additional choices
        name = re.sub(r'and\s+\d+x\w+.*', '', name, flags=re.I)
        
        # Remove trailing conjunctions and numbers
        name = re.sub(r'\s+(and|or)\s*.*', '', name, flags=re.I)
        
        # Remove explanatory text in parentheses at the end
        name = re.sub(r'\s*\([^)]*\)\s*$', '', name)
        
        name = re.sub(r'\s+', ' ', name)  # Normalize whitespace
        
        return name.strip()
        
    def _is_valid_material(self, name: str) -> bool:
        """Check if an item name represents a valid crafting material"""
        if not name or len(name) < 3:
            return False
            
        # Skip obvious non-materials
        skip_words = ['recipe', 'skill', 'level', 'point', 'guide', 'section', 
                     'total', 'cost', 'gold', 'silver', 'copper', 'requires',
                     'you should', 'prioritize', 'potions', 'that use']
        
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
    
    def scrape_expansion(self, expansion: str) -> str:
        """Override to reset chosen materials for each expansion"""
        self.chosen_materials = {}  # Reset for each expansion
        return super().scrape_expansion(expansion)


def main():
    parser = argparse.ArgumentParser(description='Scrape WoW Alchemy materials from wow-professions.com')
    parser.add_argument('--expansion', '-e', type=str, 
                       help='Specific expansion to scrape (e.g., vanilla, outland, northrend)')
    parser.add_argument('--output', '-o', type=str, default='../auctionator-shopping-lists/alchemy.txt',
                       help='Output filename (default: ../auctionator-shopping-lists/alchemy.txt)')
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