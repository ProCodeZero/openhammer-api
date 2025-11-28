import xml.etree.ElementTree as ET
import json
from pathlib import Path

def parse_catalogue(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    ns = {'bs': 'http://www.battlescribe.net/schema/catalogueSchema'}
    
    # Extract faction from catalogue name
    catalogue_name = root.get('name', '')
    faction = extract_faction(catalogue_name)
    
    units = []
    
    shared_entries = root.find('.//bs:sharedSelectionEntries', ns)
    
    if shared_entries is not None:
        for unit in shared_entries.findall('.//bs:selectionEntry[@type="model"]', ns):
            unit_data = {
                'name': unit.get('name'),
                'id': unit.get('id'),
                'faction': faction,
                'points': None,
                'stats': {},
                'invuln_save': None,
                'weapons': {
                    'ranged': [],
                    'melee': []
                },
                'abilities': [],
                'special_rules': [],
                'keywords': []
            }
            
            # Get points cost
            cost = unit.find('.//bs:cost[@name="pts"]', ns)
            if cost is not None:
                unit_data['points'] = int(float(cost.get('value')))
            
            # Get unit stats
            for profile in unit.findall('.//bs:profile[@typeName="Unit"]', ns):
                for char in profile.findall('.//bs:characteristic', ns):
                    stat_name = char.get('name')
                    stat_value = char.text
                    unit_data['stats'][stat_name] = stat_value
            
            # Get invulnerable save
            for info_link in unit.findall('.//bs:infoLink', ns):
                link_name = info_link.get('name', '')
                if 'Invulnerable' in link_name:
                    unit_data['invuln_save'] = link_name
            
            # Get special rules
            for info_link in unit.findall('.//bs:infoLink[@type="rule"]', ns):
                rule_name = info_link.get('name')
                if rule_name and rule_name != 'Invulnerable Save':
                    unit_data['special_rules'].append(rule_name)
            
            # Get ranged weapons
            for weapon in unit.findall('.//bs:profile[@typeName="Ranged Weapons"]', ns):
                weapon_data = {'name': weapon.get('name')}
                for char in weapon.findall('.//bs:characteristic', ns):
                    weapon_data[char.get('name')] = char.text
                unit_data['weapons']['ranged'].append(weapon_data)
            
            # Get melee weapons
            for weapon in unit.findall('.//bs:profile[@typeName="Melee Weapons"]', ns):
                weapon_data = {'name': weapon.get('name')}
                for char in weapon.findall('.//bs:characteristic', ns):
                    weapon_data[char.get('name')] = char.text
                unit_data['weapons']['melee'].append(weapon_data)
            
            # Get abilities
            for ability in unit.findall('.//bs:profile[@typeName="Abilities"]', ns):
                ability_data = {
                    'name': ability.get('name'),
                    'description': ability.find('.//bs:characteristic[@name="Description"]', ns).text if ability.find('.//bs:characteristic[@name="Description"]', ns) is not None else None
                }
                unit_data['abilities'].append(ability_data)
            
            # Get keywords from categoryLinks
            for category in unit.findall('.//bs:categoryLink', ns):
                keyword = category.get('name')
                if keyword:
                    unit_data['keywords'].append(keyword)
            
            # Only add if it has stats
            if unit_data['stats']:
                units.append(unit_data)
    
    return units

def extract_faction(catalogue_name):
    """Extract faction name from catalogue name"""
    if ' - ' in catalogue_name:
        parts = catalogue_name.split(' - ')
        return parts[-1].strip()
    return catalogue_name.strip()

# Parse and save to JSON
units = parse_catalogue('data/BSData/Imperium - Adeptus Custodes.cat')

# Create json directory
Path('data/json').mkdir(parents=True, exist_ok=True)

# Save to file
with open('data/json/Imperium_-_Adeptus_Custodes.json', 'w', encoding='utf-8') as f:
    json.dump(units, f, indent=2, ensure_ascii=False)

print(f"Saved {len(units)} units to data/json/Imperium_-_Adeptus_Custodes.json")