from flask import Flask, jsonify, request
import requests
import mymessage_pb2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import random
import binascii
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# إعدادات التشفير
AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'
keys = set()  # مجموعة لتخزين المفاتيح الصالحة

# المفتاح الداخلي (تم تغييره إلى "22")

# قاموس لتخزين المستخدمين المضافين
users = {}

# دالة إنشاء مفتاح UID عشوائي
def generate_random_uid_64():
    return random.randint(1, 9_223_372_036_854_775_807)

# دالة تشفير الرسالة
def encrypt_message(key, iv, plaintext):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(plaintext, AES.block_size)
    encrypted_message = cipher.encrypt(padded_message)
    return encrypted_message

# دالة جلب التوكينات
def fetch_tokens():
    token_url = "https://api-get-jwt-by-alinas.vercel.app/get?uid=4983756423&password=F24B336BFCAFA17C36F954C83A0E7E806E221028E9C642C603E9D47934754A6B"

    try:
        response = requests.get(token_url, timeout=5)

        if response.status_code == 200:
            data = response.json()

            # التحقق من النجاح
            if data.get("status") == "success":
                return data.get("token")

            print("API returned failure status")
            return None

        else:
            print(f"Failed to fetch token, status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error fetching token: {e}")
        return None

# دالة إرسال طلبات الرسائل
def send_request(token, hex_encrypted_data):
    url = "https://loginbp.ggpolarbear.com/RequestAddingFriend"
    payload = bytes.fromhex(hex_encrypted_data)
    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/x-www-form-urlencoded",
        'Expect': "100-continue",
        'Authorization': f"Bearer {token}",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB53"
    }

    # تجاوز التحقق من الشهادة
    response = requests.post(url, data=payload, headers=headers)
    return response.status_code
    
    
def remove(token, hex_encrypted_data):
    url = "https://loginbp.ggpolarbear.com/RemoveFriend"
    payload = bytes.fromhex(hex_encrypted_data)
    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/x-www-form-urlencoded",
        'Expect': "100-continue",
        'Authorization': f"Bearer {token}",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB53"
    }

    # تجاوز التحقق من الشهادة
    response = requests.post(url, data=payload, headers=headers,verify=False)
    print(response.status_code)
    print(response.text)

# إضافة مفتاح جديد (يتم الاحتفاظ به ولكن لن يتم استخدامه للتحقق)

# إرسال طلبات الرسائل باستخدام مفتاح (يتم الاحتفاظ به ولكن لن يتم استخدامه للتحقق)
@app.route('/request', methods=['GET'])
def send_spam():
    user_id = request.args.get('uid')

    # معالجة الطلبات
    message = mymessage_pb2.MyMessage()
    message.field1 = 9797549324
    message.field2 = int(user_id)
    message.field3 = 22

    serialized_message = message.SerializeToString()
    encrypted_data = encrypt_message(AES_KEY, AES_IV, serialized_message)
    hex_encrypted_data = binascii.hexlify(encrypted_data).decode('utf-8')

    tokens = fetch_tokens()
    if not tokens:
        return jsonify({"error": "No tokens available"}), 500

    success_count = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(lambda token: send_request(token, hex_encrypted_data), tokens)

    success_count = sum(1 for result in results if result)

    return jsonify({"message": f"SUCCESSFULLY SENT {success_count} FRIEND REQUESTS"}), 200

# إزالة صديق باستخدام UID (يتحقق من .المفتاح الداخلي)
@app.route('/remove/<uid>', methods=['GET'])
def remove_friend(uid):
    # التحقق من المفتاح الداخلي

    message = mymessage_pb2.MyMessage()
    message.field1 = 9797549324
    message.field2 = int(uid)
    message.field3 = 22
    print(uid)
    serialized_message = message.SerializeToString()
    encrypted_data = encrypt_message(AES_KEY, AES_IV, serialized_message)
    hex_encrypted_data = binascii.hexlify(encrypted_data).decode('utf-8')

    token = fetch_tokens()
    if not token:
        return jsonify({"error": "No tokens available"}), 500
        
    try:
    	remove(token, hex_encrypted_data)
    	return jsonify({"message": f"User with UID {uid} removed successfully"}), 200
    except Exception as e:
    	return jsonify({"message":str(e)})
#    else:
#        return jsonify({"error": f"Failed to remove user with UID {uid}"}), response.status_code

@app.route('/add/<uid>', methods=['GET'])
def add_friend(uid):
    player_name_url = f"https://api-info-nrml-alinas.vercel.app/player-info?uid={uid}&region=ME"

    player_name = "Unknown"

    try:
        response = requests.get(player_name_url, timeout=5)

        if response.status_code == 200:
            data = response.json()

            # جلب الاسم الصحيح
            player_name = (
                data.get("basicInfo", {})
                    .get("nickname", "Unknown")
            )
        else:
            player_name = "Unknown"

    except Exception as e:
        player_name = "Unknown"

    # إضافة المستخدم إلى البروتوباف
    message = mymessage_pb2.MyMessage()
    message.field1 = 9797549324
    message.field2 = int(uid)
    message.field3 = 22

    serialized_message = message.SerializeToString()
    encrypted_data = encrypt_message(AES_KEY, AES_IV, serialized_message)
    hex_encrypted_data = binascii.hexlify(encrypted_data).decode('utf-8')

    token = fetch_tokens()
    if not token:
        return jsonify({"error": "No tokens available"}), 500

    send_request(token, hex_encrypted_data)

    # حفظ المستخدم
    users[uid] = {
        "uid": uid,
        "player_name": player_name
    }

    return jsonify({
        "message": f"User with UID {uid} added successfully",
        "player_name": player_name
    }), 200

# عرض قائمة المستخدمين المضافين (يتحقق من المفتاح الداخلي)
@app.route('/list', methods=['GET'])
def list_users():

    return jsonify({"users": users}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009)
