from Bot.Plugins.Base import PluginBase


class AFKSwitcherPlugin(PluginBase):
    """
    This plugin moves a client after a client output mute and a specified timeout (in ms) to a dedicated AFK channel.
    When the client umutes, they will be moved back to their old channel but only if they still reside in AFK channel.

    Configuration options for config.json:
    "kleest": {
        "afk": {
          "cid": 42,
          "timeout": 1337
        }
    }
    """

    CONFIG_NAMESPACE = "kleest"
    CLIENT_VAL_OLD_CHANNEL = CONFIG_NAMESPACE + ".old_channel"

    def __init__(self, bot_instance):
        super().__init__(bot_instance)

        # load config
        self.afk_cid = bot_instance.get_user_setting(AFKSwitcherPlugin.CONFIG_NAMESPACE + ".afk.cid")
        self.afk_timeout = bot_instance.get_user_setting(AFKSwitcherPlugin.CONFIG_NAMESPACE + ".afk.timeout")

        if self.afk_cid is None:
            raise AttributeError(str(self.__class__.__name__), "No AFK cid set")

        if self.afk_timeout is None:
            raise AttributeError(str(self.__class__.__name__), "No timeout set")

        self.afk_cid = int(self.afk_cid)
        self.afk_timeout = int(self.afk_timeout)

        # register events
        self.bot_instance.register_value_changed_callback("client_output_muted", self.on_client_output_muted)

    def on_client_output_muted(self, clid, key, old_value, value):
        """!
        @brief Callback when a client changes their mute state.

        @param clid Client ID
        @param key Unused
        @param old_value Unused
        @param value Current mute state
        @return None
        """
        cid = int(self.bot_instance.get_client_value(clid, "cid"))
        if bool(int(value)):
            # client is muted
            self.bot_instance.start_timer(self.on_client_afk, self.afk_timeout, True, clid, cid)
        else:
            # client is not muted
            self.on_client_unafk(clid, cid)

    def on_client_afk(self, clid, cid):
        """!
        @brief Callback when the AFK timer has elapsed

        @param clid Client ID
        @param cid Old channel ID (where client went AFK)
        @return None
        """
        # only move client back if they are still muted
        if bool(int(self.bot_instance.get_client_value(clid, "client_output_muted"))):
            self.bot_instance.switch_client_to_channel(clid, self.afk_cid)
            # save old channel for later unafk use
            self.bot_instance.set_client_value(clid, AFKSwitcherPlugin.CLIENT_VAL_OLD_CHANNEL, cid)

    def on_client_unafk(self, clid, cid):
        """!
        @brief Callback when a client ended their AFK state.

        @param clid Client ID
        @param cid Current channel ID
        @return None
        """
        old_cid = self.bot_instance.get_client_value(clid, AFKSwitcherPlugin.CLIENT_VAL_OLD_CHANNEL)
        # only move the client if there is an old channel set and the client is still in AFK channel
        if old_cid is not None and cid == self.afk_cid:
            self.bot_instance.switch_client_to_channel(clid, old_cid)
