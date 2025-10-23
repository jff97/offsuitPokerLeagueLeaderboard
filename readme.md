# Poker League Analytics Platform

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A sophisticated analytics and leaderboard platform that manages poker league statistics across multiple venues. This full-stack Python application leverages advanced algorithms for player ranking, performance analysis, and automated reporting.

## 🚀 Key Features

- **Advanced Player Analytics**
  - TrueSkill™-based player ranking system
  - ROI analysis and performance tracking
  - Network analysis for player interaction patterns
  - Weighted spring graph visualization for player relationships

- **Robust Data Management**
  - Azure Cosmos DB integration
  - Multi-source data ingestion (CSV, API, manual entry)
  - Automated data validation and cleaning
  - Historical data preservation and analysis

- **Smart Player Identity Management**
  - Adaptive name disambiguation system
  - Automated conflict detection
  - Player identity resolution across venues

- **Modern Web Interface**
  - Flask-based REST API
  - Real-time leaderboard updates
  - Administrative dashboard
  - Responsive design for mobile access

## 🛠 Technical Stack

- **Backend**: Python 3.8+, Flask
- **Database**: Azure Cosmos DB
- **Analytics**: NetworkX, Pandas, NumPy
- **API Integration**: REST APIs, External Data Sources
- **DevOps**: GitHub Actions, Azure Cloud

## 🏗 Architecture

The application follows a modular, service-oriented architecture:

```
offsuit_analyzer/
├── analytics/        # Statistical analysis and ranking algorithms
├── data_service/     # Data ingestion and processing
├── datamodel/        # Core domain models
├── persistence/      # Database interactions
├── name_tools/       # Identity management system
├── web/             # Web API and controllers
└── email_smtp_service/ # Automated notifications
```

## 🎯 Key Technical Achievements

- Implemented Microsoft's TrueSkill™ algorithm for accurate player ranking across diverse game formats
- Developed an adaptive name disambiguation system using fuzzy matching and historical data analysis
- Built a scalable data ingestion pipeline handling multiple venues and data formats
- Created a network analysis system for understanding player relationships and game dynamics

## 💡 Innovation Highlights

- **Smart Player Matching**: Advanced algorithms to track players across different venues and naming conventions
- **Network Analysis**: Visual and statistical analysis of player interactions and game dynamics
- **Automated Data Processing**: Intelligent systems for data validation, cleaning, and integration

## 📊 Data Analysis Capabilities

- Player performance tracking across multiple venues
- ROI calculation and trend analysis
- Player interaction network visualization
- Historical performance analysis

## 🔒 Security & Data Privacy

- Secure data handling with Azure Cosmos DB
- Role-based access control
- Data validation and sanitization
- Automated backup systems

## 🌐 Live API Endpoints

- Main Application: [https://api.johnfoxweb.com/](https://api.johnfoxweb.com/)
- Leaderboards:
  - TrueSkill Rankings: [/api/leaderboards/trueskill](https://api.johnfoxweb.com/api/leaderboards/trueskill)
  - Percentile Rankings: [/api/leaderboards/percentile](https://api.johnfoxweb.com/api/leaderboards/percentile)
- Admin Functions:
  - Refresh Rounds: [/api/admin/refreshrounds](https://api.johnfoxweb.com/api/admin/refreshrounds)
  - Refresh Legacy Data: [/api/admin/refreshlegacyrounds](https://api.johnfoxweb.com/api/admin/refreshlegacyrounds)

## 🚧 Future Enhancements

- Machine learning-based player skill prediction
- Advanced statistical analysis tools
- Enhanced visualization capabilities
- Mobile application development

---

*This project demonstrates expertise in full-stack development, data engineering, analytics, and cloud infrastructure, while solving complex real-world challenges in data management and analysis.*
