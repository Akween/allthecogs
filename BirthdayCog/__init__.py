from .birthdaycog import Birthday


async def setup(bot):
    bot.add_cog(Birthday(bot))
