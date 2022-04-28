import os
from argparse import ArgumentParser
from PIL import Image
from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade

#
# Parameters
#

rows = 1
columns = 6
duration = 1.0
imageName = 'pngegg.png'
epsilon = 0.001
timeCodesPerSecond = 120
flank = 1.0 / timeCodesPerSecond 

parser = ArgumentParser()
parser.add_argument('-r', dest='rows', default=rows, help='Number of rows of the animation strip.')
parser.add_argument('-c', dest='columns', default=columns, help='Number of columns of the animation strip.')
parser.add_argument('-d', dest='duration', default=duration, help='Duration in seconds.')
parser.add_argument('-i', dest='imageName', default=imageName, help='Use another image beside the included animation strip.')
parser.add_argument('-t', dest='timeCodesPerSecond', default=timeCodesPerSecond, help='Number of frames used per second.')
parser.add_argument('-f', dest='flank', default=flank, help='Value used to simulate a step interpolation.')
args = parser.parse_args()

rows = args.rows
columns = args.columns
duration = duration
imageName = args.imageName
timeCodesPerSecond = args.timeCodesPerSecond
flank = args.flank

# Depending calculations

clips = rows * columns
columnsStep = 1.0 / float(columns)
rowsStep = 1.0 / float(rows)

frameStep = (duration * timeCodesPerSecond) / clips

endTimeCode = (frameStep * clips) - flank

#
# Image conversion
#

image = Image.open(imageName)
width, height = image.size

rgbImage = image.convert('RGB')
for y in range(1, height):
    for x in range(1 , width):
        pixel = rgbImage.getpixel((x,y))
        modify = list(pixel)
        for c in range(3):
            modify[c] = int(pow(modify[c]/255.0, 2.2) * 255.0) 
        rgbImage.putpixel((x,y), tuple(modify))
rgbImage.save('0/image0_lin.jpg')

for y in range(1, height):
    for x in range(1 , width):
        pixel = image.getpixel((x,y))
        modify = list(pixel)
        for c in range(3):
            modify[c] = 0 
        image.putpixel((x,y), tuple(modify))
image.save('0/image0_unlit_a.png') 

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

scene0.AddScaleOp().Set(Gf.Vec3d(1.0, 1.0, 1.0))

#
# Node
#

node0.AddTransformOp().Set(Gf.Matrix4d((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))

for i in range(clips):
    nodeName = "node" + str(i + 1)
    currentNode = UsdGeom.Xform.Define(stage, '/untitled/scene0/node0/' + nodeName)
    
    scale = currentNode.AddScaleOp()
    for k in range(clips + 1):
        timeStamp = k * frameStep
        scaleValue = (epsilon, epsilon, epsilon)
        if i == k:
            if k > 0:
                scale.Set(time = timeStamp - flank, value = (epsilon, epsilon, epsilon))
            scaleValue = (1.0, 1.0, 1.0)
        scale.Set(time = timeStamp, value = scaleValue)
        if i == k:
            timeStamp = (k + 1) * frameStep
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
    
    texCoords = currentMesh.CreatePrimvar("st0", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.vertex)
    
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

UsdGeom.SetStageMetersPerUnit(stage, 0.1)

#
# Saving
#

stage.GetRootLayer().Save()

# Convert

os.system("usdcat untitled.usda -o untitled.usdc")

# Pack

os.system("usdzip -r untitled.usdz 0 untitled.usdc")
print("Info: Saved USDZ 'untitled.usdz'")
