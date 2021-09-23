from bpy.types import (
    Operator,
    OperatorFileListElement,
    Panel
)
from bpy.props import (
    StringProperty,
    CollectionProperty
)
from bpy_extras.io_utils import ImportHelper
import bpy
import pickle
from os.path import splitext, join, basename

bl_info = {
    "name": "PyBulletSimImporter",
    "author": "Huy Ha <hqh2101@columbia.edu>",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "3D View > Toolbox > Animation tab > PyBullet Simulation Importer",
    "description": "Imports PyBullet Simulation Results",
    "warning": "",
    "category": "Animation",
}


class ANIM_OT_import_pybullet_sim(Operator, ImportHelper):
    bl_label = "Import simulation"
    bl_idname = "pybulletsim.import"
    bl_description = "Imports a PyBullet Simulation"
    bl_options = {'REGISTER', 'UNDO'}
    files = CollectionProperty(
        name="Simulation files",
        type=OperatorFileListElement,
    )
    directory =  StringProperty(subtype='DIR_PATH')
    filename_ext = ".pkl"
    filter_glob =  StringProperty(
        default='*.pkl',
        options={'HIDDEN'})
    skip_frames = 1  # TODO turn into option during import

    def execute(self, context):
        for file in self.files:
            filepath = join(self.directory, file.name)
            with open(filepath, 'rb') as pickle_file:
                data = pickle.load(pickle_file)

                for obj_key in data:
                    pybullet_obj = data[obj_key]
                    # Load mesh of each link
                    assert pybullet_obj['type'] == 'mesh'

                    # Delete lights and camera
                    parts = 0
                    final_objs = []

                    for (i,mesh) in enumerate(pybullet_obj['mesh_path']):
                        extension = splitext(mesh)[1]
                    #extension = splitext(pybullet_obj['mesh_path'])[1]
                    # Handle different mesh formats
                        if 'obj' in extension:
                            bpy.ops.import_scene.obj(
                                filepath=pybullet_obj['mesh_path'][i],
                                axis_forward='-Z', axis_up='Y')
                        elif 'dae' in extension:
                            bpy.ops.wm.collada_import(
                                filepath=pybullet_obj['mesh_path'][i])
                        elif 'stl' in extension:
                            bpy.ops.import_mesh.stl(
                                filepath=pybullet_obj['mesh_path'][i])
                        else:
                            print("Unsupported File Format:{}".format(extension))
                            return
                    
                        for import_obj in context.selected_objects:
                            bpy.ops.object.select_all(action='DESELECT')
                            import_obj.select = True
                            if 'Camera' in import_obj.name \
                                    or 'Light' in import_obj.name\
                                    or 'Lamp' in import_obj.name:
                                bpy.ops.object.delete(use_global=True)
                            else:
                                scale = pybullet_obj['mesh_scale']
                                if scale is not None:
                                    import_obj.scale.x = scale[0]
                                    import_obj.scale.y = scale[1]
                                    import_obj.scale.z = scale[2]
                                final_objs.append(import_obj)
                                parts += 1

                    bpy.ops.object.select_all(action='DESELECT')
                    for obj in final_objs:
                        if obj.type == 'MESH':
                            obj.select = True
                    if len(context.selected_objects):
                        context.scene.objects.active =\
                            context.selected_objects[0]
                        # join them
                        bpy.ops.object.join()
                    blender_obj = context.scene.objects.active
                    blender_obj.name = obj_key

                    # Keyframe motion of imported object
                    for frame_count, frame_data in enumerate(
                            pybullet_obj['frames']):
                        if frame_count % self.skip_frames != 0:
                            continue
                        pos = frame_data['position']
                        orn = frame_data['orientation']
                        context.scene.frame_set(
                            frame_count // self.skip_frames)
                        # Apply position and rotation
                        # blender_obj.location.x = 0
                        # blender_obj.location.y = 0
                        # blender_obj.location.z = 0

                        blender_obj.rotation_mode = 'QUATERNION'
                        blender_obj.rotation_quaternion.x = orn[0]
                        blender_obj.rotation_quaternion.y = orn[1]
                        blender_obj.rotation_quaternion.z = orn[2]
                        blender_obj.rotation_quaternion.w = orn[3]

                        blender_obj.location.x = pos[0]
                        blender_obj.location.y = pos[1]
                        blender_obj.location.z = pos[2]
                        
                        bpy.ops.anim.keyframe_insert_menu(
                            type='Rotation')
                        bpy.ops.anim.keyframe_insert_menu(
                            type='Location')
        return {'FINISHED'}


class VIEW3D_PT_pybullet_recorder(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Animation"
    bl_label = 'PyBulletSimImporter'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("pybulletsim.import")


def register():
    bpy.utils.register_class(VIEW3D_PT_pybullet_recorder)
    bpy.utils.register_class(ANIM_OT_import_pybullet_sim)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_pybullet_recorder)
    bpy.utils.unregister_class(ANIM_OT_import_pybullet_sim)


if __name__ == "__main__":
    register()