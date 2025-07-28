#!/usr/bin/env python3
"""
Master script to scrape all target professions
Runs individual profession scrapers with proper rate limiting
"""

import subprocess
import sys
import time
import argparse
from pathlib import Path

# Target professions
PROFESSIONS = ['alchemy', 'blacksmithing', 'engineering', 'leatherworking']

def run_profession_scraper(profession: str, expansion: str = None, rate_limit: float = 2.0):
    """
    Run the scraper for a specific profession
    
    Args:
        profession: Name of the profession to scrape
        expansion: Specific expansion (None for all)
        rate_limit: Rate limit between requests
    """
    script_name = f"scrape_{profession}.py"
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"Error: Scraper script {script_name} not found")
        return False
        
    # Build command
    cmd = [sys.executable, str(script_path), '--rate-limit', str(rate_limit)]
    
    if expansion:
        cmd.extend(['--expansion', expansion])
        
    print(f"Running {profession} scraper...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 minute timeout
        
        if result.returncode == 0:
            print(f"✓ {profession.title()} scraping completed successfully")
            if result.stdout:
                print(f"  Output: {result.stdout.strip()}")
        else:
            print(f"✗ {profession.title()} scraping failed")
            if result.stderr:
                print(f"  Error: {result.stderr.strip()}")
                
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"✗ {profession.title()} scraping timed out")
        return False
    except Exception as e:
        print(f"✗ {profession.title()} scraping failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Scrape all WoW professions from wow-professions.com')
    parser.add_argument('--expansion', '-e', type=str, 
                       help='Specific expansion to scrape for all professions')
    parser.add_argument('--profession', '-p', type=str, choices=PROFESSIONS,
                       help='Scrape only a specific profession')
    parser.add_argument('--rate-limit', '-r', type=float, default=2.0,
                       help='Rate limit between requests in seconds (default: 2.0)')
    parser.add_argument('--delay', '-d', type=float, default=5.0,
                       help='Delay between profession scrapers in seconds (default: 5.0)')
    
    args = parser.parse_args()
    
    if args.profession:
        professions_to_scrape = [args.profession]
    else:
        professions_to_scrape = PROFESSIONS
        
    print(f"Starting profession scraping for: {', '.join(professions_to_scrape)}")
    if args.expansion:
        print(f"Target expansion: {args.expansion}")
    else:
        print("Target: All expansions")
        
    print(f"Rate limit: {args.rate_limit}s between requests")
    print(f"Delay between professions: {args.delay}s")
    print("-" * 50)
    
    successful = []
    failed = []
    
    for i, profession in enumerate(professions_to_scrape):
        # Add delay between professions (except for the first one)
        if i > 0:
            print(f"Waiting {args.delay}s before next profession...")
            time.sleep(args.delay)
            
        success = run_profession_scraper(profession, args.expansion, args.rate_limit)
        
        if success:
            successful.append(profession)
        else:
            failed.append(profession)
            
    print("-" * 50)
    print("Scraping Summary:")
    print(f"✓ Successful: {', '.join(successful) if successful else 'None'}")
    print(f"✗ Failed: {', '.join(failed) if failed else 'None'}")
    
    if failed:
        print(f"\nFailed professions can be re-run individually:")
        for profession in failed:
            print(f"  python scrape_{profession}.py")
            
    return 0 if not failed else 1

if __name__ == "__main__":
    sys.exit(main())