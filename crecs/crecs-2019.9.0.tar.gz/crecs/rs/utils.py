# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

from crecs import ds
from crecs.rs import abc


def get_n_users(users: abc.UsersT, default: int) -> int:
    if users is None:
        return default

    if isinstance(users, int):
        return 1

    if isinstance(users, ds.Matrix):
        return users.n_users

    return len(users)
