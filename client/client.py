from http.client import responses
from operator import index
from warnings import catch_warnings

from User import User
from requests import session
import time

session = session()
basic_url = "http://127.0.0.1:5000"

logo = r"""            _    _
           | |  | |
           | |__| | __ _ _ __   __ _ _ __ ___   __ _ _ __
           |  __  |/ _' | '_ \ / _' | '_ ' _ \ / _' | '_ \
           | |  | | (_| | | | | (_| | | | | | | (_| | | | |
           |_|  |_|\__,_|_| |_|\__, |_| |_| |_|\__,_|_| |_|
                                __/ |
                               |___/
"""



# בודק האם יש עוגייה פעילה
def check_cookie():
    try:
        response = session.get(f"{basic_url}/check_cookie")
        if response.status_code == 200:
            data = response.json()
            if data.get("active"):
                print("פעילה")
            else:
                print("לא פעילה")
        else:
            print("שגיאה בבדיקה")

    except Exception as e:
        print(f"An error: {e}")


def login():
    print("Log in")
    # בדירת תקינות לשם
    while True:      # ימשיך לבקש קלט כל עוד לא הוכנסה שם תקין
        name = input('Input your name: ')
        if len(name) < 2 or not name.isalpha():
            print("Please enter at least 2 letters")
        else:
            break  # יוצאים מהלולאה אם השם תקין
    # בדיקת תקינות לסיסמא
    while True:      # ימשיך לבקש קלט כל עוד לא הוכנסה סיסמא תקינה
        password = input("Input your password: ")
        if len(password) < 8 or (
                not any(i.isalpha() for i in password) or not any(i.isdigit() for i in password) or not any(
            not i.isalnum() for i in password)):
            print("The password should be at least 8 characters long, and contain an English letter and a number")
        else:
            break  # יוצאים מהלולאה אם הסיסמה תקינה

    message = {
        "name": name,
        "password": password,
    }
    response = session.post(f"{basic_url}/login", json=message)
    if response.status_code == 200:
        print(f"Hello {response.json()['name']}")
    else:
        print(f"Error: {response.status_code}, Details: {response.text}")

    return response


def signup():
    print("Sign up")
    try:
        response = session.get(f"{basic_url}/get_last_line")

        if response.status_code == 200:
            user_data = response.json()
            # מקבל את ה-ID מהתשובה
            user_id = user_data.get('id')
            input_id = user_id if user_id is not None else 100  # טיפול במקרה שאין ID
        else:
            # אם הקובץ ריק מציב בקוד 101
            input_id = 100
    except Exception as e:
        print(f"An error: {e}")
        return

    while True:
        name = input('Input your name: ')
        if len(name) < 2 or not name.isalpha():
            print("Please enter at least 2 letters")
        else:
            break  # יוצאים מהלולאה אם השם תקין
    # בדיקת תקינות לקוד
    while True:
        password = input("Input your password: ")
        if len(password) < 8 or (
                not any(i.isalpha() for i in password) or not any(i.isdigit() for i in password) or not any(
            not i.isalnum() for i in password)):
            print("The password should be at least 8 characters long, and contain an English letter and a number")
        else:
            break  # יוצאים מהלולאה אם הסיסמה תקינה

    #     יוצר מופע חדש של מחלקת User
    # מזמן את הבנאי
    message = User(name, input_id + 1, password)
    # נפונקצייה to_dict נמצאת במחלקה והיא שולחת את האובייקט  נכון

    try:
        response = session.post(f"{basic_url}/signup", json=message.to_dict())

        if response.status_code == 200:
            print(f"Hello {response.json()['name']}")
        else:
            print(f"Error: {response.status_code}, Details: {response.text}")
    except Exception as e:
        print(f"An error: {e}")
        return  # הוספת return במקרה של שגיאה

    return response  # הוספת return בסוף הפונקציה


def word_choice():
    # מוודא שהקלט שהוכנס הוא מספר שלם
    while True:
        try:
            num = int(input("input a number to search a word: "))
            break  # יוצא מהלולאה אם הקלט הוא מספר שלם
        except ValueError:
            print("Please enter a integer.")
    try:
        # המספר נשלח לפונקציה בשרת שמחזירה מילה
        response = session.get(f"{basic_url}/word_choice", params={'num': num})
        if response.status_code == 200:
            return response.text
        else:
            print(f"Error: {response.status_code}, Details: {response.text}")
    except Exception as e:
        print(f"An error: {e}")


# הפונקציה מחזירה מערך של השלבים
def steps_list():
    try:
        response = session.get(f"{basic_url}/steps_list")
        if response.status_code == 200:
            steps = response.json()
            return steps
        else:
            print(f"Error: {response.status_code}, Details: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")


# פונקציית המשחק
def play():
    print(logo)
    first = True
    # כל עוד ההתחברות או ההרשמה לא צלחו מבקש להירשם שוב
    while first or (session.get(f"{basic_url}/check_cookie").status_code == 200 and
                    not session.get(f"{basic_url}/check_cookie").json().get("active")):
        first = False
        try:
            # תחילה מזמן את ההתחברות
            response = login()
            # אם אין כזה משתמש מעביר להרשמה
            if response.status_code == 400 and "User not exists, you need to signup" in response.json().get("error", ""):
                print("User does not exist. Redirecting to signup...")
                s_response = signup()
                if s_response.status_code == 400 and "User already exists, you need to login" in s_response.json().get("error", ""):
                    print("User is exist. Redirecting to log in...")
                elif s_response.status_code == 200:
                    currentUser = s_response.json()    # שומר את השחקן הנוכחי
            elif response.status_code == 200:
                currentUser = response.json()     # שומר את השחקן הנוכחי
        except Exception as e:
            print(f"An error occurred during login/signup: {e}")
            return
    # המילה שהתקבלה לפי המספר של המשתמש
    this_word = word_choice()
    if this_word:
        print('-' * len(this_word))
    else:
        print("No word found.")

    step = 0
    # result מתעדכנת כל פעם במילה שהתגלתה בינתיים
    result = "_" * len(this_word)
    # רשימת השלבים
    list_steps = steps_list()
    while step < 7 and '_' in result:
        try:
            check_cookie = session.get(f"{basic_url}/check_cookie")  # עדכן את ה-checkCookie בכל איטרציה

            if check_cookie.status_code == 200 and check_cookie.json().get("active"):
                # r מכיל מעדכן כל פעם את המילים שקיימות במילה המבוקשת
                r = ""
                char = input("input a char")

                if char in this_word:
                    index = 0
                    for i in this_word:
                        if i == char:
                            r = r + char
                        # אם במילה הגלויה בינתיים יש במקום הזה אות סימן שבסיבובים הקודמים התגלתה כבר אות
                        elif result[index] != '_':
                            r = r + result[index]
                        else:
                            r = r + "_"
                        index += 1
                    print(r)
                    result = r
                    r = ""

                else:
                    print(list_steps[step])
                    print(f"נסיונות {6 - step} נותרו לך-")
                    step += 1
            else:
                print("Your session is over, you must log in again to continue playing")
                login()
        except Exception as e:
            print(f"An error occurred during the game: {e}")
            return
    if not '_' in result:     # הלולאה נגמרה כי המילה גולתה
        to_update = {"new_word": this_word,
                     "winer": True,
                     "user_id": currentUser['id']
                     }
        try:
            response = session.patch(f"{basic_url}/update_user", json=to_update)
            if response.status_code != 200:
                print(f"Error: {response.status_code}, Details: {response.text}")

            print('כל הכבוד!!! ניצחת 😀 !')
        except Exception as e:
            print(f"An error occurred while updating user: {e}")
    else:
        to_updata = {"new_word": this_word,
                     "winer": False,
                     "user_id": currentUser['id']
                     }
        try:
            response = session.patch(f"{basic_url}/update_user", json=to_updata)
            if response.status_code != 200:
                print(f"Error: {response.status_code}, Details: {response.text}")

            print('נגמרו חל כל הנסיונות 😥 אולי תצליח פעם הבאה')
        except Exception as e:
            print(f"An error occurred while updating user: {e}")
    choice = int(input('input 1 to play again, input 2 to see your history or 3 to break away'))
    if choice == 1:
        play()
    elif choice == 2:
        try:
            if response.status_code == 200:    # האובייקט לאחר העידכון
                h = response.json()
                print("History")
                print(f"You won {h['win_count']} times out of {h['games_count']} games")
                print("")
                print("Words that appeared in previous games:")
                for word in h['list_words']:
                    print(word)

            else:
                print("It is not possible to see the history at the moment")
        except Exception as e:
            print(f"An error occurred while fetching history: {e}")
    elif choice == 3:
        try:
            # התנתקות
            session.get(f"{basic_url}/logout")

            print("Thank you for being with us")
            print("We look forward to seeing you again in the future")
        except Exception as e:
            print(f"An error occurred during logout: {e}")
    else:    # קלט לא תקין
        print("No valid input was entered")


def main():
    play()


if __name__ == "__main__":
    main()
