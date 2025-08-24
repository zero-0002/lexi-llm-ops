"""
Logging configuration để tắt debug logs từ các thư viện external
"""
import logging
import warnings

def suppress_debug_logs():
    """Tắt các debug logs từ các thư viện external để giảm noise"""
    
    # Tắt warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    
    # Set logging levels cao hơn cho các thư viện external
    external_loggers = [
        'openai',
        'httpx', 
        'httpcore',
        'urllib3',
        'langsmith',
        'requests',
        'langchain',
        'langchain_openai',
        'langchain_core',
        'httpcore._sync.connection_pool',
        'httpcore._sync.http11',
        'asyncio',
        'mcp'
    ]
    
    for logger_name in external_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    # Set root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    print("🔇 Debug logs suppressed for external libraries")

def enable_debug_logs():
    """Bật lại debug logs nếu cần debug"""
    logging.basicConfig(level=logging.DEBUG)
    print("🔊 Debug logs enabled")

# Auto suppress when imported
suppress_debug_logs()
