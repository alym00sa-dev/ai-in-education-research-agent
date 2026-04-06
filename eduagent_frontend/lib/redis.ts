import Redis from "ioredis";

declare global {
  // eslint-disable-next-line no-var
  var _redis: Redis | undefined;
}

function getRedis(): Redis | null {
  if (!process.env.REDIS_URL) return null;
  if (!global._redis) {
    global._redis = new Redis(process.env.REDIS_URL, {
      maxRetriesPerRequest: 3,
      connectTimeout: 5000,
    });
  }
  return global._redis;
}

export default getRedis;
