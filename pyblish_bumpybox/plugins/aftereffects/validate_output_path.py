from pyblish import api
from pyblish_bumpybox import inventory


class RepairOutputPathAction(api.Action):
    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):
        import pyblish_aftereffects

        # Get the errored instances
        failed = []
        for result in context.data["results"]:
            if (result["error"] is not None and
               result["instance"] is not None and
               result["instance"] not in failed):
                failed.append(result["instance"])

        # Apply pyblish.logic to get the instances for the plug-in
        instances = api.instances_by_plugin(failed, plugin)

        for instance in instances:

            cmd = "app.project.renderQueue.item({0}).outputModule(1)"
            cmd += ".setSettings({1})"

            data = '{{"Output File Info":{{"Full Flat Path":"{0}"}}}}'

            class_object = ValidateOutputPath()
            path = class_object.get_expected_path(instance)

            pyblish_aftereffects.send(cmd.format(instance.data["index"],
                                                 data.format(path)))


class ValidateOutputPath(api.InstancePlugin):

    order = inventory.get_order(__file__, "ValidateOutputPath")
    label = "Output Path"
    families = ["img.*"]
    actions = [RepairOutputPathAction]

    def process(self, instance):

        current_path = instance.data["output"].replace("\\", "/")
        expected_path = self.get_expected_path(instance)

        msg = "Output path is not correct."
        msg += " Current: {0}".format(current_path)
        msg += " Expected: {0}".format(expected_path)
        assert current_path == expected_path, msg

    def get_expected_path(self, instance):
        import os

        current_path = instance.data["output"]

        path = instance.context.data["currentFile"]
        func = os.path.join
        basename = instance.data["name"].replace(" ", "_") + ".[####]"
        basename += os.path.splitext(current_path)[1]
        expected_path = func(os.path.dirname(path), "workspace",
                             os.path.splitext(os.path.basename(path))[0],
                             basename)

        return expected_path.replace("\\", "/")
