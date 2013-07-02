##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import json

from britefury.pres.pres import JS
from britefury.pres.html import Html





class Shader (object):
	def __init__(self, vs_source, fs_source):
		self.vs_source = vs_source
		self.fs_source = fs_source


	def __js__(self, pres_ctx, scene):
		return '{0}.createShader({1}, {2})'.format(scene, json.dumps(self.vs_source), json.dumps(self.fs_source))



class Entity (object):
	def __init__(self, shader):
		self.shader = shader

	def __js__(self, pres_ctx, scene):
		raise NotImplementedError, 'abstract'


class MeshEntity (Entity):
	def __init__(self, shader, vertex_attrib_names_sizes, vertices, index_buffer_modes_data):
		super(MeshEntity, self).__init__(shader)
		self.vertex_attrib_names_sizes = vertex_attrib_names_sizes
		self.vertices =  vertices
		self.index_buffer_modes_data = index_buffer_modes_data

	def __js__(self, pres_ctx, scene):
		shader = self.shader.__js__(pres_ctx, scene)
		vertex_attrib_names_sizes = json.dumps(self.vertex_attrib_names_sizes)
		vertices = json.dumps(self.vertices)
		index_buffer_modes_data = json.dumps(self.index_buffer_modes_data)
		return '{0}.createLiteralMeshEntity({1}, {2}, {3}, {4})'.format(scene, shader, vertex_attrib_names_sizes, vertices, index_buffer_modes_data)


class UVMeshEntity (Entity):
	def __init__(self, shader, data_source):
		super(UVMeshEntity, self).__init__(shader)
		self.data_source = data_source

	def __js__(self, pres_ctx, scene):
		shader = self.shader.__js__(pres_ctx, scene)
		entity = '{0}.createUVMeshEntity({1})'.format(scene, shader)
		return self.data_source.__js__(pres_ctx, scene, entity)



class UVMeshDataSource (object):
	def __js__(self, pres_ctx, scene, entity):
		raise NotImplementedError, 'abstract'


class UVMeshDataLiteral (UVMeshDataSource):
	def __init__(self, u_segs, v_segs, u_closed, v_closed, vertex_positions, vertex_attribs_names_sizes_data):
		super(UVMeshDataLiteral, self).__init__()
		self.u_segs = u_segs
		self.v_segs = v_segs
		self.u_closed = u_closed
		self.v_closed = v_closed
		self.vertex_positions = vertex_positions
		self.vertex_attribs_names_sizes_data = vertex_attribs_names_sizes_data

	def __js__(self, pres_ctx, scene, entity):
		u_segs = json.dumps(self.u_segs)
		v_segs = json.dumps(self.v_segs)
		u_closed = json.dumps(self.u_closed)
		v_closed = json.dumps(self.v_closed)
		vertex_positions = json.dumps(self.vertex_positions)
		vertex_attribs_names_sizes_data = json.dumps(self.vertex_attribs_names_sizes_data)
		#uSegs, vSegs, closedU, closedV, vertexPositions, vertexAttribsNamesSizesData
		return '{0}.refreshUVMesh({1}, {2}, {3}, {4}, {5}, {6})'.format(entity, u_segs, v_segs, u_closed, v_closed, vertex_positions, vertex_attribs_names_sizes_data)


class UVMeshDataResource (UVMeshDataSource):
	def __init__(self, resource):
		super(UVMeshDataResource, self).__init__()
		self.resource = resource

	def __js__(self, pres_ctx, scene, entity):
		resource = self.resource.build_js(pres_ctx)
		return '{0}.attachResource({1})'.format(entity, resource)


class Camera (object):
	def __js__(self, pres_ctx, scene):
		raise NotImplementedError, 'abstract'



class TurntableCamera (Camera):
	def __init__(self, fov_y, near_frac, far_frac, focal_point, orbital_radius, azimuth, altitude):
		self.fov_y = fov_y
		self.near_frac = near_frac
		self.far_frac = far_frac
		self.focal_point = focal_point
		self.orbital_radius = orbital_radius
		self.azimuth = azimuth
		self.altitude = altitude

	def __js__(self, pres_ctx, scene):
		# fovY, nearFrac, farFrac, focalPoint, orbitalRadius, azimuth, altitude
		fov_y = json.dumps(self.fov_y)
		near_frac = json.dumps(self.near_frac)
		far_frac = json.dumps(self.far_frac)
		focal_point = json.dumps(self.focal_point)
		orbital_radius = json.dumps(self.orbital_radius)
		azimuth = json.dumps(self.azimuth)
		altitude = json.dumps(self.altitude)
		return '{0}.createTurntableCamera({1}, {2}, {3}, {4}, {5}, {6}, {7})'.format(scene, fov_y, near_frac, far_frac, focal_point, orbital_radius, azimuth, altitude)



class Scene (JS):
	def __init__(self, camera, entities):
		self.camera = camera
		self.entities = entities


	def __js__(self, pres_ctx):
		js_src = """
		(function(canvas) {{
			var scene = webglscene(canvas);
			scene.setCamera({0});
			{1}
			scene.redraw();
		}})(node);
		"""
		camera = self.camera.__js__(pres_ctx, 'scene')
		entities = ['scene.addEntity({0});\n'.format(entity.__js__(pres_ctx, 'scene'))   for entity in self.entities]
		return js_src.format(camera, ''.join(entities))

	def build_js(self, pres_ctx):
		return self.__js__(pres_ctx)


def scene_canvas(width, height, scene):
	return Html('<canvas width="{0}" height="{1}"></canvas>'.format(width, height)).js_eval(scene)
