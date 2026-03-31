#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import logging
import os
from typing import Callable, Dict, List

import numpy as np

try:
    from pxr import Gf, Usd, UsdGeom, UsdShade
except ImportError:
    raise ImportError(
        "OpenUSD is required for UsdConverter. "
        "Install it with: pip install simulariumio[usd]"
    )

from ..constants import DISPLAY_TYPE, VIZ_TYPE
from ..data_objects import AgentData, DisplayData, DimensionData, TrajectoryData
from ..trajectory_converter import TrajectoryConverter
from .usd_data import UsdData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class UsdConverter(TrajectoryConverter):
    def __init__(
        self,
        input_data: UsdData,
        progress_callback: Callable[[float], None] = None,
        callback_interval: float = 10,
    ):
        """
        This object reads simulation trajectory outputs
        from USD (Universal Scene Description) files
        and writes them in the format used
        by the Simularium viewer

        Parameters
        ----------
        input_data : UsdData
            An object containing info for reading
            USD simulation trajectory outputs
        progress_callback : Callable [[float], None] (optional)
            Callback function that accepts 1 float argument and returns None
            which will be called at a given progress interval, determined by
            callback_interval requested, providing the current percent progress
            Default: None
        callback_interval : float (optional)
            If a progress_callback was provided, the period between updates
            to be sent to the callback, in seconds
            Default: 10
        """
        self._obj_data = {}
        self._mesh_to_obj = {}
        super().__init__(input_data, progress_callback, callback_interval)
        self._data = self._read(input_data)

    @staticmethod
    def _geometry_hash(points, face_vertex_indices) -> str:
        """Compute a hash for mesh geometry to identify duplicates."""
        pts_bytes = np.array(points).round(6).tobytes()
        idx_bytes = np.array(face_vertex_indices, dtype=np.int32).tobytes()
        return hashlib.sha256(pts_bytes + idx_bytes).hexdigest()

    @staticmethod
    def _extract_color(prim) -> str:
        """Extract hex color from a mesh prim's material binding."""
        binding = UsdShade.MaterialBindingAPI(prim)
        material = binding.GetDirectBinding().GetMaterial()
        if not material:
            return ""
        for child in material.GetPrim().GetChildren():
            shader = UsdShade.Shader(child)
            color_input = shader.GetInput("diffuseColor")
            if color_input:
                color = color_input.Get()
                if color:
                    return "#{:02x}{:02x}{:02x}".format(
                        int(color[0] * 255),
                        int(color[1] * 255),
                        int(color[2] * 255),
                    )
        return ""

    @staticmethod
    def _find_xform_prim(mesh_prim):
        """Find the prim that carries xform ops for a mesh.

        Blender exports USD with an Xform parent that holds
        translate/rotate/scale while the child Mesh has none.
        Other tools put xform ops directly on the Mesh prim.
        This checks the mesh first, then its parent.
        """
        xformable = UsdGeom.Xformable(mesh_prim)
        if xformable.GetOrderedXformOps():
            return mesh_prim
        parent = mesh_prim.GetParent()
        if parent and not parent.IsPseudoRoot():
            parent_xformable = UsdGeom.Xformable(parent)
            if parent_xformable.GetOrderedXformOps():
                return parent
        return mesh_prim

    @staticmethod
    def _get_xform_op(prim, op_suffix: str):
        """Get a specific xform op from a prim by op name suffix."""
        xformable = UsdGeom.Xformable(prim)
        for op in xformable.GetOrderedXformOps():
            if op.GetOpName().endswith(op_suffix):
                return op
        return None

    @staticmethod
    def _write_obj(
        path: str,
        points,
        face_vertex_counts,
        face_vertex_indices,
    ) -> None:
        """Write mesh geometry to a Wavefront OBJ file."""
        with open(path, "w") as f:
            for pt in points:
                f.write(f"v {pt[0]} {pt[1]} {pt[2]}\n")
            idx = 0
            for count in face_vertex_counts:
                # OBJ uses 1-based indexing
                face = " ".join(
                    str(face_vertex_indices[idx + i] + 1) for i in range(count)
                )
                f.write(f"f {face}\n")
                idx += count

    def _read(self, input_data: UsdData) -> TrajectoryData:
        """
        Return a TrajectoryData object containing the USD data
        """
        print("Reading USD Data -------------")
        try:
            stage = Usd.Stage.Open(input_data.usd_file_path)
        except Exception:
            stage = None
        if stage is None:
            raise FileNotFoundError(
                f"Could not open USD file: {input_data.usd_file_path}"
            )

        # Stage metadata
        start_frame = int(stage.GetStartTimeCode())
        end_frame = int(stage.GetEndTimeCode())
        fps = stage.GetFramesPerSecond()
        meters_per_unit = UsdGeom.GetStageMetersPerUnit(stage)

        # Collect mesh prims and find their transform sources.
        # Blender puts xform ops on a parent Xform prim, not the Mesh itself.
        mesh_prims = [p for p in stage.Traverse() if p.IsA(UsdGeom.Mesh)]
        xform_prims = [self._find_xform_prim(p) for p in mesh_prims]

        # Optionally trim to the last frame that has actual keyframe data
        if input_data.trim_to_animation:
            last_keyed = start_frame
            for xf in xform_prims:
                xformable = UsdGeom.Xformable(xf)
                for op in xformable.GetOrderedXformOps():
                    samples = op.GetTimeSamples()
                    if samples:
                        last_keyed = max(last_keyed, int(samples[-1]))
            end_frame = min(end_frame, last_keyed)

        total_frames = end_frame - start_frame + 1
        n_agents = len(mesh_prims)

        if n_agents == 0:
            log.warning("No mesh prims found in USD file")

        # Extract and deduplicate mesh geometry.
        # Non-uniform scale is baked into the vertices so the OBJ shape is
        # correct, then the result is normalized to fit in a unit sphere.
        # Vertices are scaled relative to the prim's local origin (NOT
        # re-centered) so that the viewer's `vertex * radius` scaling
        # preserves the original pivot point — e.g. a cylinder whose origin
        # is at one end will still extend outward from that end.
        hash_to_obj: Dict[str, str] = {}
        mesh_max_dists: Dict[str, float] = {}
        obj_counter = 0
        for i, prim in enumerate(mesh_prims):
            mesh = UsdGeom.Mesh(prim)
            points = mesh.GetPointsAttr().Get()
            fvc = mesh.GetFaceVertexCountsAttr().Get()
            fvi = mesh.GetFaceVertexIndicesAttr().Get()

            # Bake scale into vertices (use first-frame scale)
            scale_op = self._get_xform_op(xform_prims[i], "scale")
            scale = np.array(scale_op.Get(start_frame)) if scale_op else np.ones(3)
            pts = np.array(points) * scale

            geo_hash = self._geometry_hash(pts, fvi)
            if geo_hash not in hash_to_obj:
                max_dist = np.max(np.linalg.norm(pts, axis=1))
                if max_dist > 0:
                    pts = pts / max_dist
                obj_filename = f"mesh_{obj_counter}.obj"
                obj_counter += 1
                hash_to_obj[geo_hash] = obj_filename
                self._obj_data[obj_filename] = (pts, fvc, fvi)
                mesh_max_dists[obj_filename] = max_dist

            self._mesh_to_obj[prim.GetName()] = hash_to_obj[geo_hash]

        # Build AgentData
        dimensions = DimensionData(total_frames, n_agents)
        result = AgentData.from_dimensions(dimensions)

        # Per-agent constants (invariant across frames)
        agent_type_names: List[str] = []
        xformables = []
        for agent_idx, prim in enumerate(mesh_prims):
            result.unique_ids[:, agent_idx] = agent_idx
            result.viz_types[:, agent_idx] = VIZ_TYPE.DEFAULT

            # Use display name from user-provided display_data if available,
            # otherwise fall back to the prim name. This ensures result.types
            # and result.display_data use the same key.
            raw_name = prim.GetName()
            if raw_name in input_data.display_data:
                agent_type_names.append(input_data.display_data[raw_name].name)
            else:
                agent_type_names.append(raw_name)

            xf = xform_prims[agent_idx]
            xformables.append(UsdGeom.Xformable(xf))

            # Radius = max distance from origin to any vertex (with scale
            # baked in), matching the normalization used for the OBJ geometry.
            obj_filename = self._mesh_to_obj[prim.GetName()]
            max_dist = mesh_max_dists.get(obj_filename, 1.0)
            result.radii[:, agent_idx] = max_dist * meters_per_unit

        # Extract position and rotation per frame from each prim's composed
        # local transform, which correctly handles any combination of xform ops.
        result.n_agents[:] = n_agents
        for frame_idx in range(total_frames):
            result.times[frame_idx] = frame_idx / fps
            result.types[frame_idx] = list(agent_type_names)

            frame_time = Usd.TimeCode(start_frame + frame_idx)
            for agent_idx in range(n_agents):
                local = xformables[agent_idx].GetLocalTransformation(frame_time)
                gf_xform = Gf.Transform(local)

                # Position
                pos = gf_xform.GetTranslation()
                result.positions[frame_idx][agent_idx] = (
                    np.array(pos) * meters_per_unit
                )

                # Rotation: Decompose(X, Y, Z) returns Euler angles matching
                # THREE.js Euler('XYZ') — both use intrinsic XYZ convention.
                euler_deg = gf_xform.GetRotation().Decompose(
                    Gf.Vec3d(1, 0, 0),
                    Gf.Vec3d(0, 1, 0),
                    Gf.Vec3d(0, 0, 1),
                )
                result.rotations[frame_idx][agent_idx] = np.radians(euler_deg)

            self.check_report_progress(frame_idx / total_frames)

        # Unwrap any 2-pi Euler jumps across frames
        for agent_idx in range(int(n_agents)):
            for axis in range(3):
                result.rotations[:total_frames, agent_idx, axis] = np.unwrap(
                    result.rotations[:total_frames, agent_idx, axis]
                )

        # Build display data
        for prim in mesh_prims:
            type_name = prim.GetName()
            if type_name in input_data.display_data:
                display_data = input_data.display_data[type_name]
                result.display_data[display_data.name] = display_data
            else:
                color = self._extract_color(prim)
                obj_filename = self._mesh_to_obj[type_name]
                result.display_data[type_name] = DisplayData(
                    name=type_name,
                    display_type=DISPLAY_TYPE.OBJ,
                    url=obj_filename,
                    color=color,
                )

        # Center and scale
        if input_data.center:
            agent_data, scale_factor = TrajectoryConverter.center_and_scale_agent_data(
                result, input_data.meta_data.scale_factor
            )
        else:
            agent_data, scale_factor = TrajectoryConverter.scale_agent_data(
                result, input_data.meta_data.scale_factor
            )

        input_data.spatial_units.multiply(1.0 / scale_factor)
        input_data.meta_data.scale_factor = scale_factor
        input_data.meta_data._set_box_size()
        return TrajectoryData(
            meta_data=input_data.meta_data,
            agent_data=agent_data,
            time_units=input_data.time_units,
            spatial_units=input_data.spatial_units,
            plots=input_data.plots,
        )

    def save(
        self, output_path: str, binary: bool = True, validate_ids: bool = True
    ) -> None:
        """
        Save the trajectory as a .simularium file and write any
        OBJ geometry files alongside it.

        Parameters
        ----------
        output_path: str
            where to save the file (without extension)
        binary: bool (optional)
            save in binary format? otherwise use JSON
            Default: True
        validate_ids: bool
            additional validation to check agent ID size?
            Default = True
        """
        output_dir = os.path.dirname(output_path) or "."
        for obj_filename, (points, fvc, fvi) in self._obj_data.items():
            obj_path = os.path.join(output_dir, obj_filename)
            self._write_obj(obj_path, points, fvc, fvi)
        super().save(output_path, binary, validate_ids)
