"""
Footy-Brain v5 WebSocket Router
Real-time WebSocket endpoints for live match data streaming.
"""

import json
import asyncio
import logging
from typing import Dict, Set, Optional
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import redis.asyncio as redis

from apps.api_server.deps import get_redis_client

logger = logging.getLogger(__name__)

router = APIRouter()

# Connection manager for WebSocket clients
class ConnectionManager:
    """Manages WebSocket connections for real-time data streaming."""
    
    def __init__(self):
        # fixture_id -> set of websockets
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # websocket -> fixture_id mapping
        self.connection_fixtures: Dict[WebSocket, int] = {}
        
    async def connect(self, websocket: WebSocket, fixture_id: int):
        """Accept WebSocket connection and add to fixture group."""
        await websocket.accept()
        
        if fixture_id not in self.active_connections:
            self.active_connections[fixture_id] = set()
        
        self.active_connections[fixture_id].add(websocket)
        self.connection_fixtures[websocket] = fixture_id
        
        logger.info(f"WebSocket connected for fixture {fixture_id}. Total connections: {len(self.active_connections[fixture_id])}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        if websocket in self.connection_fixtures:
            fixture_id = self.connection_fixtures[websocket]
            
            if fixture_id in self.active_connections:
                self.active_connections[fixture_id].discard(websocket)
                
                # Clean up empty fixture groups
                if not self.active_connections[fixture_id]:
                    del self.active_connections[fixture_id]
            
            del self.connection_fixtures[websocket]
            
            logger.info(f"WebSocket disconnected for fixture {fixture_id}")
    
    async def send_to_fixture(self, fixture_id: int, message: dict):
        """Send message to all connections for a specific fixture."""
        if fixture_id not in self.active_connections:
            return
        
        message_str = json.dumps(message)
        disconnected = set()
        
        for websocket in self.active_connections[fixture_id]:
            try:
                await websocket.send_text(message_str)
            except Exception as e:
                logger.error(f"Error sending message to WebSocket: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected sockets
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected clients."""
        message_str = json.dumps(message)
        
        for fixture_connections in self.active_connections.values():
            for websocket in fixture_connections:
                try:
                    await websocket.send_text(message_str)
                except Exception:
                    pass  # Will be cleaned up on next send
    
    def get_connection_count(self, fixture_id: Optional[int] = None) -> int:
        """Get connection count for a fixture or total."""
        if fixture_id:
            return len(self.active_connections.get(fixture_id, set()))
        return sum(len(connections) for connections in self.active_connections.values())


# Global connection manager
manager = ConnectionManager()


class RedisSubscriber:
    """Redis subscriber for real-time data broadcasting."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.pubsub = None
        self.running = False
    
    async def start_listening(self):
        """Start listening to Redis pub/sub channels."""
        if self.running:
            return
        
        self.running = True
        self.pubsub = self.redis_client.pubsub()
        
        # Subscribe to live data channels
        await self.pubsub.subscribe(
            "live-odds",
            "live-events", 
            "live-stats",
            "live-feed"
        )
        
        logger.info("Started Redis subscriber for WebSocket broadcasting")
        
        try:
            async for message in self.pubsub.listen():
                if not self.running:
                    break
                
                if message['type'] == 'message':
                    await self._handle_redis_message(message)
                    
        except Exception as e:
            logger.error(f"Error in Redis subscriber: {e}")
        finally:
            await self.stop_listening()
    
    async def stop_listening(self):
        """Stop listening to Redis pub/sub channels."""
        self.running = False
        
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
            self.pubsub = None
        
        logger.info("Stopped Redis subscriber")
    
    async def _handle_redis_message(self, message):
        """Handle incoming Redis message and broadcast to WebSocket clients."""
        try:
            channel = message['channel'].decode('utf-8')
            data = json.loads(message['data'].decode('utf-8'))
            
            # Extract fixture_id from the message
            fixture_id = data.get('fixture_id')
            
            if not fixture_id:
                logger.warning(f"No fixture_id in message from channel {channel}")
                return
            
            # Add metadata
            websocket_message = {
                "type": channel.replace('-', '_'),  # live-odds -> live_odds
                "fixture_id": fixture_id,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            }
            
            # Broadcast to clients subscribed to this fixture
            await manager.send_to_fixture(fixture_id, websocket_message)
            
        except Exception as e:
            logger.error(f"Error handling Redis message: {e}")


# Global Redis subscriber
redis_subscriber: Optional[RedisSubscriber] = None


@router.websocket("/live/{fixture_id}")
async def websocket_live_fixture(
    websocket: WebSocket,
    fixture_id: int,
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    WebSocket endpoint for live fixture data.
    
    Streams real-time odds, events, and statistics for a specific fixture.
    """
    global redis_subscriber
    
    # Initialize Redis subscriber if not already running
    if not redis_subscriber:
        redis_subscriber = RedisSubscriber(redis_client)
        # Start subscriber in background task
        asyncio.create_task(redis_subscriber.start_listening())
    
    await manager.connect(websocket, fixture_id)
    
    try:
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "fixture_id": fixture_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Connected to live data for fixture {fixture_id}"
        }))
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for client messages (ping/pong, subscriptions, etc.)
                message = await websocket.receive_text()
                
                try:
                    data = json.loads(message)
                    await _handle_client_message(websocket, fixture_id, data)
                except json.JSONDecodeError:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON format"
                    }))
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket loop: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error for fixture {fixture_id}: {e}")
    finally:
        manager.disconnect(websocket)


async def _handle_client_message(websocket: WebSocket, fixture_id: int, data: dict):
    """Handle incoming client messages."""
    message_type = data.get('type')
    
    if message_type == 'ping':
        # Respond to ping with pong
        await websocket.send_text(json.dumps({
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    elif message_type == 'subscribe':
        # Handle subscription to specific data types
        data_types = data.get('data_types', [])
        await websocket.send_text(json.dumps({
            "type": "subscription_confirmed",
            "fixture_id": fixture_id,
            "data_types": data_types,
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    elif message_type == 'get_status':
        # Send current connection status
        await websocket.send_text(json.dumps({
            "type": "status",
            "fixture_id": fixture_id,
            "connections": manager.get_connection_count(fixture_id),
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    else:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        }))


@router.websocket("/admin/monitor")
async def websocket_admin_monitor(websocket: WebSocket):
    """
    Admin WebSocket endpoint for monitoring all connections.
    
    Provides real-time statistics about WebSocket connections and data flow.
    """
    await websocket.accept()
    
    try:
        while True:
            # Send connection statistics every 5 seconds
            stats = {
                "type": "connection_stats",
                "timestamp": datetime.utcnow().isoformat(),
                "total_connections": manager.get_connection_count(),
                "fixtures_with_connections": len(manager.active_connections),
                "fixture_details": {
                    str(fixture_id): len(connections) 
                    for fixture_id, connections in manager.active_connections.items()
                }
            }
            
            await websocket.send_text(json.dumps(stats))
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Admin monitor WebSocket error: {e}")


# Health check endpoint for WebSocket service
@router.get("/health")
async def websocket_health():
    """Health check for WebSocket service."""
    return {
        "status": "healthy",
        "total_connections": manager.get_connection_count(),
        "active_fixtures": len(manager.active_connections),
        "redis_subscriber_running": redis_subscriber.running if redis_subscriber else False
    }
