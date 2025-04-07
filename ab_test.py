"""
Custom A/B testing library for educational experiments.
Provides functionality for running experiments, assigning users to groups,
and analyzing results.
"""

import random
import pandas as pd
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.collection import Collection


class Reset:
    """Class for resetting experiment data in MongoDB."""
    
    def __init__(self, client=None):
        """Initialize Reset object.
        
        Parameters
        ----------
        client : pymongo.MongoClient, optional
            MongoDB client instance, by default None
        """
        if client is None:
            self.client = MongoClient(host='localhost', port=27017)
        else:
            self.client = client
            
    def reset_database(self, db_name="online_course"):
        """Reset the database by removing experiment fields.
        
        Parameters
        ----------
        db_name : str, optional
            Name of database to reset, by default "online_course"
        
        Returns
        -------
        dict
            Dictionary summarizing reset results
        """
        print(f"Client type: {type(self.client)}")
        
        if isinstance(self.client, Collection):
            # Handle the case when client is a Collection
            collection = self.client
            update_result = collection.update_many(
                {"inExperiment": True},
                {"$unset": {"inExperiment": "", "group": ""}}
            )
            return {collection.name: {
                "matched": update_result.matched_count,
                "modified": update_result.modified_count
            }}

        db = self.client[db_name]
        results = {}
        
        for collection_name in db.list_collection_names():
            collection = db[collection_name]
            update_result = collection.update_many(
                {"inExperiment": True},
                {"$unset": {"inExperiment": "", "group": ""}}
            )
            results[collection_name] = {
                "matched": update_result.matched_count,
                "modified": update_result.modified_count
            }
        
        return results
    

class Experiment:
    """Class for running A/B test experiments."""
    
    def __init__(self, repo=None, db="online_course", collection="applicants"):
        self.db_name = db
        self.collection_name = collection
        
        print(f"Input repo type: {type(repo)}")
        
        # Check if repo is None or a MongoClient instance
        if repo is None or isinstance(repo, MongoClient):
            # Use the repo directly as the client
            self.client = repo if repo is not None else MongoClient(host='localhost', port=27017)
            self.collection = self.client[db][collection]
        else:
            self.collection = repo.collection
            self.client = self.collection.database.client
        
        print(f"Final client type: {type(self.client)}")
        print(f"Final collection type: {type(self.collection)}")
    
    def reset_experiment(self):
        """Reset experimental data in the collection.
        
        Returns
        -------
        dict
            Dictionary containing reset results
        """
        reset_tool = Reset(self.client)
        result = reset_tool.reset_database(self.db_name)
        return result.get(self.collection_name, {"matched": 0, "modified": 0})
    
    def run_experiment(self, days=7, assignment=True, seed=42):
        """Run an A/B test experiment over a specified number of days.
        
        Parameters
        ----------
        days : int, optional
            Number of days to run experiment, by default 7
        assignment : bool, optional
            Whether to assign users to groups, by default True
        seed : int, optional
            Random seed for group assignment, by default 42
            
        Returns
        -------
        dict
            Dictionary with experiment results
        """
        if assignment:
            # Reset random seed for consistent assignment
            random.seed(seed)
        
        # Calculate date range for experiment
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=days)
        
        # Dictionary to store daily results
        daily_results = {}
        
        # Run experiment for each day in range
        current_date = start_date
        while current_date < end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            
            if assignment:
                # Assign users to groups
                if hasattr(self, 'repo') and hasattr(self.repo, 'assign_to_groups'):
                    result = self.repo.assign_to_groups(date_str)
                else:
                    # Create our own assignment logic
                    result = self._assign_groups_for_date(date_str)
            else:
                # Just count users without assignment
                result = self._count_users_for_date(date_str)
                
            daily_results[date_str] = result
            current_date += timedelta(days=1)
                
        # Calculate overall experiment results
        total_assigned = sum(day.get('n', 0) for day in daily_results.values())
        
        # Get final statistics on experiment groups
        stats = self._calculate_experiment_stats()
        
        return {
            "days": days,
            "total_assigned": total_assigned,
            "daily_results": daily_results,
            "statistics": stats
        }
    
    def _assign_groups_for_date(self, date_string):
        """Assign users created on a specific date to experiment groups.
        
        Parameters
        ----------
        date_string : str
            Date string in format YYYY-MM-DD
            
        Returns
        -------
        dict
            Dictionary with assignment results
        """
        # Convert string to datetime
        start_date = datetime.strptime(date_string, "%Y-%m-%d")
        end_date = start_date + timedelta(days=1)
        
        # Find applicable users
        query = {
            "createdAt": {"$gte": start_date, "$lt": end_date},
            "admissionsQuiz": "incomplete"
        }
        users = list(self.collection.find(query))
        
        # Shuffle users for random assignment
        random.shuffle(users)
        
        # Split users into control and treatment groups
        midpoint = len(users) // 2
        
        # Assign control group
        control_group = users[:midpoint]
        for user in control_group:
            user['inExperiment'] = True
            user['group'] = "No email (control)"
            
        # Assign treatment group
        treatment_group = users[midpoint:]
        for user in treatment_group:
            user['inExperiment'] = True
            user['group'] = "email (treatment)"
            
        # Update users in database
        modified_count = 0
        matched_count = 0
        
        all_users = control_group + treatment_group
        for user in all_users:
            result = self.collection.update_one(
                {"_id": user["_id"]},
                {"$set": {
                    "inExperiment": user["inExperiment"],
                    "group": user["group"]
                }}
            )
            matched_count += result.matched_count
            modified_count += result.modified_count
            
        return {
            "n": matched_count,
            "n_modified": modified_count,
            "control_size": len(control_group),
            "treatment_size": len(treatment_group)
        }
    
    def _count_users_for_date(self, date_string):
        """Count users created on a specific date without assigning groups.
        
        Parameters
        ----------
        date_string : str
            Date string in format YYYY-MM-DD
            
        Returns
        -------
        dict
            Dictionary with user counts
        """
        # Convert string to datetime
        start_date = datetime.strptime(date_string, "%Y-%m-%d")
        end_date = start_date + timedelta(days=1)
        
        # Count applicable users
        query = {
            "createdAt": {"$gte": start_date, "$lt": end_date},
            "admissionsQuiz": "incomplete"
        }
        count = self.collection.count_documents(query)
        
        return {"count": count}
    
    def _calculate_experiment_stats(self):
        """Calculate statistics for the current experiment.
        
        Returns
        -------
        dict
            Dictionary with experiment statistics
        """
        # Count users in each group
        control_count = self.collection.count_documents({
            "inExperiment": True,
            "group": "No email (control)"
        })
        
        treatment_count = self.collection.count_documents({
            "inExperiment": True,
            "group": "email (treatment)"
        })
        
        # Count completed quizzes in each group
        control_completed = self.collection.count_documents({
            "inExperiment": True,
            "group": "No email (control)",
            "admissionsQuiz": "complete"
        })
        
        treatment_completed = self.collection.count_documents({
            "inExperiment": True,
            "group": "email (treatment)",
            "admissionsQuiz": "complete"
        })
        
        # Calculate completion rates
        control_rate = control_completed / control_count if control_count > 0 else 0
        treatment_rate = treatment_completed / treatment_count if treatment_count > 0 else 0
        
        return {
            "control_group": {
                "total": control_count,
                "completed": control_completed,
                "completion_rate": control_rate
            },
            "treatment_group": {
                "total": treatment_count,
                "completed": treatment_completed,
                "completion_rate": treatment_rate
            },
            "difference": treatment_rate - control_rate
        }