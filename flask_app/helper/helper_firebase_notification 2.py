# helper_firebase_notification.py

import logging
from firebase_admin import messaging

logger = logging.getLogger(__name__)


def send_push(token, title, body):

    if not token:
        logger.error("No token provided for push notification")
        return False
    
    if not title or not body:
        logger.error("Title and body are required for push notification")
        return False
    
    try:
        # Create the message
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=token,
            # Optional: Add data payload
            data={
                'click_action': 'FLUTTER_NOTIFICATION_CLICK',
            }
        )
        
        # Send the message
        response = messaging.send(message)
        logger.info(f"Successfully sent message: {response}")
        return True
        
    except messaging.UnregisteredError:
        logger.warning(f"Token is unregistered or invalid: {token}")
        return False
    except messaging.InvalidArgumentError as e:
        logger.error(f"Invalid argument: {e}")
        return False
    except Exception as e:
        logger.error(f"Error sending push notification: {e}")
        return False

