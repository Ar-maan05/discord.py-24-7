import discord
from discord import colour
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient
#import webserver
#from webserver import keep_alive
#import os
import datetime
import asyncio
import random
from random import choice
import time
import youtube_dl

client = commands.Bot(command_prefix="#")
client.remove_command("help")

status = ['Jamming out to music!', 'Eating?', 'Sleeping!']

filtered_words = ["bitch", "nigga", "bsdk"]


@client.event
async def on_ready():
	change_status.start()
	print("Bot is ready")


@client.event
async def on_message(msg):
	for word in filtered_words:
		if word in msg.content:
			await msg.delete()

	await client.process_commands(msg)


@client.command(aliases=['b'])
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
	await member.send(f"You has been banned from the server, Because: " + reason +
		". To appeal join this server https://discord.gg/XZcNs6pe")
	await ctx.send(f"{member} was banned!")
	await member.ban(reason=reason)


@client.command(aliases=['ub'])
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
	banned_users = await ctx.guild.bans()
	member_name, member_disc = member.split('#')

	for banned_entry in banned_users:
		user = banned_entry.user

		if (user.name, user.discriminator) == (member_name, member_disc):
			await ctx.guild.unban(user)
			await ctx.send(member_name + " has baan unbanned!")
			return

	await ctx.send(member + " was not found")


@client.command(aliases=['k'])
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
	await ctx.send(member.name + " has been kicked from the server")
	await member.kick(reason=reason)


@client.command(aliases=['m'])
@commands.has_permissions(kick_members=True)
async def mute(ctx, member: discord.Member):
	muted_role = ctx.guild.get_role(848905740956729425)

	await member.add_roles(muted_role)

	await ctx.send(member.mention + " was muted!")


@client.command(aliases=['um'])
@commands.has_permissions(kick_members=True)
async def unmute(ctx, member: discord.Member):
	muted_role = ctx.guild.get_role(848905740956729425)

	await member.remove_roles(muted_role)

	await ctx.send(member.mention + " was unmuted!")


def convert(time):
	pos = ["s", "m", "h", "d"]

	time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600*24}

	unit = time[-1]

	if unit not in pos:
		return -1
	try:
		val = int(time[:-1])
	except:
		return -2

	return val * time_dict[unit]


@client.command()
@commands.has_role(841660167245529169)
async def giveaway(ctx):
	await ctx.send(
	    "Let's start with this giveaway! Answer these questions within 15 seconds!"
	)

	questions = [
	    "Which channel should it be hosted in?",
	    "What should be the duration of the giveaway? (s|m|h|d)",
	    "What is the prize of the giveaway?"
	]

	answers = []

	def check(m):
		return m.author == ctx.author and m.channel == ctx.channel

	for i in questions:
		await ctx.send(i)

		try:
			msg = await client.wait_for('message', timeout=15.0, check=check)
		except asyncio.TimeoutError:
			await ctx.send(
			    'You didn\'t answer in time, please be quicker next time!')
			return
		else:
			answers.append(msg.content)

	try:
		c_id = int(answers[0][2:-1])
	except:
		await ctx.send(
		    f"You didn't mention a channel properly. Do it like this {ctx.channel.mention} next time."
		)
		return

	channel = client.get_channel(c_id)

	time = convert(answers[1])
	if time == -1:
		await ctx.send(
		    f"You didn't answer with a proper unit. Use (s|m|h|d) next time!")
		return
	elif time == -2:
		await ctx.send(
		    f"The time just be an integer. Please enter an integer next time.")
		return
		
	prize = answers[2]

	await ctx.send(
	    f"The giveaway will be in {channel.mention} and will last {answers[1]} seconds!"
	)

	embed = discord.Embed(title="Giveaway!",
	                      description=f"{prize}",
	                      color=ctx.author.color)

	embed.add_field(name="Hosted by:", value=ctx.author.mention)

	embed.set_footer(text=f"Ends {answers[1]} from now!")

	my_msg = await channel.send(embed=embed)

	await my_msg.add_reaction("🎉")

	await asyncio.sleep(time)

	new_msg = await channel.fetch_message(my_msg.id)

	users = await new_msg.reactions[0].users().flatten()
	users.pop(users.index(client.user))

	winner = random.choice(users)

	await channel.send(
	    f"Congratulations! {winner.mention} won the prize: {prize}!")


@client.command()
@commands.has_permissions(kick_members=True)
async def reroll(ctx, channel: discord.TextChannel, id_: int):
	try:
		new_msg = await channel.fetch_message(id_)
	except:
		await ctx.send(
		    "The ID that was entered was incorrect, make sure you have entered the correct giveaway message ID."
		)
	users = await new_msg.reactions[0].users().flatten()
	users.pop(users.index(client.user))

	winner = random.choice(users)

	await channel.send(
	    f"Congratulations the new winner is: {winner.mention} for the giveaway rerolled!"
	)

@client.command(aliases=['c'])
@commands.has_permissions(manage_messages = True)
async def clear(ctx, amount=2):
	await ctx.channel.purge(limit = amount)

@client.group(invoke_without_command = True)
async def help(ctx):
	em = discord.Embed(title = "Help", description = "Use #help <command> for extended information on a command", color = ctx.author.color)
	
	em.add_field(name = "Moderation", value = "kick, ban, unban, mute, unmute, ping")
	em.add_field(name = "Giveaway", value = "giveaway, reroll")
	em.add_field(name = "Fun", value = "music, credits, creditz, hello, die")


	await ctx.send(embed = em)

@help.command()
async def kick(ctx):
	em = discord.Embed(title = "Kick", description = "Kicks a member from the server", color = ctx.author.color)

	em.add_field(name = "**Syntax**", value = "#kick <member> [reason]")

	await ctx.send(embed = em)


@help.command()
async def ban(ctx):
	em = discord.Embed(title = "Ban", description = "Bans a member from the server", color = ctx.author.color)

	em.add_field(name = "**Syntax**", value = "#ban <member> [reason]")

	await ctx.send(embed = em)


@help.command()
async def unban(ctx):
	em = discord.Embed(title = "Unban", description = "Unbans a member from the server", color = ctx.author.color)

	em.add_field(name = "**Syntax**", value = "#unban <username(with tag)>")

	await ctx.send(embed = em)


@help.command()
async def mute(ctx):
	em = discord.Embed(title = "Mute", description = "Mutes a member", color = ctx.author.color)

	em.add_field(name = "**Syntax**", value = "#mute <member> [reason]")

	await ctx.send(embed = em)


@help.command()
async def unmute(ctx):
	em = discord.Embed(title = "Unmute", description = "Unmutes a member", color = ctx.author.color)

	em.add_field(name = "**Syntax**", value = "#unmute <member>")

	await ctx.send(embed = em)


@help.command()
async def giveaway(ctx):
	em = discord.Embed(title = "Giveaway", description = "Starts a giveaway in the specified channel", color = ctx.author.color)

	em.add_field(name = "**Syntax**", value = "Type #giveaway into chat and then follow the instructions!")

	await ctx.send(embed = em)


@help.command()
async def ping(ctx):
	em = discord.Embed(title = "Ping", description = "Tells the latency of the bot!", color = ctx.author.color)

	em.add_field(name = "**Syntax**", value = "Type #ping to get the latency of the bot")

	await ctx.send(embed = em)

@help.command()
async def music(ctx):
	em = discord.Embed(title = "Music Commands (Sorry but the music commands aren't working temporarily)", description = "The music commands are: ", color = ctx.author.color)

	em.add_field(name = "**Play**", value = "#play <song name>")
	em.add_field(name = "**Stop**", value = "#stop <makes the bot stop playing and leave the vc>")

	await ctx.send(embed = em)

@help.command()
async def credits(ctx):
	em = discord.Embed(title = "Credits", description = "The command returns the credits", color = ctx.author.color)

	em.add_field(name = "**Syntax**", value = "#credits")

	await ctx.send(embed = em)

@help.command()
async def creditz(ctx):
	em = discord.Embed(title = "Creditz", description = "The command returns the TRUE credits", color = ctx.author.color)

	em.add_field(name = "**Syntax**", value = "#creditz")

	await ctx.send(embed = em)

@help.command()
async def hello(ctx):
	em = discord.Embed(title = "Hello", description = "This command returns a random welcome message", color = ctx.author.color)

	em.add_field(name = "**Syntax**", value = "#hello")

	await ctx.send(embed = em)

@help.command()
async def die(ctx):
	em = discord.Embed(title = "Die", description = "This command returns random last words", color = ctx.author.color)

	em.add_field(name = "**Syntax**", value = "#die")

	await ctx.send(embed = em)

@help.command()
async def reroll(ctx):
	em = discord.Embed(title = "Reroll", description = "Used to reroll a giveaway", color = ctx.author.color)

	em.add_field(name = "**Syntax**", value = "#reroll <channel the giveaway is in> [Message ID of the giveaway]")

	await ctx.send(embed = em)


@tasks.loop(seconds=20)
async def change_status():
	await client.change_presence(activity=discord.Game(choice(status)))

@client.command(name='ping')
async def ping(ctx):
	await ctx.send(f"**Pong!** Latency: {round(client.latency * 1000)}ms")

@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='💬┌・general')
    await channel.send(f'Welcome {member.mention}!  Ready to jam out? See `#help` command for details!')

@client.command(name='credits')
async def credits(ctx):
	await ctx.send('Made by `Low-Key#3264`')
	await ctx.send('Thanks to `DemonWeilder#9031` for the idea for the music commands')
	await ctx.send('Thanks to `OfFbeat ̥ ˊˎ-#4729` for inspiring me to actually make this bot')

@client.command(name='creditz')
async def creditz(ctx):
    await ctx.send('**No one but me, lozer!**')

@client.command(name='hello')
async def hello(ctx):
    responses = ['***grumble*** Why did you wake me up?', 'Top of the morning to you lad!', 'Hello, how are you?', 'Hi', '**Wasssuup!**']
    await ctx.send(choice(responses))

@client.command(name='die')
async def die(ctx):
    responses = ['why have you brought my short life to an end', 'i could have done so much more', 'i have a family, kill them instead']
    await ctx.send(choice(responses))

client.run("ODg3MjIyNDE1MzQyNjAwMTky.YUBAQw.cPP4nWkAuFVjrpsZcLlia9_rWyI")
