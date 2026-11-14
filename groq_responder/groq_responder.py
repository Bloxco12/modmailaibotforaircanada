import asyncio
import aiohttp
import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel


class GroqAutoResponder(commands.Cog):
    """Auto-responds to Modmail tickets using Groq AI with staff escalation."""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)
        # Tracks active AI threads and stores conversation history per thread ID
        self.active_threads = {}

    @commands.Cog.listener()
    async def on_thread_ready(self, thread, creator, category, initial_message):
        """Initializes AI tracking when a new ticket opens."""
        self.active_threads[thread.id] = [
            {
                "role": "system",
                "content": (
                    "You are an elite customer care agent for Air Canada Roblox. "
                    "Use the following information about our airline to reflect our values and tone: "
                    "\"Air Canada is more than just an airline. We're a team of people who are passionate about creating an airline people love. "
                    "Since our founding in September 2026, we have been committed to the communities we serve and our desire to deliver genuine, caring service for our guests. "
                    "We're proud of our heritage and energized by our future. We can't wait to welcome you onboard and help you discover why we are more than just an airline. "
                    "We hope our guests learn what it truly means to fly the Air Canada way, and we cannot wait to continue to serve them as their airline of choice.\" "
                    "Try to solve the guest's problem clearly, politely, and concisely. "
                    "IMPORTANT FORMATTING RULE: You MUST write every single response in English first, followed immediately below by the exact French translation of your response. "
                    "If you cannot solve their issue, do not have the required server/flight permissions or info, "
                    "or the guest asks for a human or staff member, you MUST include the exact phrase "
                    "'[ESCALATE]' at the very end of your response."
                ),
            }
        ]

    @commands.Cog.listener()
    async def on_thread_close(self, thread, closer, silent, delete_channel, message, timer):
        """Removes thread data from memory when the ticket closes."""
        self.active_threads.pop(thread.id, None)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listens for user DMs and generates a Groq AI response."""
        # Ignore bots and messages sent inside a server
        if message.author.bot or message.guild is not None:
            return

        # Ignore commands
        if message.content.startswith(self.bot.prefix):
            return

        # Wait briefly for Modmail core to create/log the thread
        await asyncio.sleep(1.5)

        thread = await self.bot.threads.find(recipient=message.author)
        if not thread or thread.id not in self.active_threads:
            return

        config = await self.db.find_one({"_id": "config"})
        if not config or not config.get("api_key"):
            return

        api_key = config["api_key"]
        model = config.get("model", "llama-3.1-8b-instant")

        # Append user message to thread history
        self.active_threads[thread.id].append({"role": "user", "content": message.content})

        async with thread.recipient.typing():
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": model,
                    "messages": self.active_threads[thread.id],
                    "temperature": 0.5,
                }

                try:
                    async with session.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=20,
                    ) as resp:
                        if resp.status != 200:
                            error_text = await resp.text()
                            await thread.channel.send(
                                f"⚠️ **Groq AI Error ({resp.status}):** Could not generate a response.\n```{error_text[:500]}```"
                            )
                            return

                        data = await resp.json()
                        ai_reply = data["choices"][0]["message"]["content"]

                except Exception as e:
                    await thread.channel.send(f"⚠️ **Groq AI Connection Error:** `{e}`")
                    return

        # Check if the AI triggered an escalation
        needs_escalation = "[ESCALATE]" in ai_reply
        clean_reply = ai_reply.replace("[ESCALATE]", "").strip()

        # Save AI response to conversation memory
        self.active_threads[thread.id].append({"role": "assistant", "content": clean_reply})

        # Send reply to the user and log it in the Modmail ticket channel
        await thread.recipient.send(clean_reply)
        embed = discord.Embed(
            description=clean_reply,
            color=discord.Color.blurple(),
        )
        embed.set_author(name="Groq AI Responder", icon_url=self.bot.user.display_avatar.url)
        await thread.channel.send(embed=embed)

        # Trigger Staff Escalation alert in the ticket channel
        if needs_escalation:
            escalation_embed = discord.Embed(
                title="🚨 Staff Escalation",
                description=(
                    "The AI assistant could not fully resolve this issue and has escalated the ticket.\n\n"
                    f"Run `{self.bot.prefix}taketicketover` to disable the AI and take over this conversation."
                ),
                color=discord.Color.red(),
            )
            await thread.channel.send(content="@here", embed=escalation_embed)

    @commands.command(name="taketicketover")
    @checks.has_permissions(PermissionLevel.SUPPORTER)
    async def taketicketover(self, ctx):
        """Stops the AI from responding in the current ticket channel."""
        thread = await self.bot.threads.find(channel=ctx.channel)
        if not thread:
            return await ctx.send("❌ This command must be used inside an active Modmail ticket channel.")

        if thread.id in self.active_threads:
            self.active_threads.pop(thread.id)
            embed = discord.Embed(
                title="✅ Ticket Taken Over",
                description=f"{ctx.author.mention} has taken over this ticket. Groq AI is now disabled for this thread.",
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("ℹ️ Groq AI is not active in this ticket.")

    @commands.command(name="setgroqkey")
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def setgroqkey(self, ctx, api_key: str):
        """Sets the Groq API key in Modmail's database."""
        await self.db.find_one_and_update(
            {"_id": "config"},
            {"$set": {"api_key": api_key}},
            upsert=True,
        )
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        await ctx.send("✅ Groq API key saved! Your message was deleted for security.")

    @commands.command(name="setgroqmodel")
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def setgroqmodel(self, ctx, model_name: str):
        """Optional: Change the Groq model (default: llama-3.1-8b-instant)."""
        await self.db.find_one_and_update(
            {"_id": "config"},
            {"$set": {"model": model_name}},
            upsert=True,
        )
        await ctx.send(f"✅ Groq model updated to `{model_name}`.")


async def setup(bot):
    await bot.add_cog(GroqAutoResponder(bot))
