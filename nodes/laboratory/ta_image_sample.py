import bpy
import cv2
import uuid
import random
import numpy as np
from logging import getLogger
from bpy.props import EnumProperty, StringProperty, IntProperty

from ...utils import cv_register_class, cv_unregister_class, OCVLPreviewNode, convert_to_cv_image, updateNode
from ...auth import ocvl_auth

logger = getLogger(__name__)

IMAGE_MODE_ITEMS = [
    ("FILE", "FILE", "From file", "", 0),
    ("PLANE", "PLANE", "Plane color", "", 1),
    ("RANDOM", "RANDOM", "Random figures", "", 2),
    ]


class OCVLImageImporterOp(bpy.types.Operator):
    bl_idname = "image.image_importer"
    bl_label = "OCVL Image Import Operator"

    n_id = StringProperty(default='')

    filepath = StringProperty(
        name="File Path",
        description="Filepath used for importing the font file",
        maxlen=1024, default="", subtype='FILE_PATH')

    origin = StringProperty("")

    def execute(self, context):
        node_tree, node_name = self.origin.split('|><|')
        node = bpy.data.node_groups[node_tree].nodes[node_name]
        node.loc_filepath = self.filepath
        node.loc_name_image = ''
        node.process()
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class OCVLSimpleImageSampleNode(OCVLPreviewNode):
    ''' Image sample '''
    bl_icon = 'IMAGE_DATA'

    def update_layout(self, context):
        logger.debug("UPDATE_LAYOUT")
        self.update_sockets(context)
        updateNode(self, context)

    def update_prop_search(self, context):
        logger.debug("UPDATE_PROP_SEARCH")
        self.process()
        updateNode(self, context)

    width_in = IntProperty(default=100, min=1, max=1024, update=updateNode, name="width_in")
    height_in = IntProperty(default=100, min=1, max=1020, update=updateNode, name="height_in")
    width_out = IntProperty(default=0, name="width_out")
    height_out = IntProperty(default=0, name="height_out")
    image_out = StringProperty(default=str(uuid.uuid4()))

    loc_name_image = StringProperty(default='', update=update_prop_search)
    loc_filepath = StringProperty(default='', update=updateNode)
    loc_image_mode = EnumProperty(items=IMAGE_MODE_ITEMS, default="RANDOM", update=update_layout)

    def sv_init(self, context):
        self.width = 200
        self.outputs.new('StringsSocket', 'image_out')
        self.outputs.new('StringsSocket', 'width_out')
        self.outputs.new('StringsSocket', 'height_out')
        self.update_layout(context)

        if not np.bl_listener:
            from pynput import mouse
            from ...utils import on_click_callback

            np.bl_listener = mouse.Listener(on_click=on_click_callback, )

            np.bl_listener.start()
            np.bl_listener.wait()

    def wrapped_process(self):
        logger.info("Process: self: {}, loc_image_mode: {}, loc_filepath: {}".format(self, self.loc_image_mode, self.loc_filepath))
        image = None
        uuid_ = None
        if self.loc_image_mode in ["PLANE", "RANDOM"]:
            width_in = self.get_from_props("width_in")
            height_in = self.get_from_props("height_in")
            image = np.zeros((width_in, height_in, 3), np.uint8)
            image[:,:,] = (76, 76, 53)
            if self.loc_image_mode == "RANDOM":
                for i in range(20):
                    pt1 = (random.randint(1, width_in), random.randint(1, height_in))
                    pt2 = (random.randint(1, width_in), random.randint(1, height_in))
                    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                    image = cv2.line(image, pt1, pt2, color, random.randint(1, 10))
        elif self.loc_image_mode == "FILE":
            if self.loc_name_image in bpy.data.images:
                image = convert_to_cv_image(bpy.data.images[self.loc_name_image])
                uuid_ = self.loc_name_image
            elif self.loc_filepath:
                image = cv2.imread(self.loc_filepath)
            if image is None:
                image = np.zeros((200, 200, 3), np.uint8)

        image, self.image_out = self._update_node_cache(image=image, resize=False, uuid_=uuid_)

        self.outputs['image_out'].sv_set(self.image_out)
        self.refresh_output_socket("height_out", image.shape[0])
        self.refresh_output_socket("width_out", image.shape[1])
        self.make_textures(image, uuid_=self.image_out)
        self._add_meta_info(image)

    def _add_meta_info(self, image):
        self.n_meta = "\n".join(["Width: {}".format(image.shape[1]),
                                 "Height: {}".format(image.shape[0]),
                                 "Channels: {}".format(image.shape[2]),
                                 "DType: {}".format(image.dtype),
                                 "Size: {}".format(image.size)])

    def _update_node_cache(self, image=None, resize=False, uuid_=None):
        old_image_out = self.image_out
        self.socket_data_cache.pop(old_image_out, None)
        uuid_ = uuid_ if uuid_ else str(uuid.uuid4())
        self.socket_data_cache[uuid_] = image
        return image, uuid_

    def draw_buttons(self, context, layout):
        origin = self.get_node_origin()
        self.add_button(layout, "loc_image_mode", expand=True)

        if self.loc_image_mode == "FILE":
            col = layout.row().column()
            col_split = col.split(1, align=True)
            col_split.operator('image.image_importer', text='', icon="FILE_FOLDER").origin = origin
        elif self.loc_image_mode == "PLANE":
            pass
        elif self.loc_image_mode == "RANDOM":
            pass

        if self.n_id not in self.texture:
            return

        location_y = -20 if self.loc_image_mode in ["PLANE", "RANDOM"] else -40
        self.draw_preview(layout=layout, prop_name="image_out", location_x=10, location_y=location_y)

    def copy(self, node):
        self.n_id = ''
        self.process()
        node.process()

    def update_sockets(self, context):
        self.process()


if ocvl_auth.ocvl_ext:
    from ...extend.laboratory.ta_image_sample import OCVLImageSampleNode


def register():
    cv_register_class(OCVLImageImporterOp)
    cv_register_class(OCVLImageSampleNode)
    cv_register_class(OCVLSimpleImageSampleNode)


def unregister():
    cv_unregister_class(OCVLSimpleImageSampleNode)
    cv_unregister_class(OCVLImageSampleNode)
    cv_unregister_class(OCVLImageImporterOp)
