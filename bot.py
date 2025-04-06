import discord
from discord.ext import commands
import requests

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Trial tracking and team locking
user_trials = {}
user_teams = {}

# HuggingChat endpoint (unofficial, free)
def query_ai(prompt):
    try:
        headers = {"Content-Type": "application/json"}
        json_data = {
            "messages": [{"role": "user", "content": prompt}],
            "model": "meta-llama/Llama-2-13b-chat-hf"
        }
        response = requests.post("https://api.perplexity.ai/chat/completions", headers=headers, json=json_data)
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def join(ctx, team: str):
    user_id = str(ctx.author.id)
    if user_id in user_teams:
        await ctx.send("You've already joined a team.")
    else:
        user_teams[user_id] = team.lower()
        await ctx.send(f"{ctx.author.display_name} joined team **{team}**!")

@bot.command()
async def debate(ctx, *, topic):
    user_id = str(ctx.author.id)

    if user_trials.get(user_id, 0) >= 3:
        await ctx.send("❌ You've reached your 3 free debates. Upgrade to premium!")
        return

    team = user_teams.get(user_id, "No team")
    await ctx.send(f"**{ctx.author.display_name}** from team **{team}** is debating:\n💬 *{topic}*")

    await ctx.send("🧠 Thinking...")
    response = query_ai(topic)
    await ctx.send(f"🤖 AI: {response}")

    user_trials[user_id] = user_trials.get(user_id, 0) + 1

@bot.command()
async def trials(ctx):
    count = user_trials.get(str(ctx.author.id), 0)
    await ctx.send(f"You've used {count}/3 free debates.")

@bot.command()
async def team(ctx):
    team = user_teams.get(str(ctx.author.id), "None")
    await ctx.send(f"Your team: **{team}**")

# Run your bot
bot.run("")  # Replace with actual token
