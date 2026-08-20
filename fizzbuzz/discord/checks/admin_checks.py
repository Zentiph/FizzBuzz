"""Admin-only check using DB admin roles."""

import discord
from discord import app_commands

from ...db.settings import settings_manager
from ..ui.emoji import Status
from .guild_checks import NotInGuild
from .types import Check

__author__ = "Gavin Borne"
__license__ = "MIT"

__all__ = ["Unauthorized", "admin_only", "owner_only"]


class Unauthorized(app_commands.CheckFailure):
    """Raised when an unauthorized user attempts to use an authorized command."""

    def __init__(self, message: str | None = None) -> None:
        """Raised when an unauthorized user attempts to use an authorized command.

        Args:
            message (str | None, optional): The error message.
                Leave as None for a default. Defaults to None.
        """
        super().__init__(
            message
            or f"{Status.FAILURE} You do not have permissions to use this command."
        )


def admin_only() -> Check:
    """A check that ensures a command can only be used by an admin."""

    async def predicate(interaction: discord.Interaction) -> bool:  # NOSONAR
        member = interaction.user

        if interaction.guild is None or isinstance(member, discord.User):
            raise NotInGuild()

        if interaction.guild.owner_id == member.id:
            return True
        if member.guild_permissions.administrator:
            return True

        admin_role_ids = await settings_manager.get_admin_role_ids(interaction.guild.id)
        if admin_role_ids and any(r.id in admin_role_ids for r in member.roles):
            return True

        raise Unauthorized()

    return app_commands.check(predicate)


def owner_only() -> Check:
    """A check that ensures a command can only be used by the owner."""

    def predicate(interaction: discord.Interaction) -> bool:
        member = interaction.user

        if interaction.guild is None or isinstance(member, discord.User):
            raise NotInGuild()

        if interaction.guild.owner_id == member.id:
            return True

        raise Unauthorized()

    return app_commands.check(predicate)
