from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from User import User
import json
import random

app = Flask(__name__)
CORS(app, supports_credentials=True)


# התנתקות
@app.route('/logout', methods=["GET"])
def logout():
    response = make_response({"message": "Logged out successfully"})
    response.set_cookie('user_name', '', expires=0)  # בטל את העוגייה
    return response


# עדכון הקמשתמש בקובץ
@app.route('/update_user', methods=["PATCH"])
def update_user():
    obj = request.json
    users = read_users()  # קורא לפונקציה שקוראת את המשתמשים מהקובץ לרשימה
    user_id = int(obj.get('user_id'))  # וגם ממיר אותו לסוג מספר מקבל את הקוד הנוכחי מצד לקוח

    if user_id is None:
        return jsonify({"error": "error"}), 400  # אם לא התקבל id

    try:
        for u in users:
            if int(u['id']) == user_id:  # השוואת ה-ID
                u['games_count'] += 1  # עדכן את games_count
                u['list_words'].append(obj["new_word"])
                # מונע כפילויות
                u['list_words'] = list(dict.fromkeys(u['list_words']))
                if obj.get('winer') == True:
                    u['win_count'] += 1
                break
        else:
            return jsonify({"error": f"User not found"}), 404  # אם המשתמש לא נמצא
        write_users(users)  # מחזיר לקובץ את לאחר העידכון
        return jsonify(u), 200
    except Exception as e:
        return jsonify({"error": "Problem to update"}), 500


# פונקציה לקריאת המשתמשים מקובץ JSON
def read_users():
    try:
        with open('./'
                  'users.json', 'r') as f:
            return json.load(f)  # טוען את תוכן ה-JSON
    except FileNotFoundError:
        return []  # אם הקובץ לא קיים, מחזיר רשימה ריקה
    except json.JSONDecodeError:
        return []  # אם יש שגיאה
    except Exception as e:
        print(f"Error reading users: {str(e)}")
        return []


# פונקציה להכסת משתמשים לקובץ JSON
def write_users(users):
    try:
        with open('./users.json', 'w') as f:
            json.dump(users, f, indent=4)  # כותב את המשתמשים לקובץ בפורמט מסודר
    except Exception as e:
        print(f"Failed to write users to JSON: {str(e)}")


# פונקציה לבדוק אם משתמש קיים
def userExists(name, password):
    # print(f"name:{name}")
    # print(f"pass:{password}")
    try:
        users = read_users()
        for user in users:
            # print(f"n:{user['name']}")
            # print(f"pas:{user['password']}")
            if user['name'] == name and user['password'] == password:
                # המשתמש קיים
                return True, user
    except Exception as e:
        print(f"Error checking if user exists: {str(e)}")
    return False, None  # המשתמש לא קיים


@app.route('/login', methods=["POST"])
# התחברות
def login():
    obj = request.json
    try:
        exsist, user = userExists(obj['name'], obj['password'])
        # אם לא נשלח אובייקט
        if not obj:
            return jsonify({"error": "Invalid or missing JSON"}), 400
        # במקרה שהמשתמש לא קיים
        if not exsist:
            return jsonify({"error": "User not exists, you need to signup"}), 400

        response = make_response(jsonify(user))     # response מכיל את האובייקט הנוכחי של המשתמש שנמצא בקובץ
        # עוגייה עם תוכלת חיים של 10 דקות
        response.set_cookie('user_name', str(user['name']), max_age=600, httponly=True, secure=False)
        return response
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500


@app.route('/signup', methods=["POST"])
def signup():
    obj = request.json
    try:
        # קורא את המשתמשים מבקובץ
        users = read_users()
        ex, _ = userExists(obj['name'], obj['password'])
        if not obj:
            return jsonify({"error": "Invalid or missing JSON"}), 400
        if ex:
            return jsonify({"error": "User already exists, you need to login"}), 400

        user = User(obj['name'], obj['id'], obj['password'])
        users.append(user.to_dict()) # דוחף את המשתמש החדש לרשימת המשתמשים
        # מכניס בחזרה את כל המשתמשים לקובץ
        write_users(users)

        response = make_response(jsonify(user.to_dict()))
        response.set_cookie('user_name', str(obj['name']), max_age=600, httponly=True, secure=False)
        return response
    except Exception as e:
        return jsonify({"error": f"Signup failed: {str(e)}"}), 500


@app.route('/check_cookie', methods=["GET"])
# פונקצייה שסודקת אם יש עוגייה פעילה
def check_cookie():
    user_id = request.cookies.get('user_name')
    if user_id:
        return jsonify({"active": True}), 200
    else:
        return jsonify({"active": False}), 200


@app.route('/word_choice', methods=["GET"])
# מחזיר מילה מתוך הקובץ
def word_choice():
    num = request.args.get('num')
    # ממיר למספר
    num = int(num)
    if not num:
        return jsonify({"error": "Invalid or missing num"}), 400
    # ממלא רשימה במילים
    with open('./words.txt', 'r', encoding='utf-8') as f:
        my_list = f.read().splitlines()
    # מערבב את הרשימה
    random.shuffle(my_list)
    # מחזיר מילה במקום הרצוי בצורה מעגלית
    index = num % len(my_list)
    return my_list[index]


@app.route('/steps_list', methods=["GET"])
# פונקציה שיוצרת רשימה עם כל השלבים לפי הקובץ
def steps_list():
    with open('game_steps.txt', 'r') as file:
        content = file.read()
    # מחלקת את הקובץ לפי שורות ריקות
    return [part.strip() for part in content.split('\n\n') if part.strip()]


@app.route('/get_last_line', methods=["GET"])
# פונקציה שמחזירה את ה-id של המשתמש האחרון בקובץ
def get_last_line():
    try:
        users = read_users()
        if not users:
            return jsonify({"error": "The file is empty"}), 400
        last_user = users[-1]  # מקבל את המשתמש האחרון
        return jsonify({'id': last_user['id']}), 200
    except Exception as e:
        return jsonify({"error": "Reading the file failed"}), 500


if __name__ == "__main__":
    app.run(debug=True)
