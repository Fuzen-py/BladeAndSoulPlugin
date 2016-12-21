import discord
from os import path

from BladeAndSoul import character as Character
from BladeAndSoul.bns import avg_dmg
from BladeAndSoul.bns import fetch_profile
from BladeAndSoul.errors import (CharacterNotFound, Error, InvalidData,
                                 ServiceUnavialable)
from discord.ext import commands

import json

from .values import DATA


def fetch_user(id):
    P = path.join(DATA, id)
    if not path.exists:
        return
    with open(P, errors='backslashreplace') as f:
        return json.load(f)


async def find_character(ctx, char):
    if char and not char.isnumeric():
        return await Character(char)
    if len(ctx.message.raw_mentions):
        char = ctx.message.raw_mentions[0]
        char = fetch_user(str(char))
        if not char:
            raise CharacterNotFound
        char = char.get('Character Name')
        if not char:
            raise CharacterNotFound
        return await Character(char)
    if char:
        fetch_user(char)
        if not char:
            raise CharacterNotFound
        char = await Character(char)
        if char is None:
            raise InvalidData
        return char


class BladeAndSoul:
    """Blade And Soul Commands."""

    def __init__(self, bot: commands.Bot):
        """Init Statement."""
        self.bot = bot

    @commands.group(pass_context=True)
    async def bns(self, ctx):
        """Blade And Soul Command Group."""
        pass

    @bns.command(pass_context=True)
    async def profile(self, ctx, *, char=None):
        """Blade And Soul Profile."""
        try:
            await self.bot.say((await find_character(ctx,
                                                     char)).pretty_profile())
            return
        except CharacterNotFound:
            await self.bot.say('Could not find character')
            return
        except ServiceUnavialable:
            await self.bot.say('Cannot access BNS try again later.')
        except (Error, InvalidData) as e:
            await self.bot.say('An unexpected error has occured.')

    @bns.command(pass_context=True)
    async def stats(self, ctx, *, char=None):
        """Blade And Soul Stats."""
        try:
            await self.bot.say((await find_character(ctx,
                                                     char)).pretty_stats())
            return
        except CharacterNotFound:
            await self.bot.say('Could not find character')
            return
        except ServiceUnavialable:
            await self.bot.say('Cannot access BNS try again later.')
        except (Error, InvalidData):
            await self.bot.say('An unexpected error has occured.')

    @bns.command(pass_context=True)
    async def gear(self, ctx, *, char=None):
        """Blade And Soul Gear, for the requested character."""
        try:
            await self.bot.say((await find_character(ctx, char)).pretty_gear())
            return
        except CharacterNotFound:
            await self.bot.say('Could not find character')
            return
        except ServiceUnavialable:
            await self.bot.say('Cannot access BNS try again later.')
        except (Error, InvalidData):
            await self.bot.say('An unexpected error has occured.')

    @bns.command(pass_context=True)
    async def outfit(self, ctx, *, char=None):
        """Blade And Soul Outfit, for the requested character."""
        try:
            await self.bot.say((await find_character(ctx,
                                                     char)).pretty_outfit())
            return
        except CharacterNotFound:
            await self.bot.say('Could not find character')
            return
        except ServiceUnavialable:
            await self.bot.say('Cannot access BNS try again later.')
        except (Error, InvalidData):
            await self.bot.say('An unexpected error has occured.')

    @bns.command(pass_context=True)
    async def save(self, ctx, *, char):
        """Save Character, so you dont have to type the name everytime."""
        with open(path.join(DATA, str(ctx.message.author.id)), 'w',
                  errors='backslashreplace') as f:
            json.dump({'Character Name': (await fetch_profile(char)).name}, f)
        await self.bot.say('Saved')

    @bns.command(pass_context=True, name='avg')
    async def avg_dmg(self, ctx, attack_power: str, critical_rate: str,
                      critical_damage: str, elemental_bonus: str='100%'):
        """Inaccurate, maybe broken."""
        embed = discord.Embed()
        embed.title = 'Average Damage'
        auth = ctx.message.author
        avatar = auth.avatar_url or auth.default_avatar_url
        embed.set_author(name=str(auth), icon_url=avatar)
        no_blue, with_blue = avg_dmg(attack_power, critical_rate,
                                     critical_damage, elemental_bonus)
        embed.add_field(name='No Buff', value=no_blue)
        embed.add_field(name='Blue Buff', value=with_blue)
        await self.bot.say(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(BladeAndSoul(bot))
