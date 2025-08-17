#!/usr/bin/env python3
"""
🌊 STREAMING RESPONSE TEST
=========================
Test streaming legal chat responses
"""
import asyncio
import aiohttp
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='🌊 [STREAM-TEST] %(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_streaming_flow():
    """Test complete streaming flow"""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Send legal query to get conversation_id
        logger.info("📤 Step 1: Sending legal query...")
        
        query_payload = {
            "user_id": f"stream_test_{int(time.time())}",
            "message": "Tôi có quyền khởi kiện nếu chủ nhà đuổi tôi ra khỏi nhà trọ mà không báo trước không?",
            "conversation_id": None
        }
        
        try:
            async with session.post(f"{base_url}/api/legal-chat/send-query", json=query_payload) as response:
                if response.status == 200:
                    query_result = await response.json()
                    logger.info(f"✅ Query sent successfully: {query_result}")
                    conversation_id = query_result.get("conversation_id")
                    
                    if conversation_id:
                        # Step 2: Test streaming response
                        logger.info(f"🌊 Step 2: Testing streaming response for conversation: {conversation_id}")
                        await test_stream_response(session, base_url, conversation_id)
                        
                        # Step 3: Check if we need to trigger generation
                        if query_result.get("status") == "waiting_for_generation":
                            logger.info("🔄 Step 3: Triggering response generation...")
                            await trigger_generation(session, base_url, conversation_id, query_payload["user_id"])
                            
                            # Wait a bit and test streaming again
                            await asyncio.sleep(2)
                            logger.info("🌊 Step 4: Testing streaming after generation...")
                            await test_stream_response(session, base_url, conversation_id)
                    else:
                        logger.error("❌ No conversation_id returned")
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Query failed: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Error in query step: {e}")

async def test_stream_response(session, base_url, conversation_id):
    """Test streaming response for given conversation"""
    start_time = time.time()
    tokens_received = 0
    chunks_received = 0
    first_token_time = None
    
    try:
        async with session.get(f"{base_url}/api/legal-chat/stream-legal-response/{conversation_id}") as response:
            logger.info(f"📡 Streaming response status: {response.status}")
            
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"❌ Streaming failed: {response.status} - {error_text}")
                return
            
            logger.info("🔄 Reading streaming chunks...")
            
            async for chunk in response.content.iter_chunked(1024):
                if chunk:
                    current_time = time.time()
                    if first_token_time is None:
                        first_token_time = current_time
                        logger.info(f"⚡ First token received at {round((current_time - start_time) * 1000, 2)}ms")
                    
                    chunks_received += 1
                    chunk_text = chunk.decode('utf-8', errors='ignore')
                    tokens_received += len(chunk_text)
                    
                    # Log sample of received data
                    if chunks_received <= 5:
                        logger.info(f"📦 Chunk {chunks_received}: {chunk_text[:100]}...")
                    
                    # Check for completion
                    if '[DONE]' in chunk_text:
                        logger.info("✅ Received [DONE] marker")
                        break
                    elif '[ERROR]' in chunk_text:
                        logger.error(f"❌ Received error: {chunk_text}")
                        break
            
            total_time = time.time() - start_time
            first_token_latency = (first_token_time - start_time) if first_token_time else 0
            
            logger.info("📊 Streaming Statistics:")
            logger.info(f"   📦 Total chunks: {chunks_received}")
            logger.info(f"   📝 Total characters: {tokens_received}")
            logger.info(f"   ⏱️ Total time: {round(total_time * 1000, 2)}ms")
            logger.info(f"   ⚡ First token latency: {round(first_token_latency * 1000, 2)}ms")
            logger.info(f"   📈 Average chars/sec: {round(tokens_received / total_time, 2) if total_time > 0 else 0}")
            
    except Exception as e:
        logger.error(f"❌ Streaming error: {e}")

async def trigger_generation(session, base_url, conversation_id, user_id):
    """Trigger response generation if needed"""
    generation_payload = {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "rewrite_query": "query about tenant rights",
        "use_web_search": True,
        "use_retrieval": True
    }
    
    try:
        async with session.post(f"{base_url}/api/legal-chat/generate-legal-response", json=generation_payload) as response:
            if response.status == 200:
                result = await response.json()
                logger.info(f"✅ Generation triggered: {result}")
            else:
                error_text = await response.text()
                logger.error(f"❌ Generation failed: {response.status} - {error_text}")
                
    except Exception as e:
        logger.error(f"❌ Generation error: {e}")

# Test different scenarios
async def test_multiple_scenarios():
    """Test multiple streaming scenarios"""
    logger.info("🚀 Starting comprehensive streaming tests...")
    
    scenarios = [
        ("Basic Legal Query", "Tôi muốn biết về quyền lợi của người thuê nhà"),
        ("Contract Query", "Hợp đồng thuê nhà có những điều khoản bắt buộc nào?"),
        ("Dispute Query", "Làm thế nào để giải quyết tranh chấp với chủ nhà?")
    ]
    
    for scenario_name, query in scenarios:
        logger.info(f"\n🎯 Testing scenario: {scenario_name}")
        logger.info(f"📝 Query: {query}")
        
        # Create a mini test for this scenario
        base_url = "http://localhost:8000"
        
        async with aiohttp.ClientSession() as session:
            query_payload = {
                "user_id": f"test_{scenario_name.lower().replace(' ', '_')}_{int(time.time())}",
                "message": query,
                "conversation_id": None
            }
            
            try:
                async with session.post(f"{base_url}/api/legal-chat/send-query", json=query_payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        conversation_id = result.get("conversation_id")
                        if conversation_id:
                            await test_stream_response(session, base_url, conversation_id)
                        else:
                            logger.warning(f"⚠️ No conversation_id for {scenario_name}")
                    else:
                        logger.error(f"❌ Query failed for {scenario_name}: {response.status}")
                        
            except Exception as e:
                logger.error(f"❌ Scenario {scenario_name} failed: {e}")
        
        # Small delay between scenarios
        await asyncio.sleep(1)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "multiple":
        asyncio.run(test_multiple_scenarios())
    else:
        asyncio.run(test_streaming_flow())
