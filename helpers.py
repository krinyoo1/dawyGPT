from pathlib import Path
import time

BASE_DIR = Path(__file__).resolve().parent

BALANCE_FILE = BASE_DIR / "data" / "balance"
BEG_FILE = BASE_DIR / "data" / "beg"

def get_data(file_of_interest, user_id: str, value_of_interest: int, create_on_missing: bool, def_value: int): # returns value, target_index, lines
    target_index = None
    value = None
    found_value = False

    file_of_interest.parent.mkdir(parents=True, exist_ok=True)
    if not file_of_interest.exists():
        file_of_interest.touch()

    with file_of_interest.open("r") as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        line = line.strip().split(";")
        storedID = line[0]
        if storedID == user_id:
            found_value = True
            target_index = i
            value = int(line[value_of_interest])
            break

    if create_on_missing and def_value is not None:
        if not found_value:
            value = def_value
            target_index = len(lines)
            lines.append(f"{user_id};{value}\n")

    return value, target_index, lines

def write_data(file_of_interest, user_id: str, value, lines, target_index):
    if target_index is None:
        if value is None:
            return
        lines.append(f"{user_id};{value}\n")
    elif target_index == len(lines):
        lines.append(f"{user_id};{value}\n")
    elif value is None:
        del lines[target_index]
    else:
        lines[target_index] = f"{user_id};{value}\n"

    with file_of_interest.open("w") as file:
        file.writelines(lines)

def edit_balance(user_id: str, type: str, amount: int):
    DEFAULT_BALANCE = 100

    balance, target_index, lines = get_data(file_of_interest=BALANCE_FILE, user_id=user_id, value_of_interest=1, create_on_missing=True, def_value=DEFAULT_BALANCE)

    match type:
        case "add":
            balance += amount
        case "remove":
            balance -= amount
        case "edit":
            balance = amount
        case "read":
            pass
        case _:
            raise ValueError("Incorrect type!")

    write_data(file_of_interest=BALANCE_FILE, user_id=user_id, value=str(balance), lines=lines, target_index=target_index)

    return balance

def beg_cooldown(user_id: str, type: str):
    DEFAULT_COOLDOWN = 3 * 60 # 3 minutes
    TIME_NOW = int(time.time())
    is_cooldown = False

    last_cooldown, target_index, lines = get_data(file_of_interest=BEG_FILE, user_id=user_id, value_of_interest=1, create_on_missing=False, def_value=None)

    match type:
        case "read":
            if last_cooldown is None:
                return False
            if TIME_NOW - float(last_cooldown) > DEFAULT_COOLDOWN:
                write_data(file_of_interest=BEG_FILE, user_id=user_id, value=None, lines=lines, target_index=target_index)
            else:
                is_cooldown = True
        case "write":
            write_data(file_of_interest=BEG_FILE, user_id=user_id, value=TIME_NOW, lines=lines, target_index=target_index)
            is_cooldown = True

    return is_cooldown