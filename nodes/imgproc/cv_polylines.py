import cv2
import uuid
from gettext import gettext as _
from bpy.props import EnumProperty, StringProperty, IntProperty, FloatVectorProperty, BoolProperty

from ...utils import cv_register_class, cv_unregister_class, OCVLNode, updateNode, LINE_TYPE_ITEMS


class OCVLpolylinesNode(OCVLNode):
    bl_icon = 'GREASEPENCIL'

    _doc = _("Draws several polygonal curves.")

    image_in = StringProperty(name="image_in", default=str(uuid.uuid4()),
        description=_("Input image."))
    image_out = StringProperty(name="image_out", default=str(uuid.uuid4()),
        description=_("Output image."))

    pts_in = StringProperty(default=str(uuid.uuid4()), update=updateNode,
        description=_("Array of polygonal curves."))
    isClosed_in = BoolProperty(default=False, update=updateNode,
        description=_("Flag indicating whether the drawn polylines are closed or not. If they are closed, the function draws a line from the last vertex of each curve to its first vertex."))
    color_in = FloatVectorProperty(update=updateNode, default=(.7, .7, .1, 1.0), size=4, min=0.0, max=1.0, subtype='COLOR',
        description=_("Polyline color."))
    thickness_in = IntProperty(default=2, min=1, max=10, update=updateNode,
        description=_("Thickness of the polyline edges."))
    lineType_in = EnumProperty(items=LINE_TYPE_ITEMS, default="LINE_AA", update=updateNode,
        description=_("Type of the line segments. See the line description."))
    shift_in = IntProperty(default=0, min=0, max=100, update=updateNode,
        description=_("Number of fractional bits in the vertex coordinates."))

    def sv_init(self, context):
        self.width = 150
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new('StringsSocket', "pts_in")
        self.inputs.new('StringsSocket', "thickness_in").prop_name = 'thickness_in'
        self.inputs.new('StringsSocket', "shift_in").prop_name = 'shift_in'
        self.inputs.new('SvColorSocket', 'color_in').prop_name = 'color_in'

        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in", "pts_in"])

        kwargs = {
            'img_in': self.get_from_props("image_in"),
            'pts_in': [self.get_from_props("pts_in")],
            'isClosed_in': self.get_from_props("isClosed_in"),
            'color_in': self.get_from_props("color_in"),
            'thickness_in': self.get_from_props("thickness_in"),
            'lineType_in': self.get_from_props("lineType_in"),
            'shift_in': self.get_from_props("shift_in"),
            }

        image_out = self.process_cv(fn=cv2.polylines, kwargs=kwargs)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'lineType_in')
        self.add_button(layout, 'isClosed_in')


def register():
    cv_register_class(OCVLpolylinesNode)


def unregister():
    cv_unregister_class(OCVLpolylinesNode)
