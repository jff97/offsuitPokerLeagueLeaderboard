from typing import List, Tuple, Dict, Any, Optional
from collections import defaultdict
import trueskill
import pandas as pd
from offsuit_analyzer.datamodel import Round
from offsuit_analyzer import persistence
from offsuit_analyzer.config import config


class PlayerRating:
    def __init__(self, name: str, rating: trueskill.Rating):
        self.name = name
        self.rating = rating

    @property
    def conservative_score(self) -> float:
        return self.rating.mu - 3 * self.rating.sigma

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "mu": self.rating.mu,
            "sigma": self.rating.sigma,
            "conservative": self.conservative_score,
        }


class TrueSkillEngine:
    def __init__(
        self,
        mu: Optional[float] = None,
        sigma: Optional[float] = None,
        beta: Optional[float] = None,
        tau: Optional[float] = None,
        draw_probability: Optional[float] = None,
    ):
        env_kwargs = {}
        if mu is not None:
            env_kwargs["mu"] = mu
        if sigma is not None:
            env_kwargs["sigma"] = sigma
        if beta is not None:
            env_kwargs["beta"] = beta
        if tau is not None:
            env_kwargs["tau"] = tau
        if draw_probability is not None:
            env_kwargs["draw_probability"] = draw_probability

        self.env = trueskill.TrueSkill(**env_kwargs)
        self.ratings: Dict[str, trueskill.Rating] = defaultdict(self.env.Rating)

    def process_round(self, round_results: List[Tuple[str, int]]):
        sorted_players = sorted(round_results, key=lambda x: x[1])
        teams = [[self.ratings[name]] for name, _ in sorted_players]
        ranks = [place - 1 for _, place in sorted_players]
        new_ratings = self.env.rate(teams, ranks=ranks)
        for (name, _), team_rating in zip(sorted_players, new_ratings):
            self.ratings[name] = team_rating[0]

    def process_multiple_rounds(
        self, rounds: List[Dict[str, Any]], sort_by_date_key: str = "date"
    ):
        rounds_sorted = sorted(rounds, key=lambda r: r.get(sort_by_date_key, ""))
        for round_data in rounds_sorted:
            results = [(p["name"], p["place"]) for p in round_data["results"]]
            self.process_round(results)

    def get_leaderboard(self) -> List[PlayerRating]:
        players = [
            PlayerRating(name, rating) for name, rating in self.ratings.items()
        ]
        return sorted(players, key=lambda p: p.conservative_score, reverse=True)

    def get_rating(self, player_name: str) -> trueskill.Rating:
        return self.ratings[player_name]

    def reset(self):
        self.ratings.clear()


def prepare_round_data(rounds: List[Round]) -> List[Dict[str, Any]]:
    """
    Convert a list of Round objects into a format consumable by TrueSkillEngine.
    """
    processed: List[Dict[str, Any]] = []

    for round_obj in rounds:
        # Inline extraction: sort by points descending, assign placement
        sorted_players = sorted(round_obj.players, key=lambda p: p.points, reverse=True)
        results = [(player.player_name, i + 1) for i, player in enumerate(sorted_players)]

        if results and round_obj.round_date:
            processed.append({
                "date": round_obj.round_date,
                "results": [{"name": n, "place": p} for n, p in results]
            })

    return processed


def print_leaderboard(leaderboard: List[PlayerRating], max_sigma: float = None) -> None:
    print("\nLeaderboard (ranked by conservative skill estimate):")
    print(f"{'Rank':<5} {'Name':<20} {'Conservative':>14} {'Mu':>8} {'Sigma':>8}")
    print("-" * 60)

    filtered = leaderboard
    if max_sigma is not None:
        filtered = [p for p in leaderboard if p.rating.sigma <= max_sigma]

    for rank, player in enumerate(filtered, start=1):
        r = player.rating
        print(
            f"{rank:<5} {player.name:<20} {player.conservative_score:14.2f} {r.mu:8.2f} {r.sigma:8.2f}"
        )

def leaderboard_to_dataframe(
    leaderboard: List[PlayerRating]) -> pd.DataFrame:
    data = []
    for rank, player in enumerate(leaderboard, start=1):
        r = player.rating
        data.append({
            "Rank": rank,
            "Name": player.name,
            "Conservative Ranking (Raw - 3*uncertainty)": round(player.conservative_score, 2),
            "Raw Ranking": round(r.mu, 2),
            "Uncertainty": round(r.sigma, 2),
        })

    return pd.DataFrame(data)

def build_trueskill_leaderboard(rounds: List[Round]):
    processed_rounds = prepare_round_data(rounds)

    engine = TrueSkillEngine(beta=config.BETA_TRUESKILL, draw_probability=0.0, tau=config.TAU_TRUESKILL)

    engine.process_multiple_rounds(processed_rounds)

    leaderboard = engine.get_leaderboard()
    df_trueskill = leaderboard_to_dataframe(leaderboard)
    return df_trueskill
