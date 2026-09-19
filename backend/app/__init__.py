"""DukaanSetu — Flask Application Factory"""
import os
from flask import Flask, jsonify
from flask_cors import CORS

from app.config.settings import config


def create_app(config_name=None):
    """Create and configure the Flask application."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    # CORS — allow frontend origins
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000", "*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })

    # Register error handlers
    register_error_handlers(app)

    # Register routes
    register_routes(app)

    return app


def register_error_handlers(app):
    """Register global error handlers."""

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({
            "success": False,
            "error": {"code": "BAD_REQUEST", "message": str(e.description) if hasattr(e, 'description') else "Bad request"}
        }), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({
            "success": False,
            "error": {"code": "UNAUTHORIZED", "message": "Authentication required"}
        }), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({
            "success": False,
            "error": {"code": "FORBIDDEN", "message": "Access denied"}
        }), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "success": False,
            "error": {"code": "NOT_FOUND", "message": "Resource not found"}
        }), 404

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal error: {e}")
        return jsonify({
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": "Something went wrong. Please try again."}
        }), 500


def register_routes(app):
    """Register all route blueprints."""

    # Health check
    @app.route('/health')
    def health():
        return jsonify({"status": "ok"})

    # Import and register blueprints
    from app.routes.auth import auth_bp
    from app.routes.products import products_bp
    from app.routes.inventory import inventory_bp
    from app.routes.transactions import transactions_bp
    from app.routes.analytics import analytics_bp
    from app.routes.voice import voice_bp
    from app.routes.suppliers import suppliers_bp
    from app.routes.borrowings import borrowings_bp
    from app.routes.notifications import notifications_bp
    from app.routes.assistant import assistant_bp
    from app.routes.reorder import reorder_bp
    from app.routes.customers import customers_bp
    from app.routes.orders import orders_bp
    from app.routes.festivals import festivals_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(voice_bp, url_prefix='/api/voice')
    app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')
    app.register_blueprint(borrowings_bp, url_prefix='/api/borrowings')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(assistant_bp, url_prefix='/api/assistant')
    app.register_blueprint(reorder_bp, url_prefix='/api/reorder')
    app.register_blueprint(customers_bp, url_prefix='/api/customers')
    app.register_blueprint(orders_bp, url_prefix='/api/purchase-orders')
    app.register_blueprint(festivals_bp, url_prefix='/api/festivals')
