import json
from os import path

import discord
from BladeAndSoul import character as Character
from BladeAndSoul.bns import avg_dmg, fetch_profile
from BladeAndSoul.errors import (CharacterNotFound, Error, InvalidData,
                                 ServiceUnavialable)
from discord.ext import commands

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

    @staticmethod
    def color_pick(faction):
        if faction is None:
            return discord.Color.darker_grey()
        if faction == 'Cerulean Order':
            return discord.Color.blue()
        return discord.Color.red()

    @commands.group(pass_context=True)
    async def bns(self, ctx):
        """Blade And Soul Command Group."""
        pass

    @bns.command(pass_context=True)
    async def profile(self, ctx, *, char=None):
        """Blade And Soul Profile."""
        try:
            character = await find_character(ctx, char)
            embed = discord.Embed(color=self.color_pick(character['Faction']))
            embed.set_author(name=character['Character Name'],
                             icon_url=character['Picture'])
            embed.add_field(name='Display Name', value=character['Account Name'])
            embed.add_field(name='Server', value=character["Server"])
            embed.add_field(name='Character', value=character['Character Name'])
            if character['HM Level']:
                embed.add_field(name='Level',
                                value= f'{character["Level"]} HM {character["HM Level"]}')
            else:
                embed.add_field(name='Level', value=character["Level"])
            embed.add_field(name='Weapon', value=character["Gear"]["Weapon"])
            if character['Faction']:
                embed.add_field(name='Faction', value=character['Faction'])
                embed.add_field(name='Faction Rank', value=character['Faction Rank'])
                if character['Clan']:
                    embed.add_field(name='Clan', value=character['Clan'])
            if len(character['Other Characters']):
                embed.add_field(name='ALTS',
                                value='\n'.join(character['Other Characters']))
            embed.set_image(url=character['Picture'])
            try:
                await self.bot.say(embed=embed)
            except discord.Forbidden:
                await self.bot.say(character.pretty_profile())
        except CharacterNotFound:
            await self.bot.say('Could not find character')
            return
        except ServiceUnavialable:
            await self.bot.say('Cannot access BNS try again later.')
        except (Error, InvalidData):
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
            character = await find_character(ctx, char)
            embed = discord.Embed(color=self.color_pick(character['Faction']))
            embed.set_author(name=character['Character Name'],
                             icon_url=character['Picture'])
            outfit = character['Outfit']
            for k in ['Clothes', 'Head', 'Face', 'Adornment']:
                v = outfit[k]
                if v is not None:
                    embed.add_field(name=k, value=v)
            try:
                await self.bot.say(embed=embed)
            except discord.Forbidden:
                await self.bot.say(character.pretty_outfit())

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
            json.dump({'Character Name': (await fetch_profile(char))['Character Name']}, f)
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
