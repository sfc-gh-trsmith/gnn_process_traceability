import os
import logging
from datetime import datetime
from typing import Optional, Any
import snowflake.connector

logger = logging.getLogger(__name__)

_connection: Optional[snowflake.connector.SnowflakeConnection] = None
_connection_error: Optional[str] = None
_last_attempt: Optional[datetime] = None

def get_auth_token() -> Optional[str]:
    token_path = '/snowflake/session/token'
    if os.path.exists(token_path):
        try:
            with open(token_path) as f:
                return f.read().strip()
        except Exception as e:
            logger.warning(f"Failed to read SPCS token: {e}")
    
    return os.getenv('SNOWFLAKE_PAT')

def get_connection() -> Optional[snowflake.connector.SnowflakeConnection]:
    global _connection, _connection_error, _last_attempt
    _last_attempt = datetime.utcnow()
    
    try:
        if _connection is not None and not _connection.is_closed():
            try:
                _connection.cursor().execute("SELECT 1")
                return _connection
            except Exception:
                _connection = None
        
        token = get_auth_token()
        account = os.getenv('SNOWFLAKE_ACCOUNT')
        user = os.getenv('SNOWFLAKE_USER')
        
        database = os.getenv('SNOWFLAKE_DATABASE', 'GNN_PROCESS_TRACEABILITY')
        schema = os.getenv('SNOWFLAKE_SCHEMA', 'GNN_PROCESS_TRACEABILITY')
        warehouse = os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')
        
        if token:
            conn_params = {
                'account': account,
                'user': user,
                'token': token,
                'authenticator': 'PROGRAMMATIC_ACCESS_TOKEN',
                'database': database,
                'schema': schema,
                'warehouse': warehouse,
            }
        else:
            connection_name = os.getenv('SNOWFLAKE_CONNECTION_NAME', 'demo')
            conn_params = {
                'connection_name': connection_name,
                'database': database,
                'schema': schema,
                'warehouse': warehouse,
            }
        
        _connection = snowflake.connector.connect(**conn_params)
        _connection_error = None
        logger.info("Successfully connected to Snowflake")
        return _connection
        
    except Exception as e:
        _connection_error = str(e)
        _connection = None
        logger.error(f"Failed to connect to Snowflake: {e}")
        return None

def get_connection_status() -> dict:
    return {
        'connected': _connection is not None and not (_connection.is_closed() if _connection else True),
        'error': _connection_error,
        'last_attempt': _last_attempt.isoformat() if _last_attempt else None,
    }

def execute_query(query: str, params: Optional[dict] = None) -> list[dict[str, Any]]:
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        columns = [desc[0].lower() for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        return []
    finally:
        cursor.close()

def close_connection():
    global _connection
    if _connection:
        try:
            _connection.close()
        except Exception:
            pass
        _connection = None
