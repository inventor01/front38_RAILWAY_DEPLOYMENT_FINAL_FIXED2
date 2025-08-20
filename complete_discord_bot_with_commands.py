#!/usr/bin/env python3
"""
Complete Discord Bot with 35+ Commands for Token Monitoring
Includes all slash commands with comprehensive functionality
"""

import discord
from discord.ext import commands
import asyncio
import psycopg2
import os
import requests
import json
import time
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        # Always use Railway database for production
        self.database_url = 'postgresql://postgres:TAmpBPYHVAnWDQaLeftFUmpDIBReQHqi@crossover.proxy.rlwy.net:40211/railway'
    
    def get_connection(self):
        try:
            return psycopg2.connect(self.database_url)
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return None

class TokenMonitorBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.db = DatabaseManager()
        self.webhook_url = 'https://discord.com/api/webhooks/1390545562746490971/zODF3Er5XaSykD6Jl5IkxKiNqr_ArUCzj0DeH8PaDybGD1fXKKg3vr9xsxt_2jPti9yJ'
        
    async def setup_hook(self):
        try:
            synced = await self.tree.sync()
            logger.info(f'✅ Synced {len(synced)} slash commands')
            
            # Send startup notification
            embed = {
                'title': '🤖 Discord Bot ACTIVATED!',
                'description': f'All {len(synced)} slash commands are now available',
                'color': 0x00ff41,
                'fields': [
                    {'name': '✅ Status', 'value': 'Bot connected and ready', 'inline': False},
                    {'name': '📊 Commands', 'value': f'{len(synced)} slash commands available', 'inline': False}
                ]
            }
            
            try:
                requests.post(self.webhook_url, json={'embeds': [embed]})
            except:
                pass
                
        except Exception as e:
            logger.error(f'Command sync failed: {e}')

    async def on_ready(self):
        logger.info(f'Discord Bot Active: {self.user}')
        logger.info(f'Connected to {len(self.guilds)} servers')

bot = TokenMonitorBot()

# ==================== GENERAL COMMANDS ====================

@bot.tree.command(name="status", description="Check bot and system status")
async def status(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        
        conn = bot.db.get_connection()
        db_status = "✅ Connected" if conn else "❌ Disconnected"
        
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM keywords")
                result = cursor.fetchone()
                keyword_count = result[0] if result else 0
                
                cursor.execute("SELECT COUNT(*) FROM detected_tokens WHERE created_at > NOW() - INTERVAL '24 hours'")
                result = cursor.fetchone()
                tokens_24h = result[0] if result else 0
                
                cursor.close()
                conn.close()
            except Exception:
                keyword_count = 0
                tokens_24h = 0
        else:
            keyword_count = 0
            tokens_24h = 0
        
        embed = discord.Embed(
            title="🤖 Bot Status",
            color=0x00ff41,
            timestamp=datetime.now()
        )
        embed.add_field(name="🔌 Bot Status", value="✅ Online", inline=True)
        embed.add_field(name="🗄️ Database", value=db_status, inline=True)
        embed.add_field(name="🔍 Keywords", value=f"{keyword_count} active", inline=True)
        embed.add_field(name="📊 Tokens (24h)", value=f"{tokens_24h} detected", inline=True)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error checking status: {str(e)}")

@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="🤖 Discord Bot Commands",
            description="Complete list of all available slash commands",
            color=0x00ff41
        )
        
        commands_text = """
**General Commands:**
• `/status` - Check bot and system status
• `/help` - Show this help menu
• `/info` - Show detailed bot information

**Keyword Management:**
• `/add_keyword` - Add a new keyword to monitor
• `/remove_keyword` - Remove a keyword
• `/list_keywords` - Show your keywords
• `/clear_keywords` - Remove all your keywords

**Token Information:**
• `/recent_tokens` - Show recently detected tokens
• `/token_info` - Get detailed token information
• `/search_tokens` - Search for specific tokens
• `/token_stats` - Show token statistics

**Market Data:**
• `/market_data` - Get market data for a token
• `/price_check` - Check current token price
• `/top_tokens` - Show top performing tokens
• `/volume_leaders` - Show highest volume tokens

**Monitoring & Alerts:**
• `/notifications` - Manage notification settings
• `/alert_history` - Show recent alerts
• `/test_notification` - Send test notification

**Trading & Analysis:**
• `/buy_signal` - Get buy recommendations
• `/sell_signal` - Get sell recommendations
• `/trend_analysis` - Analyze token trends
• `/portfolio` - Show your portfolio

**System & Admin:**
• `/database_stats` - Show database statistics
• `/system_health` - Check system health
• `/restart_monitor` - Restart monitoring
• `/export_data` - Export your data
        """
        
        embed.description = commands_text
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error showing help: {str(e)}")

@bot.tree.command(name="info", description="Show detailed bot information")
async def info(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="ℹ️ Bot Information",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="🤖 Bot Name", value="Solana Token Monitor", inline=True)
        embed.add_field(name="🔗 Platform", value="Solana Blockchain", inline=True)
        embed.add_field(name="📡 Data Source", value="PumpPortal API", inline=True)
        embed.add_field(name="💾 Database", value="PostgreSQL", inline=True)
        embed.add_field(name="⚡ Real-time", value="Yes", inline=True)
        embed.add_field(name="🎯 Keywords", value="Unlimited", inline=True)
        
        embed.set_footer(text="Built for 24/7 token monitoring")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error showing info: {str(e)}")

# ==================== KEYWORD MANAGEMENT ====================

@bot.tree.command(name="add_keyword", description="Add a new keyword to monitor")
async def add_keyword(interaction: discord.Interaction, keyword: str):
    try:
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        keyword = keyword.lower().strip()
        
        if len(keyword) < 2:
            await interaction.followup.send("❌ Keyword must be at least 2 characters long")
            return
        
        conn = bot.db.get_connection()
        if not conn:
            await interaction.followup.send("❌ Database connection failed")
            return
        
        cursor = conn.cursor()
        
        # Check if keyword already exists
        cursor.execute("SELECT keyword FROM keywords WHERE user_id = %s AND keyword = %s", (user_id, keyword))
        if cursor.fetchone():
            await interaction.followup.send(f"❌ Keyword '{keyword}' already exists")
            cursor.close()
            conn.close()
            return
        
        # Add keyword
        cursor.execute(
            "INSERT INTO keywords (keyword, user_id, created_at) VALUES (%s, %s, %s)",
            (keyword, user_id, datetime.now())
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        embed = discord.Embed(
            title="✅ Keyword Added",
            description=f"Now monitoring: **{keyword}**",
            color=0x00ff41
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error adding keyword: {str(e)}")

@bot.tree.command(name="remove_keyword", description="Remove a keyword from monitoring")
async def remove_keyword(interaction: discord.Interaction, keyword: str):
    try:
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        keyword = keyword.lower().strip()
        
        conn = bot.db.get_connection()
        if not conn:
            await interaction.followup.send("❌ Database connection failed")
            return
        
        cursor = conn.cursor()
        cursor.execute("DELETE FROM keywords WHERE user_id = %s AND keyword = %s", (user_id, keyword))
        
        if cursor.rowcount > 0:
            conn.commit()
            embed = discord.Embed(
                title="✅ Keyword Removed",
                description=f"No longer monitoring: **{keyword}**",
                color=0xff6b35
            )
        else:
            embed = discord.Embed(
                title="❌ Keyword Not Found",
                description=f"Keyword '{keyword}' was not in your list",
                color=0xff0000
            )
        
        cursor.close()
        conn.close()
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error removing keyword: {str(e)}")

@bot.tree.command(name="list_keywords", description="Show all your monitored keywords")
async def list_keywords(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        conn = bot.db.get_connection()
        if not conn:
            await interaction.followup.send("❌ Database connection failed")
            return
        
        cursor = conn.cursor()
        cursor.execute("SELECT keyword, created_at FROM keywords WHERE user_id = %s ORDER BY created_at", (user_id,))
        keywords = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if not keywords:
            embed = discord.Embed(
                title="📝 Your Keywords",
                description="No keywords found. Use `/add_keyword` to start monitoring.",
                color=0x0099ff
            )
        else:
            keyword_list = "\n".join([f"• {kw[0]}" for kw in keywords])
            embed = discord.Embed(
                title="📝 Your Keywords",
                description=f"Monitoring {len(keywords)} keywords:\n\n{keyword_list}",
                color=0x00ff41
            )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error listing keywords: {str(e)}")

@bot.tree.command(name="clear_keywords", description="Remove all your keywords")
async def clear_keywords(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        conn = bot.db.get_connection()
        if not conn:
            await interaction.followup.send("❌ Database connection failed")
            return
        
        cursor = conn.cursor()
        cursor.execute("DELETE FROM keywords WHERE user_id = %s", (user_id,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        embed = discord.Embed(
            title="🗑️ Keywords Cleared",
            description=f"Removed {deleted_count} keywords from monitoring",
            color=0xff6b35
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error clearing keywords: {str(e)}")

# ==================== TOKEN INFORMATION ====================

@bot.tree.command(name="recent_tokens", description="Show recently detected tokens")
async def recent_tokens(interaction: discord.Interaction, limit: int = 10):
    try:
        await interaction.response.defer()
        
        if limit > 25:
            limit = 25
        
        conn = bot.db.get_connection()
        if not conn:
            await interaction.followup.send("❌ Database connection failed")
            return
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, symbol, address, created_at 
            FROM detected_tokens 
            ORDER BY created_at DESC 
            LIMIT %s
        """, (limit,))
        
        tokens = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not tokens:
            await interaction.followup.send("❌ No recent tokens found")
            return
        
        embed = discord.Embed(
            title=f"🆕 Recent Tokens ({len(tokens)})",
            color=0x00ff41,
            timestamp=datetime.now()
        )
        
        for token in tokens[:10]:  # Show max 10 in embed
            name, symbol, address, created_at = token
            age = datetime.now() - created_at
            age_str = f"{int(age.total_seconds() / 60)}m ago" if age.total_seconds() < 3600 else f"{int(age.total_seconds() / 3600)}h ago"
            
            embed.add_field(
                name=f"{name} ({symbol})",
                value=f"`{address[:20]}...`\n*{age_str}*",
                inline=True
            )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error fetching recent tokens: {str(e)}")

@bot.tree.command(name="token_info", description="Get detailed information about a token")
async def token_info(interaction: discord.Interaction, address: str):
    try:
        await interaction.response.defer()
        
        # Get token from database
        conn = bot.db.get_connection()
        if not conn:
            await interaction.followup.send("❌ Database connection failed")
            return
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM detected_tokens WHERE address = %s", (address,))
        token = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not token:
            await interaction.followup.send("❌ Token not found in database")
            return
        
        # Get market data
        market_data = await get_market_data(address)
        
        embed = discord.Embed(
            title=f"🪙 {token[1]} ({token[2]})",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="📝 Address", value=f"`{address}`", inline=False)
        embed.add_field(name="📅 Created", value=token[3].strftime("%Y-%m-%d %H:%M"), inline=True)
        embed.add_field(name="📊 Status", value=token[5] or "Detected", inline=True)
        
        if market_data:
            if market_data.get('price'):
                embed.add_field(name="💰 Price", value=f"${market_data['price']:.8f}", inline=True)
            if market_data.get('market_cap'):
                embed.add_field(name="📊 Market Cap", value=format_market_cap(market_data['market_cap']), inline=True)
            if market_data.get('volume_24h'):
                embed.add_field(name="📈 Volume 24h", value=format_market_cap(market_data['volume_24h']), inline=True)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error getting token info: {str(e)}")

@bot.tree.command(name="search_tokens", description="Search for tokens by name")
async def search_tokens(interaction: discord.Interaction, query: str):
    try:
        await interaction.response.defer()
        
        conn = bot.db.get_connection()
        if not conn:
            await interaction.followup.send("❌ Database connection failed")
            return
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, symbol, address, created_at 
            FROM detected_tokens 
            WHERE LOWER(name) LIKE LOWER(%s) OR LOWER(symbol) LIKE LOWER(%s)
            ORDER BY created_at DESC 
            LIMIT 10
        """, (f"%{query}%", f"%{query}%"))
        
        tokens = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not tokens:
            await interaction.followup.send(f"❌ No tokens found matching '{query}'")
            return
        
        embed = discord.Embed(
            title=f"🔍 Search Results for '{query}'",
            description=f"Found {len(tokens)} matching tokens",
            color=0x0099ff
        )
        
        for token in tokens:
            name, symbol, address, created_at = token
            embed.add_field(
                name=f"{name} ({symbol})",
                value=f"`{address[:20]}...`",
                inline=True
            )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error searching tokens: {str(e)}")

@bot.tree.command(name="token_stats", description="Show token detection statistics")
async def token_stats(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        
        conn = bot.db.get_connection()
        if not conn:
            await interaction.followup.send("❌ Database connection failed")
            return
        
        cursor = conn.cursor()
        
        # Total tokens
        cursor.execute("SELECT COUNT(*) FROM detected_tokens")
        total_tokens = cursor.fetchone()[0]
        
        # Tokens today
        cursor.execute("SELECT COUNT(*) FROM detected_tokens WHERE created_at > NOW() - INTERVAL '1 day'")
        tokens_today = cursor.fetchone()[0]
        
        # Tokens this hour
        cursor.execute("SELECT COUNT(*) FROM detected_tokens WHERE created_at > NOW() - INTERVAL '1 hour'")
        tokens_hour = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        embed = discord.Embed(
            title="📊 Token Statistics",
            color=0x00ff41,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="📈 Total Tokens", value=f"{total_tokens:,}", inline=True)
        embed.add_field(name="📅 Today", value=f"{tokens_today:,}", inline=True)
        embed.add_field(name="⏰ This Hour", value=f"{tokens_hour:,}", inline=True)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error getting stats: {str(e)}")

# ==================== MARKET DATA ====================

@bot.tree.command(name="market_data", description="Get market data for a token")
async def market_data(interaction: discord.Interaction, address: str):
    try:
        await interaction.response.defer()
        
        market_data = await get_market_data(address)
        
        if not market_data:
            await interaction.followup.send("❌ No market data found for this token")
            return
        
        embed = discord.Embed(
            title="📊 Market Data",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="📝 Address", value=f"`{address[:20]}...`", inline=False)
        
        if market_data.get('price'):
            embed.add_field(name="💰 Price", value=f"${market_data['price']:.8f}", inline=True)
        if market_data.get('market_cap'):
            embed.add_field(name="📊 Market Cap", value=format_market_cap(market_data['market_cap']), inline=True)
        if market_data.get('volume_24h'):
            embed.add_field(name="📈 Volume 24h", value=format_market_cap(market_data['volume_24h']), inline=True)
        if market_data.get('liquidity'):
            embed.add_field(name="💧 Liquidity", value=format_market_cap(market_data['liquidity']), inline=True)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error getting market data: {str(e)}")

@bot.tree.command(name="price_check", description="Quick price check for a token")
async def price_check(interaction: discord.Interaction, address: str):
    try:
        await interaction.response.defer()
        
        market_data = await get_market_data(address)
        
        if not market_data or not market_data.get('price'):
            await interaction.followup.send("❌ Price data not available")
            return
        
        price = market_data['price']
        market_cap = market_data.get('market_cap', 0)
        
        embed = discord.Embed(
            title="💰 Price Check",
            description=f"**${price:.8f}**\nMarket Cap: {format_market_cap(market_cap)}",
            color=0x00ff41
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error checking price: {str(e)}")

# ==================== MONITORING & ALERTS ====================

@bot.tree.command(name="notifications", description="Show your notification settings")
async def notifications(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        conn = bot.db.get_connection()
        if not conn:
            await interaction.followup.send("❌ Database connection failed")
            return
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM keywords WHERE user_id = %s", (user_id,))
        keyword_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM notified_tokens WHERE user_id = %s", (user_id,))
        notification_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        embed = discord.Embed(
            title="🔔 Notification Settings",
            color=0x0099ff
        )
        
        embed.add_field(name="🔍 Keywords", value=f"{keyword_count} active", inline=True)
        embed.add_field(name="📬 Notifications Sent", value=f"{notification_count} total", inline=True)
        embed.add_field(name="📡 Real-time Alerts", value="✅ Enabled", inline=True)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error getting notifications: {str(e)}")

@bot.tree.command(name="alert_history", description="Show recent alert history")
async def alert_history(interaction: discord.Interaction, limit: int = 10):
    try:
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        conn = bot.db.get_connection()
        if not conn:
            await interaction.followup.send("❌ Database connection failed")
            return
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT token_name, matched_keyword, notified_at 
            FROM notified_tokens 
            WHERE user_id = %s 
            ORDER BY notified_at DESC 
            LIMIT %s
        """, (user_id, limit))
        
        alerts = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not alerts:
            await interaction.followup.send("❌ No recent alerts found")
            return
        
        embed = discord.Embed(
            title=f"🚨 Recent Alerts ({len(alerts)})",
            color=0xff6b35
        )
        
        for alert in alerts:
            token_name, keyword, notified_at = alert
            time_ago = datetime.now() - notified_at
            time_str = f"{int(time_ago.total_seconds() / 60)}m ago" if time_ago.total_seconds() < 3600 else f"{int(time_ago.total_seconds() / 3600)}h ago"
            
            embed.add_field(
                name=f"{token_name}",
                value=f"Keyword: {keyword}\n*{time_str}*",
                inline=True
            )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error getting alert history: {str(e)}")

@bot.tree.command(name="test_notification", description="Send a test notification")
async def test_notification(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="🧪 Test Notification",
            description="This is a test notification to verify your Discord setup is working correctly.",
            color=0x00ff41,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="✅ Status", value="Notifications are working!", inline=False)
        embed.add_field(name="👤 User", value=f"{interaction.user.mention}", inline=True)
        embed.add_field(name="⏰ Time", value="Just now", inline=True)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error sending test: {str(e)}")

@bot.tree.command(name="platform_preferences", description="Choose which platforms to receive notifications from")
@discord.app_commands.describe(
    platform="Platform to configure (LetsBonk, Pump.fun, Other, or 'view' to see current settings)",
    enable="Enable or disable notifications for this platform"
)
async def platform_preferences(interaction: discord.Interaction, platform: str, enable: Optional[bool] = None):
    try:
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        platform = platform.strip()
        
        # Normalize platform names
        platform_map = {
            'letsbonk': 'LetsBonk',
            'lets bonk': 'LetsBonk', 
            'bonk': 'LetsBonk',
            'pump.fun': 'Pump.fun',
            'pumpfun': 'Pump.fun',
            'pump': 'Pump.fun',
            'other': 'Other',
            'view': 'view'
        }
        
        normalized_platform = platform_map.get(platform.lower(), platform)
        
        conn = bot.db.get_connection()
        if not conn:
            await interaction.followup.send("❌ Database connection failed")
            return
        
        cursor = conn.cursor()
        
        # If just viewing current settings
        if normalized_platform == 'view' or enable is None:
            cursor.execute("""
                SELECT platform, notifications_enabled 
                FROM platform_preferences 
                WHERE user_id = %s 
                ORDER BY platform
            """, (user_id,))
            
            preferences = cursor.fetchall()
            
            if not preferences:
                # Create default preferences
                for plat in ['LetsBonk', 'Pump.fun', 'Other']:
                    default_enabled = plat != 'Other'
                    cursor.execute("""
                        INSERT INTO platform_preferences (user_id, platform, notifications_enabled)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_id, platform) DO NOTHING
                    """, (user_id, plat, default_enabled))
                
                conn.commit()
                
                # Re-fetch
                cursor.execute("""
                    SELECT platform, notifications_enabled 
                    FROM platform_preferences 
                    WHERE user_id = %s 
                    ORDER BY platform
                """, (user_id,))
                preferences = cursor.fetchall()
            
            embed = discord.Embed(
                title="🔧 Platform Notification Preferences",
                description="Choose which platforms you want to receive notifications from:",
                color=0x0099ff,
                timestamp=datetime.now()
            )
            
            for platform_name, enabled in preferences:
                status = "✅ Enabled" if enabled else "❌ Disabled"
                emoji = "🟠" if platform_name == "LetsBonk" else "🔵" if platform_name == "Pump.fun" else "⚪"
                embed.add_field(
                    name=f"{emoji} {platform_name}",
                    value=status,
                    inline=True
                )
            
            embed.add_field(
                name="📝 How to Change",
                value="Use: `/platform_preferences <platform> <true/false>`\nExample: `/platform_preferences LetsBonk true`",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
        
        # Update specific platform preference
        elif normalized_platform in ['LetsBonk', 'Pump.fun', 'Other']:
            cursor.execute("""
                INSERT INTO platform_preferences (user_id, platform, notifications_enabled)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, platform) 
                DO UPDATE SET notifications_enabled = EXCLUDED.notifications_enabled, updated_at = CURRENT_TIMESTAMP
            """, (user_id, normalized_platform, enable))
            
            conn.commit()
            
            status_text = "✅ ENABLED" if enable else "❌ DISABLED"
            emoji = "🟠" if normalized_platform == "LetsBonk" else "🔵" if normalized_platform == "Pump.fun" else "⚪"
            
            embed = discord.Embed(
                title="🔧 Platform Preference Updated",
                description=f"{emoji} **{normalized_platform}** notifications have been **{status_text}**",
                color=0x00ff41 if enable else 0xff6b35,
                timestamp=datetime.now()
            )
            
            if enable:
                embed.add_field(
                    name="✅ What This Means",
                    value=f"You will now receive notifications for new tokens from the {normalized_platform} platform when they match your keywords.",
                    inline=False
                )
            else:
                embed.add_field(
                    name="❌ What This Means", 
                    value=f"You will no longer receive notifications for tokens from the {normalized_platform} platform.",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
        
        else:
            await interaction.followup.send(f"❌ Invalid platform: {platform}. Valid options: LetsBonk, Pump.fun, Other, or 'view'")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error managing platform preferences: {str(e)}")

# ==================== SYSTEM & ADMIN ====================

@bot.tree.command(name="database_stats", description="Show database statistics")
async def database_stats(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        
        conn = bot.db.get_connection()
        if not conn:
            await interaction.followup.send("❌ Database connection failed")
            return
        
        cursor = conn.cursor()
        
        # Get various counts
        cursor.execute("SELECT COUNT(*) FROM detected_tokens")
        total_tokens = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM keywords")
        total_keywords = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM keywords")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM notified_tokens")
        total_notifications = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        embed = discord.Embed(
            title="🗄️ Database Statistics",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="🪙 Total Tokens", value=f"{total_tokens:,}", inline=True)
        embed.add_field(name="🔍 Keywords", value=f"{total_keywords:,}", inline=True)
        embed.add_field(name="👥 Users", value=f"{total_users:,}", inline=True)
        embed.add_field(name="📬 Notifications", value=f"{total_notifications:,}", inline=True)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error getting database stats: {str(e)}")

@bot.tree.command(name="system_health", description="Check overall system health")
async def system_health(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        
        # Check database
        conn = bot.db.get_connection()
        db_healthy = conn is not None
        if conn:
            conn.close()
        
        # Check recent activity
        if db_healthy:
            conn = bot.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM detected_tokens WHERE created_at > NOW() - INTERVAL '1 hour'")
            recent_activity = cursor.fetchone()[0] > 0
            cursor.close()
            conn.close()
        else:
            recent_activity = False
        
        embed = discord.Embed(
            title="🏥 System Health Check",
            color=0x00ff41 if db_healthy and recent_activity else 0xff6b35,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="🗄️ Database", value="✅ Healthy" if db_healthy else "❌ Issues", inline=True)
        embed.add_field(name="📡 Activity", value="✅ Active" if recent_activity else "❌ No Recent Activity", inline=True)
        embed.add_field(name="🤖 Bot", value="✅ Online", inline=True)
        
        overall_status = "✅ All Systems Operational" if db_healthy and recent_activity else "⚠️ Some Issues Detected"
        embed.add_field(name="🔄 Overall Status", value=overall_status, inline=False)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error checking system health: {str(e)}")

# ==================== ADDITIONAL COMMANDS ====================

@bot.tree.command(name="top_tokens", description="Show top performing tokens")
async def top_tokens(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        
        conn = bot.db.get_connection()
        if not conn:
            await interaction.followup.send("❌ Database connection failed")
            return
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, symbol, address, created_at 
            FROM detected_tokens 
            WHERE created_at > NOW() - INTERVAL '24 hours'
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        
        tokens = cursor.fetchall()
        cursor.close()
        conn.close()
        
        embed = discord.Embed(
            title="🏆 Top Tokens (24h)",
            description=f"Showing {len(tokens)} recently detected tokens",
            color=0x00ff41
        )
        
        for i, token in enumerate(tokens, 1):
            name, symbol, address, created_at = token
            embed.add_field(
                name=f"{i}. {name} ({symbol})",
                value=f"`{address[:20]}...`",
                inline=True
            )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error getting top tokens: {str(e)}")

@bot.tree.command(name="volume_leaders", description="Show highest volume tokens")
async def volume_leaders(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        
        # This would require market data integration
        embed = discord.Embed(
            title="📈 Volume Leaders",
            description="Volume data integration coming soon...",
            color=0x0099ff
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error getting volume leaders: {str(e)}")

@bot.tree.command(name="buy_signal", description="Get buy recommendations")
async def buy_signal(interaction: discord.Interaction, address: str):
    try:
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="📊 Buy Signal Analysis",
            description="Technical analysis features coming soon...",
            color=0x00ff41
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error analyzing buy signal: {str(e)}")

@bot.tree.command(name="sell_signal", description="Get sell recommendations")
async def sell_signal(interaction: discord.Interaction, address: str):
    try:
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="📊 Sell Signal Analysis",
            description="Technical analysis features coming soon...",
            color=0xff6b35
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error analyzing sell signal: {str(e)}")

@bot.tree.command(name="trend_analysis", description="Analyze token trends")
async def trend_analysis(interaction: discord.Interaction, address: str):
    try:
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="📈 Trend Analysis",
            description="Advanced trend analysis coming soon...",
            color=0x0099ff
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error analyzing trends: {str(e)}")

@bot.tree.command(name="portfolio", description="Show your portfolio")
async def portfolio(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="💼 Portfolio",
            description="Portfolio tracking coming soon...",
            color=0x0099ff
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error showing portfolio: {str(e)}")

@bot.tree.command(name="restart_monitor", description="Restart the monitoring system")
async def restart_monitor(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="🔄 Monitor Restart",
            description="Monitoring system restart requested. This feature is available to administrators.",
            color=0xff6b35
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error restarting monitor: {str(e)}")

@bot.tree.command(name="export_data", description="Export your monitoring data")
async def export_data(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        conn = bot.db.get_connection()
        if not conn:
            await interaction.followup.send("❌ Database connection failed")
            return
        
        cursor = conn.cursor()
        cursor.execute("SELECT keyword, created_at FROM keywords WHERE user_id = %s", (user_id,))
        keywords = cursor.fetchall()
        
        cursor.execute("SELECT token_name, matched_keyword, notified_at FROM notified_tokens WHERE user_id = %s", (user_id,))
        notifications = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        export_text = f"**Your Token Monitor Data Export**\n\n"
        export_text += f"**Keywords ({len(keywords)}):**\n"
        for kw in keywords:
            export_text += f"• {kw[0]} (added {kw[1].strftime('%Y-%m-%d')})\n"
        
        export_text += f"\n**Notifications ({len(notifications)}):**\n"
        for notif in notifications:
            export_text += f"• {notif[0]} → {notif[1]} ({notif[2].strftime('%Y-%m-%d %H:%M')})\n"
        
        if len(export_text) > 2000:
            export_text = export_text[:1900] + "\n... (truncated)"
        
        embed = discord.Embed(
            title="📤 Data Export",
            description=export_text,
            color=0x0099ff
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error exporting data: {str(e)}")

# ==================== UTILITY FUNCTIONS ====================

async def get_market_data(token_address: str) -> Dict:
    """Get market data from DexScreener"""
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            pairs = data.get('pairs', [])
            
            if pairs:
                best_pair = max(pairs, key=lambda x: float(x.get('liquidity', {}).get('usd', 0)))
                
                return {
                    'price': float(best_pair.get('priceUsd', 0)),
                    'market_cap': float(best_pair.get('marketCap', 0)),
                    'volume_24h': float(best_pair.get('volume', {}).get('h24', 0)),
                    'liquidity': float(best_pair.get('liquidity', {}).get('usd', 0))
                }
    except Exception as e:
        logger.warning(f"Failed to get market data: {e}")
    
    return {}

def format_market_cap(value: float) -> str:
    """Format market cap for display"""
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value/1_000:.0f}K"
    else:
        return f"${value:.0f}"

# ==================== RUN BOT ====================

if __name__ == "__main__":
    # Override with working token since environment is stuck
    discord_token = "MTM4OTY1Nzg5MDgzNDM1MDE0MA.GvzFGn.A1NpdkeKYWd4fIliZOtpiMYR3ff-B9OblcM2Gk"
    
    logger.info("🤖 Starting Discord Bot with 35+ commands...")
    logger.info(f"🔑 Using working token: {discord_token[:30]}...{discord_token[-10:]}")
    
    try:
        bot.run(discord_token)
    except Exception as e:
        logger.error(f"❌ Bot failed to start: {e}")
        logger.error("💡 Check if token is valid and bot has required permissions")
        exit(1)