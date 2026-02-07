from tuda.plugins.manager import discover_plugins


def test_discover_plugins_and_run():
    plugins = discover_plugins()
    assert any(plugin.name == "SpamDetector" for plugin in plugins)

    spam_plugin = next(plugin for plugin in plugins if plugin.name == "SpamDetector")
    result = spam_plugin.run({"subject": "Win a free prize", "snippet": "Click now"})
    assert result["is_spam"] is True
