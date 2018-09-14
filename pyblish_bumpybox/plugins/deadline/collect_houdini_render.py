from pyblish import api
from pyblish_bumpybox import inventory


class CollectHoudiniRender(api.ContextPlugin):
    """ Append render output path to instances.

    ContextPlugin to ensure processing, even if instance is disabled.
    Offset to get instances from Houdini collection.
    """

    order = inventory.get_order(__file__, "CollectHoudiniRender")
    label = "Houdini Render"
    hosts = ["houdini"]

    def process(self, context):
        import os

        import hou

        import clique

        for instance in context:

            # Skip invalid instance families
            if "render" not in instance.data.get("families", []):
                continue

            node = instance[0]

            # Get expected output files.
            files = []
            if node.parm("trange").eval() == 0:
                frame = int(hou.frame())
                files.append(node.parm("vm_picture").evalAtFrame(frame))
            else:
                start = node.parm("f1").eval()
                end = node.parm("f2").eval()
                step = node.parm("f3").eval()
                for frame in range(int(start), int(end) + 1, int(step)):
                    files.append(node.parm("vm_picture").evalAtFrame(frame))

            # Get extension
            ext = os.path.splitext(files[0])[1]

            # Create output collection.
            collections = clique.assemble(files, minimum_items=1)[0]
            collection = None
            for col in collections:
                if col.format("{tail}") == ext:
                    collection = col

            if collection:
                instance.data["render"] = collection.format()
