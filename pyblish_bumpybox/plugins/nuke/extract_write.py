from pyblish import api
from pyblish_bumpybox import inventory


class Extract(api.InstancePlugin):
    """Super class for write and writegeo extractors."""

    order = inventory.get_order(__file__, "Extract")
    optional = True
    hosts = ["nuke"]
    match = api.Subset
    targets = ["process.local"]

    def execute(self, instance):
        import nuke

        # Get frame range
        node = instance[0]
        first_frame = nuke.root()["first_frame"].value()
        last_frame = nuke.root()["last_frame"].value()

        if node["use_limit"].value():
            first_frame = node["first"].value()
            last_frame = node["last"].value()

        # Render frames
        nuke.execute(node.name(), int(first_frame), int(last_frame))


class ExtractWrite(Extract):
    """ Extract output from write nodes. """

    order = inventory.get_order(__file__, "ExtractWrite")
    families = ["write", "local"]
    label = "Write"

    def process(self, instance):
        import os

        self.execute(instance)

        # Validate output
        for filename in list(instance.data["collection"]):
            if not os.path.exists(filename):
                instance.data["collection"].remove(filename)
                self.log.warning("\"{0}\" didn't render.".format(filename))


class ExtractCache(Extract):

    order = inventory.get_order(__file__, "ExtractCache")
    label = "Cache"
    families = ["cache", "local"]

    def process(self, instance):
        import os

        self.execute(instance)

        # Validate output
        msg = "\"{0}\" didn't render.".format(instance.data["output_path"])
        assert os.path.exists(instance.data["output_path"]), msg


class ExtractCamera(Extract):

    order = inventory.get_order(__file__, "ExtractCamera")
    label = "Camera"
    families = ["camera", "local"]

    def process(self, instance):
        import os

        node = instance[0]
        node["writeGeometries"].setValue(False)
        node["writePointClouds"].setValue(False)
        node["writeAxes"].setValue(False)

        file_path = node["file"].getValue()
        node["file"].setValue(instance.data["output_path"])

        self.execute(instance)

        node["writeGeometries"].setValue(True)
        node["writePointClouds"].setValue(True)
        node["writeAxes"].setValue(True)

        node["file"].setValue(file_path)

        # Validate output
        msg = "\"{0}\" didn't render.".format(instance.data["output_path"])
        assert os.path.exists(instance.data["output_path"]), msg


class ExtractGeometry(Extract):

    order = inventory.get_order(__file__, "ExtractGeometry")
    label = "Geometry"
    families = ["geometry", "local"]

    def process(self, instance):
        import os

        node = instance[0]
        node["writeCameras"].setValue(False)
        node["writePointClouds"].setValue(False)
        node["writeAxes"].setValue(False)

        file_path = node["file"].getValue()
        node["file"].setValue(instance.data["output_path"])

        self.execute(instance)

        node["writeCameras"].setValue(True)
        node["writePointClouds"].setValue(True)
        node["writeAxes"].setValue(True)

        node["file"].setValue(file_path)

        # Validate output
        msg = "\"{0}\" didn't render.".format(instance.data["output_path"])
        assert os.path.exists(instance.data["output_path"]), msg
