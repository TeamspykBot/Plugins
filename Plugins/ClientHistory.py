import time

from Bot.Plugins.Base import PluginBase


class ClientHistoryPlugin(PluginBase):
    """
    This plugin write the current timestamp + user count at that time in the database everytime the usercount changes.
    Useful to plot teamspeak activity.

    The plugin provides no commands.

    optional example json ( can be inserted in config.json under plugins ):

    "mydayyy_client_history": {
        "table_name": "MydayyyClientHistory"
    }
    """

    def __init__(self, bot_instance):
        super().__init__(bot_instance)

        self.mysql = bot_instance.get_mysql_instance()

        if self.mysql is None:
            print("ClientHistory requires mysql. Exiting.")
            exit()

        self.client_history_table = bot_instance.get_user_setting(
            "mydayyy_client_history.table_name") or "MydayyyClientHistory"

        self.setup_table()

    def on_initial_data(self, client_list, channel_list):
        self.insert_client_count(len(client_list))

    def on_client_joined(self, event):
        self.insert_client_count(len(self.bot_instance.get_clients()))

    def on_client_left(self, event):
        self.insert_client_count(len(self.bot_instance.get_clients())-1)

    # MYSQL FUNCTIONALITY
    def insert_client_count(self, count, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        query = "INSERT INTO `{0}` (Count, Timestamp) VALUES (%s, %s)".format(self.client_history_table)
        self.bot_instance.execute_query(query, count, timestamp)

    def setup_table(self):
        self.bot_instance.execute_query("SET sql_notes = 0;")

        query = "CREATE TABLE IF NOT EXISTS `{0}` (" \
                "`Id` int(11) NOT NULL AUTO_INCREMENT, " \
                "`Count` int(11) DEFAULT NULL, " \
                "`Timestamp` int(11) DEFAULT NULL, " \
                "PRIMARY KEY (`Id`))".format(self.client_history_table)

        self.bot_instance.execute_query(query)

        self.bot_instance.execute_query("SET sql_notes = 1;")
