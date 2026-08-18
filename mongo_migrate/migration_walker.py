from dataclasses import dataclass
from pathlib import Path
from typing import Self

from mongo_migrate.enums import BaseFlag, Target
from mongo_migrate.utils import timestamp_from_filename


@dataclass
class Migration:
    filename: str
    previous: Self | None
    next: Self | None

    @property
    def timestamp(self) -> str:
        """ Migration timestamp """
        ret = timestamp_from_filename(self.filename)
        return ret

    @property
    def basename(self) -> str:
        """ Migration file base name (without extension) """
        ret = Path(self.filename).stem
        return ret

class MigrationWalker:
    """
    Migration walker.

    Facilitates walking between migrations
        such as finding first/last/next/previous migration etc.
    """
    def __init__(self, migration_filenames: list[str]) -> None:
        """
        Populate list of disconnected migrations.
        Connect migrations among each other by establishing previous and next migrations.
        Map migrations to timestamps.
        """
        migration_filenames.sort()

        migrations = [ Migration(filename=filename, previous=None, next=None) for filename in migration_filenames]
        num_migrations = len(migrations)

        for idx, migration in enumerate(migrations):
            previous_migration = None if idx == 0 else migrations[idx-1]
            next_migration = None if idx == num_migrations - 1 else migrations[idx+1]

            migration.previous = previous_migration
            migration.next = next_migration

        self._migrations = migrations

        self._migration_map = {m.timestamp: m for m in self._migrations}
        self._timestamps = list(self._migration_map.keys())

    @property
    def last_migration(self) -> Migration:
        return self._migrations[-1]

    @property
    def first_migration(self) -> Migration:
        return self._migrations[0]

    def has_migration(self, timestamp: str) -> bool:
        """
        Whether migration with given timestamp is present.
        """
        ret = timestamp in self._migration_map
        return ret

    def get_migration(self, timestamp: str) -> Migration:
        """
        Get migration by timestamp.
        """
        ret = self._migration_map[timestamp]
        return ret

    def get_target_timestamp(self, keyword_target: str, reference_timestamp: str | BaseFlag) -> str | BaseFlag:
        """
        Get migration timestamp based on keyword and reference timestamp.

        keyword_target (str): head/base/+N/-N

        If target is head, last timestamp is returned.
        If target is base, base is returned (does not correspond to any timestamp).
        Reference timestamp can be base (no completed migrations)
        """
        if keyword_target == Target.head:
            return self.last_migration.timestamp
        
        if keyword_target == Target.base:
            return BaseFlag.base

        if keyword_target.startswith("+"):
            next_timestamp = self._get_next_timestamp(reference_timestamp, int(keyword_target[1:]))
            return next_timestamp

        if keyword_target.startswith("-"):
            previous_timestamp = self._get_previous_timestamp(reference_timestamp, int(keyword_target[1:]))
            return previous_timestamp

        raise ValueError(f"Keyword target {keyword_target} not recognized!")


    def get_migrations_between(self, timestamp_from: str | BaseFlag, timestamp_to: str) -> list[Migration]:
        """
        Get migrations between given timestamps.

        timestamp_to is included, timestamp_from is not i.e. migrations start from one after timestamp_from.
        """
        migration_start = self.first_migration if timestamp_from == BaseFlag.base else self.get_migration(timestamp_from).next or self.last_migration
        migration_end = self.get_migration(timestamp_to)

        timestamps_between = self._get_timestamps_between(migration_start.timestamp, migration_end.timestamp)
        ret = [self._migration_map[timestamp] for timestamp in timestamps_between]
        return ret


    def _get_timestamps_between(self, start_timestamp: str, end_timestamp: str) -> list[str]:
        """
        Get list of timestamps between the given two.

        Both timestamps are included.
        """
        idx_start = self._timestamps.index(start_timestamp)
        idx_end = self._timestamps.index(end_timestamp)
        ret = self._timestamps[idx_start : idx_end + 1]
        return ret


    def _get_next_timestamp(self, reference_timestamp: str | BaseFlag, step: int) -> str:
        """
        Get migration timestamp given number of steps after reference timestamp.
        """
        # NOTE: assumes start = base and step = 0 never happens
        if step == 0:
            return reference_timestamp
        
        if reference_timestamp == BaseFlag.base:
            next_timestamp = self.first_migration.timestamp
        else:
            reference_migration = self.get_migration(reference_timestamp)
            next_migration = reference_migration.next
            if next_migration is None:
                return self.last_migration.timestamp
            next_timestamp = next_migration.timestamp

        return self._get_next_timestamp(next_timestamp, step-1)
    
    def _get_previous_timestamp(self, reference_timestamp: str | BaseFlag, step: int) -> str | BaseFlag:
        """
        Get migration given number of steps before reference timestamp.
        """
        if step == 0:
            return reference_timestamp
        
        if reference_timestamp == BaseFlag.base:
            return BaseFlag.base
        
        reference_migration = self.get_migration(reference_timestamp)
        previous_migration = reference_migration.previous
        if previous_migration is None:
            return BaseFlag.base

        return self._get_previous_timestamp(previous_migration.timestamp, step-1)