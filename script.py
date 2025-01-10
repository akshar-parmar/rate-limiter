from flask import Flask,request
import redis
app = Flask(__name__)

#Connect to redis server
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
RATE_LIMIT_COUNT = 4

#steps
#1 : check if key exist in redis
#2 if it does not exist , then it means user is hitting the api for the first time
#3 register the key with value 1 in redis
#4 if key exist then it means, user has hit the api earlier, 
#check if the value of that key if count is equal or greater then rate_limit_count show rate limit exceeded message.
#or else if the value is less then count then simple increment the value, and maintain the ttl, means expire of the key

@app.before_request
def rate_limiter_check():
    user_id = request.headers.get("User-Agent")
    print(f"user_id is {user_id}")
    redis_key = f"user_id_{user_id}"
    if(redis_client.exists(redis_key)!=1):
        # key not existed
        print(f"setting the key in redis : {redis_key}")
        redis_client.setex(redis_key,60,1)
    else:
        #key already existed
        print(f"key already exist")
        count = int(redis_client.get(redis_key))
        if(count >= RATE_LIMIT_COUNT):
            return "rate limit exceeded", 429
        else:
            redis_client.incr(redis_key)
            #if we want to reset the expiry un comment the below line
            # redis_client.expire(redis_key,60)
            print(f"{redis_key} : {count}")

@app.route('/api/users', methods=['GET'])
def hello_world():
    return "Hello, Flask!", 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
