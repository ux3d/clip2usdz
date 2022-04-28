import os

from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade

#
# Parameters
#

rows = 1
columns = 6
fps = 6.0
epsilon = 0.001
sampling = 5.0
flank = 0.5

clips = rows * columns
columnsStep = 1.0 / float(columns)
rowsStep = 1.0 / float(rows)

timeCodesPerSecond = fps * sampling
endTimeCode = clips * timeCodesPerSecond 

# 
# Stage
#

stage = Usd.Stage.CreateNew('untitled.usda')

#

untitled = UsdGeom.Xform.Define(stage, '/untitled')

scope = UsdGeom.Scope.Define(stage, '/untitled/Materials')

scene0 = UsdGeom.Xform.Define(stage, '/untitled/scene0')

node0 = UsdGeom.Xform.Define(stage, '/untitled/scene0/node0')

#
# Material
#

material = UsdShade.Material.Define(stage, '/untitled/Materials/material0')

#
# Shaders
#

uvset0 = UsdShade.Shader.Define(stage, '/untitled/Materials/material0/uvset0')

uvset0.CreateIdAttr("UsdPrimvarReader_float2")
uvset0.CreateInput('varname', Sdf.ValueTypeNames.Token).Set('st0')

#

tex_emissive = UsdShade.Shader.Define(stage, '/untitled/Materials/material0/tex_emissive')

tex_emissive.CreateIdAttr("UsdUVTexture")
tex_emissive.CreateInput('file', Sdf.ValueTypeNames.Asset).Set("0/image0_lin.jpg")
tex_emissive.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(uvset0.ConnectableAPI(), 'result')
tex_emissive.CreateInput("wrapS", Sdf.ValueTypeNames.Token).Set("clamp")
tex_emissive.CreateInput("wrapT", Sdf.ValueTypeNames.Token).Set("clamp")

#

tex_opacity = UsdShade.Shader.Define(stage, '/untitled/Materials/material0/tex_opacity')

tex_opacity.CreateIdAttr("UsdUVTexture")
tex_opacity.CreateInput('file', Sdf.ValueTypeNames.Asset).Set("0/image0_unlit_a.png")
tex_opacity.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(uvset0.ConnectableAPI(), 'result')
tex_opacity.CreateInput("wrapS", Sdf.ValueTypeNames.Token).Set("clamp")
tex_opacity.CreateInput("wrapT", Sdf.ValueTypeNames.Token).Set("clamp")

#

pbr_shader = UsdShade.Shader.Define(stage, '/untitled/Materials/material0/pbr_shader')

pbr_shader.CreateIdAttr("UsdPreviewSurface")
pbr_shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
pbr_shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(1.0)
pbr_shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(tex_opacity.ConnectableAPI(), 'rgb')
pbr_shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).ConnectToSource(tex_opacity.ConnectableAPI(), 'a')
pbr_shader.CreateInput("emissiveColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(tex_emissive.ConnectableAPI(), 'rgb')

material.CreateSurfaceOutput().ConnectToSource(pbr_shader.ConnectableAPI(), "surface")

#
# Scene
#

scene0.AddScaleOp().Set(Gf.Vec3d(100.0, 100.0, 100.0))

#
# Node
#

node0.AddTransformOp().Set(Gf.Matrix4d((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))

for i in range(clips):
    nodeName = "node" + str(i + 1)
    currentNode = UsdGeom.Xform.Define(stage, '/untitled/scene0/node0/' + nodeName)
    
    scale = currentNode.AddScaleOp()
    for k in range(clips + 1):
        timeStamp = k * fps * sampling
        scaleValue = (epsilon, epsilon, epsilon)
        if i == k:
            if k > 0:
                scale.Set(time = timeStamp - flank, value = (epsilon, epsilon, epsilon))
            scaleValue = (1.0, 1.0, 1.0)
        scale.Set(time = timeStamp, value = scaleValue)
        if i == k:
            timeStamp = (k + 1) * fps * sampling
            scale.Set(time = timeStamp - flank, value = scaleValue)
    
    # Mesh
    
    meshName = "mesh" + str(i)
    currentMesh = UsdGeom.Mesh.Define(stage, '/untitled/scene0/node0/' + nodeName + '/' + meshName)
    currentMesh.CreateDoubleSidedAttr(1)
    currentMesh.CreateExtentAttr([(-1, 0, -1), (1, 0, 1)])
    currentMesh.CreateFaceVertexCountsAttr([3, 3])
    currentMesh.CreateFaceVertexIndicesAttr([0, 1, 2, 3, 2, 1])
    
    currentMesh.CreateNormalsAttr([(0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0)])
    currentMesh.SetNormalsInterpolation('vertex')
    
    currentMesh.CreatePointsAttr([(-1, 0, -1), (-1, 0, 1), (1, 0, -1), (1, 0, 1)])
    
    texCoords = currentMesh.CreatePrimvar("st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.vertex)
    
    column = i % columns
    row = i // columns
     
    uv = []
    uv.append( (columnsStep * float(column + 0), rowsStep * float(row + 1)) )
    uv.append( (columnsStep * float(column + 0), rowsStep * float(row + 0)) )
    uv.append( (columnsStep * float(column + 1), rowsStep * float(row + 1)) )
    uv.append( (columnsStep * float(column + 1), rowsStep * float(row + 0)) )
    texCoords.Set(uv)
    
    currentMesh.CreateSubdivisionSchemeAttr('none')        
    
    UsdShade.MaterialBindingAPI(currentMesh).Bind(material)
    
#
# Stage settings
#

prim = stage.GetPrimAtPath('/untitled')
stage.SetDefaultPrim(prim)

stage.SetStartTimeCode(0.0)
stage.SetEndTimeCode(endTimeCode)
stage.SetTimeCodesPerSecond(timeCodesPerSecond)

stage.SetMetadata('upAxis', 'Y')

#
# Saving
#

stage.GetRootLayer().Save()

# Convert

os.system("usdcat untitled.usda -o untitled.usdc")

# Pack

os.system("usdzip -r untitled.usdz 0 untitled.usdc")
print("Info: Saved USDZ 'untitled.usdz'")
