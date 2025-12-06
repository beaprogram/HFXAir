# helper_firebase_notification.py

import logging
from typing import List, Dict
import firebase_admin
from firebase_admin import messaging, credentials
import os
from pathlib import Path
import requests

from flask_app.constants import (
    HTTP_OK,
    FCM_BATCH_SIZE,
    EXPO_BATCH_SIZE,
    NOTIF_HTTP_TIMEOUT
)

logger = logging.getLogger(__name__)


def send_push(token: str, title: str, body: str) -> bool:
    """Send a push notification to a single FCM token.

    Returns True on success, False on failure.
    """
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


def _fetch_tokens_for_subscription(ticket_no: str = None, flight_id: str = None) -> List[str]:
    """Fetch expo/FCM tokens from the user_subscriptions table for given ticket or flight.

    Returns a list of tokens (may be empty).
    """
    if not ticket_no and not flight_id:
        return []

    try:
        # Import here to avoid circular imports at module import time
        from flask_app.app import get_db_connection

        conn = get_db_connection()
        cur = conn.cursor()

        if ticket_no and flight_id:
            cur.execute(
                "SELECT DISTINCT expo_token FROM user_subscriptions WHERE (ticket_no = %s OR flight_id = %s) AND expo_token IS NOT NULL",
                (ticket_no, flight_id),
            )
        elif ticket_no:
            cur.execute(
                "SELECT DISTINCT expo_token FROM user_subscriptions WHERE ticket_no = %s AND expo_token IS NOT NULL",
                (ticket_no,),
            )
        else:
            cur.execute(
                "SELECT DISTINCT expo_token FROM user_subscriptions WHERE flight_id = %s AND expo_token IS NOT NULL",
                (flight_id,),
            )

        rows = cur.fetchall()
        tokens = [r[0] for r in rows if r and r[0]]

        cur.close()
        conn.close()

        return tokens
    except Exception as e:
        logger.error(f"Error fetching tokens from DB: {e}")
        return []


def notify_subscribers(ticket_no: str = None, flight_id: str = None, title: str = "", body: str = "") -> Dict[str, object]:
    """Query subscriptions and send notifications to all matched tokens.

    Returns a summary dict with keys: total_tokens, sent_count, failed_count, failed_tokens.
    """
    # Ensure Firebase Admin SDK is initialized (use same creds as package if available)
    try:
        firebase_admin.get_app()
    except ValueError:
        # Not initialized yet - try to initialize using FIREBASE_CREDENTIALS_PATH or default path
        firebase_creds_path = os.getenv(
            'FIREBASE_CREDENTIALS_PATH',
            'config/testing-hfxair-firebase-adminsdk-fbsvc-c584fb82ef.json'
        )
        if not os.path.isabs(firebase_creds_path):
            base_dir = Path(__file__).resolve().parent.parent
            firebase_creds_path = str(base_dir / firebase_creds_path)
        try:
            cred = credentials.Certificate(firebase_creds_path)
            firebase_admin.initialize_app(cred)
            logger.info(f"Initialized Firebase Admin with credentials at {firebase_creds_path}")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")

    tokens = _fetch_tokens_for_subscription(ticket_no=ticket_no, flight_id=flight_id)

    if not tokens:
        logger.info("No subscription tokens found for given ticket_no/flight_id")
        return {"total_tokens": 0, "sent_count": 0, "failed_count": 0, "failed_tokens": []}

    # Separate Expo tokens (ExponentPushToken[...]) vs FCM tokens
    expo_tokens = [t for t in tokens if isinstance(t, str) and t.startswith("ExponentPushToken")]
    fcm_tokens = [t for t in tokens if isinstance(t, str) and not t.startswith("ExponentPushToken")]

    sent_total = 0
    failed_total = 0
    failed_tokens = []

    # 1) Send FCM tokens via Firebase Admin (multicast, up to 500 per batch)
    if fcm_tokens:
        BATCH_SIZE = FCM_BATCH_SIZE
        for i in range(0, len(fcm_tokens), BATCH_SIZE):
            batch = fcm_tokens[i:i+BATCH_SIZE]
            try:
                # Build list of Message objects
                messages = [
                    messaging.Message(
                        notification=messaging.Notification(title=title, body=body),
                        token=t,
                        data={"click_action": "FLUTTER_NOTIFICATION_CLICK"}
                    ) for t in batch
                ]

                # Prefer bulk send APIs when available
                if hasattr(messaging, 'send_multicast'):
                    multicast = messaging.MulticastMessage(notification=messaging.Notification(title=title, body=body), tokens=batch, data={"click_action": "FLUTTER_NOTIFICATION_CLICK"})
                    response = messaging.send_multicast(multicast)
                    sent_total += getattr(response, 'success_count', 0)
                    failed_total += getattr(response, 'failure_count', 0)
                    for idx, resp in enumerate(getattr(response, 'responses', [])):
                        if not getattr(resp, 'success', False):
                            failed_tokens.append(batch[idx])
                    logger.info(f"FCM batch sent (multicast): success={getattr(response, 'success_count', 0)} failures={getattr(response, 'failure_count', 0)}")
                elif hasattr(messaging, 'send_all'):
                    response = messaging.send_all(messages)
                    sent_total += getattr(response, 'success_count', 0)
                    failed_total += getattr(response, 'failure_count', 0)
                    for idx, resp in enumerate(getattr(response, 'responses', [])):
                        if not getattr(resp, 'success', False):
                            failed_tokens.append(batch[idx])
                    logger.info(f"FCM batch sent (send_all): success={getattr(response, 'success_count', 0)} failures={getattr(response, 'failure_count', 0)}")
                else:
                    # Fallback: send messages one by one
                    for t_idx, msg in enumerate(messages):
                        try:
                            messaging.send(msg)
                            sent_total += 1
                        except Exception as e:
                            failed_total += 1
                            failed_tokens.append(batch[t_idx])
                            logger.error(f"Failed to send FCM message to token {batch[t_idx]}: {e}")
                    logger.info(f"FCM batch sent (per-message fallback): sent={sent_total} failed={failed_total}")
            except Exception as e:
                logger.error(f"Error sending FCM multicast batch: {e}")
                failed_total += len(batch)
                failed_tokens.extend(batch)

    # 2) Send Expo tokens via Expo Push API (chunked, up to 100 per request)
    if expo_tokens:
        EXPO_BATCH = EXPO_BATCH_SIZE
        expo_endpoint = "https://exp.host/--/api/v2/push/send"
        headers = {"Accept": "application/json", "Accept-encoding": "gzip, deflate", "Content-Type": "application/json"}
        for i in range(0, len(expo_tokens), EXPO_BATCH):
            batch = expo_tokens[i:i+EXPO_BATCH]
            messages = []
            for t in batch:
                messages.append({
                    "to": t,
                    "title": title,
                    "body": body,
                    "data": {"click_action": "FLUTTER_NOTIFICATION_CLICK"}
                })

            try:
                resp = requests.post(expo_endpoint, json=messages, headers=headers, timeout=NOTIF_HTTP_TIMEOUT)
                if resp.status_code == HTTP_OK:
                    # The Expo response contains tickets; assume success for delivered tickets
                    # We can't know exact delivered count without polling receipts; count all as sent here
                    sent_total += len(batch)
                    logger.info(f"Expo batch sent: count={len(batch)}")
                else:
                    logger.error(f"Expo push failed: status={resp.status_code} body={resp.text}")
                    failed_total += len(batch)
                    failed_tokens.extend(batch)
            except Exception as e:
                logger.error(f"Error sending Expo push batch: {e}")
                failed_total += len(batch)
                failed_tokens.extend(batch)

    return {
        "total_tokens": len(tokens),
        "sent_count": sent_total,
        "failed_count": failed_total,
        "failed_tokens": failed_tokens,
    }