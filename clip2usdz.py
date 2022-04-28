import os

from pxr import Sdf, Usd, UsdGeom, UsdShade

#
# Parameters
#

endTimeCode = 143.5
timeCodesPerSecond = 120.0

# 
# Stage
#

stage = Usd.Stage.CreateNew('untitled.usda')

#

untitled = UsdGeom.Xform.Define(stage, '/untitled')

scope = UsdGeom.Scope.Define(stage, '/untitled/Materials')

#
# Material
#

material = UsdShade.Material.Define(stage, '/untitled/Materials/material0')

#
# Shaders
#

uvset0 = UsdShade.Shader.Define(stage, '/untitled/Materials/material0/uvset0')

uvset0.CreateIdAttr("UsdPrimvarReader_float2")
uvset0.CreateInput('varname',Sdf.ValueTypeNames.Token).Set('st0')

#

tex_emissive = UsdShade.Shader.Define(stage, '/untitled/Materials/material0/tex_emissive')

tex_emissive.CreateIdAttr("UsdUVTexture")
tex_emissive.CreateInput('file', Sdf.ValueTypeNames.Asset).Set("0/image0_lin.jpg")
tex_emissive.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(uvset0.ConnectableAPI(), 'result')

#

tex_opacity = UsdShade.Shader.Define(stage, '/untitled/Materials/material0/tex_opacity')

tex_opacity.CreateIdAttr("UsdUVTexture")
tex_opacity.CreateInput('file', Sdf.ValueTypeNames.Asset).Set("0/image0_unlit_a.png")
tex_opacity.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(uvset0.ConnectableAPI(), 'result')

#

pbr_shader = UsdShade.Shader.Define(stage, '/untitled/Materials/material0/pbr_shader')

pbr_shader.CreateIdAttr("UsdPreviewSurface")
pbr_shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
pbr_shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(1.0)

material.CreateSurfaceOutput().ConnectToSource(pbr_shader.ConnectableAPI(), "surface")

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
