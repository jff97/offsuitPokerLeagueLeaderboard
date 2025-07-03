import os  # for file and folder path operations
import pandas as pd  # for working with CSV files and DataFrames
import re  # for regex operations (parsing strings)
from collections import defaultdict  # for handling grouped data cleanly

def get_csv_files(folder_path):
    """Get list of all CSV files in the provided folder."""
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".csv")]

def parse_points(value):
    """Extract numeric points from a string like '21 points'."""
    match = re.search(r'\d+', str(value))  # find the first number in the string
    return int(match.group()) if match else 0  # return the number if found, otherwise 0

def extract_points_from_column(df):
    """Extract numeric points from the specified column and add as 'Points'."""
    df['Points'] = df.iloc[:, 1].apply(parse_points)
    return df

def sort_players_by_points(df):
    """Sort players by descending points and reset the index."""
    return df.sort_values(by='Points', ascending=False).reset_index(drop=True)

def assign_placements(df):
    """Assign placement ranks to players based on points with ties getting the same rank."""
    df['Placement'] = df['Points'].rank(ascending=False, method='min').astype(int)
    return df

def calculate_percentage_rank(placement, total_players):
    """Convert a placement rank into a percentage rank (higher is better)."""
    if total_players <= 1:
        return 100.0
    return round((1 - (placement - 1) / (total_players - 1)) * 100, 2)

def build_results_list(df):
    """Build and return a list of tuples (player, percentage rank)."""
    total_players = len(df)
    results = []
    for _, row in df.iterrows():
        pct_rank = calculate_percentage_rank(row['Placement'], total_players)
        results.append((row['Player'], pct_rank))
    return results

def rank_players_by_round_points(df_round):
    """
    Given a DataFrame with players and their points for a single round,
    return a list of (player, percentage rank) for players who showed up.
    """
    df_round = extract_points_from_column(df_round)

    if df_round.empty:
        return []

    df_round = sort_players_by_points(df_round)
    df_round = assign_placements(df_round)

    results = build_results_list(df_round)
    return results


def normalize_player_name(name):
    """Normalize player names:
    - Trim whitespace
    - Lowercase
    - Collapse multiple spaces into one
    - Remove non-alphanumeric characters except space
    """
    name = str(name).strip().lower()  # trim and lowercase
    name = re.sub(r'\s+', ' ', name)  # replace multiple spaces with one
    name = re.sub(r'[^a-z0-9 ]', '', name)  # remove non-alphanumeric chars excepC:\Users\jicfo\OneDrive\Documents\GitHub\pokerScraper\june2025\outputt space
    name = re.sub(r'\s+', ' ', name).strip()  # ensure single spacing again
    name = fix_special_name_cases(name)
    return name

def fix_special_name_cases(name):
    if "pyerre" in name:
        return "pyerre l"
    if "bonnie" in name:
        return "bonnie l"
    return name


def process_csv(file_path):
    """Process a single CSV file and return a list of (player, percentage rank) tuples from all rounds."""
    df = pd.read_csv(file_path)  # load CSV file into DataFrame
    df = df.rename(columns={df.columns[1]: "Player"})  # standardize name column to "Player"
    
    df['Player'] = df['Player'].apply(normalize_player_name)  # normalize all player names
    
    rounds = [col for col in df.columns if "Round" in col]  # find all round columns

    all_results = []
    for round_col in rounds:
        df_round = df[['Player', round_col]].copy()  # extract only player and round columns
        round_results = rank_players_by_round_points(df_round)  # rank for that round
        all_results.extend(round_results)  # accumulate results

    return all_results

def aggregate_results(all_results):
    """Aggregate all round results into a cumulative leaderboard."""
    player_stats = defaultdict(lambda: {'TotalPercent': 0, 'RoundsPlayed': 0})  # track total % and round count

    for player, pct_rank in all_results:
        player_stats[player]['TotalPercent'] += pct_rank  # sum of percentage ranks
        player_stats[player]['RoundsPlayed'] += 1  # count of rounds played

    records = []
    for player, stats in player_stats.items():
        avg_pct = round(stats['TotalPercent'] / stats['RoundsPlayed'], 2)  # average percentage rank
        if stats['RoundsPlayed'] > 4:  # only include players with more than 4 rounds
            records.append({
            'Player': player,
            'RoundsPlayed': stats['RoundsPlayed'],
            'AveragePercentageRank': avg_pct
            })

    leaderboard = pd.DataFrame(records)  # create DataFrame from summary
    leaderboard.sort_values(by='AveragePercentageRank', ascending=False, inplace=True)  # sort descending
    leaderboard.reset_index(drop=True, inplace=True)  # reset index for clean display
    return leaderboard

def main():
    folder = input("Enter the folder path with CSV files: ").strip()  # ask user for CSV folder path
    if not os.path.isdir(folder):  # check if valid directory
        print("Invalid folder.")
        return

    all_results = []
    for csv_file in get_csv_files(folder):  # iterate over all CSV files in folder
        all_results.extend(process_csv(csv_file))  # collect all player rankings

    leaderboard = aggregate_results(all_results)  # compute final leaderboard
    print("\nCumulative Leaderboard (based on average % rank):\n")
    print(leaderboard.to_string(index=False))  # pretty print leaderboard

    output_path = os.path.join(folder, "cumulative_leaderboard.csv")  # prepare output file path
    leaderboard.to_csv(output_path, index=False)  # save leaderboard to CSV
    print(f"\nSaved to {output_path}")  # notify user

if __name__ == "__main__":
    main()  # run the script
