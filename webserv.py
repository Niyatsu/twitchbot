import hashlib
import mysql.connector
import requests
import config
import hmac
import mysql
from flask import (
    Flask,
    request,
    json,
    make_response,
    render_template,
    redirect,
    url_for,
    flash,
    session,
)
from flask_mysqldb import MySQL
from wtforms import Form, StringField, PasswordField, validators, BooleanField
from passlib.hash import sha256_crypt

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "twitchbot"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)
base_telegram_url = "https://api.telegram.org/bot"
bot_token = config.BOT_TOKEN


def send_notification_to_telegram(broadcaster_id, category_name="", title=""):
    caption = ""
    broadcaster = next(
        (brd for brd in config.TWITCH_BROADCASTERS if brd["id"] == broadcaster_id), None
    )
    if broadcaster != None:
        # if event_type == config.TW_EVENT_ONLINE:
        #     caption = f'Привет! <b>{broadcaster["username"]}</b> запустил стрим на <b>Twitch</b>! \n<a href="www.twitch.tv/{broadcaster["username"]}">Присоединяйся!</a> '
        # elif event_type == config.TW_EVENT_UPDATE:

        caption = f'Прикинь, <b>{broadcaster["username"]}</b> сейчас стримит <b>{category_name}</b>!\n<b>{broadcaster["username"]}</b> говорит: {title}\n<a href="www.twitch.tv/{broadcaster["username"]}">Присоединяйся!</a> '
        data = {
            "chat_id": "",
            "photo": broadcaster["notification_photo"],
            "parse_mode": "HTML",
            "caption": caption,
        }
        for chat in config.NOTIFICATION_CHAT_LIST:
            data["chat_id"] = chat
            requests.get(f"{base_telegram_url}{bot_token}/sendPhoto", data=data)

        return
    else:
        return


def send_update_notification_to_telegram(broadcaster_id, category_name, title):
    broadcaster = next(
        (brd for brd in config.TWITCH_BROADCASTERS if brd["id"] == broadcaster_id), None
    )
    for chat in config.NOTIFICATION_CHAT_LIST:
        data = {
            "chat_id": chat,
            "photo": broadcaster["notification_photo"],
            "parse_mode": "HTML",
            "caption": f'Привет! <b>{broadcaster["username"]}</b> запустил стрим на <b>Twitch</b>! \n<a href="www.twitch.tv/{broadcaster["username"]}">Присоединяйся!</a> ',
        }
        requests.get(f"{base_telegram_url}{bot_token}/sendPhoto", data=data)
    return


# Get AUTH TOKEN from Twitch
def get_auth_token():
    # Query from client_id, client_secret, all that for CREDENTIALS FLOW AUTH
    query = "client_id=ezjav452jr5yk9sz48azocnnd8lv47&client_secret=xtrizbj6ja1ce08ltqu5y614axkc5k&grant_type=client_credentials"

    response = requests.post(
        "https://id.twitch.tv/oauth2/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=query,
    )

    response = response.json()
    token = response["access_token"]
    return token


# Get additional channel info, when an event is fired
def get_channel_info(brd_id):
    token = get_auth_token()
    channel_info = requests.get(
        f"https://api.twitch.tv/helix/channels?broadcaster_id={brd_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "Client-ID": config.TWITCH_CLIENT_ID,
        },
    ).json()
    return channel_info


# Subscribe to events from all broadcasters in config file, only for foing live here
def twitch_subscribe_for_events(event_type):
    # Get the token
    token = get_auth_token()
    sub_success = []

    # loop through the list of broadcasters and subscribe to each
    for broadcaster in config.TWITCH_BROADCASTERS:
        data = {
            "type": event_type,
            "version": "1",
            "condition": {"broadcaster_user_id": broadcaster["id"]},
            "transport": {
                "method": "webhook",
                #                "callback": 'https://df50-93-184-231-61.eu.ngrok.io/twitchEventHandler',
                "callback": "https://niyatsu.pythonanywhere.com/twitchEventHandler",
                "secret": config.TWITCH_SUB_SECRET,
            },
        }
        r = requests.post(
            "https://api.twitch.tv/helix/eventsub/subscriptions",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Client-ID": config.TWITCH_CLIENT_ID,
            },
            data=json.dumps(data),
        )
        if r.status_code != 202:
            break

    return sub_success


# Delete all subscriptions in case something goes wrong
def twitch_delete_subscriptions():
    token = get_auth_token()
    # List all of active subs, then delete one by one
    r = requests.get(
        "https://api.twitch.tv/helix/eventsub/subscriptions",
        headers={
            "Authorization": f"Bearer {token}",
            "Client-ID": f"{config.TWITCH_CLIENT_ID}",
        },
    ).json()

    print(r)
    for i in r["data"]:
        requests.delete(
            f'{config.TWITCH_BASE_SUB_URL}?id={i["id"]}',
            headers={
                "Authorization": f"Bearer {token}",
                "Client-ID": config.TWITCH_CLIENT_ID,
            },
        )

    return


# Every twitch message has to be verified using HMAC, look up the algorithm in twitch docs
def verify_twitch_message(
    twitch_message_id,
    twitch_message_timestamp,
    twitch_request_body,
    twitch_sent_signature,
):
    HMAC_PREFIX = "sha256="
    hmac_secret = config.TWITCH_SUB_SECRET
    hmac_message = f"{twitch_message_id}{twitch_message_timestamp}{twitch_request_body}"

    signature = (
        HMAC_PREFIX
        + hmac.new(
            bytes(hmac_secret, "ascii"),
            bytes(hmac_message, "ascii"),
            digestmod=hashlib.sha256,
        ).hexdigest()
    )
    # print(signature)
    return signature == twitch_sent_signature


# Root route. No use.
@app.route("/")
def hello():
    return render_template("index.html")


# Just for some testing
@app.route("/telebotresponse", methods=["POST"])
def issuehook():
    data = request.data
    print(request.headers.get("Host"))
    return data


# Testing telegram bot again
@app.route("/sendtestmessage")
def send_mess():
    broadcaster = next(
        (brd for brd in config.TWITCH_BROADCASTERS if brd["id"] == "42078350"), None
    )
    for chat in config.NOTIFICATION_CHAT_LIST:
        data = {
            "chat_id": chat,
            "photo": broadcaster["notification_photo"],
            "parse_mode": "HTML",
            "caption": f'Привет! <b>{broadcaster["username"]}</b> запустил стрим на <b>Twitch</b>! \n<a href="www.twitch.tv/{broadcaster["username"]}">Присоединяйся!</a> ',
        }

        requests.get(f"{base_telegram_url}{bot_token}/sendPhoto", data=data)
    return "", 200


@app.route("/subscribeLiveEvents")
def subscribe_for_events():
    success = twitch_subscribe_for_events(config.TW_EVENT_ONLINE)

    return f"{str(success)}", 200


@app.route("/subscribeChannelUpdates")
def subscribe_for_updates():
    success = twitch_subscribe_for_events(config.TW_EVENT_UPDATE)

    return f"{str(success)}", 200


@app.route("/subscribeOfflineEvents")
def subscribe_for_offline():
    success = twitch_subscribe_for_events(config.TW_EVENT_OFFLINE)
    return f"{str(success)}", 200


# List the subscriptions for debug purposes
@app.route("/listsubs")
def list_subs_for_dev():
    token = get_auth_token()
    r = requests.get(
        "https://api.twitch.tv/helix/eventsub/subscriptions",
        headers={
            "Authorization": f"Bearer {token}",
            "Client-ID": f"{config.TWITCH_CLIENT_ID}",
        },
    ).json()
    # print(f'DEBUG {r}')
    subs = []
    for i in r["data"]:
        subs.append({"id": i["id"], "type": i["type"]})
    return render_template("subscriptions.html", subs=subs)


# Invoke the removal of all subs
@app.route("/unsubscribeAll")
def delete_all_subscriptions():
    twitch_delete_subscriptions()

    return f"OK", 200


# Main event handler
@app.route("/twitchEventHandler", methods=["POST"])
def handle_event():
    # print(request.headers)
    # Get all headers to verify the authencity of message first

    # Connect to DB
    db_conn = mysql.connector.connect(
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        database=config.DB_NAME,
    )
    cursor = db_conn.cursor()
    # Get all headers from twitch request for verification of the message
    tw_mess_id = request.headers.get(config.TW_MESS_ID)
    tw_mess_time = request.headers.get(config.TW_MESS_TIME)
    tw_request_body = request.get_data(
        True, True, False
    )  # To get RAW request body data
    tw_mess_sign = request.headers.get(config.TW_MESS_SIGN)

    # Test for message authencity comparing the signatures
    if verify_twitch_message(tw_mess_id, tw_mess_time, tw_request_body, tw_mess_sign):
        # Handle webhook verification (return the challenge with 200 code)
        if request.headers.get(config.TW_MESS_TYPE) == "webhook_callback_verification":
            challenge = request.json
            challenge = challenge["challenge"]
            response = make_response(challenge, 200)
            response.mimetype = "text/plain"
            return response
        # if sub was revoked try to resub
        elif request.headers.get(config.TW_MESS_TYPE) == "revocation":
            twitch_subscribe_for_events(config.TW_EVENT_ONLINE)
            return "OK", 200
        # Here are notifications
        else:

            # В сообщениях об оффлайне другая структура ответа. Нужно проверять тип подписки, т.к. в уведомлении
            # об оффлайне нет айди месседжа.
            response = request.json
            event_type = response["subscription"]["type"]

            # If a streamer went online or changed their channel, request additional information and send to telegram

            if (
                event_type == config.TW_EVENT_ONLINE
                or event_type == config.TW_EVENT_UPDATE
            ):
                brd_id = response["event"]["broadcaster_user_id"]
                mes_id = response["event"]["id"]

                # Check if there have been messages with this id before. If there are no records in the DB - send notif and write to DB
                cursor.execute(f"SELECT * from events where message_id={mes_id}")
                events = cursor.fetchall()

                if len(events) == 0:
                    channel_info = get_channel_info(brd_id)
                    send_notification_to_telegram(
                        brd_id,
                        channel_info["data"][0]["game_name"],
                        channel_info["data"][0]["title"],
                    )
                    cursor.execute(
                        f"INSERT INTO events (message_id, broadcaster_id) VALUES ({mes_id}, {brd_id})"
                    )

            # If the streamer went offline, delete all messages related to him in DB, so that nex time he is online, notification is sent
            if event_type == config.TW_EVENT_OFFLINE:
                brd_id = response["event"]["broadcaster_user_id"]
                cursor.execute(f"DELETE FROM events WHERE broadcaster_id={brd_id}")

            db_conn.commit()
            db_conn.close()

            return "OK", 200

        return "Ok", 200
    else:
        return "Failed to verify signature", 400


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form["login"]
        password_candidate = request.form["password"]
        cur = mysql.connection.cursor()

        result = cur.execute("SELECT * FROM admins WHERE login = %s", [login])
        if result > 0:
            user = cur.fetchone()
            password = user["password"]

            if sha256_crypt.verify(password_candidate, password):
                session["logged_in"] = True
                session["username"] = login
                flash("You're now logged in!", "success")
                return redirect(url_for("hello"))
            else:
                error = "Invalid login!"
                return render_template("login.html", error=error)
            cur.close()
        else:
            error = "No such user!"
            return render_template("login.html", error=error)

        # print(f"DEBUG: {login}, {password_candidate}")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register_admin():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        login = form.login.data
        password = sha256_crypt.hash(str(form.password.data))
        curs = mysql.connection.cursor()
        is_unique = curs.execute("SELECT * FROM admins WHERE login = %s", [login])
        if is_unique > 0:
            flash("This login is already taken, choose a new one!", "danger")
            error = "Login taken!"
            return render_template("register.html", form=form)
        else:
            curs.execute(
                "INSERT INTO admins (login, password) VALUES (%s, %s)",
                (login, password),
            )
            mysql.connection.commit()
            curs.close()
            return redirect(url_for("hello"))

    return render_template("register.html", form=form)


@app.route("/listadmins")
def list_admins():
    curs = mysql.connection.cursor()

    query = curs.execute("SELECT * FROM admins")
    admins = curs.fetchall()

    if query > 0:
        return render_template("adminslist.html", admins=admins)
    else:
        msg = "No admins!"
        return render_template("adminslist.html", msg=msg)


@app.route("/listbroadcasters")
def list_broadcasters():

    cur = mysql.connection.cursor()

    query = cur.execute("SELECT * FROM broadcasters")
    broadcasters = cur.fetchall()

    if query > 0:
        return render_template("listbroadcasters.html", broadcasters=broadcasters)
    else:
        msg = "No Broadcasters"
        return render_template("listbroadcasters.html", msg=msg)


@app.route("/addbroadcaster", methods=["GET", "POST"])
def add_broadcaster():
    form = BroadcasterForm(request.form)

    if request.method == "POST" and form.validate():
        broadcaster_id = form.broadcaster_id.data
        broadcaster_username = form.broadcaster_username.data
        notification_photo = form.notification_photo.data
        use_thumbnail = form.use_thumbnail.data
        print(f"DEBUG: {use_thumbnail}")
        cur = mysql.connection.cursor()
        is_not_unique = cur.execute(
            "SELECT * FROM broadcasters WHERE broadcaster_id = %s", [broadcaster_id]
        )
        if is_not_unique > 0:
            flash("This broadcaster is already in the database", "warning")
            error = "Duplicate broadcaster!"
            return render_template("addbroadcaster.html", form=form)
        else:
            cur.execute(
                "INSERT INTO broadcasters (broadcaster_id, username, notification_photo, use_thumbnail) VALUES (%s, %s, %s, %s)",
                (
                    broadcaster_id,
                    broadcaster_username,
                    notification_photo,
                    use_thumbnail,
                ),
            )
            mysql.connection.commit()
            cur.close()
            return redirect(url_for("list_broadcasters"))

    return render_template("addbroadcaster.html", form=form)


@app.route("/editbroadcaster/<string:id>", methods=["GET", "POST"])
def edit_broadcaster(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM broadcasters WHERE id = %s", [id])
    broadcaster = cur.fetchone()

    form = BroadcasterForm(request.form)
    form.broadcaster_id.data = broadcaster["broadcaster_id"]
    form.broadcaster_username.data = broadcaster["username"]
    form.notification_photo.data = broadcaster["notification_photo"]
    form.use_thumbnail.data = broadcaster["use_thumbnail"]
    if request.method == "POST" and form.validate():
        print(request.form)
        broadcaster_id = request.form["broadcaster_id"]
        broadcaster_username = request.form["broadcaster_username"]
        notification_photo = request.form["notification_photo"]
        use_thumbnail = 1 if "use_thumbnail" in request.form else 0

        cur.execute(
            "UPDATE broadcasters SET broadcaster_id = %s, username = %s, notification_photo = %s, use_thumbnail = %s WHERE id = %s",
            (
                broadcaster_id,
                broadcaster_username,
                notification_photo,
                use_thumbnail,
                id,
            ),
        )

        mysql.connection.commit()
        cur.close()
        flash("Broadvaster successfully edited.", "success")
        return redirect(url_for("list_broadcasters"))

    mysql.connection.commit()
    cur.close()

    return render_template("editbroadcaster.html", form=form)


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized, please login!", "danger")
            return redirect(url_for("login"))

    return wrap


class BroadcasterForm(Form):
    broadcaster_id = StringField("Broadcaster ID", [validators.DataRequired()])
    broadcaster_username = StringField(
        "Broadcaster Twitch Username", [validators.DataRequired()]
    )
    notification_photo = StringField(
        "Photo URL", [validators.DataRequired(), validators.Length(max=250)]
    )
    use_thumbnail = BooleanField("Use Thumbnail")


class RegisterForm(Form):
    login = StringField("Login", [validators.Length(min=4, max=20)])
    password = PasswordField(
        "Password",
        [
            validators.DataRequired(),
            validators.EqualTo("confirm", message="Passwords do not match"),
        ],
    )
    confirm = PasswordField("Confirm")


if __name__ == "__main__":
    app.secret_key = "@zer!zone"
    app.run(debug=True)
