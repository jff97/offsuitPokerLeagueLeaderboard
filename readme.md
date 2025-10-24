# Poker League Analytics Platform

### 🏆 [View Live Trueskill Rankings For Offsuit Poker League 🔗](https://www.offsuitpokerleague.com/brookes-top-mates-player-rankings)

Production analytics platform powering Microsoft Trueskill player rankings for a Milwaukee-area No-Limit Texas Hold'em tournament league. Built with:

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Live Rankings](https://img.shields.io/badge/production-deployed-brightgreen.svg)](https://www.offsuitpokerleague.com/brookes-top-mates-player-rankings)

## 🌐 Public Analytics Dashboard

- **All deployed leaderboards and analytics**
  - Live Site: [Project Homepage](https://jff97.github.io/PokerAnalyzerDisplayWebsite/)
  - Multiple Leaderboard Views:
    - TrueSkill™ Rankings
    - Players Outlasted Rankings
    - ROI Performance Rankings
  - Player interaction weighted graph Visualizations
  - Player community connected/disconnected ness metrics
- **Independent Frontend Implementation**
  - Frontend Repository: [PokerAnalyzerDisplayWebsite](https://github.com/jff97/PokerAnalyzerDisplayWebsite)
  - Static site consuming public API endpoints
  - Completely decoupled from backend implementation
  - Architecture enables easy integration with alternative frontend implementations

## 📊 Ranking Systems & Player Analytics

- **TrueSkill™ Rankings**
  - Official Offsuit Poker League ranking system using Microsoft's unbiased Bayesian algorithm
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
    - TrueSkill Rankings: [/api/leaderboard/trueskill](https://api.johnfoxweb.com/api/leaderboard/trueskill)
    - Players Outlasted: [/api/leaderboard/percentile](https://api.johnfoxweb.com/api/leaderboard/percentile)
  - Admin Functions (Require Authorization):
    - Refresh Rounds: [/api/admin/refreshrounds](https://api.johnfoxweb.com/api/admin/refreshrounds)

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

## 💡 Featured Code Highlights

The following files showcase advanced software engineering principles and algorithmic implementations:

### Advanced Analytics & Machine Learning
- [`analytics/trueskill_analyzer.py`](offsuit_analyzer/analytics/trueskill_analyzer.py)
  - Custom implementation of Microsoft's TrueSkill™ Bayesian ranking system
  - Sophisticated player rating system with uncertainty quantification
  - Efficient batch processing of historical tournament data

### Network Analysis & Data Visualization
- [`analytics/player_weighted_spring_graph.py`](offsuit_analyzer/analytics/player_weighted_spring_graph.py)
  - Dynamic force-directed graph visualization using NetworkX
  - Weighted player interaction modeling
  - Color mapping based on TrueSkill ratings
  - Multi-threaded graph layout optimization

### Intelligent Name Management
- [`name_tools/adaptive_name_problem_detector.py`](offsuit_analyzer/name_tools/adaptive_name_problem_detector.py)
  - Fuzzy string matching with configurable thresholds
  - Adaptive name disambiguation system
  - Multi-stage name conflict resolution
  - Automated email notification system for detected conflicts

### Clean API Architecture
- [`web/controllers/leaderboard_controller.py`](offsuit_analyzer/web/controllers/leaderboard_controller.py) & [`web/services/leaderboard_service.py`](offsuit_analyzer/web/services/leaderboard_service.py)
  - Strict separation between API endpoints and business logic
  - Service layer completely independent of HTTP/REST concerns
  - Analytics systems decoupled from delivery mechanism
  - Could deploy analytics engine separately from API service