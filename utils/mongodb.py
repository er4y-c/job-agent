import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from dotenv import load_dotenv

load_dotenv()


class MongoDB:
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB using connection string from environment"""
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            raise ValueError("MONGODB_URI not found in environment variables")
        
        self.client = MongoClient(mongodb_uri)
        # Extract database name from URI or use default
        db_name = os.getenv("MONGODB_DATABASE", "job_agent")
        self.db = self.client[db_name]
    
    def get_collection(self, collection_name: str) -> Collection:
        """Get a collection from the database"""
        if self.db is None:
            raise RuntimeError("Database connection not initialized")
        return self.db[collection_name]
    
    def close(self):
        """Close the MongoDB connection"""
        if self.client is not None:
            self.client.close()


class JobAgentDB:
    """Database operations for Job Agent application"""
    
    def __init__(self):
        self.mongo = MongoDB()
        self.cv_analyses = self.mongo.get_collection("cv_analyses")
        self.job_searches = self.mongo.get_collection("job_searches")
        self.job_analyses = self.mongo.get_collection("job_analyses")
        self.suitability_reports = self.mongo.get_collection("suitability_reports")
        self.cover_letters = self.mongo.get_collection("cover_letters")
    
    # CV Analysis operations
    def save_cv_analysis(self, data: Dict[str, Any]) -> str:
        """Save CV analysis result"""
        doc = {
            **data,
            "created_at": datetime.now(),
            "type": "cv_analysis"
        }
        result = self.cv_analyses.insert_one(doc)
        return str(result.inserted_id)
    
    def get_cv_analyses(self) -> List[Dict[str, Any]]:
        """Get all CV analyses sorted by creation date"""
        return list(self.cv_analyses.find().sort("created_at", -1))
    
    def get_cv_analysis_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific CV analysis by ID"""
        from bson import ObjectId
        return self.cv_analyses.find_one({"_id": ObjectId(doc_id)})
    
    # Job Search operations
    def save_job_search(self, data: Dict[str, Any]) -> str:
        """Save job search results"""
        doc = {
            **data,
            "created_at": datetime.now(),
            "type": "job_search"
        }
        result = self.job_searches.insert_one(doc)
        return str(result.inserted_id)
    
    def get_job_searches(self) -> List[Dict[str, Any]]:
        """Get all job searches sorted by creation date"""
        return list(self.job_searches.find().sort("created_at", -1))
    
    def get_job_search_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific job search by ID"""
        from bson import ObjectId
        return self.job_searches.find_one({"_id": ObjectId(doc_id)})
    
    # Job Analysis operations
    def save_job_analysis(self, data: Dict[str, Any]) -> str:
        """Save job analysis result"""
        doc = {
            **data,
            "created_at": datetime.now(),
            "type": "job_analysis"
        }
        result = self.job_analyses.insert_one(doc)
        return str(result.inserted_id)
    
    def get_job_analyses(self) -> List[Dict[str, Any]]:
        """Get all job analyses sorted by creation date"""
        return list(self.job_analyses.find().sort("created_at", -1))
    
    def get_job_analysis_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific job analysis by ID"""
        from bson import ObjectId
        return self.job_analyses.find_one({"_id": ObjectId(doc_id)})
    
    # Suitability Report operations
    def save_suitability_report(self, data: Dict[str, Any]) -> str:
        """Save suitability report"""
        doc = {
            **data,
            "created_at": datetime.now(),
            "type": "suitability_report"
        }
        result = self.suitability_reports.insert_one(doc)
        return str(result.inserted_id)
    
    def get_suitability_reports(self) -> List[Dict[str, Any]]:
        """Get all suitability reports sorted by creation date"""
        return list(self.suitability_reports.find().sort("created_at", -1))
    
    def get_suitability_report_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific suitability report by ID"""
        from bson import ObjectId
        return self.suitability_reports.find_one({"_id": ObjectId(doc_id)})
    
    # Cover Letter operations
    def save_cover_letter(self, data: Dict[str, Any]) -> str:
        """Save cover letter"""
        doc = {
            **data,
            "created_at": datetime.now(),
            "type": "cover_letter"
        }
        result = self.cover_letters.insert_one(doc)
        return str(result.inserted_id)
    
    def get_cover_letters(self) -> List[Dict[str, Any]]:
        """Get all cover letters sorted by creation date"""
        return list(self.cover_letters.find().sort("created_at", -1))
    
    def get_cover_letter_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific cover letter by ID"""
        from bson import ObjectId
        return self.cover_letters.find_one({"_id": ObjectId(doc_id)})
    
    def close(self):
        """Close database connection"""
        self.mongo.close()


# Global database instance
db = JobAgentDB()