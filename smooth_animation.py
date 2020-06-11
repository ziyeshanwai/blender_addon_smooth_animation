bl_info = {
    "name": "Animation low pass smooth tool",
    "author": "liyou Wang",
    "version": (0, 1, 1),
    "blender": (2, 83, 0),
    "location": "Graph Editor > Key > Smoooth Animation",
    "description": ("Adds an option for smooth animation."),
    "category": "Animation"}

import bpy
import sys
import numpy as np
import scipy.signal as signal


class smoothanimationNodes(bpy.types.Operator):

    bl_idname = "graph_key.smoothanimation"
    bl_label = "Smooth animation"

    low_pass_parameter_n = bpy.props.FloatProperty(
        name = "N",
        description = "The order of the filter",
        min = 0,
        max = 20,
        step = 1,
        default = 8,
        unit = 'LENGTH',
        precision = 1
    )
    low_pass_parameter_wn = bpy.props.FloatProperty(
        name="Wn",
        description="The critical frequency or frequencies",
        min=0.0,
        max=2,
        step=0.001,
        default=0.02,
        unit='LENGTH',
        precision=1
    )

    def smooth_curve(self, curve):
        kf_pts = curve.keyframe_points

        if len(kf_pts) < 2:
            self.report({'ERROR_INVALID_INPUT'}, 'Please select whole curves')
            return False
        cos = [points.co[1] for points in kf_pts]
        coes_array = np.array(cos)
        n = int(self.low_pass_parameter_n)
        wn = self.low_pass_parameter_wn
        b, a = signal.butter(n, wn, 'lowpass')
        time_series_filt = signal.filtfilt(b, a, coes_array, axis=0)
        for i in range(0, len(time_series_filt)):
            curve.keyframe_points[i].co[1]=time_series_filt[i]
        curve.select = False
        curve.select = True
        return True

    def execute(self, context):
        smooth_object = bpy.context.active_object
        fcurves = smooth_object.data.shape_keys.animation_data.action.fcurves

        for curve in fcurves:
            if not curve.select:
                continue

            self.smooth_curve(curve)

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        smooth_object = bpy.context.active_object

        if not smooth_object:
            self.report({'ERROR_INVALID_INPUT'}, 'Please select object which animation curve should be smoothed')
            return {'CANCELLED'}

        if not smooth_object.data.shape_keys.animation_data:
            self.report({'ERROR_INVALID_INPUT'}, 'Selected object has no animated data')
            return {'CANCELLED'}

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "low_pass_parameter_n", text='n: ', icon='CURVE_NCIRCLE', slider=True, expand=True)
        layout.prop(self, "low_pass_parameter_wn", text='wn: ', icon='CURVE_NCIRCLE', slider=True, expand=True)
        layout.separator()


def menu_func(self, context):
    self.layout.operator(smoothanimationNodes.bl_idname)


def register():
    bpy.utils.register_class(smoothanimationNodes)
    bpy.types.GRAPH_MT_key.prepend(menu_func)


def unregister():
    bpy.utils.unregister_class(smoothanimationNodes)
    bpy.types.GRAPH_MT_key.remove(menu_func)


if __name__ == "__main__":
    register()
