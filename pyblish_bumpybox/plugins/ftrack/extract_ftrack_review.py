import json
import subprocess

import pyblish.api


class ExtractFtrackReview(pyblish.api.InstancePlugin):
    """Extracts component for review.

    Offset to get extraction data from studio plugins.
    """

    families = ["review", "trackItem.ftrackEntity.shot"]
    order = pyblish.api.ExtractorOrder + 0.2
    label = "Review"
    optional = True

    def process(self, instance):

        path = instance.data["output_path"]

        cmd = (
            "ffprobe -v error -count_frames -select_streams v:0 -show_entries "
            "stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 "
            "\"{0}\""
        )
        frame_count = subprocess.check_output(cmd.format(path))

        cmd = (
            "ffprobe -v 0 -of compact=p=0:nk=1 -select_streams 0 -show_entries"
            " stream=r_frame_rate \"{0}\""
        )
        # ffprobe returns a math string, hence the "eval"
        frame_rate = eval(subprocess.check_output(cmd.format(path)))

        # Add Ftrack review component
        components = instance.data.get("ftrackComponentsList", [])
        server_location = instance.context.data["ftrackSession"].query(
            "Location where name is \"ftrack.server\""
        ).one()

        data = {
          "assettype_data": {"short": instance.data["review_family"]},
          "asset_data": instance.data.get("asset_data"),
          "assetversion_data": {
            "version": instance.data.get(
                "version", instance.context.data["version"]
            ),
          },
          "component_data": {
            "name": "ftrackreview-mp4",
            "metadata": {
                "ftr_meta": json.dumps({
                    "frameIn": 1,
                    "frameOut": frame_count,
                    "frameRate": str(frame_rate)
                })
            }
          },
          "component_overwrite": True,
          "component_location": server_location,
          "component_path": path
        }

        # From NukeStudio the reviews needs to be parented to the shots.
        if "trackItem.ftrackEntity.shot" in instance.data["families"]:
            data["asset_data"]["parent"] = instance.data["entity"]

        components.append(data)
        instance.data["ftrackComponentsList"] = components
