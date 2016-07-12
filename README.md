# bitslack
slackbot module using slacker, selenium and phantomjs

## getting started

install slacker, selenium, websocket-client and phantomjs(slacker and selenium can install by pip).

    pip install selenium slacker websocket-client

see http://phantomjs.org/ to install phantomjs.

create channel #test and then;

    git clone https://github.com/plant004/bitslack.git
    cd bitslack
    echo SLACK_API_KEY='[your slack api key]'>> settings.py
    echo SLACK_ICON_URL='[your slack bot icon url]'>> settings.py
    python hello.py


### how to use aipo.py

if you try aipo.py, install simple-aes.

    pip install simple-aes

and add some parameters to settings.py;

    echo AIPO_BASE_URL='[http://your-aipo-domain.com/aipo/portal/]'>> settings.py
    echo AIPO_LOGIN_PATH=''>> settings.py
    echo AIPO_LOGOUT_PATH='?action=ALJLogoutUser'>> settings.py
    echo AIPO_KEY='[your-aes-key]'>> settings.py
    python aipo.py

### how to use skype_proxy.py


if you try skype_proxy.py, install Skype4Py.

    pip install Skype4Py

and before run skype_proxy.py, you must create p2p group chat and get chat name.
you can create p2p group chat to type "/createmoderatedchat" on skype,
and you can get chat name to type "/get name" on skype.

and then add some parameters to settings.py;

    echo SKYPE_CHAT_CHANNEL_LIST = (>> settings.py
    echo     (u'[skype group chat name]', '#test',),>> settings.py
    echo )>> settings.py
    python skype_proxy.py

