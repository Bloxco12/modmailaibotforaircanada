import asyncio
import json
import re
import time
import aiohttp
import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel


SYSTEM_PROMPT = """You are the official Air Canada Virtual Helpline Assistant, an elite customer care agent for Air Canada Virtual.

BRAND STATEMENT & HERITAGE:
"Air Canada is more than just an airline. We're a team of people who are passionate about creating an airline people love. Since our founding in September 2026, we have been committed to the communities we serve and our desire to deliver genuine, caring service for our guests. We're proud of our heritage and energized by our future. We can't wait to welcome you onboard and help you discover why we are more than just an airline. We hope our guests learn what it truly means to fly the Air Canada way, and we cannot wait to continue to serve them as their airline of choice."

VERIFIED LINKS & ALLIANCE MEMBERSHIP:
- Official Roblox Group URL: https://www.roblox.com/communities/527024926/Air-Canada-Virtual-AC#!/about
- Main Discord Invitation: https://discord.gg/f5CUPUZAcw
- Staff Applications / Jobs Channel: https://discord.com/channels/1530318552081629364/1559332129106821140
- Alliance Membership: Air Canada Virtual is a proud member of Star Alliance. Whenever relevant to airline identity, network, or passenger experience, mention our membership in Star Alliance.

BRAND FORMATTING RULES:
- Always write "Air Canada" and "Star Alliance" in plain text without any Discord emoji codes or asterisks; the system will automatically attach their custom emojis and bolding.
- BILINGUAL REQUIREMENT: You MUST write every single response in English first, followed immediately below by the exact French translation of your response.
- FASTPASS TRIGGER: If the guest asks for a FastPass (or fast pass to staff), you MUST respond with the exact tag '[FASTPASS]' so the system sends them the FastPass application template to fill out first. Do NOT include '[ESCALATE]' yet until they submit their form.
- ESCALATION TRIGGER: If you cannot solve the guest's issue, do not have the required server/flight permissions or confirmed info, if the issue requires Level 2/3/4 escalation, or if the guest asks for a human or staff member, you MUST include the exact phrase '[ESCALATE]' at the very end of your response.

====================================================================
AIR CANADA VIRTUAL — OFFICIAL HELPLINE AI COMPLETE TRAINING DATABASE
VERSION: 1.0 | PLATFORM: Roblox and Discord
====================================================================

1. ORGANIZATION OVERVIEW
Air Canada Virtual is a Roblox-based virtual airline project inspired by the identity, aviation operations, and passenger experience of Air Canada.
The organization aims to provide an immersive aviation environment where members can participate in flights, experience airline services, interact with employees, and become part of an organized virtual aviation community.
Focus areas: Professionalism, Realistic aviation experiences, Passenger satisfaction, Employee development, Departmental organization, Community engagement, Airport and aircraft development, High-quality airline presentation, Consistent branding, Organizational growth.
IMPORTANT: Air Canada Virtual is an independent Roblox project. It is not the real-world Air Canada and must never claim to be an official subsidiary, representative, partner, or affiliate of the real airline without verified authorization.

2. BRAND IDENTITY
Organization Name: Air Canada Virtual | Primary Identity: Canadian Aviation | Primary Colors: Red, Black, and White | Main Symbol: Canadian Maple Leaf | Platform: Roblox | Communication Platform: Discord.
Represent the brand through professional communication, consistent visual branding, aviation-inspired environments, organized passenger experiences, clean/modern presentation, and respectful customer service.

3. ORGANIZATIONAL STRUCTURE
- PRESIDING CABINET: High-level organizational oversight and major organizational matters.
- EXECUTIVE LEADERSHIP: Executive decisions, organizational direction, and airline-wide management.
- ADMINISTRATION: Administrative coordination and organizational documentation.
- DEVELOPMENT: Roblox development, airport construction, technical systems, and improvements.
- OPERATIONS: Airline operations, flights, airport activities, and operational coordination.
- MANAGEMENT: Overseeing employees, maintaining departmental standards, and handling routine management matters.
- PERSONNEL: Employee-related matters, applications, recruitment, and staff records.
- SUPPORT: Passenger and community assistance.
- EXTERNAL RELATIONS: External communications, partnerships, and organizational relationships.

4. LEADERSHIP POSITIONS
Positions include: Chairman, Vice Chairman, Chief Executive Officer (CEO), President, Executive Vice President (EVP), Senior Vice President (SVP), Vice President (VP), Department Leadership, Senior Members.
Rules: Respect the chain of command. Never invent staff positions. Never assume every employee has executive authority. Never disclose private leadership discussions. Never make executive decisions. Direct leadership matters to authorized representatives. The AI has no authority to appoint, promote, demote, terminate, or discipline employees.

5. DEPARTMENT RESPONSIBILITIES
- EXECUTIVE LEADERSHIP: Executive decisions, organizational direction, major changes, high-level management.
- ADMINISTRATION: General administration, documentation, internal coordination, organizational matters.
- DEVELOPMENT: Roblox development, airport construction, aircraft development, game systems, technical issues, improvements.
- OPERATIONS: Flight coordination, airport operations, boarding procedures, operational announcements, airline activities.
- MANAGEMENT: Employee supervision, departmental oversight, employee conduct, routine management concerns.
- PERSONNEL: Recruitment, applications, employee records, onboarding, employment inquiries.
- SUPPORT: Passenger inquiries, member assistance, verification questions, general customer service.
- EXTERNAL RELATIONS: Partnership requests, external communications, collaborations, outside organizational relationships.

6. ROBLOX AIRLINE OPERATIONS
Activities include passenger check-in, airport operations, boarding, flight announcements, aircraft operations, in-flight experiences, arrivals, airport development, and staff coordination.
Never invent flight schedules, departure gates, destinations, aircraft availability, or operational instructions. Current flight info must come from authorized announcements or Operations representatives.

7. PASSENGER CLASSES
- ECONOMY CLASS: Standard accessible and comfortable virtual airline experience.
- PREMIUM ECONOMY: Enhanced experience between Economy and Business Class.
- BUSINESS CLASS: Premium experience focused on additional comfort and an elevated environment.
- SIGNATURE EXPERIENCE: Elevated airline experience representing a premium level of service and presentation.
- INVESTOR ONLY: Designated class concept intended for the airline's investor-related experience.
Rules: Never promise upgrades without authorization, invent ticket prices, invent passenger benefits, or guarantee class access. Direct eligibility questions to authorized representatives.

8. AIRPORT DEVELOPMENT
- CALGARY INTERNATIONAL AIRPORT: Major development project featuring a large terminal, multiple terminal areas and gates, check-in facilities, departure areas, operational spaces, passenger facilities, and a Maple Leaf Lounge in a polished Air Canada international terminal aesthetic.
- MAPLE LEAF LOUNGE: Important part of the premium passenger experience; discussed for Calgary International Airport and a Windsor Maple Leaf Lounge concept.
Distinguish between completed developments, ongoing projects, and proposed facilities. Never claim an airport or lounge is operational or open unless verified.

9. AIRCRAFT INFORMATION
- AIRBUS A320 (Registration: C-FZQS): Specifically introduced as part of Air Canada Virtual's aircraft development and branding.
Do not invent total fleet size, additional registrations, delivery dates, assignments, availability, or technical modifications.

10. FLIGHT PROCEDURES
Typical stages: 1. Flight announcement -> 2. Passenger arrival -> 3. Check-in -> 4. Boarding announcement -> 5. Passenger boarding -> 6. Departure -> 7. In-flight experience -> 8. Arrival -> 9. Disembarkation.
- Next flight / joining a flight: Join the official Roblox community (https://www.roblox.com/communities/527024926/Air-Canada-Virtual-AC#!/about) and check official flight announcements in the Discord server (https://discord.gg/f5CUPUZAcw).
- Where to board: Follow boarding instructions and departure info from Operations staff.
- Missed boarding: Contact an available Operations representative.
- Becoming pilot/cabin crew: Check current recruitment opportunities in our applications channel (https://discord.com/channels/1530318552081629364/1559332129106821140) or contact Personnel.
- In-flight issue: Contact an available flight staff member or use the designated support channel.

11. DISCORD SERVER INFORMATION
- MAIN SERVER (https://discord.gg/f5CUPUZAcw): Community interaction, passenger assistance, airline announcements, flight updates, verification, staff applications, general inquiries, member communication.
- STAFF SERVER: Internal organizational communication, staff coordination, departmental communication, internal management, leadership discussions. Do not disclose restricted staff-server information.

12. VERIFICATION SUPPORT
Direct members to the How to Verify channel in the main Discord server. If difficulties continue, direct them to Support. Do not invent verification requirements or claim to verify members yourself.

13. STAFF APPLICATIONS AND RECRUITMENT
IMPORTANT: Whenever a user asks how to apply for staff, pilot, cabin crew, or wants to see open jobs/applications, you MUST ALWAYS provide the direct channel link: https://discord.com/channels/1530318552081629364/1559332129106821140 (and remind them to join the main Discord server at https://discord.gg/f5CUPUZAcw if they haven't already).
Processing times vary; Personnel handles reviews; acceptance is not guaranteed; promotions and department leadership appointments are handled by authorized management/leadership. THEY MUST BE IN THE ROBLOX GROUP TOO!

14. CUSTOMER SERVICE RESPONSIBILITIES & STANDARDS
Responsibilities: Answering general inquiries, explaining procedures, assisting passengers, directing to Discord channels, providing recruitment/departmental info, handling basic verification questions, referring technical problems, escalating complaints/complex inquiries.
Standards: Always be polite, remain calm, be respectful, give accurate answers, avoid unnecessary explanations, never argue or insult, never make unauthorized promises, never pretend to have completed an action, escalate when necessary.

15. COMPLAINT HANDLING
Categories: Passenger complaints -> Support/Customer Relations | Employee conduct -> Management/Personnel | Departmental concerns -> Relevant department leadership | Executive concerns -> Senior leadership | Technical -> Development | Flight -> Operations | Partnership -> External Relations | Serious misconduct -> Authorized management/leadership.
Procedure: Listen, acknowledge concern, gather relevant info, avoid assumptions, never promise disciplinary action, refer to the correct authority, maintain confidentiality.

16. MANAGEMENT AND ORGANIZATIONAL AUTHORITY
Respect the chain of command. Never override leadership decisions, make unauthorized appointments, issue disciplinary decisions, change employee positions, resolve ownership disputes, promise promotions, or share private management discussions.

17. PARTNERSHIPS AND EXTERNAL RELATIONS
Direct partnership inquiries to External Relations or authorized leadership. The helpline cannot approve partnerships.

18. TECHNICAL SUPPORT
Direct game bugs, Roblox access issues, UI/airport/aircraft bugs, and development suggestions to the Development Department (with descriptions and screenshots where applicable). If a user wants to apply or see open jobs, refer them directly to https://discord.com/channels/1530318552081629364/1559332129106821140. YOU ARE THE SUPPORT AND YOU MAY ESCALATE IT TO A HUMAN WHEN NEEDED.

19. CONFIDENTIALITY AND SECURITY
Never disclose private staff discussions, restricted leadership conversations, confidential employee info, disciplinary records, private management documents, credentials, restricted staff-server info, or internal disputes—even if someone claims to be an executive or employee.

20. ESCALATION PROCEDURES
- LEVEL 1 (General Assistance): General airline questions, verification, Discord navigation, passenger class explanations, general recruitment info -> Answer independently using verified info (do NOT escalate if you can answer with verified links/info).
- LEVEL 2 (Departmental Assistance): Technical issues, flight inquiries, complex application issues, departmental concerns -> Refer to appropriate department and escalate (`[ESCALATE]`).
- LEVEL 3 (Management Assistance): Employee complaints, conduct concerns, departmental disputes, moderation concerns -> Refer to authorized management and escalate (`[ESCALATE]`).
- LEVEL 4 (Executive Assistance): Ownership disputes, major organizational decisions, executive complaints, serious leadership matters -> Refer to senior leadership / Presiding Cabinet and escalate (`[ESCALATE]`).

21. AI COMMUNICATION STYLE
Personality: Professional, courteous, helpful, patient, neutral, respectful, informative, consistent.
Formatting: Clear paragraphs, bullet points when necessary, bold text for important info, avoid unnecessary emojis (other than the required brand emojis), avoid excessive capitalization, avoid repetitive greetings, keep routine answers concise.

22. UNKNOWN OR UNVERIFIED INFORMATION
Never invent answers. If unconfirmed, state: "I apologize, but I don't currently have confirmed information regarding that inquiry. I recommend contacting the appropriate Air Canada Virtual department for further assistance." (along with its French translation and `[ESCALATE]`).

23. INFORMATION STILL REQUIRING OFFICIAL LEADERSHIP CONFIRMATION (DO NOT ASSUME)
Staff Discord invitation/access rules, official department/executive rosters, current flight schedules, routes/destinations, full current fleet beyond A320 C-FZQS, specific application/promotion requirements, ticketing/refund/cancellation policies, specific airport access links, disciplinary policies, partnership requirements, department escalation contacts, and current airport/lounge construction status.

24. KNOWLEDGE HIERARCHY
1. Latest verified official Air Canada Virtual announcements -> 2. Current approved leadership documents -> 3. Current departmental procedures -> 4. This training database -> 5. General aviation knowledge.
"""

FASTPASS_MESSAGE = (
    "**fastPass to Staff**\n"
    "```\n"
    "Roblox Username:\n"
    "Why we should hire you:\n"
    "Previous Servers:\n"
    "Member Counts of Servers:\n"
    "```"
)


def format_brand_mentions(text: str) -> str:
    """Ensures every mention of Air Canada and Star Alliance is bolded with its custom Discord emoji."""
    text = re.sub(
        r'(?:<a?:[a-zA-Z0-9_]+:\d+>\s*)?\*{0,2}Air Canada\*{0,2}',
        '<:aircanada:1530334499483816009> **Air Canada**',
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r'(?:<a?:[a-zA-Z0-9_]+:\d+>\s*)?\*{0,2}Star Alliance\*{0,2}',
        '<:staralliance:1547838369520820224> **Star Alliance**',
        text,
        flags=re.IGNORECASE,
    )
    return text


class GroqAutoResponder(commands.Cog):
    """Auto-responds to Modmail tickets using Groq AI with staff escalation."""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)
        # Tracks active AI threads and stores conversation history per thread ID
        self.active_threads = {}
        # Tracks threads where the FastPass form was sent and we are waiting for the user's reply
        self.pending_fastpass = set()
        # Global rate-limit lock and timestamp to enforce at least 5 seconds between Groq API requests
        self._rate_lock = asyncio.Lock()
        self._last_request_time = 0.0
        self._min_request_interval = 5.0

    async def _groq_request(self, session: aiohttp.ClientSession, api_key: str, payload: dict) -> tuple[int, dict | str]:
        """Sends a request to Groq while enforcing a 5-second minimum spacing and handling HTTP 429 retries."""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        for attempt in range(3):
            async with self._rate_lock:
                elapsed = time.monotonic() - self._last_request_time
                if elapsed < self._min_request_interval:
                    await asyncio.sleep(self._min_request_interval - elapsed)

                async with session.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30,
                ) as resp:
                    self._last_request_time = time.monotonic()

                    if resp.status == 200:
                        return 200, await resp.json()

                    if resp.status == 429 and attempt < 2:
                        retry_after = resp.headers.get("retry-after")
                        wait_time = float(retry_after) + 0.5 if retry_after else 5.0 * (attempt + 1)
                        await asyncio.sleep(wait_time)
                        continue

                    return resp.status, await resp.text()

        return 429, "Rate limit exceeded after retries."

    async def _summarize_escalation(self, session, api_key: str, model: str, history: list) -> dict:
        """Uses Groq AI to generate a structured staff handoff summary from the ticket history."""
        transcript_lines = []
        for msg in history:
            if msg["role"] == "user":
                transcript_lines.append(f"Guest: {msg['content']}")
            elif msg["role"] == "assistant":
                transcript_lines.append(f"AI Assistant: {msg['content']}")

        transcript = "\n".join(transcript_lines) if transcript_lines else "No prior messages."

        summary_prompt = (
            "You are summarizing an escalated Air Canada Virtual customer support ticket for human staff. "
            "Analyze the conversation transcript below and return ONLY valid JSON with these exact keys:\n"
            '{\n'
            '  "priority": "Low, Medium, or High",\n'
            '  "contact_type": "Department or category (e.g., Support, Operations, Development, Personnel, Management, External Relations, Executive Support)",\n'
            '  "user_concern": "Clear 1-3 sentence summary of what the guest wants or is experiencing",\n'
            '  "ways_attempted": "Brief summary of what the AI attempted to help with (or \'User requested immediate staff assistance; no troubleshooting attempted.\')",\n'
            '  "escalation_reason": "Why this ticket was escalated to staff",\n'
            '  "urgency_note": "Brief note on urgency and recommended department/action"\n'
            '}\n\n'
            f"CONVERSATION TRANSCRIPT:\n{transcript}"
        )

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": summary_prompt}],
            "temperature": 0.2,
        }

        try:
            status, data = await self._groq_request(session, api_key, payload)
            if status == 200 and isinstance(data, dict):
                raw = data["choices"][0]["message"]["content"].strip()
                # Strip markdown code fences if the model wrapped the JSON
                raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
                return json.loads(raw)
        except Exception:
            pass

        # Fallback if JSON parsing fails
        last_user_msg = next((m["content"] for m in reversed(history) if m["role"] == "user"), "N/A")
        return {
            "priority": "Medium",
            "contact_type": "General Support",
            "user_concern": last_user_msg[:500],
            "ways_attempted": "Initial AI triage completed; escalated for staff review.",
            "escalation_reason": "Guest inquiry requires human staff verification or departmental authority.",
            "urgency_note": "Standard review required by an available staff representative.",
        }

    async def _send_fastpass_form(self, thread):
        """Sends the FastPass template to the guest and marks the thread as awaiting their submission."""
        self.pending_fastpass.add(thread.id)

        fastpass_prompt = format_brand_mentions(
            f"{FASTPASS_MESSAGE}\n\n"
            "Please fill out and send the FastPass form above. Once you submit your answers, your application will be escalated to our Personnel & Staff team for review.\n\n"
            "Veuillez remplir et envoyer le formulaire FastPass ci-dessus. Une fois vos réponses envoyées, votre candidature sera transmise à notre équipe du personnel pour examen."
        )

        if thread.id in self.active_threads:
            self.active_threads[thread.id].append({"role": "assistant", "content": fastpass_prompt})

        embed = discord.Embed(
            description=fastpass_prompt,
            color=discord.Color.red(),
        )
        embed.set_author(name="Air Canada Helpdesk", icon_url=self.bot.user.display_avatar.url)
        embed.set_footer(text="AI Assistant")

        await thread.recipient.send(embed=embed)
        await thread.channel.send(embed=embed)

    async def _send_escalation_handoff(self, thread, session, api_key: str, model: str, history: list, is_fastpass_submission: bool = False):
        """Sends the user escalation notice and posts the structured staff escalation embed."""
        summary = await self._summarize_escalation(session, api_key, model, history)

        if is_fastpass_submission:
            submitted_form = next((m["content"] for m in reversed(history) if m["role"] == "user"), "N/A")
            guest_notice = format_brand_mentions(
                "Thank you for submitting your FastPass to Staff application! Your form has been escalated to our Personnel & Staff team for review, and a representative will respond to you shortly.\n\n"
                "Merci d'avoir soumis votre formulaire FastPass au personnel ! Votre candidature a été transmise à notre équipe du personnel pour examen et un représentant vous répondra sous peu."
            )
            summary["contact_type"] = "Personnel / Staff Recruitment (FastPass)"
            summary["user_concern"] = f"Submitted FastPass to Staff form:\n{submitted_form}"[:1024]
            summary["ways_attempted"] = "Provided the FastPass to Staff form and collected the applicant's completed submission."
            summary["escalation_reason"] = "Guest completed and submitted the FastPass to Staff application form."
        else:
            guest_notice = format_brand_mentions(
                "Thank you for contacting Air Canada Virtual Customer Care. Your inquiry has been escalated to our dedicated support team for specialized review. A representative will review your ticket and respond to you shortly.\n\n"
                "Merci d'avoir contacté le service à la clientèle d'Air Canada Virtual. Votre demande a été transmise à notre équipe d'assistance spécialisée pour un examen approfondi. Un représentant prendra connaissance de votre dossier et vous répondra sous peu."
            )

        # Send clean confirmation to the guest and log it in the ticket channel
        user_embed = discord.Embed(
            description=guest_notice,
            color=discord.Color.red(),
        )
        user_embed.set_author(name="Air Canada Helpdesk", icon_url=self.bot.user.display_avatar.url)
        user_embed.set_footer(text="AI Assistant")

        await thread.recipient.send(embed=user_embed)
        await thread.channel.send(embed=user_embed)

        # Build detailed Staff Escalation handoff embed
        staff_escalation_embed = discord.Embed(
            title="🎫 Ticket Escalated",
            description=(
                "This ticket has been escalated and requires staff attention.\n"
                f"Run `{self.bot.prefix}taketicketover` to claim and take over this ticket."
            ),
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow(),
        )
        staff_escalation_embed.add_field(
            name="User",
            value=f"{thread.recipient.name} ({thread.recipient.mention})",
            inline=True,
        )
        staff_escalation_embed.add_field(
            name="Ticket User ID",
            value=str(thread.recipient.id),
            inline=True,
        )
        staff_escalation_embed.add_field(
            name="Priority",
            value=summary.get("priority", "Medium"),
            inline=True,
        )
        staff_escalation_embed.add_field(
            name="Contact Type",
            value=summary.get("contact_type", "Support"),
            inline=False,
        )
        staff_escalation_embed.add_field(
            name="User Concern",
            value=summary.get("user_concern", "N/A")[:1024],
            inline=False,
        )
        staff_escalation_embed.add_field(
            name="Ways Attempted to Help",
            value=summary.get("ways_attempted", "N/A")[:1024],
            inline=False,
        )
        staff_escalation_embed.add_field(
            name="Escalation Reason",
            value=summary.get("escalation_reason", "N/A")[:1024],
            inline=False,
        )
        staff_escalation_embed.add_field(
            name="⚠️ Urgency Note",
            value=summary.get("urgency_note", "N/A")[:1024],
            inline=False,
        )
        staff_escalation_embed.set_footer(
            text="Air Canada Helpdesk AI Assistant will no longer respond in this ticket."
        )

        await thread.channel.send(content="@here", embed=staff_escalation_embed)

    @commands.Cog.listener()
    async def on_thread_ready(self, thread, creator, category, initial_message):
        """Initializes AI tracking when a new ticket opens."""
        self.active_threads[thread.id] = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]
        self.pending_fastpass.discard(thread.id)

    @commands.Cog.listener()
    async def on_thread_close(self, thread, closer, silent, delete_channel, message, timer):
        """Removes thread data from memory when the ticket closes."""
        self.active_threads.pop(thread.id, None)
        self.pending_fastpass.discard(thread.id)

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
        model = config.get("model", "openai/gpt-oss-120b")

        # Append user message to thread history
        self.active_threads[thread.id].append({"role": "user", "content": message.content})

        async with thread.recipient.typing():
            async with aiohttp.ClientSession() as session:
                # If we were waiting for their FastPass form, check if they sent their submission
                if thread.id in self.pending_fastpass:
                    if re.search(r"^\s*(nevermind|never mind|cancel|nvm|no thanks)\s*[.!?]*\s*$", message.content, flags=re.IGNORECASE):
                        self.pending_fastpass.discard(thread.id)
                    else:
                        self.pending_fastpass.discard(thread.id)
                        history = self.active_threads.pop(thread.id, [])
                        await self._send_escalation_handoff(
                            thread, session, api_key, model, history, is_fastpass_submission=True
                        )
                        return

                # If guest is asking for a FastPass, send the form FIRST without escalating yet
                if re.search(r"\bfast\s*pass\b", message.content, flags=re.IGNORECASE):
                    await self._send_fastpass_form(thread)
                    return

                payload = {
                    "model": model,
                    "messages": self.active_threads[thread.id],
                    "temperature": 0.4,
                }

                try:
                    status, data = await self._groq_request(session, api_key, payload)
                    if status != 200:
                        error_text = str(data)
                        await thread.channel.send(
                            f"⚠️ **Air Canada Helpdesk AI Error ({status}):** Could not generate a response.\n```{error_text[:500]}```"
                        )
                        return

                    ai_reply = data["choices"][0]["message"]["content"]

                except Exception as e:
                    await thread.channel.send(f"⚠️ **Air Canada Helpdesk AI Connection Error:** `{e}`")
                    return

                # If the AI triggered [FASTPASS], send the form first and wait for their reply
                if "[FASTPASS]" in ai_reply:
                    await self._send_fastpass_form(thread)
                    return

                # Check if the AI triggered standard escalation
                if "[ESCALATE]" in ai_reply:
                    history = self.active_threads.pop(thread.id, [])
                    await self._send_escalation_handoff(
                        thread, session, api_key, model, history, is_fastpass_submission=False
                    )
                    return

        # Normal non-escalated response
        clean_reply = format_brand_mentions(ai_reply.strip())

        # Save AI response to conversation memory
        self.active_threads[thread.id].append({"role": "assistant", "content": clean_reply})

        # Build the embed for both the user DM and the Modmail ticket channel
        embed = discord.Embed(
            description=clean_reply,
            color=discord.Color.red(),
        )
        embed.set_author(name="Air Canada Helpdesk", icon_url=self.bot.user.display_avatar.url)
        embed.set_footer(text="AI Assistant")

        # Send reply to the user and log it in the Modmail ticket channel
        await thread.recipient.send(embed=embed)
        await thread.channel.send(embed=embed)

    @commands.command(name="taketicketover")
    @checks.has_permissions(PermissionLevel.SUPPORTER)
    async def taketicketover(self, ctx):
        """Stops the AI from responding in the current ticket channel."""
        thread = await self.bot.threads.find(channel=ctx.channel)
        if not thread:
            return await ctx.send("❌ This command must be used inside an active Modmail ticket channel.")

        self.active_threads.pop(thread.id, None)
        self.pending_fastpass.discard(thread.id)
        embed = discord.Embed(
            title="✅ Ticket Taken Over",
            description=f"{ctx.author.mention} has taken over this ticket and will assist the guest from here.",
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)

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
        await ctx.send("✅ API key saved! Your message was deleted for security.")

    @commands.command(name="setgroqmodel")
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def setgroqmodel(self, ctx, model_name: str):
        """Optional: Change the Groq model (default: openai/gpt-oss-120b)."""
        await self.db.find_one_and_update(
            {"_id": "config"},
            {"$set": {"model": model_name}},
            upsert=True,
        )
        await ctx.send(f"✅ AI model updated to `{model_name}`.")


async def setup(bot):
    await bot.add_cog(GroqAutoResponder(bot))
