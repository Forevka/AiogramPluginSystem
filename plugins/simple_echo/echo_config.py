"""
    you can add 'to_handlers' key if you dont wanna
    pass all this config ex:
    config = {
        "payload": 'everything ok',
        "foo": 'bar',
        'beeeep': 'booop',
        'to_handlers': {
            "ill_go": "nothig_cant_stop_me_now"
        }
    }

    and in 'plugin_config' inside handler will be:
    {
        "ill_go": "nothig_cant_stop_me_now"
    }
"""

config = {
    "payload": 'everything ok',
    "foo": 'bar',
    'beeeep': 'booop'
}