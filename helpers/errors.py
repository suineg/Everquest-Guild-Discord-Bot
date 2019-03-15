class Error(Exception):

    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)


class InvalidRaidRosterFile(Error):
    pass
