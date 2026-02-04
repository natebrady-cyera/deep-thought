"""
Claude AI service via AWS Bedrock.
"""
import boto3
import json
from typing import List, Dict, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def get_bedrock_client():
    """
    Get AWS Bedrock runtime client.
    Uses AWS profile from environment for local development.
    """
    session = boto3.Session(
        profile_name=settings.aws_profile,
        region_name=settings.aws_bedrock_region
    )

    return session.client('bedrock-runtime')


def build_canvas_context(canvas_data: Dict[str, Any], nodes_data: List[Dict[str, Any]]) -> str:
    """
    Build context string from canvas and nodes for Claude.

    Args:
        canvas_data: Canvas information
        nodes_data: List of node data

    Returns:
        Formatted context string
    """
    context = f"# Deal Canvas: {canvas_data['name']}\n\n"

    if canvas_data.get('description'):
        context += f"**Description**: {canvas_data['description']}\n\n"

    context += "## Canvas Contents\n\n"

    if not nodes_data:
        context += "*(No nodes yet - empty canvas)*\n"
    else:
        for node in nodes_data:
            # Skip nodes excluded from context
            if node.get('exclude_from_context'):
                continue

            context += f"### {node['title']} ({node['node_type']})\n"

            # Add node data
            if node.get('data'):
                for key, value in node['data'].items():
                    if isinstance(value, str) and value.strip():
                        context += f"**{key}**: {value}\n"

            context += "\n"

    return context


def chat_with_claude(
    messages: List[Dict[str, str]],
    system_prompt: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 1.0,
) -> Dict[str, Any]:
    """
    Send messages to Claude via AWS Bedrock and get response.

    Args:
        messages: List of message dicts with 'role' and 'content'
        system_prompt: Optional system prompt
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature (0-1)

    Returns:
        Response dict with content and usage stats
    """
    try:
        client = get_bedrock_client()

        # Build request body
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if system_prompt:
            request_body["system"] = system_prompt

        logger.info(f"Calling Bedrock with {len(messages)} messages, model: {settings.aws_bedrock_model_id}")

        # Call Bedrock
        response = client.invoke_model(
            modelId=settings.aws_bedrock_model_id,
            body=json.dumps(request_body)
        )

        # Parse response
        response_body = json.loads(response['body'].read())

        logger.info(f"Bedrock response received, usage: {response_body.get('usage', {})}")

        return {
            "content": response_body['content'][0]['text'],
            "usage": response_body.get('usage', {}),
            "stop_reason": response_body.get('stop_reason'),
            "model": response_body.get('model'),
        }

    except Exception as e:
        logger.error(f"Error calling Claude via Bedrock: {e}", exc_info=True)
        raise Exception(f"Failed to get AI response: {str(e)}")


def create_sales_assistant_prompt(canvas_context: str) -> str:
    """
    Create system prompt for sales assistant chat.

    Args:
        canvas_context: Formatted context from canvas

    Returns:
        System prompt string
    """
    return f"""You are a helpful AI assistant for Deep Thought, a sales deal intelligence platform for Cyera (a data security company specializing in DSPM and DLP).

Your role is to help sales professionals manage and strategize on their enterprise security deals by analyzing the deal canvas and providing insights, recommendations, and guidance.

## Current Deal Context

{canvas_context}

## Your Capabilities

1. **Deal Analysis**: Analyze the current state of the deal based on the canvas information
2. **Strategic Guidance**: Provide recommendations on next steps and strategies
3. **Question Discovery**: Identify questions that need to be answered to progress the deal
4. **Risk Assessment**: Highlight potential risks or concerns
5. **Product Fit**: Discuss how Cyera's solutions might address the customer's needs

## Guidelines

- Be concise and actionable in your responses
- Focus on practical sales advice
- Ask clarifying questions when you need more information
- Reference specific information from the canvas when relevant
- Help prioritize next steps

How can I help you with this deal?"""


def create_whats_next_prompt(canvas_context: str) -> str:
    """
    Create prompt for "What's Next" recommendations.

    Args:
        canvas_context: Formatted context from canvas

    Returns:
        Prompt string for what's next analysis
    """
    return f"""Based on the following deal canvas, provide a concise analysis of what should happen next to move this deal forward.

{canvas_context}

Please provide:

1. **Immediate Next Steps** (2-3 most important actions)
2. **Key Questions** (What we need to learn/clarify)
3. **Potential Risks** (What could derail this deal)
4. **Recommended Focus Areas** (Where to invest time/energy)

Keep your response focused and actionable."""
