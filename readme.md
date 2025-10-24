# Poker League Analytics Platform

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Live Rankings](https://img.shields.io/badge/live-rankings-orange.svg)](https://www.offsuitpokerleague.com/brookes-top-mates-player-rankings)

> **Production Deployment**: This analytics platform powers the official player rankings for [Offsuit Poker League](https://www.offsuitpokerleague.com/brookes-top-mates-player-rankings), a sweepstakes league running No-Limit Texas Hold'em tournaments across multiple venues in the greater Milwaukee metropolitan area. The league offers free entry and awards prizes to top 5 players at the monthly championship tournament.

## 🌐 Public Analytics Dashboard

- **Independent Frontend Implementation**
  - Live Site: [Analytics Dashboard](https://jff97.github.io/PokerAnalyzerDisplayWebsite/)
  - Frontend Repository: [PokerAnalyzerDisplayWebsite](https://github.com/jff97/PokerAnalyzerDisplayWebsite)
  - Static site consuming public API endpoints
  - Completely decoupled from backend implementation

## 📊 Ranking Systems & Player Analytics

- **TrueSkill™ Rankings**
  - Main Offsuit Poker League official ranking system using Microsoft's unbiased Bayesian algorithm
  - Same system used for Xbox Live competitive videogame matchmaking
  - Accurately measures and adapts to player skill levels
  - Specifically tuned for texas holdum tournaments

- **Performance Metrics**
  - Players Outlasted %: Average percentage of players outlasted per tournament
  - In The Money (ITM) %: Tournament cash out rate (approx top 15-20%)
  - ROI Analysis: How profitable of a tournament player you would be with typical tournament payouts 
  - First Place %: Tournament victories

## 🎯 Technical Innovations & Achievements

- **Advanced Player Ranking**
  - Implemented and tuned Microsoft's TrueSkill™ algorithm for poker tournaments
  - Accurate skill measurement for Texas Holdum no limit which has a large amount of luck

- **Security Infrastructure**
  - Cloudflare reverse proxy implementation for API protection
  - Domain-specific access control
  - DDoS mitigation
  - Bot protection through request filtering

- **Intelligent Identity Management**
  - Developed adaptive name disambiguation system
  - Alerts administrators when new entries likely match existing players
  - Uses fuzzy matching and historical name analysis

- **High-Performance Architecture**
  - Lightning-fast response times through smart caching strategy
  - Leaderboards recalculate only when new tournament data arrives
  - Zero redundant processing
  - Minimized database interactions
  - Resource-efficient enough to run on Azure free tier API instance

- **Player Network Analysis System**
  - Weighted spring graph visualization shows strength of TrueSkill confidence
  - Connected communities indicate well-calibrated skill ratings through player overlap
  - Isolated communities highlight areas where ratings may need more cross-venue validation
  - Maps player migration patterns between venues for rating reliability analysis

## 🔌 API Endpoints
  - Base URL: [https://api.johnfoxweb.com/](https://api.johnfoxweb.com/)
  - Public Leaderboards:
    - TrueSkill Rankings: [/api/leaderboards/trueskill](https://api.johnfoxweb.com/api/leaderboards/trueskill)
    - Players Outlasted: [/api/leaderboards/percentile](https://api.johnfoxweb.com/api/leaderboards/percentile)
  - Admin Functions:
    - Refresh Rounds: [/api/admin/refreshrounds](https://api.johnfoxweb.com/api/admin/refreshrounds)
    - Refresh Legacy Data: [/api/admin/refreshlegacyrounds](https://api.johnfoxweb.com/api/admin/refreshlegacyrounds)

## 🛠 Technical Stack

- **Backend**: Python 3.8+, Flask
- **Database & Caching**: Azure Cosmos DB, In-memory caching
- **Analytics**: NetworkX, Pandas, NumPy
- **API Integration**: REST APIs, External Data Sources
- **Performance**: Multi-level caching, Query optimization
- **DevOps**: GitHub Actions, Azure Cloud

## 🏗 Architecture

The application follows a modular, service-oriented architecture:

```
offsuit_analyzer/
├── config.py         # Environment configuration and API keys
├── analytics/        # Player ranking algorithms and statistical analysis
├── data_service/     # Data ingestion and processing
├── datamodel/        # Core domain models for tournament and player data
├── persistence/      # Database interactions
├── name_tools/       # Player Identity disambiguation system
├── web/              # Web API and controllers
└── email_smtp_service/ # Automated notifications
```