# nexusflow/services/webhook_service.py
import httpx
import hmac
import hashlib
import json
from typing import Dict, Any, List

class WebhookService:
    """Service for managing webhooks for flow events"""
    
    async def send_webhook(self, url: str, event_type: str, payload: Dict[str, Any], secret: Optional[str] = None):
        """
        Send a webhook to the specified URL
        
        Args:
            url: Webhook URL
            event_type: Type of event (e.g., "flow.completed", "flow.failed")
            payload: Event payload
            secret: Webhook secret for signature verification
        """
        # Create the full payload with metadata
        full_payload = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": payload
        }
        
        # Create headers
        headers = {
            "Content-Type": "application/json",
            "X-NexusFlow-Event": event_type
        }
        
        # Add signature if secret is provided
        if secret:
            payload_bytes = json.dumps(full_payload).encode()
            signature = hmac.new(
                secret.encode(),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            headers["X-NexusFlow-Signature"] = signature
        
        # Send the webhook
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=full_payload,
                    headers=headers,
                    timeout=10.0
                )
                return response.status_code < 400
            except Exception as e:
                logger.error(f"Error sending webhook to {url}: {str(e)}")
                return False
