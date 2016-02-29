import bpy
from mathutils import Vector

bl_info = {
    "name": "Set equal edge lengths.",
    "author": "Michal Krupa",
    "version": (1, 0, 0),
    "blender": (2, 70, 0),
    "location": "",
    "warning": "",
    "description": "",
    "wiki_url": "",
    "category": "Mesh",
}


def set_edge_length(mesh, edge_index, edge_length=1.0):
	"""
	Scales the edge to match the edge length provided as an argument.
	
	@param mesh: Mesh to modify edge on
	@param edge_index: Index of the edge
	@param edge_length: Final edge length
	"""
    vt1 = mesh.edges[edge_index].vertices[0]
    vt2 = mesh.edges[edge_index].vertices[1]
    center = (mesh.vertices[vt1].co + mesh.vertices[vt2].co) * .5
    
    for v in (mesh.vertices[vt1], mesh.vertices[vt2]):
        new_co = (v.co - center).normalized() * (edge_length / 2.0)
        v.co = new_co + center

class EdgeEqualizeBase(bpy.types.Operator):
    """
    Never register this class as an operator, it's a base class used to keep polymorphism.
    """
    
    
    def __init__(self):
        self.selected_edges = []
        self.edge_lengths = []
        
    def invoke(self, context, event):
        ob = context.object
        ob.update_from_editmode()

        # --- Get the mesh data
        me = ob.data
        if len(me.edges) < 1:
            self.report({'ERROR'}, "This mesh has no edges!")
            return

        # --- gather selected edges        
        self.selected_edges = [i.index for i in bpy.context.active_object.data.edges if i.select == True]

        # --- if none report an error and quit
        if not self.selected_edges:
            self.report({'ERROR'}, "You have to select some edges!")
            return
        
        # --- gather lenghts of the edges before the operator was applied
        for edge in self.selected_edges:
            vt1 = me.edges[edge].vertices[0]
            vt2 = me.edges[edge].vertices[1]
            a_to_b_vec = me.vertices[vt1].co - me.vertices[vt2].co
            self.edge_lengths.append(a_to_b_vec.length)
        
        return self.execute(context)
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH' and (obj.mode == 'EDIT'))
            
    def do_equalize(self, ob, scale=1.0):
        me = ob.data
        current_mode = ob.mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

		
        target_length = self._get_target_length()

        for edge, base_length in zip(self.selected_edges, self.edge_lengths):
            set_edge_length(me, edge, target_length * scale, base_length)
                
        bpy.ops.object.mode_set(mode=current_mode, toggle=False)
		
	def _get_target_length(self):
		"""
		Implement this method in your child classes to achieve different behaviours.
		"""
		raise NotImplementedError()
        

class EdgeEqualizeAverageOperator(EdgeEqualizeBase):
    bl_idname = "mo.edge_equalize_average"
    bl_label = "Equalize edges length to average"
    bl_options = {'REGISTER', 'UNDO'}
    
    scale = bpy.props.FloatProperty(name="Scale", default=1.0)
    
    def _get_target_length(self):
		"""
		Calculates the average length of all edges.
		"""
        if not self.edge_lengths:
            return 0.0
        return sum(self.edge_lengths) / float(len(self.selected_edges))

    def execute(self, context):
        ob = bpy.context.object
        
        if ob.type != 'MESH':
            raise TypeError("Active object is not a Mesh")

        if ob:
            self.do_equalize(ob, self.scale)
        
        return {'FINISHED'}
    
class EdgeEqualizeShortestOperator(EdgeEqualizeBase):
    bl_idname = "mo.edge_equalize_short"
    bl_label = "Equalize edges length to shortest"
    bl_options = {'REGISTER', 'UNDO'}
    
    scale = bpy.props.FloatProperty(name="Scale", default=1.0)
    
    def _get_target_length(self):
		"""
		Calculates the smallest length of all edges.
		"""
        if not self.edge_lengths:
            return 0.0
        return min(self.edge_lengths)

    def execute(self, context):
        ob = bpy.context.object
        
        if ob.type != 'MESH':
            raise TypeError("Active object is not a Mesh")
        
        if ob:
            self.do_equalize(ob, self.scale)
        
        return {'FINISHED'}
    
class EdgeEqualizeLongestOperator(EdgeEqualizeBase):
    bl_idname = "mo.edge_equalize_long"
    bl_label = "Equalize edges length to longest"
    bl_options = {'REGISTER', 'UNDO'}
    
    scale = bpy.props.FloatProperty(name="Scale", default=1.0)
    
    def _get_target_length(self):
		"""
		Calculates the biggest length of all edges.
		"""
        if not self.edge_lengths:
            return 0.0
        return max(self.edge_lengths)

    def execute(self, context):
        ob = bpy.context.object

        if ob.type != 'MESH':
            raise TypeError("Active object is not a Mesh")

        if ob:
            self.do_equalize(ob, self.scale)
        
        return {'FINISHED'}


def register():
    bpy.utils.register_class(EdgeEqualizeAverageOperator)
    bpy.utils.register_class(EdgeEqualizeShortestOperator)
    bpy.utils.register_class(EdgeEqualizeLongestOperator)

	
def unregister():
	bpy.utils.unregister_class(EdgeEqualizeAverageOperator)
	bpy.utils.unregister_class(EdgeEqualizeShortestOperator)
	bpy.utils.unregister_class(EdgeEqualizeLongestOperator)


if __name__ == "__main__":
    register()
