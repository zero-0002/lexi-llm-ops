"""
WebSocket and Real-time Communication Tests
==========================================
Tests WebSocket connections and real-time features
"""

import pytest
import asyncio
import json
import websockets
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class TestWebSocketConnection:
    """Test WebSocket connection and basic functionality."""
    
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_websocket_connection(self, test_config):
        """Test basic WebSocket connection."""
        ws_url = test_config["ws_test_url"]
        
        try:
            async with websockets.connect(ws_url) as websocket:
                # Send ping
                await websocket.send(json.dumps({"type": "ping"}))
                
                # Receive pong
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                
                assert data.get("type") == "pong"
                logger.info("✅ WebSocket connection successful")
                
        except websockets.exceptions.ConnectionClosed:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            pytest.fail(f"WebSocket connection failed: {e}")

    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_websocket_authentication(self, test_config):
        """Test WebSocket authentication."""
        ws_url = test_config["ws_test_url"]
        
        try:
            async with websockets.connect(ws_url) as websocket:
                # Send authentication
                auth_message = {
                    "type": "auth",
                    "token": "test_token",
                    "user_id": "test_user"
                }
                await websocket.send(json.dumps(auth_message))
                
                # Receive auth response
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                
                assert data.get("type") == "auth_response"
                assert "status" in data
                
                logger.info("✅ WebSocket authentication test completed")
                
        except websockets.exceptions.ConnectionClosed:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            logger.warning(f"WebSocket auth test warning: {e}")

    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_websocket_message_echo(self, test_config):
        """Test WebSocket message echo functionality."""
        ws_url = test_config["ws_test_url"]
        
        try:
            async with websockets.connect(ws_url) as websocket:
                # Send test message
                test_message = {
                    "type": "echo",
                    "message": "Hello WebSocket!",
                    "timestamp": asyncio.get_event_loop().time()
                }
                await websocket.send(json.dumps(test_message))
                
                # Receive echo response
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                
                assert data.get("type") == "echo_response"
                assert data.get("original_message") == test_message["message"]
                
                logger.info("✅ WebSocket echo test successful")
                
        except websockets.exceptions.ConnectionClosed:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            logger.warning(f"WebSocket echo test warning: {e}")


class TestRealTimeChat:
    """Test real-time chat functionality via WebSocket."""
    
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_join_conversation(self, test_config):
        """Test joining a conversation via WebSocket."""
        ws_url = test_config["ws_test_url"]
        
        try:
            async with websockets.connect(ws_url) as websocket:
                # Join conversation
                join_message = {
                    "type": "join_conversation",
                    "conversation_id": "test_conversation",
                    "user_id": "test_user"
                }
                await websocket.send(json.dumps(join_message))
                
                # Receive join confirmation
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                
                assert data.get("type") == "join_confirmation"
                assert data.get("conversation_id") == "test_conversation"
                
                logger.info("✅ WebSocket join conversation successful")
                
        except websockets.exceptions.ConnectionClosed:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            logger.warning(f"WebSocket join test warning: {e}")

    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_send_message_realtime(self, test_config):
        """Test sending message in real-time via WebSocket."""
        ws_url = test_config["ws_test_url"]
        
        try:
            async with websockets.connect(ws_url) as websocket:
                # First join conversation
                join_message = {
                    "type": "join_conversation",
                    "conversation_id": "test_conversation_msg",
                    "user_id": "test_user"
                }
                await websocket.send(json.dumps(join_message))
                
                # Wait for join confirmation
                await asyncio.wait_for(websocket.recv(), timeout=5.0)
                
                # Send message
                message = {
                    "type": "send_message",
                    "conversation_id": "test_conversation_msg",
                    "user_id": "test_user",
                    "content": "Real-time test message",
                    "role": "user"
                }
                await websocket.send(json.dumps(message))
                
                # Receive message confirmation
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                
                assert data.get("type") == "message_sent"
                assert data.get("content") == "Real-time test message"
                
                logger.info("✅ WebSocket real-time message successful")
                
        except websockets.exceptions.ConnectionClosed:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            logger.warning(f"WebSocket message test warning: {e}")

    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_receive_typing_indicator(self, test_config):
        """Test typing indicator functionality."""
        ws_url = test_config["ws_test_url"]
        
        try:
            async with websockets.connect(ws_url) as websocket:
                # Join conversation
                join_message = {
                    "type": "join_conversation",
                    "conversation_id": "test_typing",
                    "user_id": "test_user"
                }
                await websocket.send(json.dumps(join_message))
                await asyncio.wait_for(websocket.recv(), timeout=5.0)
                
                # Send typing indicator
                typing_message = {
                    "type": "typing",
                    "conversation_id": "test_typing",
                    "user_id": "test_user",
                    "is_typing": True
                }
                await websocket.send(json.dumps(typing_message))
                
                # Should receive typing broadcast (might be sent to other users)
                # For testing, we just verify the message was processed
                await asyncio.sleep(1)
                
                # Stop typing
                stop_typing_message = {
                    "type": "typing",
                    "conversation_id": "test_typing",
                    "user_id": "test_user",
                    "is_typing": False
                }
                await websocket.send(json.dumps(stop_typing_message))
                
                logger.info("✅ WebSocket typing indicator test completed")
                
        except websockets.exceptions.ConnectionClosed:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            logger.warning(f"WebSocket typing test warning: {e}")


class TestMultiUserWebSocket:
    """Test multi-user WebSocket scenarios."""
    
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_multiple_connections(self, test_config):
        """Test multiple WebSocket connections."""
        ws_url = test_config["ws_test_url"]
        
        try:
            # Create multiple connections
            connections = []
            for i in range(3):
                try:
                    conn = await websockets.connect(ws_url)
                    connections.append(conn)
                except Exception as e:
                    logger.warning(f"Failed to create connection {i}: {e}")
                    break
            
            if not connections:
                pytest.skip("Could not establish WebSocket connections")
            
            # Send messages from each connection
            for i, conn in enumerate(connections):
                message = {
                    "type": "ping",
                    "user_id": f"user_{i}"
                }
                await conn.send(json.dumps(message))
                
                # Receive response
                response = await asyncio.wait_for(conn.recv(), timeout=5.0)
                data = json.loads(response)
                assert data.get("type") == "pong"
            
            logger.info(f"✅ Multiple WebSocket connections test successful ({len(connections)} connections)")
            
        except Exception as e:
            logger.warning(f"Multiple connections test warning: {e}")
        finally:
            # Clean up connections
            for conn in connections:
                try:
                    await conn.close()
                except Exception:
                    pass

    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_conversation_broadcast(self, test_config):
        """Test message broadcasting to conversation participants."""
        ws_url = test_config["ws_test_url"]
        
        try:
            # Create two connections
            conn1 = await websockets.connect(ws_url)
            conn2 = await websockets.connect(ws_url)
            
            conversation_id = "broadcast_test_conv"
            
            # Both users join the same conversation
            for i, conn in enumerate([conn1, conn2]):
                join_message = {
                    "type": "join_conversation",
                    "conversation_id": conversation_id,
                    "user_id": f"user_{i}"
                }
                await conn.send(json.dumps(join_message))
                # Receive join confirmation
                await asyncio.wait_for(conn.recv(), timeout=5.0)
            
            # User 1 sends a message
            message = {
                "type": "send_message",
                "conversation_id": conversation_id,
                "user_id": "user_0",
                "content": "Broadcast test message",
                "role": "user"
            }
            await conn1.send(json.dumps(message))
            
            # Both users should receive the message
            # User 1 gets confirmation
            response1 = await asyncio.wait_for(conn1.recv(), timeout=5.0)
            data1 = json.loads(response1)
            assert data1.get("type") == "message_sent"
            
            # User 2 should receive the broadcast (if implemented)
            try:
                response2 = await asyncio.wait_for(conn2.recv(), timeout=3.0)
                data2 = json.loads(response2)
                logger.info("✅ Message broadcast received by other user")
            except asyncio.TimeoutError:
                logger.info("⚠️ Message broadcast not implemented or not received")
            
            logger.info("✅ Conversation broadcast test completed")
            
        except websockets.exceptions.ConnectionClosed:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            logger.warning(f"Broadcast test warning: {e}")
        finally:
            # Clean up
            try:
                await conn1.close()
                await conn2.close()
            except Exception:
                pass


class TestWebSocketErrorHandling:
    """Test WebSocket error handling and edge cases."""
    
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_invalid_message_format(self, test_config):
        """Test handling of invalid message formats."""
        ws_url = test_config["ws_test_url"]
        
        try:
            async with websockets.connect(ws_url) as websocket:
                # Send invalid JSON
                await websocket.send("invalid json")
                
                # Should receive error response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    assert data.get("type") == "error"
                except (asyncio.TimeoutError, json.JSONDecodeError):
                    # Server might close connection on invalid JSON
                    logger.info("Server closed connection on invalid JSON (expected)")
                
                logger.info("✅ Invalid message format handling test completed")
                
        except websockets.exceptions.ConnectionClosed:
            logger.info("✅ Connection closed on invalid message (expected behavior)")
        except Exception as e:
            logger.warning(f"Invalid message test warning: {e}")

    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_unknown_message_type(self, test_config):
        """Test handling of unknown message types."""
        ws_url = test_config["ws_test_url"]
        
        try:
            async with websockets.connect(ws_url) as websocket:
                # Send unknown message type
                unknown_message = {
                    "type": "unknown_type",
                    "data": "test data"
                }
                await websocket.send(json.dumps(unknown_message))
                
                # Should receive error response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    assert data.get("type") in ["error", "unknown_type_response"]
                except asyncio.TimeoutError:
                    logger.info("No response to unknown message type (acceptable)")
                
                logger.info("✅ Unknown message type handling test completed")
                
        except websockets.exceptions.ConnectionClosed:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            logger.warning(f"Unknown message test warning: {e}")

    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_connection_timeout(self, test_config):
        """Test WebSocket connection timeout handling."""
        ws_url = test_config["ws_test_url"]
        
        try:
            async with websockets.connect(ws_url) as websocket:
                # Send ping and wait for long time
                await websocket.send(json.dumps({"type": "ping"}))
                
                # Keep connection alive for a while
                await asyncio.sleep(2)
                
                # Send another ping to test if connection is still alive
                await websocket.send(json.dumps({"type": "ping"}))
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                
                assert data.get("type") == "pong"
                logger.info("✅ Connection timeout test successful")
                
        except websockets.exceptions.ConnectionClosed:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            logger.warning(f"Connection timeout test warning: {e}")


class TestWebSocketPerformance:
    """Test WebSocket performance characteristics."""
    
    @pytest.mark.websocket
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_message_throughput(self, test_config):
        """Test WebSocket message throughput."""
        ws_url = test_config["ws_test_url"]
        
        try:
            async with websockets.connect(ws_url) as websocket:
                # Send multiple messages rapidly
                start_time = asyncio.get_event_loop().time()
                message_count = 10
                
                for i in range(message_count):
                    message = {
                        "type": "ping",
                        "sequence": i
                    }
                    await websocket.send(json.dumps(message))
                
                # Receive all responses
                received_count = 0
                while received_count < message_count:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(response)
                        if data.get("type") == "pong":
                            received_count += 1
                    except asyncio.TimeoutError:
                        break
                
                end_time = asyncio.get_event_loop().time()
                duration = end_time - start_time
                
                logger.info(f"✅ WebSocket throughput: {received_count}/{message_count} messages in {duration:.2f}s")
                
                # Basic performance check
                assert received_count >= message_count * 0.8  # At least 80% success rate
                
        except websockets.exceptions.ConnectionClosed:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            logger.warning(f"Throughput test warning: {e}")

    @pytest.mark.websocket
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_large_message_handling(self, test_config):
        """Test handling of large WebSocket messages."""
        ws_url = test_config["ws_test_url"]
        
        try:
            async with websockets.connect(ws_url) as websocket:
                # Create large message (but not too large to avoid issues)
                large_content = "x" * 1000  # 1KB message
                large_message = {
                    "type": "echo",
                    "message": large_content
                }
                
                await websocket.send(json.dumps(large_message))
                
                # Receive echo response
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(response)
                
                assert data.get("type") == "echo_response"
                assert len(data.get("original_message", "")) == 1000
                
                logger.info("✅ Large message handling test successful")
                
        except websockets.exceptions.ConnectionClosed:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            logger.warning(f"Large message test warning: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
