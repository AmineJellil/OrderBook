import discord
from discord.ext import commands

# Ensure you have run pip install discord.py before

# Define bot and intents
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# I got this from the dev portal here: https://discord.com/developers/applications/1297489265286053888/bot
TOKEN = 'REDACTED_USE_ENV_VAR'

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Example of a simple slash command
# @bot.tree.command(name='ping', description='Responds with Pong!')
# async def ping(interaction: discord.Interaction):
#     await interaction.response.send_message("Pong!")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Command to kick all members
@bot.command()
@commands.has_role("admin")  # Change this to the role allowed to run commands
async def kickall(ctx):
    kicked_count = 0 
    for member in ctx.guild.members:
        try:
            if member != ctx.guild.owner and not member.bot:
                await member.kick(reason="Mass kick initiated.")
                print(f"Kicked {member.name}")
                kicked_count += 1
        except Exception as e:
            print(f"Could not kick {member.name}: {e}")
    await ctx.send(f"Kicked {kicked_count} members")

# Command to kick all members with the "student" role
@bot.command()
@commands.has_role("admin")  # Only members with the "admin" role can use this command
async def kick_students(ctx):
    # Get the "student" role from the server
    student_role = discord.utils.get(ctx.guild.roles, name="student")
    
    if not student_role:
        await ctx.send("The 'student' role does not exist.")
        return

    kicked_count = 0  # Track how many members have been kicked
    for member in ctx.guild.members:
        if student_role in member.roles:
            try:
                # Kick the member with the "student" role
                await member.kick(reason="Mass kick of all students")
                kicked_count += 1
                print(f"Kicked {member.name}")
            except Exception as e:
                print(f"Failed to kick {member.name}: {e}")
    
    await ctx.send(f"Kicked {kicked_count} members with the 'student' role.")

  
@bot.event
async def on_member_join(member):
    # Fetch the invites used in the server before the user joined
    invites_before = await member.guild.invites()

    # After the user joined, compare with the previous invites to see which was used
    used_invite = None
    for invite in invites_before:
        if invite.uses > 0:  # Check if the invite has been used
            used_invite = invite
            break  # Found the used invite, break out of the loop

    if used_invite:
        if used_invite.code == 'z7BKw6fr4a':  # Admins link  https://discord.gg/z7BKw6fr4a
            admin_role = discord.utils.get(member.guild.roles, name="admin")  # Fetch admin role
            if admin_role:
                await member.add_roles(admin_role)
                print(f"Assigned 'admin' role to {member.name}")

        elif used_invite.code == '9B2Vkk7FwG':  # Students link: https://discord.gg/9B2Vkk7FwG
            student_role = discord.utils.get(member.guild.roles, name="student")  # Fetch student role
            if student_role:
                await member.add_roles(student_role)
                print(f"Assigned 'student' role to {member.name}")
        else:
            print(f"Unknown invite used by {member.name}")
    else:
        # Default to assigning the student role
        role = discord.utils.get(member.guild.roles, name="student")
        
        # Check if the role exists
        if role:
            try:
                # Assign the "student" role to the new member
                await member.add_roles(role)
                print(f"Assigned 'student' role to {member.name}")
            except Exception as e:
                print(f"Failed to assign 'student' role to {member.name}: {e}")
        else:
            print("'student' role not found")

# Command to delete all messages in the 'main' channel
@bot.command()
@commands.has_role("admin")  # Ensure only admins can run this command
async def clear_main(ctx):
    # Check if the command is issued in the 'main' channel
    if ctx.channel.name == "main":
        try:
            # Fetch and delete all messages in the 'main' channel
            await ctx.channel.purge(limit=None)
            await ctx.send("All messages in the #main channel have been deleted.", delete_after=5)
        except Exception as e:
            print(f"Error clearing messages: {e}")
            await ctx.send("An error occurred while trying to clear the #main channel.")
    else:
        await ctx.send("This command can only be used in the #main channel.")


# Error handler for students trying to use commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You don't have permission to use this command.")


bot.run(TOKEN)
