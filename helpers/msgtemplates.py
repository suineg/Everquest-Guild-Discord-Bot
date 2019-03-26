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
