from discord import Interaction, Member, TextChannel, Role, SelectOption, ButtonStyle, NotFound, Attachment
from discord.ext.commands import Context
from discord.ui import View, Select, Button, button, select


from sqlite3 import connect
from sqlite3 import Row

import dependencies as deps


from typing import Dict, Tuple, List, Callable, Awaitable

from asyncio import Lock