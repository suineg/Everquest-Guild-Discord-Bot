import interface.eqdkp as eqdkp

_NEW_LINE = '\n'


class RaidEvent:

    def __init__(self, id, name, value, icon, multidkp_pools, itempools):
        self.id = id
        self.name = name
        self.value = value
        self.icon = icon
        self.mutlidkp_pools = multidkp_pools
        self.itempools = itempools

    @classmethod
    async def convert(cls, ctx, argument):

        def check_author(m):
            return m.author == ctx.author

        # Try to match the event to whats available on eqdkp
        events = eqdkp.get_events()

        event = [event
                 for event in events
                 if (argument.isnumeric() and int(argument) == event.id)
                 or (argument.lower() in event.name.lower())]

        # If there's no match, present the user with options
        if not event:
            await ctx.send(f"""```md
# {argument} is not a valid raid event

> Please select from one of the following raid events (Choose the #):

{_NEW_LINE.join([str(event.id) + ". " + event.name for event in events])}```""")
            try:
                msg = await ctx.bot.wait_for('message', check=check_author, timeout=15)
                argument = msg.content
                event = [event for event in events if argument.isnumeric() and int(argument) == event.id]
            except Exception:
                pass

        if event:
            event = event[0]
            timeout = 20
            await ctx.send(f"""```md
# Raid Event Selected

You have chosen raid [{event.id}][{event.name}] with a default value of [{event.value}][DKP]

> If this raid event is **incorrect** please type <cancel> now.

1. Enter a new DKP amount now to override the default of {event.value}
2. Otherwise, please wait {timeout} seconds to accept the default```""")
            try:
                msg = await ctx.bot.wait_for('message', check=check_author, timeout=timeout)
                answer = msg.content
                if "cancel" in msg.content.lower():
                    return None
                event.value = int(answer) if answer.isnumeric() else event.value
            except Exception:
                pass

        return event or None
