from pyblish import api
from pyblish_bumpybox import inventory


class CollectSceneVersion(api.ContextPlugin):
    """ Collects scene version from filename or passes the one found in
    the context.
    """
    # offset to get the latest currentFile update
    order = inventory.get_order(__file__, "CollectSceneVersion")
    label = "Scene Version"

    def process(self, context):
        import os
        import traceback

        filename = os.path.basename(context.data("currentFile"))

        try:
            prefix, version = self.version_get(filename, "v")
            context.set_data("version", value=int(version))
            self.log.info("Scene Version: %s" % context.data("version"))
        except:
            msg = "Could not collect scene version:\n\n"
            msg += traceback.format_exc()
            self.log.debug(msg)

    def version_get(self, string, prefix):
        """ Extract version information from filenames.  Code from Foundry"s
        nukescripts.version_get()
        """
        import re

        if string is None:
            raise ValueError("Empty version string - no match")

        regex = "[/_.]"+prefix+"\d+"
        matches = re.findall(regex, string, re.IGNORECASE)
        if not len(matches):
            msg = "No \"_"+prefix+"#\" found in \""+string+"\""
            raise ValueError(msg)
        return matches[-1:][0][1], re.search("\d+", matches[-1:][0]).group()
