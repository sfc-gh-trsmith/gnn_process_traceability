import os
import json
import logging
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx

logger = logging.getLogger(__name__)
router = APIRouter()

SPCS_TOKEN_PATH = '/snowflake/session/token'
AGENT_NAME = 'QUALITY_ENGINEER_AGENT'
DATABASE = os.getenv('SNOWFLAKE_DATABASE', 'GNN_PROCESS_TRACEABILITY')
SCHEMA = os.getenv('SNOWFLAKE_SCHEMA', 'GNN_PROCESS_TRACEABILITY')
WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')

class AgentRequest(BaseModel):
    message: str

def get_snowflake_config():
    account = os.getenv('SNOWFLAKE_ACCOUNT', 'sfsenorthamerica-trsmith_aws1')
    host = os.getenv('SNOWFLAKE_HOST')
    
    if host:
        if not host.startswith('https://'):
            host = f'https://{host}'
    else:
        account_formatted = account.lower().replace('_', '-')
        host = f'https://{account_formatted}.snowflakecomputing.com'
    
    return {
        'host': host,
        'account': account,
        'database': DATABASE,
        'schema': SCHEMA,
        'warehouse': WAREHOUSE,
    }

def get_auth_token():
    if os.path.exists(SPCS_TOKEN_PATH):
        try:
            with open(SPCS_TOKEN_PATH) as f:
                token = f.read().strip()
                if token:
                    return token, True
        except Exception as e:
            logger.warning(f"Failed to read SPCS token: {e}")
    
    pat = os.getenv('SNOWFLAKE_PAT')
    if pat:
        return pat, False
    
    return None, False

async def stream_agent_response(message: str) -> AsyncGenerator[str, None]:
    config = get_snowflake_config()
    token, is_spcs = get_auth_token()
    
    if not token:
        yield f'data: {json.dumps({"type": "error", "message": "No authentication token available"})}\n\n'
        return
    
    url = f"{config['host']}/api/v2/databases/{config['database']}/schemas/{config['schema']}/agents/{AGENT_NAME}:run"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
        'Accept': 'text/event-stream',
        'X-Snowflake-Warehouse': config['warehouse'],
    }
    
    if not is_spcs:
        role = os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')
        headers['X-Snowflake-Role'] = role
    
    payload = {
        'messages': [
            {
                'role': 'user',
                'content': [{'type': 'text', 'text': message}]
            }
        ]
    }
    
    logger.info(f"Calling agent at: {url}")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream('POST', url, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    logger.error(f"Agent error {response.status_code}: {error_text}")
                    yield f'data: {json.dumps({"type": "error", "message": f"Agent returned {response.status_code}"})}\n\n'
                    return
                
                current_event = ''
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    
                    if line.startswith('event:'):
                        current_event = line[6:].strip()
                        continue
                    
                    if line.startswith('data:'):
                        data_str = line[5:].strip()
                        if data_str == '[DONE]':
                            yield f'data: {json.dumps({"type": "done"})}\n\n'
                            continue
                        
                        try:
                            data = json.loads(data_str)
                            
                            if current_event == 'response.thinking':
                                yield f'data: {json.dumps({"type": "thinking", "text": data.get("text", "")})}\n\n'
                            
                            elif current_event == 'response.tool_use':
                                yield f'data: {json.dumps({"type": "tool_start", "tool_name": data.get("name"), "tool_use_id": data.get("tool_use_id"), "tool_type": data.get("type"), "input": data.get("input")})}\n\n'
                            
                            elif current_event == 'response.tool_result':
                                result_content = data.get('content', [])
                                result_json = None
                                sql = None
                                
                                for item in result_content:
                                    if isinstance(item, dict) and 'json' in item:
                                        result_json = item['json']
                                        if isinstance(result_json, dict):
                                            sql = result_json.get('sql')
                                
                                yield f'data: {json.dumps({"type": "tool_end", "tool_use_id": data.get("tool_use_id"), "tool_name": data.get("name"), "status": data.get("status", "complete"), "result": result_json, "sql": sql})}\n\n'
                            
                            elif current_event == 'response.text.delta':
                                yield f'data: {json.dumps({"type": "text_delta", "text": data.get("text", "")})}\n\n'
                            
                            elif current_event == 'response.text':
                                yield f'data: {json.dumps({"type": "text_delta", "text": data.get("text", "")})}\n\n'
                            
                            elif current_event == 'error':
                                yield f'data: {json.dumps({"type": "error", "message": data.get("message", "Unknown error")})}\n\n'
                            
                            elif current_event == 'done':
                                yield f'data: {json.dumps({"type": "done"})}\n\n'
                        
                        except json.JSONDecodeError:
                            continue
        
        yield f'data: {json.dumps({"type": "done"})}\n\n'
        
    except httpx.TimeoutException:
        logger.error("Agent request timed out")
        yield f'data: {json.dumps({"type": "error", "message": "Request timed out"})}\n\n'
    except Exception as e:
        logger.error(f"Agent stream error: {e}")
        yield f'data: {json.dumps({"type": "error", "message": str(e)})}\n\n'

@router.post("/run")
async def run_agent(request: AgentRequest):
    return StreamingResponse(
        stream_agent_response(request.message),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
        }
    )

@router.get("/status")
async def agent_status():
    token, is_spcs = get_auth_token()
    config = get_snowflake_config()
    
    return {
        'agent_name': AGENT_NAME,
        'database': config['database'],
        'schema': config['schema'],
        'warehouse': config['warehouse'],
        'host': config['host'],
        'auth_type': 'spcs_token' if is_spcs else ('pat' if token else 'none'),
        'configured': token is not None,
    }
