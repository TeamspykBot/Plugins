import json
import re
import urllib.request

from Bot.Plugins.Base import PluginBase


class YouTubePlugin(PluginBase):
    """
    This plugin annotates links to YouTube videos with their title in channel messages. The channel message is modified
    so that plugins that are executed at any later stage receive the annotated message.

    configuration options for config.json:
    "kleest": {
        "yt": {
          "api_key": "XXX"
        }
    }
    """

    YT_REGEX = re.compile(r"(?:https?://|www\.|https?://www\.)youtu(?:be\.(?:com|de)|\.be)/(?:attribution)?(?:"
                          r"([A-Za-z0-9_-]{11})|"
                          r".*?v=([A-Za-z0-9_-]{11})|"
                          r"v/([A-Za-z0-9_-]{11})|"
                          r"watch/([A-Za-z0-9_-]{11}))")
    YT_REQUEST_URI = \
        "https://www.googleapis.com/youtube/v3/videos?key={key}&id={ytid}&part=snippet&fields=items(snippet/title)"
    CONFIG_NAMESPACE = "kleest"

    def __init__(self, bot_instance):
        super().__init__(bot_instance)

        self.api_key = bot_instance.get_user_setting(YouTubePlugin.CONFIG_NAMESPACE + ".yt.api_key")
        if self.api_key is None:
            raise AttributeError(str(self.__class__.__name__), "No API key set")

    def on_channel_text(self, event):
        """!
        @brief Parses YouTube video IDs from a channel text.

        Supports multiple video IDs in one message!

        @param event Teamspeak event
        @return None
        """
        msg = event.args[0]["msg"]
        cid = event.args[0]["cid"]

        matches = re.finditer(YouTubePlugin.YT_REGEX, msg)
        ytids = []
        if matches:
            for match in matches:
                for group in match.groups():
                    if group is not None:
                        ytids.append(group)

        if len(ytids) > 0:
            for ytid in ytids:
                self.received_youtube_link(event, ytid, cid)

    def received_youtube_link(self, event, ytid, cid):
        """!
        @brief Handles a received YouTube video link.

        Detailed steps:
        - Queries YouTube API
        - Sends a text message containing the video's title to the channel
        - Modifies the event's message, so that later plugins received the altered version

        @param event Teamspeak event
        @param ytid YouTube video ID
        @param cid Channel ID
        @return None
        """
        title = self.query_yt_api(ytid)

        self.bot_instance.send_text_to_channel(cid, title)
        event.args[0]["msg"] += " (" + title + ")"

    def query_yt_api(self, ytid):
        """!
        @brief Queries the YouTube API for the video's title.

        @param ytid YouTube video ID
        @return Title as string
        """
        data = urllib.request.urlopen(YouTubePlugin.YT_REQUEST_URI.format(ytid=ytid, key=self.api_key)).read().decode()
        data = json.loads(data)
        title = data["items"][0]["snippet"]["title"]

        return title
