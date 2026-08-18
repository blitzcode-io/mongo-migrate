import re
from typing import Any, Iterable

from mongo_migrate.enums import Direction, Target


def slugify_message(message: str, truncate_slug_length: int = 40) -> str:
    """
    Slugify message to create a short cleaned up filename safe identifier.

    Filename incompatible characters (e.g. punctuation, /) are removed.
    Spaces are replaced by underscores.
    All characters converted to lowercase.
    
    >>> slugify_message("add ABCD data/info")
    "add_abcd_data_info"

    Procedure taken from alembic:
    https://github.com/sqlalchemy/alembic/blob/main/alembic/script/base.py    
    """
    _slug_re = re.compile(r"\w+")

    slug = "_".join(_slug_re.findall(message)).lower()
    if len(slug) > truncate_slug_length:
        slug = slug[:truncate_slug_length].rsplit("_", 1)[0] + "_"
    return slug


def timestamp_from_filename(filename: str) -> str:
    """
    Extract timestamp from migration filename.
    """
    return filename.split('_')[0]


def is_timestamp_target(target: str) -> bool:
    """
    Determine if target is timestamp.
    """
    return target.isnumeric() and len(target) == 14


def is_increment_target(target: str, sign: str) -> bool:
    """
    Determine if target is an increment +N or -N
    """
    return target.startswith(sign) and target[1:].isnumeric()


def is_upgrade_target(target: str) -> bool:
    """
    Determine if target is upgrade-compatible keyword.

    Available keywords: head, +N
    """
    return target == Target.head or is_increment_target(target, "+")


def is_downgrade_target(target: str) -> bool:
    """
    Determine if target is downgrade-compatible keyword.

    Available keywrods: base, -N
    """
    return target == Target.base or is_increment_target(target, "-")


def is_keyword_target(target: str) -> bool:
    """
    Determine if target is a keyword.
    """
    return is_upgrade_target(target) or is_downgrade_target(target)


def direction_target_is_valid(direction: Direction, target: str) -> bool:
    """
    Check validity of direction (upgrade/downgrade) and target (timestamp or keyword).

    Timestamp is a valid target for all cases.
    """
    if is_timestamp_target(target):
        return True

    if direction == Direction.up and not is_upgrade_target(target):
        return False
    
    if direction == Direction.down and not is_downgrade_target(target):
        return False

    return True

def values_are_complete(values: Iterable[Any]) -> bool:
    """
    Check if values are complete.

    Complete means all values are not null.
    """
    for value in values:
        if value is None:
            return False
    return True        