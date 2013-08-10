##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.pres import js
from larch.pres.html import Html




_plain_white_vshader = """
attribute vec3 vertexPos;
attribute vec3 vertexNrm;

uniform mat4 cameraMatrix;
uniform mat4 projectionMatrix;

varying vec3 colour;


void main(void) {
	gl_Position = projectionMatrix * cameraMatrix * vec4(vertexPos, 1.0);
	colour = vec3(dot(vertexNrm, vec3(0,1,0)))*0.5+0.5;
}"""

_plain_white_fshader = """
precision mediump float;

varying vec3 colour;

void main(void) {
	gl_FragColor = vec4(colour, 1.0);
}"""



_single_texture_vshader = """
attribute vec3 vertexPos;
attribute vec3 vertexNrm;
attribute vec2 vertexTex;

uniform mat4 cameraMatrix;
uniform mat4 projectionMatrix;

varying vec3 colour;
varying vec2 texCoord;


void main(void) {
	gl_Position = projectionMatrix * cameraMatrix * vec4(vertexPos, 1.0);
	colour = vec3(dot(vertexNrm, vec3(0,1,0)))*0.5+0.5;
	texCoord = vertexTex;
}"""

_single_texture_fshader = """
precision mediump float;

uniform sampler2D sampler;

varying vec3 colour;
varying vec2 texCoord;

void main(void) {
	vec4 lighting = vec4(colour, 1.0);
	gl_FragColor = texture2D(sampler, texCoord) * lighting;
}"""


_skybox_vshader = """
attribute vec3 vertexPos;
attribute vec2 vertexTex;

uniform mat4 cameraMatrix;
uniform mat4 projectionMatrix;
uniform vec4 camPos;

varying vec2 texCoord;


void main(void) {
	gl_Position = projectionMatrix * cameraMatrix * (vec4(vertexPos + camPos.xyz, 1.0));
	texCoord = vertexTex;
}"""

_skybox_fshader = """
precision mediump float;

uniform sampler2D sampler;

varying vec2 texCoord;

void main(void) {
	gl_FragColor = texture2D(sampler, texCoord);
}"""



class Shader (object):
	def __init__(self, vs_sources, fs_sources):
		self.vs_sources = vs_sources
		self.fs_sources = fs_sources


	def __js__(self, pres_ctx, scene_js):
		return scene_js.createShader(self.vs_sources, self.fs_sources)



class Texture (object):
	def __js__(self, pres_ctx, scene_js):
		raise NotImplementedError, 'abstract'


class Texture2D (Texture):
	def __init__(self, resource):
		self.resource = resource

	def __js__(self, pres_ctx, scene_js):
		return scene_js.createTexture2D(self.resource)


class TextureCube (Texture):
	def __init__(self, resources):
		self.resources = resources

	def __js__(self, pres_ctx, scene_js):
		resources = '[' + ', '.join([rsc.build_js(pres_ctx)    for rsc in self.resources]) + ']'
		return scene_js.createTextureCube(js.JSExprSrc(resources))


class Material (object):
	def __init__(self, shader, sampler_names_to_textures=None, use_blending=False):
		if sampler_names_to_textures is None:
			sampler_names_to_textures = {}

		self.shader = shader
		self.sampler_names_to_textures = sampler_names_to_textures
		self.use_blending = use_blending


	def has_textures(self):
		return len(self.sampler_names_to_textures) > 0

	def __js__(self, pres_ctx, scene_js):
		shader_js = self.shader.__js__(pres_ctx, scene_js)
		sampler_names_to_textures_src = '{' + ', '.join(['{0}:{1}'.format(name, texture.__js__(pres_ctx, scene_js).build_js(pres_ctx))   for name, texture in self.sampler_names_to_textures.items()]) + '}'
		return scene_js.createMaterial(shader_js, js.JSExprSrc(sampler_names_to_textures_src), self.use_blending)


	__single_texture_shader = Shader([_single_texture_vshader], [_single_texture_fshader])

	@staticmethod
	def single_texture_2d(resource):
		t = Texture2D(resource)
		return Material(Material.__single_texture_shader, {'sampler': t})


Material.plain_white = Material(Shader([_plain_white_vshader], [_plain_white_fshader]))



class Entity (object):
	def __js__(self, pres_ctx, scene_js):
		raise NotImplementedError, 'abstract'


class MeshEntity (Entity):
	def __init__(self, material, vertex_attrib_names_sizes, vertices, index_buffer_modes_data):
		super(MeshEntity, self).__init__()
		if isinstance(material, Shader):
			material = Material(material)
		self.material = material
		self.vertex_attrib_names_sizes = vertex_attrib_names_sizes
		self.vertices =  vertices
		self.index_buffer_modes_data = index_buffer_modes_data

	def __js__(self, pres_ctx, scene_js):
		material_js = self.material.__js__(pres_ctx, scene_js)
		return scene_js.createLiteralMeshEntity(material_js, self.vertex_attrib_names_sizes, self.vertices, self.index_buffer_modes_data)


class UVMeshEntity (Entity):
	def __init__(self, material, data_source):
		super(UVMeshEntity, self).__init__()
		if isinstance(material, Shader):
			material = Material(material)
		self.material = material
		self.data_source = data_source

	def __js__(self, pres_ctx, scene_js):
		material_js = self.material.__js__(pres_ctx, scene_js)
		entity_js = scene_js.createUVMeshEntity(material_js)
		return self.data_source.__js__(pres_ctx, scene_js, entity_js)



class UVMeshDataSource (object):
	def __js__(self, pres_ctx, scene_js, entity_js):
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

	def __js__(self, pres_ctx, scene_js, entity_js):
		#uSegs, vSegs, closedU, closedV, vertexPositions, vertexAttribsNamesSizesData
		return entity_js.refreshUVMesh(self.u_segs, self.v_segs, self.u_closed, self.v_closed, self.vertex_positions, self.vertex_attribs_names_sizes_data)


class UVMeshDataResource (UVMeshDataSource):
	def __init__(self, resource):
		super(UVMeshDataResource, self).__init__()
		self.resource = resource

	def __js__(self, pres_ctx, scene_js, entity_js):
		return entity_js.attachResource(self.resource)


class Camera (object):
	def __js__(self, pres_ctx, scene_js):
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

	def __js__(self, pres_ctx, scene_js):
		# fovY, nearFrac, farFrac, focalPoint, orbitalRadius, azimuth, altitude
		return scene_js.createTurntableCamera(self.fov_y, self.near_frac, self.far_frac, self.focal_point, self.orbital_radius, self.azimuth, self.altitude)


class Skybox (Entity):
	def __init__(self, face_texture_resources):
		materials = [Material(Shader([_skybox_vshader], [_skybox_fshader]), {'sampler': Texture2D(tex)})   for tex in face_texture_resources]
		self.materials = materials


	def __js__(self, pres_ctx, scene_js):
		# fovY, nearFrac, farFrac, focalPoint, orbitalRadius, azimuth, altitude
		materials_src = '[' + ', '.join([mat.__js__(pres_ctx, scene_js).build_js(pres_ctx)    for mat in self.materials]) + ']'
		return scene_js.createSkybox(js.JSExprSrc(materials_src))



class Scene (js.JS):
	def __init__(self, camera, entities):
		self.camera = camera
		self.entities = entities


	def build_js(self, pres_ctx):
		js_src = """
		(function(canvas) {{
			var scene = webglscene(canvas);
			scene.setCamera({0});
			{1}
		}})(node);
		"""
		scene_js = js.JSName('scene')
		camera_src = self.camera.__js__(pres_ctx, scene_js).build_js(pres_ctx)
		entities_jss = [scene_js.addEntity(entity.__js__(pres_ctx, scene_js))   for entity in self.entities]
		entities_src = ''.join([entity_js.build_js(pres_ctx) + '\n'   for entity_js in entities_jss])
		apply_src = js_src.format(camera_src, entities_src)
		return apply_src


def scene_canvas(width, height, scene):
	return Html('<canvas width="{0}" height="{1}"></canvas>'.format(width, height)).js_eval(scene).use_js(url='/static/webglscene.js').use_js(url='/static/gl-matrix-min.js')
