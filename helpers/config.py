import re

POINTS_URL = 'index.php/Points'
API_URL = 'api.php'

EQDKP_COLUMNS = [
    'CHARACTER',
    'CLASS',
    'DKP',
    '30DAY',
    '60DAY',
    '90DAY'
]

ADDITIONAL_FILTERS = [
    'ORDERBY',
    'TOP'
]

EQDKP_SPAN_ATTRS = {
    'positive',
    'negative',
    'neutral',
    re.compile('class_*')
}

INDEX_SORT = {
    'DKP': False,
    '30DAY': False
}

ORDER_BY_ASC_DEFAULTS = {
    'CHARACTER': True,
    'CLASS': True,
    'DKP': False,
    '30DAY': False,
    '60DAY': False,
    '90DAY': False
}

EQ_CLASS_SIMILARITIES = {
    'Enchanter': ['enc', 'enchant', 'buffbitch'],
    'Necromancer': ['nec', 'necro', 'corpsefucker'],
    'Wizard': ['wiz', 'boom'],
    'Magician': ['mag', 'mage', 'petfucker'],
    'Warrior': ['war'],
    'Paladin': ['pal', 'pussy', 'pally'],
    'Shadow Knight': ['sk', 'shd', 'op', 'shadowknight'],
    'Bard': ['brd', 'sing'],
    'Berserker': ['ber', 'zerker'],
    'Shaman': ['shm', 'sham'],
    'Druid': ['dru', 'dro'],
    'Cleric': ['clr', 'cler'],
    'Monk': ['mnk'],
    'Rogue': ['rog'],
    'Ranger': ['rng', 'rang'],
    'Beastlord': ['bst', 'beast']
}

LAST_RUN = None
SPAM_DELAY_IN_SECONDS = 5

INSULTS = [
    "Hey do me a favor shit-bag, stop spamming the channel!",
    "I swear to god, if you ping me one more time, I'm  going to delete your DKP.",
    "Go fuck an aids ridden corpse you worthless piece of shit.",
    "I sincerely hope you die in a fire.",
    "You're worse than Cupie, let's be honest."
]
