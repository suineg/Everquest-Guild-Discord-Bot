from interface import eqdkp


class Raid:

    def __init__(self, id, date, date_timestamp, note, event_id, event_name,
                 added_by_id, added_by_name, value, raid_attendees):
        self.id = id
        self.date = date
        self.date_timestamp = date_timestamp
        self.note = note
        self.event_id = event_id
        self.event_name = event_name
        self.added_by_id = added_by_id
        self.added_by_name = added_by_name
        self.value = value
        self.raid_attendees = raid_attendees

    @classmethod
    async def convert(cls, ctx, argument: int):

        def check_author(m):
            return m.author == ctx.author

        raids = eqdkp.get_raids(n=10)
        raid = [raid for raid in raids if raid.id == argument]

        if not raid:
            await ctx.send(f'`Raid id #{argument} seems to be invalid.  Please enter the correct id:`')
            try:
                msg = await ctx.bot.wait_for('message', check=check_author, timeout=30)
                argument = int(msg.content)
                raid = [raid for raid in raids if raid.id == argument]
            except Exception:
                pass

        return raid[0] if raid else None
