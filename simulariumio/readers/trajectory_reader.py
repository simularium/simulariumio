
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict, Any, List

from .reader import Reader

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class TrajectoryReader(Reader):
    def _get_spatial_bundle_data_subpoints(
        self, data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Return the spatialData's bundleData for a simulation 
        of agents with subpoints, packing buffer with jagged data is slower
        """
        bundleData: List[Dict[str, Any]] = []

        for t in range(len(data["times"])):

            frame_data = {}
            frame_data["frameNumber"] = t
            frame_data["time"] = float(data["times"][t])
            n_agents = int(data["n_agents"][t])

            i = 0
            buffer_size = 10 * n_agents
            for n in range(n_agents):
                buffer_size += 3 * len(data["subpoints"][t][n])
            local_buf = np.zeros(buffer_size)

            for n in range(n_agents):

                local_buf[i] = data["viz_types"][t, n]
                local_buf[i + 1] = data["type_ids"][t, n]
                local_buf[i + 2 : i + 5] = data["positions"][t, n]
                local_buf[i + 8] = data["radii"][t, n]

                n_subpoints = len(data["subpoints"][t][n])
                if n_subpoints > 0:
                    subpoints = [3 * n_subpoints]
                    for p in range(n_subpoints):
                        for d in range(3):
                            subpoints.append(data["subpoints"][t][n][p][d])
                    local_buf[i + 9 : i + 10 + 3 * n_subpoints] = subpoints
                    i += 10 + 3 * n_subpoints
                else:
                    local_buf[i + 9] = 0.0
                    i += 10

            frame_data["data"] = local_buf.tolist()
            bundleData.append(frame_data)

        return bundleData

    def _get_spatial_bundle_data_no_subpoints(
        self, data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Return the spatialData's bundleData for a simulation 
        of agents without subpoints, using list slicing for speed
        """
        bundleData: List[Dict[str, Any]] = []

        max_n_agents = int(np.amax(data["n_agents"], 0))
        ix_particles = np.empty((3 * max_n_agents,), dtype=int)
        for i in range(max_n_agents):
            ix_particles[3 * i : 3 * i + 3] = np.arange(i * 10 + 2, i * 10 + 2 + 3)

        frame_buf = np.zeros(10 * max_n_agents)
        for t in range(len(data["times"])):

            frame_data = {}
            frame_data["frameNumber"] = t
            frame_data["time"] = float(data["times"][t])
            n = int(data["n_agents"][t])
            local_buf = frame_buf[: 10 * n]
            local_buf[0::10] = data["viz_types"][t, :n]
            local_buf[1::10] = data["type_ids"][t, :n]
            local_buf[ix_particles[: 3 * n]] = data["positions"][t, :n].flatten()
            local_buf[8::10] = data["radii"][t, :n]
            frame_data["data"] = local_buf.tolist()
            bundleData.append(frame_data)

        return bundleData
