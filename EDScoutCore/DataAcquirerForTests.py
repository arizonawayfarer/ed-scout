import os
import sys
import glob
import pathlib
import json

import BodyAppraiser


def generate_key(body_info):

    # main_type = StarType | PlanetClass
    main_type = None
    specific_type = None
    mass = None
    terraform_state = None
    if "StarType" in body_info:
        #print(f"Star: {body_info['BodyName']}")
        main_type = 'Star'
        specific_type = BodyAppraiser.encode_star_type(body_info)
    else:
        # Planet
        #print(f"Planet: {body_info['BodyName']}")
        main_type = 'Planet'
        specific_type = BodyAppraiser.encode_body_type(body_info)

    if "MassEM" in body_info:
        mass = body_info['MassEM']
    else:
        mass = 0  # belts don't have a mass attribute

    terraform_state = None
    if 'TerraformState' in body_info and len(body_info['TerraformState']) > 0:
        terraform_state = BodyAppraiser.encode_terraform_state(body_info['TerraformState'])

    options = {
        'haveMapped': True,  # Always indicate we mapped it so we can tell the max worth
        'efficiencyBonus': True,
        'isFirstDiscoverer': not body_info['WasDiscovered'],
        'isFirstMapper': not body_info['WasMapped'],
    }

    return f"{main_type}-{specific_type}-{terraform_state}-{body_info['WasDiscovered']}-{body_info['WasMapped']}"


def test_acquire_scan_data_from_journals():
    journal_file_pattern = "Journal*.log"
    journal_path = os.path.join(str(pathlib.Path.home()), "Saved Games\\Frontier Developments\\Elite Dangerous")
    search_pattern = os.path.join(journal_path, journal_file_pattern)
    print(f"Searching with '{search_pattern}'")
    journal_files = glob.glob(search_pattern)
    print(f"Found {len(journal_files)} journals")

    scan_lines = []
    for journal_file in journal_files:
        with open(journal_file, "r", encoding='UTF-8') as journal:
            relevant_lines = [line for line in journal.readlines() if '"Scan"' in line]
            print(f"{len(relevant_lines)} found in {journal_file}")
            scan_lines.extend(relevant_lines)

    uniques = {}
    for line in scan_lines:
        data = json.loads(line)
        key = generate_key(data)

        if "MassEM" in data:
            mass = data['MassEM']
        else:
            mass = 0  # belts don't have a mass attribute

        if key not in uniques:
            uniques[key] = []
        uniques[key].append((mass, data))

    extremes_at_uniques = []
    for unique in uniques.values():
        min_value = sys.float_info.max
        min_data = None
        max_value = -sys.float_info.max
        max_data = None
        value_found = False
        for (mass, data) in unique:
            if mass < min_value:
                value_found = True
                min_value = mass
                min_data = data
            if mass > max_value:
                value_found = True
                max_value = mass
                max_data = data
        if value_found:
            min_example = json.dumps(min_data)
            extremes_at_uniques.append(min_example)
            if min_value != max_value:
                extremes_at_uniques.append(json.dumps(max_data))
            print(f"Min: {min_value}, Max: {max_value} from {len(unique)} entries")
        else: # mass-less
            (mass, data) = unique[0]
            extremes_at_uniques.append(json.dumps(data))

    with open("..\\ExampleData\\ExampleScans.json", "w") as output:
        output.writelines(s + '\n' for s in extremes_at_uniques)


if __name__ == '__main__':
    test_acquire_scan_data_from_journals()