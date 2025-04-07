# Data-Driven Decision Making: A/B Testing Platform

An advanced experimental framework for optimizing user conversion through statistically rigorous A/B testing methodologies. This system enables educational institutions to quantifiably measure the impact of different engagement strategies on applicant completion rates.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-green.svg)](https://www.mongodb.com/)
[![Dash](https://img.shields.io/badge/Dash-2.6+-orange.svg)](https://dash.plotly.com/)

Demographics tab
![UI-Demographics Tab](screenshots/screenshot1.png)
Experiment Tab
![UI-Experiment Tab](screenshots/screenshot2.png)

## Overview

This platform implements a comprehensive A/B testing framework specifically designed for educational institutions seeking to optimize their applicant conversion funnel. The system measures the effectiveness of email reminders on admissions quiz completion rates through a controlled experimental design.

The architecture follows a clean separation of concerns with dedicated modules for:

- Database interactions (`MongoRepository`)
- Statistical analysis (`StatsBuilder`)
- Data visualization (`GraphBuilder`)
- Experimental design (`Experiment`)
- Interactive dashboard presentation (Dash application)

## Technical Architecture
### Repository Structure
```
ab-testing-platform/
├── ab_test.py                  # Core experimental framework
│   ├── class Reset             # Database cleanup utilities
│   └── class Experiment        # Experiment execution and analysis
├── business.py                 # Business logic and visualization
│   ├── class GraphBuilder      # Data visualization components
│   └── class StatsBuilder      # Statistical analysis utilities
├── database.py                 # Data access layer
│   └── class MongoRepository   # MongoDB interaction patterns
├── app.py                      # Interactive Dash application
│   ├── app.layout              # Dashboard UI structure
│   └── app.callbacks           # Interactive UI event handlers
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
└── LICENSE                     # MIT License
```

### Key Components

#### `ab_test.py`
Contains the core experimental framework with two primary classes:
- `Experiment`: Manages the experiment lifecycle including user assignment to control/treatment groups and result calculation
- `Reset`: Handles database cleanup between experimental runs

#### `database.py`
Implements the data access layer through `MongoRepository`, which encapsulates all MongoDB interactions including:
- Geographic data enrichment with ISO country code normalization
- Age calculation from birthdate fields
- Education level categorization with custom sorting logic
- Time-series aggregation for daily incomplete quiz metrics
- Contingency table generation for statistical analysis

#### `business.py`
Houses business logic with two key classes:
- `GraphBuilder`: Creates interactive visualizations for demographic analysis and experimental results
- `StatsBuilder`: Performs statistical calculations including:
  - Chi-square tests for independence
  - Power analysis for sample size determination
  - Probability modeling for experimental duration planning

#### `app.py`
Implements the interactive Dash application with:
- Responsive visualizations based on user selections
- Dynamic experiment parameter configuration
- Real-time statistical analysis and result presentation

## Statistical Methodology

The platform employs rigorous statistical methods to ensure experimental validity:

1. **Power Analysis**: Dynamically calculates required sample sizes based on desired effect size detection thresholds
2. **Random Assignment**: Implements stratified random sampling to ensure balanced and unbiased group assignments
3. **Chi-Square Analysis**: Tests for statistical independence between treatment groups and completion rates
4. **Probability Modeling**: Utilizes historical data to forecast acquisition rates and optimal experiment duration

## Business Applications

### Marketing Optimization

The platform enables the marketing department to:

- Quantify the ROI of different communication strategies
- Optimize resource allocation for maximum conversion impact
- Test messaging effectiveness before full-scale deployment
- Build data-driven attribution models for the conversion funnel

### Admissions Enhancement

For educational institutions, the system provides:

- Clear metrics on applicant engagement touchpoints
- Demographic insights into applicant behaviors across different segments
- Statistical evidence for intervention effectiveness
- Predictive capabilities for completion rate optimization

## Getting Started

### Prerequisites

- Python 3.9+
- MongoDB 4.4+
- Required Python packages: `pandas`, `pymongo`, `dash`, `plotly`, `scipy`, `statsmodels`, `numpy`, `country_converter`

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ab-testing-platform.git

# Install dependencies
pip install -r requirements.txt

# Configure MongoDB connection in database.py if needed

# Run the application
python display2.py
```

## Dashboard Walkthrough

The interactive dashboard provides several key features:

1. **Demographic Analysis**: Explore applicant demographics through interactive visualizations:
   - Geographic distribution via choropleth map
   - Age distribution histogram
   - Education level breakdown

2. **Experiment Configuration**:
   - Select desired effect size detection threshold
   - Configure experiment duration
   - View probability forecasts for observation acquisition

3. **Experiment Execution**:
   - Initiate experiment with configured parameters
   - View real-time results with statistical analysis
   - Interpret chi-square test results for statistical significance

## Future Enhancements

- Multi-variant testing capabilities
- Bayesian statistical models for continuous monitoring
- Segment-specific analysis for targeted interventions
- Automated email integration for treatment deployment
- A/A testing capabilities for system validation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*Developed with precision and expertise in educational analytics and conversion optimization.*