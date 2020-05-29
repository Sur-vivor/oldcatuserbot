import html
from telethon import events
from telethon.utils import get_display_name
from betray import register

_cached_msgcount = dict()
_cached_entities = dict()

@register(events.NewMessage(outgoing=True, pattern=r'\.msgcount(?: (.+))?(?:\n(\d+))?'))
async def msgcount(e):
    global _cached_msgcount, _cached_entities
    chat = e.pattern_match.group(1)
    limit = int(e.pattern_match.group(2) or 2000)
    if chat in ['this', 'here']:
        chat = e.chat_id
    try:
        chat = int(chat or e.chat_id)
    except ValueError:
        pass
    chat = await e.client.get_entity(chat)
    id = await e.client.get_peer_id(chat)
    if id not in _cached_msgcount:
        to_add = dict()
        async for member in e.client.iter_participants(chat):
            if member.deleted:
                continue
            total = (await e.client.get_messages(chat, from_user=member)).total
            to_add[member.id] = total
            _cached_entities[member.id] = member
        _cached_msgcount[id] = to_add
    msgsinfo = _cached_msgcount[id]
    text = f'Message leaderboard for {html.escape(get_display_name(chat))} <i>(above {limit} messages are only shown)</i>\n'
    for _i in sorted(msgsinfo, key=msgsinfo.get, reverse=True):
        j = msgsinfo[_i]
        i = _cached_entities[_i]
        if j < limit:
            break
        text += f'<a href="tg://user?id={i.id}">{html.escape(get_display_name(i))}</a> — {j}\n'
    await e.edit(text)
