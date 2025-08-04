"""
Build all possible 16-rank OP teams of a given stat with at least 3 level-8 characters, one level 7/8 character,
and at least one character with an inherent ability or special card that allows them to play from reserve.

Author: Joe Filippazzo
Date: August 1, 2025

To run:
    from op_teams import make_overpower_teams
    csvfile = 'data/characters.csv'
    make_overpower_teams(csvfile, 'Strength')
"""

import csv


def make_all_teams():
    """
    Quickly make all possible teams and save to CSV
    """
    stats = ['Energy', 'Fighting', 'Strength', 'Intellect']
    for stat in stats:
        make_overpower_teams(stat, save=True)


def make_overpower_teams(stat_name, csvfile='data/characters.csv', save=False):
    """
    Wrapper function to run everything
    
    Parameters
    ----------
    csvfile: str
        The path to the CSV file
    stat_name: str
        TThe primary stat to use, ['Energy', 'Fighting', 'Strength', 'Intellect']
    save: NoneType, str
        The filename of the CSV file to save
    """
    # Import data and make dict
    chars = import_characters(csvfile)
    
    # Build the teams
    valid_teams = build_valid_teams(chars, stat_name.capitalize(), show=False)
    
    # Print and/or save to CSV file
    show_teams_table(valid_teams, chars, save=save, filename=f"teams/{stat_name}_teams.txt")


def import_characters(file='data/characters.csv'):
    """
    Imports data from a CSV file with columns 'Character', 'Energy', 'Fighting', 'Strength', 'Intellect', 'Threat', and 'Special'
    and loads it into a dict
    
    Parameters
    ----------
    file: str
        Path to the CSV file
    
    Returns
    -------
    dict
        The dict of characters and stats
    """
    chars = {}

    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['Character']
            stats = [
                int(row['Energy']),
                int(row['Fighting']),
                int(row['Strength']),
                int(row['Intellect']),
                row['Threat'],
                row['Special'].strip()
            ]
            chars[name] = stats
    
    return chars


from itertools import combinations


def build_valid_teams(chars, stat_name, include=None, low_stat=7, show=True):
    """
    Builds all valid 16-rank teams from the given character dictionary in the specified stat.

    Parameters
    ----------
    chars: dict
        The dictionary of characters
    stat_name: str
        The primary stat to use, ['Energy', 'Fighting', 'Strength', 'Intellect']
    include: list or set of str, optional
        Character names that must be included in every team

    Returns
    -------
    list of tuples
        Each tuple contains (team_names, total_stat_sum)
    """
    stat_index_map = {
        "Energy": 0,
        "Fighting": 1,
        "Strength": 2,
        "Intellect": 3
    }

    if stat_name not in stat_index_map:
        raise ValueError(f"Invalid stat name '{stat_name}'. Choose from: {list(stat_index_map)}")

    stat_idx = stat_index_map[stat_name]
    include = set(include) if include else set()
    valid_teams = []

    with_8 = [(name, stats) for name, stats in chars.items() if stats[stat_idx] == 8]
    with_7_or_more = [(name, stats) for name, stats in chars.items() if stats[stat_idx] >= low_stat]

    for trio in combinations(with_8, 3):
        trio_names = {c[0] for c in trio}

        for fourth in with_7_or_more:
            if fourth[0] in trio_names:
                continue

            team = list(trio) + [fourth]

            total = sum(sum(char[1][:4]) for char in team)
            if total > 76:
                continue

            specials = [char[1][5].strip() != '' for char in team]
            if not any(specials):
                continue

            team_names = {char[0] for char in team}
            if not include.issubset(team_names):
                continue

            names = tuple(char[0] for char in team)
            valid_teams.append((names, total))

    if show:
        show_teams_table(valid_teams, chars, save=False, name=stat_name)

    else:
        return valid_teams


def show_teams_table(teams, chars, save=False, filename='valid_teams.csv', name='potential'):
    """
    Print or save teams to a CSV table
    
    Parameters
    ----------
    teams: list
        The list of teams 
    chars: dict
        The dictionary of characters
    save: bool
        Save to CSV file
    filename: str
        The filename of the CSV file to save
    """
    # Prepare team data with formatted character names
    formatted_teams = []
    for team, total in teams:
        row = []
        for char in team:
            stats = chars[char][:4]
            special = chars[char][5].strip()
            display_name = char.replace('_', ' ').title().replace('(V)', '').replace('(H)', '')
            stat_str = f"[{', '.join(str(s) for s in stats)}]"
            if special:
                display_name += f" {stat_str} ({special})"
            else:
                display_name += f" {stat_str}"
            row.append(display_name)
        row.append(str(total))
        formatted_teams.append(row)

    # Headers
    headers = ['Character 1', 'Character 2', 'Character 3', 'Character 4', 'Total']
    num_columns = len(headers)
    col_widths = [len(h) for h in headers]

    # Determine max width for each column
    for row in formatted_teams:
        for i in range(num_columns):
            col_widths[i] = max(col_widths[i], len(row[i]))

    # Build the header and separator
    header_line = "  ".join(
        f"{headers[i]:<{col_widths[i]}}" if i < 4 else f"{headers[i]:>{col_widths[i]}}"
        for i in range(num_columns)
    )
    separator_line = "=" * len(header_line)

    # Create all output lines
    lines = []
    lines.append(header_line)
    lines.append(separator_line)
    for row in formatted_teams:
        line = "  ".join(
            f"{row[i]:<{col_widths[i]}}" if i < 4 else f"{row[i]:>{col_widths[i]}}"
            for i in range(num_columns)
        )
        lines.append(line)

    # Print or save to file
    output = "\n".join(lines)
    if save:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(output + "\n")
        print(f"✅ Exported {len(teams)} teams to '{filename}'.")
    else:
        print(output)
        print(f"\n{len(teams)} {name} teams found!")
