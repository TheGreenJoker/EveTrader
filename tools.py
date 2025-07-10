def ask_input(prompt, default, cast_func=str):
    """
    Ask user for input with a default value.
    Cast input with cast_func (int, float, str).
    If empty input, return default.
    """
    while True:
        user_input = input(f"{prompt} [{default}]: ").strip()
        if not user_input:
            return default
        try:
            return cast_func(user_input)
        except ValueError:
            print(f"Invalid input, please enter a valid {cast_func.__name__}.")


def ask_yes_no(prompt, default_yes=True):
    """
    Ask user a yes/no question with default.
    Returns True/False.
    """
    default_str = "Y/n" if default_yes else "y/N"
    while True:
        user_input = input(f"{prompt} [{default_str}]: ").strip().lower()
        if not user_input:
            return default_yes
        if user_input in ('y', 'yes'):
            return True
        if user_input in ('n', 'no'):
            return False
        print("Please answer yes or no (y/n).")
