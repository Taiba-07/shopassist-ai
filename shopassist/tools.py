import random

ORDER_DB = {
    "123": {
        "status": "Out for Delivery",
        "detail": "Your order is out for delivery and will arrive today by 7 PM.",
        "item": "Wireless Headphones",
        "courier": "BlueDart",
        "eta": "Today by 7:00 PM"
    },
    "456": {
        "status": "Shipped",
        "detail": "Your order has been shipped and is in transit.",
        "item": "Running Shoes",
        "courier": "Delhivery",
        "eta": "2–3 business days"
    },
    "789": {
        "status": "Delivered",
        "detail": "Your order was delivered on April 17, 2026.",
        "item": "Smart Watch",
        "courier": "Ekart",
        "eta": "Already delivered"
    },
    "321": {
        "status": "Processing",
        "detail": "Your order is being processed and will be packed soon.",
        "item": "Laptop Bag",
        "courier": "Xpressbees",
        "eta": "5–7 business days"
    },
    "654": {
        "status": "Cancelled",
        "detail": "Your order was cancelled as per your request. Refund initiated.",
        "item": "Bluetooth Speaker",
        "courier": "N/A",
        "eta": "N/A"
    },
}


def track_order(order_id: str) -> str:
    order_id = order_id.strip()
    if order_id in ORDER_DB:
        order = ORDER_DB[order_id]
        return (
            f"📦 Order #{order_id} — {order['item']}\n"
            f"Status: {order['status']}\n"
            f"Courier: {order['courier']}\n"
            f"ETA: {order['eta']}\n"
            f"{order['detail']}"
        )
    else:
        return (
            f"❌ Order #{order_id} not found in our system. "
            "Please double-check your order ID or contact support at support@shopassist.com."
        )