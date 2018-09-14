from pyblish import api
from pyblish_bumpybox import inventory


class ExtractFtrackTasks(api.InstancePlugin):
    """ Extract Ftrack tasks.

    Offset to get shot from "extract_ftrack_shot"
    """

    families = ["task"]
    label = "Ftrack Tasks"
    optional = True
    order = inventory.get_order(__file__, "ExtractFtrackTasks")
    optional = True
    hosts = ["hiero"]

    def getTaskTypeByName(self, name):
        import ftrack

        for t in ftrack.getTaskTypes():
            if t.getName().lower() == name.lower():
                return t

        return None

    def process(self, instance):

        shot = instance.data["ftrackShot"]
        tasks = shot.getTasks()

        for tag in instance[0].tags():
            data = tag.metadata().dict()
            if "task" == data.get("tag.family", ""):
                task = None

                for t in tasks:
                    if t.getName().lower() == tag.name().lower():
                        task = t

                if not task:
                    try:
                        task = shot.createTask(
                            tag.name().lower(),
                            taskType=self.getTaskTypeByName(tag.name())
                        )
                    except Exception as e:
                        msg = "Could not create task \"{0}\": {1}"
                        self.log.error(msg.format(tag.name(), e))

                if task:
                    # Store task id on tag
                    tag.metadata().setValue("tag.id", task.getId())
