# Poker League Analytics Platform

[![Live Rankings](https://img.shields.io/badge/live-rankings-orange.svg)](https://www.offsuitpokerleague.com/brookes-top-mates-player-rankings)

> **Production Deployment**: This analytics platform powers the official player rankings for [Offsuit Poker League](https://www.offsuitpokerleague.com/brookes-top-mates-player-rankings), a sweepstakes league running No-Limit Texas Hold'em tournaments across multiple venues in the Milwaukee metropolitan area.

## 📊 Core Features

- **TrueSkill™ Rankings**
  - Main official ranking system using Microsoft's unbiased Bayesian algorithm
  - Same system used for Xbox Live competitive matchmaking
  - Specifically tuned for poker tournaments

- **High-Performance Architecture**
  - Lightning-fast response times through smart caching strategy
  - Leaderboards recalculate only when new tournament data arrives
  - Resource-efficient enough to run on Azure free tier

- **Intelligent Player Tracking**
  - Adaptive name disambiguation system
  - Network analysis for player communities
  - Cross-venue performance tracking

## 🌐 Live Implementation

- **Public Dashboard**: [Analytics Dashboard](https://jff97.github.io/PokerAnalyzerDisplayWebsite/)
- **Frontend Code**: [PokerAnalyzerDisplayWebsite](https://github.com/jff97/PokerAnalyzerDisplayWebsite)
- **API Base URL**: [https://api.johnfoxweb.com/](https://api.johnfoxweb.com/)

## 🛠 Technical Stack

- **Backend**: Python 3.8+, Flask, Azure Cloud
- **Database**: Azure Cosmos DB with intelligent caching
- **Analytics**: NetworkX, Pandas, NumPy