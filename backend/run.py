#!/usr/bin/env python3
"""
Smart Home Automation Backend - Application Runner
Production-ready Flask application entry point with comprehensive configuration
"""

import os
import sys
import logging
import signal
from pathlib import Path
from typing import Optional

# Add the backend directory to Python path for imports
backend_dir = Path(__file__).parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))

# Import application components
try:
    from backend.app import create_app
    from backend.config import get_config, validate_environment, setup_logging
    from backend.middleware import init_middleware
except ImportError as e:
    print(f"Failed to import backend modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

# Configure logging for this module
logger = logging.getLogger(__name__)

class ApplicationRunner:
    """
    Application runner class for managing Flask app lifecycle
    """
    
    def __init__(self):
        self.app = None
        self.config = None
        self.middleware_manager = None
        self.shutdown_handlers = []
        
    def setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
        signal.signal(signal.SIGTERM, signal_handler)  # Docker/systemd stop
        
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, signal_handler)  # Reload signal
    
    def validate_requirements(self) -> bool:
        """
        Validate system requirements and environment
        
        Returns:
            True if all requirements are met
        """
        try:
            # Check Python version
            if sys.version_info < (3, 8):
                logger.error("Python 3.8 or higher is required")
                return False
            
            # Validate environment variables
            if not validate_environment():
                logger.error("Environment validation failed")
                return False
            
            # Check required directories
            required_dirs = ['logs', 'uploads']
            for dir_name in required_dirs:
                dir_path = project_root / dir_name
                dir_path.mkdir(exist_ok=True)
            
            logger.info("Requirements validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Requirements validation failed: {e}")
            return False
    
    def create_application(self, config_name: Optional[str] = None) -> bool:
        """
        Create and configure Flask application
        
        Args:
            config_name: Configuration environment name
            
        Returns:
            True if application created successfully
        """
        try:
            # Get configuration
            config_name = config_name or os.environ.get('FLASK_ENV', 'development')
            self.config = get_config(config_name)
            
            # Setup logging
            setup_logging(self.config)
            
            logger.info(f"Creating application with {config_name} configuration")
            logger.info(f"Debug mode: {self.config.DEBUG}")
            
            # Create Flask application
            self.app = create_app(config_name)
            
            # Initialize middleware
            self.middleware_manager = init_middleware(self.app)
            
            logger.info("Application created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create application: {e}")
            return False
    
    def run_development_server(self):
        """Run Flask development server"""
        if not self.app:
            logger.error("Application not created")
            return False
        
        try:
            host = self.config.HOST
            port = self.config.PORT
            debug = self.config.DEBUG
            
            logger.info(f"Starting development server on {host}:{port}")
            logger.info(f"Debug mode: {debug}")
            logger.info(f"Access the application at: http://{host}:{port}")
            
            # Development server configuration
            self.app.run(
                host=host,
                port=port,
                debug=debug,
                use_reloader=debug,
                use_debugger=debug,
                threaded=True
            )
            
        except Exception as e:
            logger.error(f"Failed to start development server: {e}")
            return False
    
    def run_production_server(self):
        """Run with production WSGI server (Gunicorn)"""
        try:
            import gunicorn.app.wsgiapp as wsgi
            
            host = self.config.HOST
            port = self.config.PORT
            workers = self.config.WORKERS
            
            logger.info(f"Starting production server with {workers} workers on {host}:{port}")
            
            # Gunicorn configuration
            sys.argv = [
                'gunicorn',
                '--bind', f'{host}:{port}',
                '--workers', str(workers),
                '--worker-class', 'sync',
                '--timeout', '30',
                '--keep-alive', '60',
                '--max-requests', '1000',
                '--max-requests-jitter', '100',
                '--preload',
                '--access-logfile', '-',
                '--error-logfile', '-',
                'backend.app:create_app()'
            ]
            
            wsgi.run()
            
        except ImportError:
            logger.error("Gunicorn not available. Install with: pip install gunicorn")
            logger.info("Falling back to development server...")
            return self.run_development_server()
        except Exception as e:
            logger.error(f"Failed to start production server: {e}")
            return False
    
    def get_application_info(self) -> dict:
        """Get application information"""
        if not self.app:
            return {'status': 'not_created'}
        
        return {
            'status': 'ready',
            'name': self.app.name,
            'debug': self.app.debug,
            'config': self.config.__class__.__name__,
            'middleware_status': self.middleware_manager.get_status() if self.middleware_manager else None,
            'routes': len(self.app.url_map._rules),
            'blueprints': list(self.app.blueprints.keys())
        }
    
    def health_check(self) -> bool:
        """Perform application health check"""
        try:
            if not self.app:
                return False
            
            with self.app.test_client() as client:
                response = client.get('/api/status')
                return response.status_code == 200
                
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False
    
    def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down application...")
        
        # Call custom shutdown handlers
        for handler in self.shutdown_handlers:
            try:
                handler()
            except Exception as e:
                logger.error(f"Error in shutdown handler: {e}")
        
        logger.info("Application shutdown complete")
    
    def add_shutdown_handler(self, handler):
        """Add custom shutdown handler"""
        self.shutdown_handlers.append(handler)

def print_banner():
    """Print application startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                Smart Home Automation API                     ║
║                     Version 1.0.0                           ║
║              Raspberry Pi Pico W Controller                  ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_usage():
    """Print usage information"""
    usage = """
Usage: python backend/run.py [OPTIONS]

Options:
    --config, -c     Configuration environment (development|production|testing)
    --host, -h       Host address (default: from config)
    --port, -p       Port number (default: from config)
    --debug, -d      Enable debug mode
    --production     Run with production server (Gunicorn)
    --info           Show application information
    --health         Perform health check
    --help           Show this help message

Environment Variables:
    FLASK_ENV        Configuration environment
    FLASK_DEBUG      Debug mode (true/false)
    HOST             Host address
    PORT             Port number
    WORKERS          Number of worker processes (production)

Examples:
    python backend/run.py                    # Run with default config
    python backend/run.py --config production --port 8080
    python backend/run.py --production       # Run with Gunicorn
    python backend/run.py --info            # Show app info
    python backend/run.py --health          # Health check
    """
    print(usage)

def parse_arguments():
    """Parse command line arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Home Automation Backend')
    parser.add_argument('--config', '-c', choices=['development', 'production', 'testing'],
                       help='Configuration environment')
    parser.add_argument('--host', '-h', help='Host address')
    parser.add_argument('--port', '-p', type=int, help='Port number')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug mode')
    parser.add_argument('--production', action='store_true', help='Run with production server')
    parser.add_argument('--info', action='store_true', help='Show application information')
    parser.add_argument('--health', action='store_true', help='Perform health check')
    parser.add_argument('--help-extended', action='store_true', help='Show extended help')
    
    return parser.parse_args()

def main():
    """Main application entry point"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Show extended help if requested
    if args.help_extended:
        print_usage()
        return 0
    
    # Print banner
    if not (args.info or args.health):
        print_banner()
    
    # Create application runner
    runner = ApplicationRunner()
    
    # Setup signal handlers for graceful shutdown
    runner.setup_signal_handlers()
    
    # Validate requirements
    if not runner.validate_requirements():
        logger.error("Requirements validation failed")
        return 1
    
    # Override configuration from command line arguments
    config_name = args.config or os.environ.get('FLASK_ENV', 'development')
    
    # Create application
    if not runner.create_application(config_name):
        logger.error("Failed to create application")
        return 1
    
    # Override config from command line
    if args.host:
        runner.config.HOST = args.host
    if args.port:
        runner.config.PORT = args.port
    if args.debug:
        runner.config.DEBUG = True
    
    # Handle special commands
    if args.info:
        import json
        info = runner.get_application_info()
        print(json.dumps(info, indent=2))
        return 0
    
    if args.health:
        if runner.health_check():
            print("✓ Application health check passed")
            return 0
        else:
            print("✗ Application health check failed")
            return 1
    
    # Start server
    try:
        if args.production or config_name == 'production':
            logger.info("Starting production server...")
            success = runner.run_production_server()
        else:
            logger.info("Starting development server...")
            success = runner.run_development_server()
        
        if not success:
            logger.error("Server failed to start")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}")
        return 1
    finally:
        runner.shutdown()
    
    return 0

if __name__ == '__main__':
    # Set up basic logging before application creation
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
