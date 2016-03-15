# bitslack
slackbot module using slacker, selenium and phantomjs

## getting started

install slacker, selenium, websocket-client and phantomjs(slacker and selenium can install by pip).

    pip install selenium slacker websocket-client

see http://phantomjs.org/ to install phantomjs.

create channel #test and then;

    git clone https://github.com/plant004/bitslack.git
    cd bitslack
    echo "SLACK_API_KEY='[your slack api key]'" >> settings.py
    echo "SLACK_ICON_URL='[your slack bot icon url]'" >> settings.py
    python hello.py


### how to use aipo.py

if you try aipo.py, install simple-aes.

    pip install simple-aes

and add some parameters to settings.py.

    echo "AIPO_BASE_URL = 'http://your-aipo-domain.com/aipo/portal/'" >> settings.py
    echo "AIPO_LOGIN_PATH = ''" >> settings.py
    echo "AIPO_LOGOUT_PATH = '?action=ALJLogoutUser'" >> settings.py
    echo "AIPO_KEY='your-aes-key'" >> settings.py
    python aipo.py
