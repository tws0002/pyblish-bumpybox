import os
import subprocess

import pyblish.api


class ExtractFtrackThumbnail(pyblish.api.InstancePlugin):
    """Extracts movie from image sequence for review.

    Offset to get extraction data from studio plugins.
    """

    families = ["img"]
    order = pyblish.api.ExtractorOrder + 0.1
    label = "Thumbnail"
    optional = True

    def process(self, instance):

        if not self.check_executable("ffmpeg"):
            msg = "Skipping movie extraction because \"ffmpeg\" was not found."
            self.log.info(msg)
            return

        collection = instance.data.get("collection", [])

        if not list(collection):
            msg = "Skipping \"{0}\" because no frames was found."
            self.log.info(msg.format(instance.data["name"]))
            return

        output_file = collection.format("{head}_thumbnail.jpeg")
        input_file = list(collection)[0]
        args = [
            "ffmpeg", "-y",
            "-gamma", "2.2", "-i", input_file,
            "-vf", "scale=300:-1", output_file
        ]

        self.log.debug("Executing args: {0}".format(args))

        # Can"t use subprocess.check_output, cause Houdini doesn"t like that.
        p = subprocess.Popen(args, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, stdin=subprocess.PIPE)

        output = p.communicate()[0]

        if p.returncode != 0:
            raise ValueError(output)

        self.log.debug(output)

        # Add Ftrack review component
        components = instance.data.get("ftrackComponentsList", [])
        server_location = instance.context.data["ftrackSession"].query(
            "Location where name is \"ftrack.server\""
        ).one()
        components.append(
            {
              "assettype_data": {
                "short": "img",
              },
              "asset_data": instance.data.get("asset_data"),
              "assetversion_data": {
                "version": instance.data["version"],
              },
              "component_data": {
                "name": "thumbnail",
              },
              "component_overwrite": True,
              "component_location": server_location,
              "component_path": output_file,
              "thumbnail": True
            }
        )
        instance.data["ftrackComponentsList"] = components

    def check_executable(self, executable):
        """ Checks to see if an executable is available.

        Args:
            executable (str): The name of executable without extension.

        Returns:
            bool: True for executable existance, False for non-existance.
        """

        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(executable)
        if fpath:
            if is_exe(executable):
                return True
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip("\"")
                exe_file = os.path.join(path, executable)
                if is_exe(exe_file):
                    return True
                if is_exe(exe_file + ".exe"):
                    return True

        return False
