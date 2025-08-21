# Chat Workflow Steps

This directory contains the Motia steps for the OpenAI chat workflow.

## Structure

### API Steps (`api-steps/`)
- `api-chat.step.py` - POST endpoint to receive chat requests
- `api-get-response.step.py` - GET endpoint to retrieve chat responses

### Event Steps (`event-steps/`)
- `chat-starter.step.py` - NOOP step for workflow triggering in workbench
- `openai-processor.step.py` - Processes chat messages with OpenAI API
- `response-handler.step.py` - Handles and stores chat responses

## Workflow Flow

1. **User Request** → `POST /api/chat` (api-chat.step.py)
2. **Event Emission** → `chat.process` event
3. **OpenAI Processing** → openai-processor.step.py processes the message
4. **Response Emission** → `chat.response` event
5. **Response Storage** → response-handler.step.py stores the result
6. **User Retrieval** → `GET /api/chat/{trace_id}/response` (api-get-response.step.py)

## Environment Variables

- `OPENAI_API_KEY` - Required for OpenAI API access

## Usage

1. Send POST request to `/api/chat` with message
2. Receive trace_id in response
3. Poll GET `/api/chat/{trace_id}/response` for result
