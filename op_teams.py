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
from collections import Counter
import urllib.parse
import urllib.parse
import urllib.parse
import tempfile
import webbrowser
import urllib.parse
from html import escape


def display_teams_with_links(teams, chars):
    """
    Displays valid teams in an HTML table with clickable character names and stats.
    Opens the HTML page in the default web browser.

    Parameters
    ----------
    teams : list of tuples
        Each tuple is (character_names, total_stat_sum)
    chars : dict
        Dictionary of character stats {name: [F, E, S, I, total, ...]}
    """
    html = """
    <html>
    <head>
        <title>Valid Teams</title>
        <style>
            body { font-family: Arial, sans-serif; }
            table { border-collapse: collapse; margin: 20px; line-height: 1.5em; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
            td a { text-decoration: none; font-weight: bold; }
            .stat-line { font-size: 0.9em; color: #555; }
        </style>
    </head>
    <body>
    <h2>Valid Teams</h2>
    <table>
        <tr>
            <th>#</th><th>Character 1</th><th>Character 2</th><th>Character 3</th><th>Character 4</th><th>Total</th>
        </tr>
    """.replace('Teams<', f'Teams ({len(teams)})<')
    for idx, (names, total) in enumerate(teams):
        html += f"<tr><td>{idx + 1}</td>"
        for name in names:
            stats = chars[name]
            stat_line = f"[{stats[0]}, {stats[1]}, {stats[2]}, {stats[3]}]"  # [E, F, S, I]
            special_line = f"<br>{stats[-1]}" if stats[-1] != '' else ''
            url = f"https://www.ccgtrader.net/search?g=OVP&page=1&q={urllib.parse.quote(name)}"
            html += f"<td><a href='{url}' target='_blank'>{escape(name)}</a><br><span class='stat-line'>{stat_line}{special_line}</span></td>"
        html += f"<td>{total}</td></tr>"

    html += """
    </table>
    </body>
    </html>
    """

    # Write HTML to a temp file and open
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html", encoding="utf-8") as f:
        f.write(html)
        webbrowser.open(f"file://{f.name}")


def card_search(query):
    """
    Opens a CCGTrader search for OverPower cards using the given query string.

    Parameters
    ----------
    query : str
        The card name or keyword to search for.
    """
    base_url = "https://www.ccgtrader.net/search"
    params = {"g": "OVP", "page": "1", "q": query}
    full_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    webbrowser.open(full_url)


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
            name = row['Character'].replace(' (V)', '').replace(' (H)', '')
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

def build_valid_teams(chars, stat_name, include=None, exclude=None, stats=(8, 8, 8, 7), active_reserve=True, show=True):
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
    exclude: list or set of str, optional
        Character names that must not be included in any team
    stats: list
        The list of minimum levels for the given stat
    active_reserve: bool
        Require at least one character that can play from reserve
    show: bool
        Print the results

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
    exclude = exclude or []
    filtered_chars = {name: stats for name, stats in chars.items() if name not in exclude}

    if len(stats) != 4:
        raise ValueError("'stats' must be a list of 4 integers.")

    required = Counter(stats)

    with_8 = [c for c in filtered_chars.items() if c[1][stat_idx] == 8]
    with_7 = [c for c in filtered_chars.items() if c[1][stat_idx] == 7]
    with_6 = [c for c in filtered_chars.items() if c[1][stat_idx] == 6]

    valid_teams = []

    for eights in combinations(with_8, required[8]):
        e8_names = {c[0] for c in eights}
        pool_7 = [c for c in with_7 if c[0] not in e8_names]
        if required[7] > len(pool_7):
            continue

        for sevens in combinations(pool_7, required[7]):
            e7_names = e8_names | {c[0] for c in sevens}
            pool_6 = [c for c in with_6 if c[0] not in e7_names]
            if required[6] > len(pool_6):
                continue

            for sixes in combinations(pool_6, required[6]):
                team = list(eights) + list(sevens) + list(sixes)
                names = [c[0] for c in team]

                if not include.issubset(names):
                    continue

                total = sum(sum(char[1][:4]) for char in team)
                if total > 76:
                    continue

                if active_reserve:
                    if not any(char[1][5].strip() != '' for char in team):
                        continue

                valid_teams.append((tuple(names), total))

    if show:
        # show_teams_table(valid_teams, chars, save=False, name=stat_name)
        display_teams_with_links(valid_teams, chars)

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
