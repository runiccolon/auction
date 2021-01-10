from django_redis import get_redis_connection
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auction.settings")

conn = get_redis_connection()
conn.set(13453514647,1234, ex=30)
print('ok')
s = conn.get(13453514647)
print(s)
