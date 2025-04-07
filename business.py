import math

import numpy as np
import plotly.express as px
import scipy
from database import MongoRepository

from statsmodels.stats.contingency_tables import Table2x2
from statsmodels.stats.power import GofChisquarePower
from ab_test import Experiment


class GraphBuilder:
    """Methods for building Graphs."""

    def __init__(self, repo=MongoRepository()):

        """init

        Parameters
        ----------
        repo : MongoRepository, optional
            Data source, by default MongoRepository()
        """
        self.repo = repo

    def build_nat_choropleth(self):

        """Creates nationality choropleth map.

        Returns
        -------
        Figure
        """
        # Fetch nationality data with percentages
        df_nationality = self.repo.get_nationality_value_counts(normalize=True)
        
        # Construct choropleth visualization
        fig = px.choropleth(
            data_frame=df_nationality,
            locations="country_iso3",
            color="count_pct",
            projection="natural earth",
            color_continuous_scale=px.colors.sequential.Oranges,
            title="Applicants: Nationality"
        )
        
        # Return completed visualization
        return fig
       

    def build_age_hist(self):

        """Create age histogram.

        Returns
        -------
        Figure
        """
        # Retrieve age distribution data
        ages = self.repo.get_ages()
        
        # Generate histogram visualization
        fig = px.histogram(
            x=ages, 
            nbins=20, 
            title="Applicants: Distribution of Ages"
        )
        
        # Configure axis presentation
        fig.update_layout(
            xaxis_title="Age", 
            yaxis_title="Frequency[count]"
        )
        
        # Return completed visualization
        return fig

    def build_ed_bar(self):

        """Creates education level bar chart.

        Returns
        -------
        Figure
        """
        # Extract education distribution as percentages
        education = self.repo.get_ed_value_counts(normalize=True)
        
        # Generate horizontal bar chart
        fig = px.bar(
            x=education,
            y=education.index,
            orientation="h",
            title="Applicants: Highest Degree Earned"
        )
        
        # Set appropriate axis labels
        fig.update_layout(
            xaxis_title="Frequency [%]", 
            yaxis_title="Degree"
        )
        
        # Return completed visualization
        return fig

    def build_contingency_bar(self):

        """Creates side-by-side bar chart from contingency table.

        Returns
        -------
        Figure
        """
        # Fetch contingency table for experiment groups
        data = self.repo.get_contingency_table()
        
        # Create grouped bar visualization
        fig = px.bar(
            data_frame=data,
            barmode="group",
            title="Admissions Quiz Completion by Group"
        )
        
        # Configure chart presentation details
        fig.update_layout(
            xaxis_title="Group",
            yaxis_title="Frequency [count]",
            legend={"title": "Admissions Quiz"}
        )
        
        # Return completed visualization
        return fig


class StatsBuilder:
    """Methods for statistical analysis."""

    def __init__(self, repo=MongoRepository()):

        """init

        Parameters
        ----------
        repo : MongoRepository, optional
            Data source, by default MongoRepository()
        """
        self.repo = repo

    def calculate_n_obs(self, effect_size):

        """Calculate the number of observations needed to detect effect size.

        Parameters
        ----------
        effect_size : float
            Effect size you want to be able to detect

        Returns
        -------
        int
            Total number of observations needed, across two experimental groups.
        """
        # Initialize power analysis calculator
        chi_square_power = GofChisquarePower()
        
        # Compute required sample size per group
        group_size = math.ceil(
            chi_square_power.solve_power(
                effect_size=effect_size, 
                alpha=0.05, 
                power=0.8
            )
        )
        
        # Return total sample size across both groups
        return group_size * 2

    def calculate_cdf_pct(self, n_obs, days):

        """Calculate percent chance of gathering specified number of observations in
        specified number of days.

        Parameters
        ----------
        n_obs : int
            Number of observations you want to gather.
        days : int
            Number of days you will run experiment.

        Returns
        -------
        float
            Percentage chance of gathering ``n_obs`` or more in ``days``.
        """
        # Retrieve historical no-quiz data
        no_quiz = self.repo.get_no_quiz_per_day()
        
        # Extract distribution parameters
        summary = no_quiz.describe()
        mean = summary["mean"]
        std = summary["std"]
        
        # Adjust parameters for multi-day accumulation
        sum_mean = mean * days
        sum_std = std * np.sqrt(days)
        
        # Calculate probability using normal approximation
        cdf_value = scipy.stats.norm.cdf(
            n_obs, 
            loc=sum_mean, 
            scale=sum_std
        )
        
        # Convert to probability of exceeding threshold
        prob = 1 - cdf_value
        
        # Convert to percentage representation
        pct = prob * 100
        
        return pct

    def run_experiment(self, days):

        """Run experiment. Add results to repository.

        Parameters
        ----------
        days : int
            Number of days to run experiment for.
        """
        # Create experiment controller with appropriate DB settings
        exp = Experiment(
            repo=self.repo, 
            db="wqu-abtest", 
            collection="ds-applicants"
        )
        
        # Clear any previous experiment data
        exp.reset_experiment()
        
        # Execute experiment simulation for specified duration
        result = exp.run_experiment(days=days)
        
    def run_chi_square(self):

        """Tests nominal association.

        Returns
        -------
        A bunch containing the following attributes:

        statistic: float
            The chi^2 test statistic.

        df: int
            The degrees of freedom of the reference distribution

        pvalue: float
            The p-value for the test.
        """
        # Retrieve experiment results table
        data = self.repo.get_contingency_table()
        
        # Convert to statsmodels contingency table format
        contingency_table = Table2x2(data.values)
        
        # Execute chi-square statistical test
        chi_square_test = contingency_table.test_nominal_association()

        # Return complete test results
        return chi_square_test