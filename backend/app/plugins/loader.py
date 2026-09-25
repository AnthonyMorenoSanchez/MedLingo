import importlib
import logging
import tomllib

from app.engine.generators import REGISTRY


def load_plugins(app,path):
    plugins=[]
    config=tomllib.loads(path.read_text()) if path.exists() else {}
    for name,settings in config.items():
        if not settings.get("enabled"):continue
        try:
            if not name.replace("_", "").isalnum():raise ValueError("Invalid plugin name")
            plugin=importlib.import_module(f"app.plugins.{name}.plugin").PLUGIN
            plugin.configure(settings)
            plugin.register_routes(app)
            REGISTRY.update(plugin.register_question_types())
            plugins.append(plugin)
        except Exception:
            logging.getLogger(__name__).exception("Plugin %s failed to load; continuing",name)
    return plugins
