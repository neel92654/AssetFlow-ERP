from extensions import db
from sqlalchemy import func
from database.models import Asset

class ReportService:
    @staticmethod
    def get_asset_utilization():
        # Dynamic SQL aggregation query for asset lifecycle status counts
        results = db.session.query(
            Asset.lifecycle_status, 
            func.count(Asset.id).label('count')
        ).group_by(Asset.lifecycle_status).all()
        
        return [{"status": r.lifecycle_status, "count": r.count} for r in results]
