from pyblish import api
from pyblish_bumpybox import inventory


class ValidateTransforms(api.InstancePlugin):
    """ Freeze/Reset transforms.

    Ensure all meshes have their pivot at world zero,
    and their transforms are zero'ed out.
    """

    order = inventory.get_order(__file__, "ValidateTransforms")
    families = ["mayaAscii", "mayaBinary", "alembic"]
    label = "Transforms"
    optional = True
    targets = ["process.local"]

    def process(self, instance):
        import pymel.core as pm

        attributes = {
            "tx": 0,
            "ty": 0,
            "tz": 0,
            "rx": 0,
            "ry": 0,
            "rz": 0,
            "sx": 1,
            "sy": 1,
            "sz": 1
        }

        check = True
        for node in instance[0].members():
            v = sum(node.getRotatePivot(space="world"))
            if v > 0.09:
                msg = "\"{0}\" pivot is not at world zero."
                self.log.error(msg.format(node.name()))
                check = False

            v = sum(node.getRotation(space="world"))
            if v != 0:
                msg = "\"{0}\" pivot axis is not aligned to world."
                self.log.error(msg.format(node.name()))
                check = False

            if sum(node.scale.get()) != 3:
                msg = "\"{0}\" scale is not neutral."
                self.log.error(msg.format(node.name()))
                check = False

            for key, value in attributes.iteritems():
                attr = pm.PyNode("{0}.{1}".format(node.name(), key))
                if attr.get() != value:
                    msg = "Expected \"{0}\" value \"{1}\". Current \"{2}\""
                    self.log.error(msg.format(attr, value, attr.get()))
                    check = False

        msg = "Transforms in the scene aren't reset."
        msg += " Please reset by \"Modify\" > \"Freeze Transformations\","
        msg += " followed by \"Modify\" > \"Reset Transformations\"."
        assert check, msg
