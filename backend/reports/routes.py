from flask import Blueprint, send_file
from flask_jwt_extended import jwt_required, get_jwt
from reports.service import ReportService
from utils.common import success_response, error_response
import io
import csv

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/assets', methods=['GET'])
@jwt_required()
def asset_report():
    data = ReportService.get_asset_utilization()
    return success_response("Asset report generated", data)

@reports_bp.route('/export/csv', methods=['GET'])
@jwt_required()
def export_csv():
    claims = get_jwt()
    if claims.get('role') not in ['Admin', 'Asset Manager']:
        return error_response("Permission denied", status_code=403)
        
    data = ReportService.get_asset_utilization()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Status', 'Count'])
    for item in data:
        writer.writerow([item['status'], item['count']])
        
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    output.close()
    
    return send_file(
        mem,
        as_attachment=True,
        download_name='asset_report.csv',
        mimetype='text/csv'
    )
