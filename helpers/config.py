
POINTS_URL = 'index.php/Points'
API_URL = 'api.php'

EQ_RE_TELLS_YOU = r'^\[[a-zA-Z0-9: ]{24}\] (\w*?) tells you, \'(.*)\'$'

EQDKP_COLUMNS = ['CHARACTER', 'CLASS', 'DKP', '30DAY', '60DAY', '90DAY']

ADDITIONAL_FILTERS = ['ORDERBY', 'TOP']

INDEX_SORT = {'DKP': False, '30DAY': False}

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