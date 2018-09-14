from pyblish import api
from pyblish_bumpybox import inventory


class RepairIntermediateShapes(api.Action):
    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):
        import pymel.core as pm

        # Get the errored instances
        failed = []
        for result in context.data["results"]:
            if (result["error"] is not None and result["instance"] is not None
               and result["instance"] not in failed):
                failed.append(result["instance"])

        # Apply pyblish.logic to get the instances for the plug-in
        instances = api.instances_by_plugin(failed, plugin)

        for instance in instances:
            for node in instance[0].members():
                io = pm.ls(node.getShapes(), intermediateObjects=True)
                pm.delete(io)


class ValidateIntermediateShapes(api.InstancePlugin):
    """ Ensures there are no intermediate shapes in the scene. """

    families = ["mayaAscii", "mayaBinary", "alembic"]
    label = "Intermediate Shapes"
    order = inventory.get_order(__file__, "ValidateIntermediateShapes")
    actions = [RepairIntermediateShapes]
    optional = True
    targets = ["process.local"]

    def process(self, instance):
        import pymel.core as pm

        intermediate_objects = []
        for node in instance[0].members():
            io = pm.ls(node.getShapes(), intermediateObjects=True)
            intermediate_objects.extend(io)

        msg = "Intermediate objects present: %s" % intermediate_objects
        assert not intermediate_objects, msg
