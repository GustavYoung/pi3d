import re, os
from pi3d import *
from pi3d.loader.parse_mtl import parse_mtl
from pi3d.shape.Shape import Shape
from pi3d.Texture import Texture
from pi3d.Buffer import Buffer

#########################################################################################
#
# this block added by paddy gaunt 22 August 2012
# Copyright (c) Paddy Gaunt, 2012
# Chunks of this code are based on https://github.com/mrdoob/three.js/ by
# AlteredQualia http://alteredqualia.com
#
#########################################################################################


#########################################################################################
def parse_vertex(text):
  """Parse text chunk specifying single vertex.

  Possible formats:
    vertex index
    vertex index / texture index
    vertex index / texture index / normal index
    vertex index / / normal index
  """

  v = 0
  t = 0
  n = 0

  chunks = text.split("/")

  v = int(chunks[0])
  if len(chunks) > 1:
    if chunks[1]:
      t = int(chunks[1])
  if len(chunks) > 2:
    if chunks[2]:
      n = int(chunks[2])

  return { 'v':v, 't':t, 'n':n }

#########################################################################################
def loadFileOBJ(model, fileName):
  model.coordinateSystem = "Y-up"
  model.parent = None
  model.childModel = [] # don't really need parent and child pointers but will speed up traversing tree
  model.vNormal = False
  model.vGroup = {} # holds the information for each vertex group

  # read in the file and parse into some arrays

  filePath = os.path.split(os.path.abspath(fileName))[0]
  print filePath
  f = open(fileName, 'r')

  vertices = []
  normals = []
  uvs = []

  faces = {}

  materials = {}
  material = ""
  mcounter = 0
  mcurrent = 0
  numv = [] #number of vertices for each material (nb each vertex will have three coords)
  numi = [] #number of indices (triangle corners) for each material

  mtllib = ""

  # current face state
  group = 0
  object = 0
  smooth = 0

  for l in f:
    chunks = l.split()
    if len(chunks) > 0:

      # Vertices as (x,y,z) coordinates
      # v 0.123 0.234 0.345
      if chunks[0] == "v" and len(chunks) == 4:
        x = float(chunks[1])
        y = float(chunks[2])
        z = float(chunks[3])
        vertices.append((x,y,z))

      # Normals in (x,y,z) form; normals might not be unit
      # vn 0.707 0.000 0.707
      if chunks[0] == "vn" and len(chunks) == 4:
        x = float(chunks[1])
        y = float(chunks[2])
        z = float(chunks[3])
        normals.append((x,y,z))

      # Texture coordinates in (u,v)
      # vt 0.500 -1.352
      if chunks[0] == "vt" and len(chunks) >= 3:
        u = float(chunks[1])
        v = float(chunks[2])
        uvs.append((u,v))

      # Face
      if chunks[0] == "f" and len(chunks) >= 4:
        vertex_index = []
        uv_index = []
        normal_index = []


        # Precompute vert / normal / uv lists
        # for negative index lookup
        vertlen = len(vertices) + 1
        normlen = len(normals) + 1
        uvlen = len(uvs) + 1

        if len(numv) < (mcurrent+1): numv.append(0)
        if len(numi) < (mcurrent+1): numi.append(0)

        for v in chunks[1:]:
          numv[mcurrent] += 1
          numi[mcurrent] += 3
          vertex = parse_vertex(v)
          if vertex['v']:
            if vertex['v'] < 0:
              vertex['v'] += vertlen
            vertex_index.append(vertex['v'])
          if vertex['t']:
            if vertex['t'] < 0:
              vertex['t'] += uvlen
            uv_index.append(vertex['t'])
          if vertex['n']:
            if vertex['n'] < 0:
              vertex['n'] += normlen
            normal_index.append(vertex['n'])
        numi[mcurrent] -= 6 # number of corners of triangle = (n-2)*3 where n is the number of corners of face
        if not mcurrent in faces: faces[mcurrent] = []

        faces[mcurrent].append({
          'vertex':vertex_index,
          'uv':uv_index,
          'normal':normal_index,

          'group':group,
          'object':object,
          'smooth':smooth,
          })

      # Group
      if chunks[0] == "g" and len(chunks) == 2:
        group = chunks[1]

      # Object
      if chunks[0] == "o" and len(chunks) == 2:
        object = chunks[1]

      # Materials definition
      if chunks[0] == "mtllib" and len(chunks) == 2:
        mtllib = chunks[1]

      # Material
      if chunks[0] == "usemtl":
        if len(chunks) > 1:
          material = chunks[1]
        else:
          material = ""
        if not material in materials:
          mcurrent = mcounter
          materials[material] = mcounter
          mcounter += 1
        else:
          mcurrent = materials[material]

      # Smooth shading
      if chunks[0] == "s" and len(chunks) == 2:
        smooth = chunks[1]
  if VERBOSE:
    print "materials:  ", materials
    print "numv: ", numv

  for g in faces:
    numv[g] -= 1
    numi[g] -= 1
    
    g_vertices = []
    g_normals = []
    g_tex_coords = []
    g_indices = []
    i = 0 # vertex counter in this material
    j = 0 # triangle vertex count in this material
    if VERBOSE:
      print "len uv=",len(vertices)
    for f in faces[g]:
      iStart = i
      for v in range(len(f['vertex'])):
        g_vertices.append(vertices[f['vertex'][v]-1])
        g_normals.append(normals[f['normal'][v]-1])
        if (len(f['uv']) > 0 and len(uvs[f['uv'][v]-1]) == 2):
          g_tex_coords.append(uvs[f['uv'][v]-1])
        i += 1
      n = i - iStart - 1
      for t in range(1,n):
        g_indices.append((iStart, iStart + t, iStart + t +1))

    model.buf.append(Buffer(model, g_vertices, g_tex_coords, g_indices, g_normals))
    n = len(model.buf) - 1
    model.vGroup[g] = n

    model.buf[n].indicesLen = len(model.buf[n].indices)
    model.buf[n].material = (0.0, 0.0, 0.0, 0.0)
    model.buf[n].ttype = GL_TRIANGLES


    #for i in range(len(model.vGroup[g].normals)):
    #  print model.vGroup[g].normals[i],
    if VERBOSE:
      print
      print "indices=",len(model.buf[n].indices)
      print "vertices=",len(model.buf[n].vertices)
      print "normals=",len(model.buf[n].normals)
      print "tex_coords=",len(model.buf[n].tex_coords)

  material_lib = parse_mtl(open(os.path.join(filePath, mtllib), 'r'))
  for m in materials:
    if VERBOSE:
      print m
    if 'mapDiffuse' in material_lib[m]:
      tfileName = material_lib[m]['mapDiffuse']
      model.buf[model.vGroup[materials[m]]].texFile = tfileName
      model.buf[model.vGroup[materials[m]]].textures = [Texture(os.path.join(filePath, tfileName), False, True)] # load from file
    else:
      model.buf[model.vGroup[materials[m]]].texFile = None
      model.buf[model.vGroup[materials[m]]].textures = []
      if 'colorDiffuse' in material_lib[m]:#TODO don't create this array if texture being used though not exclusive.
      #TODO check this works with appropriate mtl file
        redVal = material_lib[m]['colorDiffuse'][0]
        grnVal = material_lib[m]['colorDiffuse'][1]
        bluVal = material_lib[m]['colorDiffuse'][2]
        model.buf[model.vGroup[materials[m]]].material = (redVal, grnVal, bluVal, 1.0)


