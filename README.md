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
