import os
import logging
from flask import Flask, jsonify
from config import config
from extensions import db, migrate, jwt, bcrypt, ma

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure upload and log directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['LOG_DIR'], exist_ok=True)

    # Configure Logging
    logging.basicConfig(
        level=logging.INFO if not app.config.get('DEBUG') else logging.DEBUG,
        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(app.config['LOG_DIR'], 'application.log')),
            logging.StreamHandler()
        ]
    )

    # Initialize Extensions
    from flask_cors import CORS
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)

    # Register Blueprints
    from auth.routes import auth_bp
    from organization.routes import org_bp
    from assets.routes import assets_bp
    from allocation.routes import allocation_bp
    from booking.routes import bookings_bp
    from maintenance.routes import maintenance_bp
    from audit.routes import audit_bp
    from dashboard.routes import dashboard_bp
    from reports.routes import reports_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(org_bp, url_prefix='/api/v1/organization')
    app.register_blueprint(assets_bp, url_prefix='/api/v1/assets')
    app.register_blueprint(allocation_bp, url_prefix='/api/v1/allocation')
    app.register_blueprint(bookings_bp, url_prefix='/api/v1/bookings')
    app.register_blueprint(maintenance_bp, url_prefix='/api/v1/maintenance')
    app.register_blueprint(audit_bp, url_prefix='/api/v1/audit')
    app.register_blueprint(dashboard_bp, url_prefix='/api/v1/dashboard')
    app.register_blueprint(reports_bp, url_prefix='/api/v1/reports')

    # Register Global Error Handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "message": "Bad Request"}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({"success": False, "message": "Forbidden"}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "message": "Not Found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"success": False, "message": "Internal Server Error"}), 500

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            "success": False,
            "message": "Request does not contain an access token."
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            "success": False,
            "message": "Signature verification failed."
        }), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "success": False,
            "message": "Token has expired."
        }), 401

    return app
