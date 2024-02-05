import sys
import sqlite3
import getpass
import re
from datetime import datetime
import os

invalidPasswords = ["e", "b"]


def showSearchedTweets(usr, data):
    validInputs = ['e', 'l', 'b', 'm']
    page = 1
    output = displayTweets(page, data)

    tweetDetailsPrompt = "Enter tweet id of a tweet to see statistics, compose a reply, or retweet, 'b' to search again, 'e' to exit the search or 'l' to logout"
    moreTweetsPrompt = " or 'm' to see more tweets"
    inputPrompt = tweetDetailsPrompt + moreTweetsPrompt

    if output == 0:
        inputPrompt = "Enter 'b' to search again, 'e' to exit the search or 'l' to logout"

    print(inputPrompt)
    userInput = input("-> ")
    print()

    while True:
        if userInput.lower() in validInputs:
            if userInput.lower() == "m":
                page += 1
                output = displayTweets(page, data)
                if output == 0:
                    inputPrompt = tweetDetailsPrompt
                    validInputs.pop()
            elif userInput.lower() == "l":
                print("You have successfully logged out\n")
                loginScreenControls()
                return
            elif userInput.lower() == "b":
                search_tweets_by_keywords(usr)
                return

            elif userInput == 'e':
                return

            print(inputPrompt)
        else:
            try:
                userInput = int(userInput)

                if not tweetIdAccessible(page, userInput, data):
                    raise ValueError
            except:
                print(
                    f"Invalid input or the tweet is inaccessible.\n\n{inputPrompt}")

            else:
                showTweetDetails(usr, userInput, data)
                print(inputPrompt)

        userInput = input("-> ")
        print()


def search_tweets_by_keywords(usr):
    # Prepare the SQL query to retrieve matching tweets
    keywords = input("Search: ")
    print()
    keywords = keywords.split()
    query = """
            SELECT tid, writer, tdate, text, replyto
            FROM tweets
            WHERE tweets.text LIKE ? COLLATE NOCASE
            """

    hashtagQuery = """
                SELECT t.tid, t.writer, t.tdate, t.text, t.replyto
                FROM mentions m
                JOIN tweets t ON m.tid = t.tid
                WHERE m.term = ? COLLATE NOCASE
                """

    matching_tweets = set()
    for keyword in keywords:
        if keyword[0] == '#':
            keyword = keyword[1:]
            cursor.execute(hashtagQuery, (keyword,))
        else:
            cursor.execute(query, (f"%{keyword}%",))
        matching_tweets.update(cursor.fetchall())

    matching_tweets = sorted(
        matching_tweets, key=lambda tweet: tweet[2], reverse=True)

    showSearchedTweets(usr, matching_tweets)


##################### Search Users #########################################
def print_search_users(page, array):
    if (page - 1) * 5 >= len(array):
        print("No more users\n")
        return 0

    print(f"{'User Id' :>10} | {'Name' :<50} | {'City' :<30}")
    print("-"*100)
    for i in range((page - 1) * 5, page * 5):
        try:
            print(
                f"{array[i][0] :>10} | {array[i][1] :<50} | {array[i][2] :<30}")
        except:
            print()
            return 1
    print()
    return 1


def search_users(keyword):
    data = []
    cursor.execute(
        """
        SELECT usr, name, city
        FROM users
        WHERE name LIKE ? COLLATE NOCASE
        ORDER BY LENGTH(name), name ASC
        """,
        (f"%{keyword}%",)
    )

    data.extend(cursor.fetchall())

    cursor.execute(
        """
        SELECT usr, name, city
        FROM users
        WHERE city LIKE ?
        ORDER BY LENGTH(city), city ASC
        """,
        (f"%{keyword}%",)
    )
    results = cursor.fetchall()
    for row in results:
        if row not in data:
            data.append(row)

    return data


def search_users_interface(usr):
    validInputs = ['l', 'e', 'b', 'm']
    keyword = input("Search: ")
    print()
    page = 1
    data = search_users(keyword)
    print_search_users(page, data)

    userBackPrompt = "Enter user id to select user, 'b' to search again, 'e' to exit the search, 'l' to logout "
    userMorePrompt = "or 'm' to see more"
    userPrompt = userBackPrompt + userMorePrompt
    while True:
        print(userPrompt)

        userInput = input("-> ")
        print()

        if userInput in validInputs:
            if userInput == 'm':
                page += 1
                output = print_search_users(page, data)
                if output == 0:
                    userPrompt = userBackPrompt
                    validInputs.pop()

            elif userInput == 'b':
                search_users_interface(usr)
                return

            elif userInput == 'e':
                return

            elif userInput.lower() == "l":
                print("You have successfully logged out\n")
                loginScreenControls()
                return
        else:
            try:
                userInput = int(userInput)
                if not UserIdAccessible(page, userInput, data):
                    raise ValueError
            except:
                print(f"Invalid input or the user is not accessible.\n")
            else:
                showFollowerDetails(userInput, usr)


def UserIdAccessible(page, userInput, data):
    for i in range((page - 1) * 5, page * 5):
        if data[i][0] == userInput:
            return 1
    return 0

###################################################################
# Add this new function to your code


def listFollowers(usr):
    # Select followers for the user
    cursor.execute("""
                   SELECT flwer
                   FROM follows
                   WHERE flwee = ?
                   """, (usr,))
    followers = cursor.fetchall()

    if not followers:
        print("You do not have any followers yet.\n")
        return

    print(f"|{'user id'.center(11)}|")
    print(f"|{'-'*11}|")
    for i in range(len(followers)):
        print(f"|{str(followers[i][0]).center(11)}|")
        followers[i] = followers[i][0]

    while True:
        print("\nEnter the user id of the follower to view details or 'b' to go back")
        userInput = input("-> ")
        print()

        if userInput.lower() == 'b':
            return
        else:
            try:
                userInput = int(userInput)
                if userInput not in followers:
                    raise ValueError
            except ValueError:
                print("Invalid input.")
            else:
                showFollowerDetails(userInput, usr)

# Add this function to support listFollowers


def showUserDetails(usr):
    cursor.execute(
        """
        SELECT COUNT(*) 
        FROM tweets 
        WHERE writer = ?
        """, (usr,))
    tweet_count = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM follows
        WHERE flwer = ?
        """, (usr,))
    following_count = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM follows
        WHERE flwee = ?
        """, (usr,))
    followers_count = cursor.fetchone()[0]

    print(f"Number of Tweets: {tweet_count}")
    print(f"Following: {following_count}")
    print(f"Followers: {followers_count}")


def print_recent_tweets(page, data):
    if (page - 1) * 3 >= len(data):
        print("No more tweets")
        return 0

    print("%s|%s|%s|%s" % ("Id".center(7), "Date".center(
        12), "Writer".center(10), "Type".center(10)))
    print("-"*62)
    for row in range((page - 1) * 3, page * 3):
        try:
            print("%s|%s|%s|%s" % (str(data[row][0]).center(7), data[row][2].center(
                12), str(data[row][1]).center(10), data[row][5].center(10)))
        except:
            print()
            return 1
    print()
    return 1


def showFollowerDetails(follower_usr, usr):
    showUserDetails(follower_usr)
    cursor.execute(
        """
        SELECT 
        Combined.tid, 
        Combined.writer, 
        MAX(Combined.dateSort) AS dateSort, 
        Combined.text, 
        Combined.replyto, 
        Combined.type
        FROM (
            SELECT 
                t.tid, 
                t.writer, 
                t.tdate AS dateSort, 
                t.text, 
                t.replyto, 
                'tweet' AS type,
                t.writer AS retweeter
            FROM tweets t
            WHERE t.writer = ?
            UNION ALL

            SELECT 
                t.tid, 
                t.writer AS writer, 
                rt.rdate AS dateSort, 
                t.text, 
                t.replyto, 
                'retweet' AS type,
                rt.usr AS retweeter
            FROM retweets rt
            JOIN tweets t ON rt.tid = t.tid
            WhERE rt.usr = ?
            ) AS Combined
        GROUP BY Combined.tid, Combined.writer, combined.retweeter
        ORDER BY dateSort DESC;
        """,
        (follower_usr, follower_usr)
    )

    recent_tweets = cursor.fetchall()

    print("\nRecent Tweets:\n")

    page = 1
    output = print_recent_tweets(page, recent_tweets)

    permanentPrompt = "\nEnter 'f' to follow this user, 'b' to go back, 'l' to logout "
    morePrompt = "or 'm' to see more tweets"
    prompt = permanentPrompt + morePrompt

    validInputs = ['f', 'l', 'b', 'm']
    while True:
        print(prompt)
        userInput = input("-> ")
        print()
        if userInput in validInputs:
            if userInput.lower() == 'f':
                followUser(usr, follower_usr)
            elif userInput.lower() == 'm':
                output = print_recent_tweets(page + 1, recent_tweets)
                if output == 0:
                    prompt = permanentPrompt
                    validInputs.pop()
                page += 1

            elif userInput.lower() == "l":
                print("You have successfully logged out\n")
                loginScreenControls()
                return

            elif userInput.lower() == 'b':
                return
        else:
            print("Invalid input.")

# Add this function to support following a user


def followUser(current_usr, follower_usr):
    tdate = datetime.now().strftime('%Y-%m-%d')
    try:
        cursor.execute("INSERT INTO follows VALUES (? , ?, ?)",
                       (current_usr, follower_usr, tdate))
        conn.commit()
        print(f"\nYou are now following {follower_usr}.")
    except sqlite3.IntegrityError:
        print("\nYou are already following this user.")


###################################################################

def retweet(usr, tid):
    cursor.execute(
        """
        INSERT INTO retweets VALUES (?, ?, date('now'));
        """, (usr, tid))
    conn.commit()

    print("You have successfully retweeted the tweet\n")


def getRepliesCount(tid):
    cursor.execute(
        """
        SELECT count(*)
        FROM tweets t1
        LEFT JOIN tweets t2 ON t1.tid = t2.replyto
        WHERE t1.replyto = ?;
        """, (tid, ))

    return cursor.fetchall()[0][0]


def getRetweetsCount(tid):
    cursor.execute(
        """
        SELECT count(r.tid) AS retweet_count
        FROM tweets t
        LEFT JOIN retweets r ON t.tid = r.tid
        WHERE t.tid = ?
        GROUP BY t.tid
        ORDER BY t.tid;
        """, (tid, ))

    return cursor.fetchall()[0][0]


def showTweetDetails(usr, tid, data):
    data = [i for i in data if i[0] == tid][0]
    print(f"{f'Tweet Id':>12}: {tid}")
    print(f"{'Written On':>12}: {data[2]}")
    print(f"{'Written By':>12}: {data[1]}")
    print(f"{'Text':>12}: {data[3]}")
    print(f"{'Retweets':>12}: {getRetweetsCount(tid)}")
    print(f"{'Replies':>12}: {getRepliesCount(tid)}\n")

    replyPrompt = "Enter 'b' to go back or 1 to compose a reply"
    retweetPrompt = " or 2 to retweet"
    inputPrompt = replyPrompt + retweetPrompt

    while True:
        print(inputPrompt)
        userInput = input("-> ")
        print()
        if userInput == '1':
            composetweet(usr, tid)

        elif userInput == '2':
            try:
                retweet(usr, tid)
            except sqlite3.IntegrityError:
                print("You have already retweeted this tweet.\n")
                inputPrompt = replyPrompt

        elif userInput.lower() == "b":
            return

        else:
            print("Invalid Input.")


def tweetIdAccessible(page, userInput, data):
    for i in range((page - 1) * 5, page * 5):
        if data[i][0] == userInput:
            return 1
    return 0


def displayTweetsRetweets(page, data):
    count = 0
    print("%s|%s|%s|%s|%s" % ("Id".center(7), "Date".center(12), "Writer".center(
        10), "Type".center(10), "writer/retweeter".center(20)))
    print("-"*62)
    for row in range((page - 1) * 5, page * 5):
        try:
            print("%s|%s|%s|%s|%s" % (str(data[row][0]).center(7), data[row][2].center(12), str(
                data[row][1]).center(10), data[row][5].center(10), str(data[row][6]).center(20)))
            count += 1
        except:
            break

    print()

    if (page - 1) * 5 >= len(data):
        print("No more tweets\n")
        return 0

    return 1


def displayTweets(page, data):
    count = 0
    print("%s|%s|%s" % ("Id".center(7), "Date".center(12), "Writer".center(10)))
    print("-"*42)
    for row in range((page - 1) * 5, page * 5):
        try:
            print("%s|%s|%s" % (str(data[row][0]).center(
                7), data[row][2].center(12), str(data[row][1]).center(10)))
            count += 1
        except:
            break

    print()

    if (page - 1) * 5 >= len(data):
        print("No more tweets\n")
        return 0

    return 1


def loggedIn(usr):
    cursor.execute(
        """
        SELECT 
        Combined.tid, 
        Combined.writer, 
        MAX(Combined.dateSort) AS dateSort, 
        Combined.text, 
        Combined.replyto, 
        Combined.type,
        combined.retweeter
        FROM (
            SELECT 
                t.tid, 
                t.writer, 
                t.tdate AS dateSort, 
                t.text, 
                t.replyto, 
                'tweet' AS type,
                t.writer AS retweeter
            FROM tweets t
            JOIN follows f ON f.flwee = t.writer
            WHERE f.flwer = ?

            UNION ALL

            SELECT 
                t.tid, 
                t.writer AS writer, 
                rt.rdate AS dateSort, 
                t.text, 
                t.replyto, 
                'retweet' AS type,
                rt.usr AS retweeter
            FROM retweets rt
            JOIN tweets t ON rt.tid = t.tid
            JOIN follows f ON f.flwee = rt.usr
            WHERE f.flwer = ?
            ) AS Combined
        GROUP BY Combined.tid, Combined.writer, combined.retweeter
        ORDER BY dateSort DESC;
        """, (usr, usr))
    data = cursor.fetchall()
    showTweets(usr, data)


def showTweets(usr, data):
    validInputs = ['l', 'b', 'c', 'e', 'u', 'f', 't', 'm']
    page = 1
    output = displayTweetsRetweets(page, data)

    tweetDetailsPrompt = "Enter tweet id of a tweet to see statistics, compose a reply, or retweet, 'c' to compose a tweet, 'f' to list followers, 'b' to go to the start, 'u' to search users, 't', to search tweets or 'l' to logout"
    moreTweetsPrompt = " or 'm' to see more tweets"
    inputPrompt = tweetDetailsPrompt + moreTweetsPrompt

    if output == 0:
        inputPrompt = "Enter 'c' to compose a tweet, 'f' to list followers, 't' to search tweets, 'u' to search users, or 'l' to logout"

    print(inputPrompt)
    userInput = input("-> ")
    print()

    while True:
        if userInput.lower() in validInputs:
            if userInput.lower() == "m":
                page += 1
                output = displayTweetsRetweets(page, data)
                if output == 0:
                    inputPrompt = tweetDetailsPrompt
                    validInputs.pop()
            elif userInput.lower() == "l":
                print("You have successfully logged out\n")
                loginScreenControls()
                return
            elif userInput.lower() == "b":
                loggedIn(usr)
                return
            elif userInput.lower() == "c":
                composetweet(usr, "NULL")
            elif userInput.lower() == "f":
                listFollowers(usr)
            elif userInput.lower() == "u":
                search_users_interface(usr)
            elif userInput.lower() == "t":
                search_tweets_by_keywords(usr)

            print(inputPrompt)
        else:
            try:
                userInput = int(userInput)

                if not tweetIdAccessible(page, userInput, data):
                    raise ValueError
            except:
                print(
                    f"Invalid input or the tweet is inaccessible.\n\n{inputPrompt}")

            else:
                showTweetDetails(usr, userInput, data)
                print(inputPrompt)

        userInput = input("-> ")
        print()


def composetweet(usr, replyTo):
    tweetText = input("Compose your tweet (hashtags start with '#'): ")

    # Input Validation: Check if tweetText contains only allowed characters
    if not re.match(r'^[a-zA-Z0-9\s.,!?#@]+$', tweetText):
        print("\nInvalid input. Only letters, numbers, spaces, and certain special characters are allowed.\n")
        return

    hashtags = re.findall(r"#(\w+)", tweetText)

    if isinstance(usr, tuple) and len(usr) == 1:
        writer_id = usr[0]  # Unpack the tuple
    else:
        writer_id = usr  # Use usr as it is if it's not a tuple

    tdate = datetime.now().strftime('%Y-%m-%d')

    # Start transaction
    conn.execute("BEGIN TRANSACTION")

    try:
        # Fetch the highest tweet ID from the tweets table
        cursor.execute("SELECT MAX(tid) FROM tweets")
        max_id = cursor.fetchone()[0]
        tweet_id = max_id + 1 if max_id is not None else 1

        # Insert the tweet with the calculated tweet ID
        cursor.execute("INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (?, ?, ?, ?, ?)",
                       (tweet_id, writer_id, tdate, tweetText, replyTo))

        # Insert hashtags and their associations with the tweet
        for i in range(len(hashtags)):
            # Ensure the hashtag is stored in the hashtags table
            hashtags[i] = hashtags[i].lower()
            cursor.execute(
                "INSERT OR IGNORE INTO hashtags (term) VALUES (?)", (hashtags[i],))

            # Insert the association of the tweet with the hashtag
            cursor.execute(
                "INSERT INTO mentions (tid, term) VALUES (?, ?)", (tweet_id, hashtags[i]))

            # print(f"Inserted mention with tweet ID: {tweet_id} and hashtag: {tag}")  # Debugging line

        # Commit the transaction if everything is successful
        conn.commit()
        print("\nYour tweet has been posted successfully!\n")

    except sqlite3.IntegrityError as e:
        # Rollback the transaction if any error occurs
        conn.rollback()
        print("An error occurred while posting your tweet:", e)


def exitMessage():
    print("You have successfully exited the program. Goodbye!")
    sys.exit()


def pullUserData(usr):
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    for row in rows:
        if row[0] == usr:
            return row


def usernameExists(usr):
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    for row in rows:
        if row[0] == usr:
            return True
    return False


def logIn():
    userId = input(
        "Enter username, 'e' to exit the program, or 'b' to go back to the login screen: ")

    if userId.lower() == "e":
        print()
        exitMessage()
        return
    elif userId.lower() == "b":
        print()
        loginScreenControls()
        return

    while True:
        try:
            userId = int(userId)

            if not usernameExists(userId):
                userId = input(
                    "\nInvalid username. Enter a valid username, 'e' to exit the program, or 'b' to go back to the login screen: ")
            else:
                break

        except:
            if userId.lower() == "e":
                print()
                exitMessage()
                return
            elif userId.lower() == "b":
                print()
                loginScreenControls()
                return

            userId = input(
                "\nInvalid username. Enter a valid username, 'e' to exit the program, or 'b' to go back to the login screen: ")

    password = getpass.getpass("Enter password: ")
    print()
    userData = pullUserData(userId)
    expectedPassword = userData[1]

    while expectedPassword != password:
        password = getpass.getpass(
            "Invalid password. Enter password again, 'e' to exit the program, 'b' to enter a different username or 'l' to go back to the login screen: ")
        if password.lower() == "e":
            print()
            exitMessage()
            return
        elif password.lower() == "b":
            print()
            logIn()
            return
        elif password.lower() == "l":
            loginScreenControls()
            return
        print()

    print("You have successfully logged in.\n")
    loggedIn(userId)


def signUp():
    print("Enter the following information below.")

    while True:
        name = input("Full Name: ")
        if re.match(r'^[a-zA-Z0-9\s.,!?#@]+$', name):
            break  # Exit the loop if the name is valid.
        else:
            print(
                "\nInvalid input. Only letters, numbers, spaces, and certain special characters are allowed.\n")
            # The loop will continue if the name is invalid.

    while True:
        email = input("Email Address: ")
        if re.match(r'^[a-zA-Z0-9\s.,!?#@]+$', email):
            break  # Exit the loop if the name is valid.
        else:
            print(
                "\nInvalid input. Only letters, numbers, spaces, and certain special characters are allowed.\n")
            # The loop will continue if the name is invalid.

    while True:
        city = input("City: ")
        if re.match(r'^[a-zA-Z0-9\s.,!?#@]+$', city):
            break  # Exit the loop if the name is valid.
        else:
            print(
                "\nInvalid input. Only letters, numbers, spaces, and certain special characters are allowed.\n")
            # The loop will continue if the name is invalid.

    while True:
        timezone = input("Timezone: ")

        if re.match(r'^[0-9.+-]+$', timezone):
            break  # Exit the loop if the name is valid.
        else:
            print("\nInvalid input. Only integers or decimals allowed\n")
            # The loop will continue if the name is invalid.

    while True:
        password = getpass.getpass("Enter your password: ")

        # Check if the password is not in the list of invalid passwords and matches the regex
        if password not in invalidPasswords and re.match(r'^[a-zA-Z0-9\s.,!?#@]+$', password):
            break  # Both conditions are met, so exit the loop.
        else:
            # Give feedback about why the password was invalid.
            if password in invalidPasswords:
                print(
                    "\nUnable to use that as password. Please enter a different password.\n")
            else:
                print(
                    "\nInvalid input. Only letters, numbers, spaces, and certain special characters are allowed.\n")

    cursor.execute("""
                    SELECT max(usr)
                    FROM users;
                   """)
    userId = cursor.fetchall()[0][0] + 1

    userData = (userId, password, name, email, city, timezone)
    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", userData)
    conn.commit()

    print("Your account was created successfully.\n")
    print("*"*30)
    if len(str(userId)) < 10:
        print(f"{'**' + ('Your user id is ' + str(userId)).center(26, ' ') + '**'}")
    else:
        print(f"{('Your user id is ' + str(userId)).center(30, ' ')}")
    print(f"{'*'*30}\n")

    print("\nYou have successfully logged in.\n")
    loggedIn(userId)


def loginScreen():

    print("Input 1, 2, or 3")
    print("1. Log in, 2. Create an account, 3. Exit")

    while True:
        try:
            userInput = int(input("-> "))
            print()

            if 1 <= userInput <= 3:
                return userInput
            print("\nInvalid input. Enter a valid input (1, 2, or 3).")
            print("1. Log in, 2. Create an account, 3. Exit")

        except:
            print("\nInvalid input. Enter a valid input (1, 2, or 3).")
            print("1. Log in, 2. Create an account, 3. Exit")


def loginScreenControls():
    userInput = loginScreen()
    if userInput == 1:
        logIn()
    elif userInput == 2:
        signUp()
    else:
        exitMessage()


def printData():
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    for row in rows:
        print(row)


def main():
    loginScreenControls()


if __name__ == "__main__":
    while True:
        databaseName = input(
            "Input the name of a valid database (the file should end with .db extension) or 'e' to exit the program: ")
        print()

        if databaseName == 'e':
            exitMessage()
        elif not os.path.exists(databaseName):
            print(f"The file '{databaseName}' does not exist.\n")
        else:
            break

    conn = sqlite3.connect(f"{databaseName}")
    cursor = conn.cursor()
    main()
    conn.close()
