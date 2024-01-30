class AlreadyActiveEventLoop(Exception):
    @classmethod
    def __init__(cls) -> None:
        cls.msg: str = "A repl event-loop is already running!"

    @classmethod
    def __str__(cls) -> str:
        return cls.msg


class ReplNotInitialized(Exception):
    @classmethod
    def __init__(cls) -> None:
        cls.msg: str = (
            "Repl instance not initialized!, run init_repl() before start_repl()"
        )

    @classmethod
    def __str__(cls) -> str:
        return cls.msg


class UnidentifiedToken(Exception):
    @classmethod
    def __init__(cls, token) -> None:
        cls.msg: str = (
            "Encountered Unidentified token while parsing the table. token: `{}`".format(
                token
            )
        )

    @classmethod
    def __str__(cls) -> str:
        return cls.msg
