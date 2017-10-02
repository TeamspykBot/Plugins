from operator import itemgetter

from Bot.Plugins.Base import PluginBase


class HelpCommandPlugin(PluginBase):
    """
    This plugin sends a list of all available commands to the user when he types a certain command

    help - Sends a list of all available commands

    optional example json ( can be inserted in config.json under plugins ):

    "mydayyy_help_command": {
        "commands": {
            "help": {
                "command": "help",
                "accesslevel": 0
            }
        }
    }
    """

    def __init__(self, bot_instance):
        super().__init__(bot_instance)

        # init command variables
        self.command_help_cmd = bot_instance.get_user_setting("mydayyy_help_command.commands.help.command") or "help"
        self.command_help_al = bot_instance.get_user_setting("mydayyy_help_command.commands.help.accesslevel") or 0

        self.bot_instance.add_chat_command(self.command_help_cmd,
                                           "Subscribes the client to receive links",
                                           self.command_help_al,
                                           self.command_help,
                                           [])

    def command_help(self, invokerid, invokername, invokeruid, msg_splitted):
        client_access_level = self.bot_instance.get_client_accesslevel(invokerid)
        chat_commands = self.bot_instance.get_all_commands()
        sorted_commands = []
        idx = 0
        for key, command in chat_commands.items():
            idx += 1
            color = "[COLOR=green]" if client_access_level >= command.accesslevel else "[COLOR=red]"
            args = " ".join(command.args)
            if args == "" or args is None:
                answer = color + "" + key + " - " + command.description + " [" + str(command.accesslevel) + "][/COLOR]"
            else:
                answer = color + "" + key + " " + args + " - " + command.description + " [" + str(command.accesslevel) + "][/COLOR]"
            sorted_commands.append([idx, answer])
            sorted_commands = sorted(sorted_commands, key=itemgetter(0))
        for answer in sorted_commands:
            self.bot_instance.send_text_to_client(invokerid, answer[1])
