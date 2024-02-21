# Telegraam Bot Tokens. Should be converted to a list to enable posting to several chats

BOT_TOKEN = "5787297127:AAG22SfqYBHqsWaBvzLav2iXitS3nSN-oy8"
# NOTIFICATION_CHAT_LIST = ['-819469609', '-1001050331505']
NOTIFICATION_CHAT_LIST = [
    "-819469609",
]


# Twitch Secret for Subscription

TWITCH_SUB_SECRET = "testing_subscription"
TWITCH_CLIENT_ID = "ezjav452jr5yk9sz48azocnnd8lv47"
TWITCH_CLIENT_SECRET = "xtrizbj6ja1ce08ltqu5y614axkc5k"
TWITCH_BASE_SUB_URL = "https://api.twitch.tv/helix/eventsub/subscriptions"

# TWITCH HEADERS SHORTPATHS

TW_MESS_ID = "Twitch-Eventsub-Message-Id"
TW_MESS_RETRY = "Twitch-Eventsub-Message-Retry"
TW_MESS_TYPE = "Twitch-Eventsub-Message-Type"
TW_MESS_SIGN = "Twitch-Eventsub-Message-Signature"
TW_MESS_TIME = "Twitch-Eventsub-Message-Timestamp"
TW_SUB_TYPE = "Twitch-Eventsub-Subscription-Type"
TW_SUB_VERSION = "Twitch-Eventsub-Subscription-Version"

TW_EVENT_ONLINE = "stream.online"
TW_EVENT_UPDATE = "channel.update"
TW_EVENT_OFFLINE = "stream.offline"

# Twitch Broadcaster IDs

TWITCH_BROADCASTER_IDS = ["42078350", "48470858", "469559912"]
NIYATSU = "42078350"
ROBOTKITTEN = "48470858"
MASHTAGA = "469559912"

TWITCH_BROADCASTERS = [
    {
        "id": "42078350",
        "username": "Niyatsu",
        "notification_photo": "https://sun9-12.userapi.com/impg/rt5eSbxTHlFcE4Ughy-KFk70M5mNGpOfM6Wn9w/xToSeHnQ65Y.jpg?size=400x300&quality=95&sign=6ddd5ee6c4be773e9cff830908c6f159&type=album",
    },
    {
        "id": "48470858",
        "username": "RobotKitten",
        "notification_photo": "https://sun9-13.userapi.com/impg/3WqtPS7nNa6yDcRhU_8Mx4zMS_D16jz5Mkd1Sg/Ub9wb-DfeBw.jpg?size=400x300&quality=95&sign=19aced1f0d1573e22db28c46166bd13c&type=album",
    },
    {
        "id": "469559912",
        "username": "MASHTAGA",
        "notification_photo": "https://sun9-59.userapi.com/impg/oExiflfyn6wBa74hFWhhx9CosfEiahIq509lew/0esecAaeBgA.jpg?size=400x300&quality=95&sign=c1903a6f08d69ce28157c1ba58004f7d&type=album",
    },
    {
        "id": "420396810",
        "username": "Orkhan2332",
        "notification_photo": "https://sun9-67.userapi.com/impg/gEg88UlnFwnGKzFitIlmc4L3-rUoMnKirxIXjA/cDdXTk7_SAM.jpg?size=400x300&quality=95&sign=be8b3e23d6ae84a3feb6990171887dfb&type=album",
    },
]

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "twitchbot"
