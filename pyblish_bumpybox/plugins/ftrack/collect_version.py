from pyblish import api
from pyblish_bumpybox import inventory


class CollectVersion(api.ContextPlugin):
    """ Collects the version from the latest scene asset """

    # offset to get current version from CollectSceneVersion
    order = inventory.get_order(__file__, "CollectVersion")
    label = "Ftrack Version"

    def process(self, context):

        session = context.data["ftrackSession"]
        task = context.data["ftrackTask"]

        if not task:
            return

        query = "select versions.version from Asset where parent.id is \"{0}\""
        query += " and type.short is \"scene\" and name is \"{1}\""
        asset = session.query(query.format(
            task["parent"]["id"],
            task["name"]
        )).first()

        # Get current version
        current_version = context.data.get("version", 1)

        if asset:
            for version in asset["versions"]:
                if current_version < version["version"]:
                    current_version = version["version"]

        context.data["version"] = current_version

        self.log.info("Current version: " + str(current_version))
