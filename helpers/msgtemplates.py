# DISCORD BOT DEFAULT TEMPLATES

LOG_ENTRY_FOR_RAID = """```md
# Raid Entry Log [{raid_id}]
> {url}

     <DATE>                    <EVENT>                 <DKP>
  ------------    ---------------------------------    -----
 {date} {event} {dkp} 

* Raid Participants
> {attendees}
```"""

LOG_ENTRY_FOR_ADJUSTMENT = """```md
# Adjustment Entry Log

Reason: {reason}
Value: {value}

* Members receiving adjustment
> {members}
```"""

ADJUSTMENT_VALUE = """```md
# Adjustment Entry

You have requested to add an adjustment: {reason}.

1. Please entry the value of this adjustment:
```"""

ADJUSTMENT_MEMBERS = """```md
2. Please enter the member(s) you would like to give this adjustment to:
> You can enter one member, or if multiple, separate with commas
```"""

ADJUSTMENT_RAID = """```md
3. Would you like to assign this adjustment to a raid? [Yes|No]
```"""

ADJUSTMENT_RAID_ID = """```md
4. What raid would you like to apply this adjustment to?  Please enter the raid id:
```"""

RAID_FOUND = """```md
# Raid Found!

You have selected Raid #[{raid_id}][{raid_event_name}] on {raid_date}

> If this is the wrong raid, please enter <cancel> now

1. Please enter the items from this raid in the following format: <Character> <DKP> <Item Name>
2. When you are done entering items, enter <done>
```"""

ADD_RAID_CREDITT = """```md
# CREDITT additions

1. Would you like to add any players to this dump? [Yes|No]```"""

ADD_RAID_CREDITT_MEMBERS = """```md
2. Please enter a comma separated list of players you would like to add:
> Example: Player1,Player2,Player3```"""

ADD_RAID_MISSING_MEMBERS = """```md
# Missing Players

The following [{count}][raiders] are not currently in EqDkp:
{member_list}

1. Would you like to add them to eqdkp & raid? [Yes|No]```"""

ADD_RAID_NOTE = """```md
# Raid Note

1. Please enter a note for this raid:```"""
