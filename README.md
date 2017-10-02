# Plugins

You can find a collection of available plugins in this repo. 

To install a plugin simply do the following:

1. Download the desired plugin
2. Move the plugin into the Bot/Plugin folder.
3. In case you have `load_all_plugins` set to false inside your config, you now need to add the plugin filename ( without the .py extension ) to the `plugin_list`. E.g CommandHelp.py would be CommandHelp
4. You may need to adjust your configs plugins section and add additional values. Every plugin is expected to provide you with a list of configuration options and an example json. You can usually find the documentation inside the plugin, which can be opened with any text editor.
