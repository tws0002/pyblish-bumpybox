from pyblish import api
from pyblish_bumpybox import inventory


class ExtractFormats(api.InstancePlugin):
    """ Extracts Maya ascii and binary files. """

    order = inventory.get_order(__file__, "ExtractFormats")
    families = ["mayaAscii", "mayaBinary"]
    optional = True
    label = "Maya Formats"
    hosts = ["maya"]
    targets = ["process.local"]

    def process(self, instance):
        import os

        import pyblish_maya

        import pymel

        # Skip any remote instances
        if "remote" in instance.data["families"]:
            return

        # Export to file.
        path = instance.data["output_path"]

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        with pyblish_maya.maintained_selection():

            # Disconnect animation if requested
            connections = []
            if instance.data.get("disconnectAnimation", False):
                # Disconnect connections to anim curves, and store for later
                for node in pymel.core.ls(type="transform"):
                    connections.extend(self.disconnect(node, "animCurveTA"))
                    connections.extend(self.disconnect(node, "animCurveTU"))
                    connections.extend(self.disconnect(node, "animCurveTL"))

            # Export selection
            pymel.core.select(instance.data["nodes"], noExpand=True)
            export_type = set(self.families) & set(instance.data["families"])
            pymel.core.system.exportSelected(
                path,
                force=True,
                type=list(export_type)[0],
                preserveReferences=False,
                constructionHistory=instance.data.get(
                    "constructionHistory", True
                )
            )

            # Reconnect animation
            for connection in connections:
                connection["source"] >> connection["destination"]

    def disconnect(self, node, connectionType):
        import maya.cmds as cmds

        connections = []
        for connection in node.connections(type=connectionType, plugs=True):
            src = connection
            dst = connection.connections(
                destination=True, source=False, plugs=True
            )[0]

            # Skip locked attributes
            if dst.get(lock=True):
                continue

            connections.append({"source": src, "destination": dst})
            connection // dst

            # Reset attribute
            values = cmds.attributeQuery(
                dst.name(includeNode=False),
                node=node.name(),
                listDefault=True
            )
            try:
                cmds.setAttr(
                    node.name() + '.' + dst.name(includeNode=False), *values
                )
            except:
                pass

        return connections
