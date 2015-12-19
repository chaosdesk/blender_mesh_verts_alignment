############################################################################
#
# mesh_verts_alignemnt.py
#
# Copyright (C) 2015 chaosdesk
# 
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.#
#
# ##### END GPL LICENSE BLOCK #####
#
############################################################################

bl_info = {
    'name': 'Verts Alignment',
    'author': 'chaosdesk',
    'version': (1,0),
    'blender': (2, 7, 5),
    "location": "View3D > UV Mapping > Verts Alignment",
    'description': 'Project from average normal of all Face',
    'warning': '',
    'wiki_url': '',
    'tracker_url': 'http://chaos-junction.tumblr.com/',
    "category": "Mesh"}


import bpy
import bisect
import itertools
import math
import mathutils
from mathutils import Vector, Matrix


class AlignVertices(object):
    def __init__(self):
        self.mesh = bpy.context.selected_objects[0].data
        self.selected_verts = [v for v in self.mesh.vertices if v.select]
        self.sorted_edge_keys = sorted(self.mesh.edge_keys)
        
    def exec_alignment(self):
        tverts = self.get_terminated_verts()
        if tverts.__len__() != 2:
            print("Please select each connected vetices.")
            return
        
        base_unitvector = self.get_vector(tverts[0].co, tverts[1].co).normalized()
        for svert in self.selected_verts:
            if svert in tverts:
                continue
            cvert = self.correction_coord(svert, tverts[0], base_unitvector)
            svert.co[0] = cvert[0]
            svert.co[1] = cvert[1]
            svert.co[2] = cvert[2]

    def get_terminated_verts(self):
        tverts = []
        exist_count = []  # corresponding selected_verts
        pgroup = list(itertools.combinations(self.selected_verts, 2))

        for cnt in range(0, len(self.selected_verts)):
            exist_count.append(0)

        for pair in pgroup:
            if self.find_edge(pair) == False:
                continue
            exist_count[self.selected_verts.index(pair[0])] += 1
            exist_count[self.selected_verts.index(pair[1])] += 1

        for cnt in range(0, len(self.selected_verts)):
            if exist_count[cnt] == 1:
                tverts.append(self.selected_verts[cnt])
        return tverts

    def find_edge(self, pair):
        v1 = pair[0].index
        v2 = pair[1].index
        for key_item in [(v1, v2), (v2, v1)]:
            idx = bisect.bisect_left(self.sorted_edge_keys, key_item)
            if idx != len(self.sorted_edge_keys) and \
                self.sorted_edge_keys[idx] == key_item:
                find_flag = True
                break
            else:
                find_flag = False
        return find_flag

    def get_vector(self, vco_to, vco_frm):
        vector = Vector((vco_to[0] - vco_frm[0],
                         vco_to[1] - vco_frm[1],
                         vco_to[2] - vco_frm[2]))
        return vector

    def correction_coord(self, vert, base_vert, base_unitvector):
        vector_a = self.get_vector(vert.co, base_vert.co)
        cos_angle = math.cos(vector_a.angle(base_unitvector))
        scale = (vector_a.length*cos_angle) / base_unitvector.length
        correct_vector = scale * base_unitvector
        
        cvert = [correct_vector[0] + base_vert.co[0],
                 correct_vector[1] + base_vert.co[1],
                 correct_vector[2] + base_vert.co[2]]
        return cvert


class VertsAlignment(bpy.types.Operator):
    """Verts Alignment"""  
    bl_idname  = "mesh.verts_alignment"  
    bl_label   = "Verts Alignment"
    bl_options = {'REGISTER', 'UNDO'}
          
    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT') 
        avertices = AlignVertices()
        avertices.exec_alignment()
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}


def menu_func(self, context):
    #self.layout.separator()
    self.layout.operator("mesh.verts_alignment", 
                         text="Verts Alignment", 
                         icon='PLUGIN')

def register():
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_MT_edit_mesh_edges.append(menu_func)
               
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.VIEW3D_MT_edit_mesh_edges.remove(menu_func)

if __name__ == '__main__':
    register()
