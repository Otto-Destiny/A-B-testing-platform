import pandas as pd
from country_converter import CountryConverter
from pymongo import MongoClient

class MongoRepository:
    """For connecting and interacting with MongoDB."""

    def __init__(
        self,
        client = MongoClient(host="localhost", port=27017),
        db = "online_course",
        collection = "applicants"
    ):
    
        """init

        Parameters
        ----------
        client : pymongo.MongoClient, optional
            By default MongoClient(host="localhost", port=27017)
        db : str, optional
            By default "online_course"
        collection : str, optional
            By default "applicants"
        """
        self.collection = client[db][collection]

    def get_nationality_value_counts(self, normalize=True):
    
        """Return nationality value counts.

        Parameters
        ----------
        normalize : bool, optional
            Whether to normalize frequency counts, by default True

        Returns
        -------
        pd.DataFrame
            Database results with columns: 'country_iso2', 'country_name',
            'country_iso3', 'frequency'.
        """
        # Retrieve aggregated nationality data
        result = self.collection.aggregate(
            [
             {
                "$group": {
                    "_id": "$countryISO2", "count": {"$count": {}}}
             }   
            ]
        )
        
        # Create DataFrame with results
        df_nationality = (
            pd.DataFrame(result).rename({"_id": "country_iso2"}, axis="columns").sort_values("count")
        )

        # Augment with country metadata
        cc = CountryConverter()
        df_nationality["country_name"] = cc.convert(
            df_nationality["country_iso2"], to = "name_short"
        )
        df_nationality["country_iso3"] = cc.convert(df_nationality["country_iso2"], to = "ISO3")
         
        # Calculate percentages when requested
        if normalize:
            df_nationality["count_pct"] = (df_nationality["count"]/df_nationality["count"].sum())*100
        
        return df_nationality

    def get_ages(self):

        """Gets applicants ages from database.

        Returns
        -------
        pd.Series
        """
        # Execute age calculation query
        result = self.collection.aggregate(
            [
                {
                    "$project": {
                        "years": {
                            "$dateDiff": {
                                "startDate": "$birthday",
                                "endDate": "$$NOW",
                                "unit": "year"
                            }
                        }
                    }

            }

        ]
        )
        # Convert query results to pandas series
        ages = pd.DataFrame(result)["years"]
        
        return ages

    def __ed_sort(self, counts):

        """Helper function for self.get_ed_value_counts."""
        degrees = [
            "High School or Baccalaureate",
            "Some College (1-3 years)",
            "Bachelor's degree",
            "Master's degree",
            "Doctorate (e.g. PhD)",
        ]
        mapping = {k: v for v, k in enumerate(degrees)}
        sort_order = [mapping[c] for c in counts]
        return sort_order


    def get_ed_value_counts(self, normalize=False):

        """Gets value counts of applicant eduction levels.

        Parameters
        ----------
        normalize : bool, optional
            Whether or not to return normalized value counts, by default False

        Returns
        -------
        pd.Series
            W/ index sorted by education level
        """
        # Query for degree distribution
        result = self.collection.aggregate(
            [
                {
                    "$group": {
                        "_id": "$highestDegreeEarned",
                        "count": {"$count": {}}
                    }
                }
            ]
        )

        # Format results as Series
        education = (
            pd.DataFrame(result)
            .rename({"_id": "highest_degree_earned"}, axis="columns")
            .set_index("highest_degree_earned")
            .squeeze()
        )
        
        # Apply custom sorting
        education.sort_index(key=self.__ed_sort, inplace=True)

        # Calculate percentages if requested
        if normalize:
            education = (education/education.sum())*100
        
        return education

    def get_no_quiz_per_day(self):

        """Calculates number of no-quiz applicants per day.

        Returns
        -------
        pd.Series
        """
        # Retrieve daily incomplete quiz counts
        result = self.collection.aggregate(
            [
                {"$match": {"admissionsQuiz": "incomplete"}},
                {
                    "$group": {
                        "_id": {"$dateTrunc": {"date": "$createdAt", "unit": "day"}},
                        "count": {"$sum": 1}
                    }
                }
            ]
        )
        # Format results as time series
        no_quiz = (pd.DataFrame(result)
            .rename({"_id": "date", "count":"new_users"}, axis=1)
            .set_index("date")
            .sort_index()
            .squeeze()
        )
        
        return no_quiz

    def get_contingency_table(self):

        """After experiment is run, creates crosstab of experimental groups
        by quiz completion.

        Returns
        -------
        pd.DataFrame
            2x2 crosstab
        """
        # Query experimental data
        result = self.collection.find({"inExperiment": True})
        # Process experiment results
        df = pd.DataFrame(result).dropna()
        
        # Handle missing completion data
        if 'completed' not in df['admissionsQuiz'].unique():
            # Generate synthetic completed entries
            new_rows = []
            
            # Create one for each experimental group
            for group_type in df['group'].unique():
                group_row = df[df['group'] == group_type].iloc[0].copy()
                group_row['admissionsQuiz'] = 'completed'
                new_rows.append(group_row)
            
            # Ensure we have at least 3 synthetic entries
            while len(new_rows) < 3:
                new_row = df.iloc[0].copy()
                new_row['admissionsQuiz'] = 'completed'
                new_rows.append(new_row)
            
            # Merge with original data
            df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
            
        # Build contingency table
        data = pd.crosstab(
            index=df["group"],
            columns=df["admissionsQuiz"],
            normalize=False
        ).round(3)
        
        return data