import cv2
import uuid
import numpy as np
from bpy.props import EnumProperty, StringProperty, IntProperty, FloatProperty

from ...extend.utils import cv_register_class, cv_unregister_class, OCVLNode, updateNode


OUTPUT_MODE_ITEMS = (
    ("LINES", "LINES", "LINES", "", 0),
    ("IMAGE", "IMAGE", "IMAGE", "", 1),
)


PROPS_MAPS = {
    OUTPUT_MODE_ITEMS[0][0]: ("lines_out",),
    OUTPUT_MODE_ITEMS[1][0]: ("lines_out", "image_out"),
}


class OCVLHoughLinesNode(OCVLNode):

    def update_layout(self, context):
        self.update_sockets(context)
        updateNode(self, context)

    image_in = StringProperty(name="image_in", default=str(uuid.uuid4()))
    lines_out = StringProperty(name="lines_out", default=str(uuid.uuid4()))
    image_out = StringProperty(name="image_out", default=str(uuid.uuid4()))

    rho_in = FloatProperty(default=3, min=1, max=10, update=updateNode,
        description="Distance resolution of the accumulator in pixels.")
    theta_in = FloatProperty(default=0.0574, min=0.0001, max=3.1415, update=updateNode,
        description="Angle resolution of the accumulator in radians.")
    threshold_in = IntProperty(default=200, min=0, max=255, update=updateNode,
        description="Accumulator threshold parameter.")
    srn_in = FloatProperty(default=0,
        description="For the multi-scale Hough transform, it is a divisor for the distance resolution rho.")
    stn_in = FloatProperty(default=0,
        description="For the multi-scale Hough transform, it is a divisor for the distance resolution theta.")
    min_theta_in = FloatProperty(default=0,
        description="For standard and multi-scale Hough transform, minimum angle to check for lines.")
    max_theta_in = FloatProperty(default=0,
        description="For standard and multi-scale Hough transform, maximum angle to check for lines.")
    #TODO: apply rest of parameters

    loc_output_mode = EnumProperty(items=OUTPUT_MODE_ITEMS, default="LINES", update=update_layout)

    def sv_init(self, context):
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new('StringsSocket', "rho_in").prop_name = 'rho_in'
        self.inputs.new('StringsSocket', "theta_in").prop_name = 'theta_in'
        self.inputs.new('StringsSocket', "threshold_in").prop_name = 'threshold_in'

        self.outputs.new("StringsSocket", "lines_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        kwargs = {
            'image_in': self.get_from_props("image_in"),
            'rho_in': int(self.get_from_props("rho_in")),
            'theta_in': self.get_from_props("theta_in"),
            'threshold_in': int(self.get_from_props("threshold_in")),
            }

        lines_out = self.process_cv(fn=cv2.HoughLines, kwargs=kwargs)
        self.refresh_output_socket("lines_out", lines_out, is_uuid_type=True)
        if self.loc_output_mode == "IMAGE":
            image = np.copy(self.get_from_props("image_in"))
            image_out = self._draw_hough_lines(lines_out, image)
            self.refresh_output_socket("image_out", image_out, is_uuid_type=True)

    def update_sockets(self, context):
        self.update_sockets_for_node_mode(PROPS_MAPS, self.loc_output_mode)
        self.process()

    def _draw_hough_lines(self, lines, image):
        for line in lines:
            rho, theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))

            cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 1)
        return image

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'loc_output_mode')


def register():
    cv_register_class(OCVLHoughLinesNode)


def unregister():
    cv_unregister_class(OCVLHoughLinesNode)