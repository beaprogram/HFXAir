from firebase_admin import messaging
import logging

logger = logging.getLogger(__name__)

def send_push(token: str, title: str, body: str):
    logger.info(f"send_push called with token: {token[:20]}..., title: {title}, body: {body}")
    
    # Validate inputs
    if not token:
        logger.error("Token is None or empty")
        return False
    
    if not isinstance(token, str):
        logger.error(f"Token is not a string, type: {type(token)}")
        return False
    
    logger.info("Creating Firebase message...")
    try:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=token
        )
        logger.info("Message created successfully")
    except Exception as e:
        logger.error(f"Failed to create message: {e}", exc_info=True)
        return False
    
    logger.info("Sending message via Firebase...")
    try:
        response = messaging.send(message)
        logger.info(f"Push sent successfully. Response: {response}")
        print("Push sent:", response)
        return True
    except ValueError as e:
        logger.error(f"ValueError - Invalid input: {e}", exc_info=True)
        print("Push failed (ValueError):", e)
        return False
    except Exception as e:
        logger.error(f"Push failed with exception: {type(e).__name__}: {e}", exc_info=True)
        print(f"Push failed ({type(e).__name__}):", e)
        return False