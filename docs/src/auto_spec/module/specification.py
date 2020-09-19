# specification.py

from user_events import receive_user_update

from asyncapi import AutoSpec


spec = AutoSpec('User Events', development='redis://localhost')
spec.subscribe(receive_user_update, channel_name='user/update')
