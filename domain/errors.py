class ConsentRequired(RuntimeError):
    """Пользователь ещё не согласился с политикой обработки ПДн."""

    def __init__(self, telegram_id: int) -> None:
        super().__init__(f"consent required for telegram_id={telegram_id}")
        self.telegram_id = telegram_id
