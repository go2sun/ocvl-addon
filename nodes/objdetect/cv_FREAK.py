import bpy
import cv2
from ocvl.core.globals import FEATURE2D_INSTANCES_DICT
from ocvl.core.node_base import OCVLNodeBase, update_node
from ocvl.nodes.objdetect.abc_Feature2D import OCVLFeature2DCalculatorDMixIn
from ocvl.operatores.abc import OCVL_OT_InitFeature2DOperator


class OCVLFREAKNode(OCVLFeature2DCalculatorDMixIn, OCVLNodeBase):

    n_doc = "Class implementing the FREAK (Fast Retina Keypoint) keypoint descriptor, described in [4]."
    _init_method = cv2.xfeatures2d.FREAK_create

    def update_and_init(self, context):
        OCVL_OT_InitFeature2DOperator.update_class_instance_dict(self, self.id_data.name, self.name)
        self.update_sockets(context)
        update_node(self, context)

    orientationNormalized_init: bpy.props.BoolProperty(default=True, update=update_and_init, description="")
    scaleNormalized_init: bpy.props.BoolProperty(default=True, update=update_and_init, description="")
    patternScale_init: bpy.props.FloatProperty(default=22.0, min=0, max=100, update=update_and_init, description="")
    nOctaves_init: bpy.props.IntProperty(default=4, min=1, max=10, update=update_and_init, description="")

    def init(self, context):
        super().init(context)

    def wrapped_process(self):
        instance = FEATURE2D_INSTANCES_DICT.get("{}.{}".format(self.id_data.name, self.name))

        if self.loc_work_mode == "DETECT":
            self._detect(instance)
        elif self.loc_work_mode == "COMPUTE":
            self._compute(instance)
        elif self.loc_work_mode == "DETECT-COMPUTE":
            self._detect_and_compute(instance)
