from discord import Member, File
from discord.ext.commands import Cog, Bot, hybrid_command, Context
from discord.app_commands import describe

from io import BytesIO
from requests import get as requests_get
from textwrap import wrap
from PIL import Image, ImageDraw, ImageFont, ImageOps