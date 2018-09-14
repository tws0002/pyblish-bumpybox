from pyblish import api
from pyblish_bumpybox import inventory


class RepairWriteNodeAction(api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):
        import os

        # Get the errored instances
        failed = []
        for result in context.data["results"]:
            if (result["error"] is not None and result["instance"] is not None
               and result["instance"] not in failed):
                failed.append(result["instance"])

        # Apply pyblish.logic to get the instances for the plug-in
        instances = api.instances_by_plugin(failed, plugin)

        for instance in instances:

            cls_instance = ValidateWriteNode()
            value = cls_instance.get_expected_value(instance)
            instance[0]["file"].setValue(value)

            ext = os.path.splitext(value)[1]
            instance[0]["file_type"].setValue(ext[1:])

            if "metadata" in instance[0].knobs().keys():
                instance[0]["metadata"].setValue("all metadata")


class ValidateWriteNode(api.InstancePlugin):
    """ Validates file output. """

    order = inventory.get_order(__file__, "ValidateWriteNode")
    optional = True
    families = ["write"]
    label = "Write Node"
    actions = [RepairWriteNodeAction]
    hosts = ["nuke"]
    targets = ["default", "process"]

    def process(self, instance):
        import os

        import nuke

        current = instance[0]["file"].getValue()
        expected = self.get_expected_value(instance)

        msg = "Output path for \"{0}\"."
        msg += " Current: \"{1}\". Expected: \"{2}\""
        assert current == expected, msg.format(
            instance[0].name(), current, expected
        )

        # Validate metadata knob
        if "metadata" in instance[0].knobs().keys():
            msg = "Metadata needs to be set to \"all metadata\"."
            assert instance[0]["metadata"].value() == "all metadata", msg

        # Validate file type
        msg = "Wrong file type \"{0}\" selected for extension \"{1}\""
        ext = os.path.splitext(current)[1][1:]
        file_type = instance[0]["file_type"].enumName(
            int(instance[0]["file_type"].getValue())
        )
        assert file_type == ext, msg.format(file_type, ext)

        # Validate no other node is called ""{instance name}_review"
        node_name = "{0}_review".format(instance.data["name"])
        for node in nuke.allNodes():
            assert node.name() != node_name

    def get_current_value(self, instance):
        import nuke

        current = ""
        if nuke.filename(instance[0]):
            current = nuke.filename(instance[0])

        return current

    def get_expected_value(self, instance):
        import os

        expected = (
            "[python {nuke.script_directory()}]/workspace/[python "
            "{nuke.thisNode().name()}]/[python {os.path.splitext("
            "os.path.basename(nuke.scriptName()))[0]}]/[python {"
            "os.path.splitext(os.path.basename(nuke.scriptName()))[0]}]_"
            "[python {nuke.thisNode().name()}]"
        )

        # Default padding starting at 4 digits.
        padding = 4
        if instance.data["collection"]:
            padding = instance.data["collection"].padding
        # Can't have less than 4 digits.
        if padding < 4:
            padding = 4

        # Extension, defaulting to exr files.
        current = self.get_current_value(instance)
        ext = os.path.splitext(os.path.basename(current))[1]
        if not ext:
            ext = ".exr"

        expected += ".%{1}d{2}".format(
            instance[0].name(),
            str(padding).zfill(2),
            ext
        )
        return expected


class ValidateReviewNodeDuplicate(api.InstancePlugin):
    """Validates there are no review nodes in the script."""

    order = inventory.get_order(__file__, "ValidateReviewNodeDuplicate")
    optional = True
    families = ["write"]
    label = "Review Node"
    hosts = ["nuke"]
    targets = ["process"]

    def process(self, instance):
        import nuke
        # Validate no other node is called ""{instance name}_review"
        node_name = "{0}_review".format(instance.data["name"])
        msg = "Can not have a node called \"{0}\".".format(node_name)
        for node in nuke.allNodes():
            assert node.name() != node_name, msg
