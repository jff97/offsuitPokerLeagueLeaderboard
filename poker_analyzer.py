import os
import pandas as pd
import re
from collections import defaultdict

def get_csv_files(folder_path):
    """Get list of all CSV files in the provided folder."""
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".csv")]

def parse_points(value):
    """Extract numeric points from a string like '21 points'."""
    match = re.search(r'\d+', str(value))
    return int(match.group()) if match else 0

def rank_players_by_round_points(df_round):
    """
    Given a DataFrame with players and their points for a single round,
    return a list of (player, percentage rank) for players who showed up.
    """
    df_round['Points'] = df_round.iloc[:, 1].apply(parse_points)
    df_round = df_round[df_round['Points'] > 0]  # Only players who participated

    if df_round.empty:
        return []

    df_round = df_round.sort_values(by='Points', ascending=False).reset_index(drop=True)
    df_round['Placement'] = df_round['Points'].rank(ascending=False, method='min').astype(int)
    total_players = len(df_round)

    results = []
    for _, row in df_round.iterrows():
        placement = row['Placement']
        pct_rank = round((1 - (placement - 1) / (total_players - 1)) * 100, 2) if total_players > 1 else 100.0
        results.append((row['Player'], pct_rank))

    return results

def process_csv(file_path):
    """Process a single CSV file and return a list of (player, percentage rank) tuples from all rounds."""
    df = pd.read_csv(file_path)
    df = df.rename(columns={df.columns[1]: "Player"})  # standardize name column
    rounds = [col for col in df.columns if "Round" in col]

    all_results = []
    for round_col in rounds:
        df_round = df[['Player', round_col]].copy()
        round_results = rank_players_by_round_points(df_round)
        all_results.extend(round_results)

    return all_results

def aggregate_results(all_results):
    """Aggregate all round results into a cumulative leaderboard."""
    player_stats = defaultdict(lambda: {'TotalPercent': 0, 'RoundsPlayed': 0})

    for player, pct_rank in all_results:
        player_stats[player]['TotalPercent'] += pct_rank
        player_stats[player]['RoundsPlayed'] += 1

    records = []
    for player, stats in player_stats.items():
        avg_pct = round(stats['TotalPercent'] / stats['RoundsPlayed'], 2)
        if stats['RoundsPlayed'] > 4:
            records.append({
            'Player': player,
            'RoundsPlayed': stats['RoundsPlayed'],
            'AveragePercentageRank': avg_pct
            })
        

    leaderboard = pd.DataFrame(records)
    leaderboard.sort_values(by='AveragePercentageRank', ascending=False, inplace=True)
    leaderboard.reset_index(drop=True, inplace=True)
    return leaderboard

def main():
    folder = input("Enter the folder path with CSV files: ").strip()
    if not os.path.isdir(folder):
        print("Invalid folder.")
        return

    all_results = []
    for csv_file in get_csv_files(folder):
        all_results.extend(process_csv(csv_file))

    leaderboard = aggregate_results(all_results)
    print("\nCumulative Leaderboard (based on average % rank):\n")
    print(leaderboard.to_string(index=False))

    output_path = os.path.join(folder, "cumulative_leaderboard.csv")
    leaderboard.to_csv(output_path, index=False)
    print(f"\nSaved to {output_path}")

if __name__ == "__main__":
    main()
