import os

from pxr import Usd, UsdGeom, UsdShade

stage = Usd.Stage.CreateNew('untitled.usda')

#

untitled = UsdGeom.Xform.Define(stage, '/untitled')

scope = UsdGeom.Scope.Define(stage, '/untitled/Materials')

# Material

material = UsdShade.Material.Define(stage, '/untitled/Materials/material0')

# Shaders

pbr_shader = UsdShade.Shader.Define(stage, '/untitled/Materials/material0/pbr_shader')

uvset0 = UsdShade.Shader.Define(stage, '/untitled/Materials/material0/uvset0')

tex_emissive = UsdShade.Shader.Define(stage, '/untitled/Materials/material0/tex_emissive')

tex_opacity = UsdShade.Shader.Define(stage, '/untitled/Materials/material0/tex_opacity')

# Stage settings

prim = stage.GetPrimAtPath('/untitled')
stage.SetDefaultPrim(prim)

stage.SetStartTimeCode(0.0)
stage.SetEndTimeCode(143.5)
stage.SetTimeCodesPerSecond(120.0)

stage.SetMetadata('upAxis', 'Y')

# Saving

stage.GetRootLayer().Save()

# Convert

os.system("usdcat untitled.usda -o untitled.usdc")

# Pack

os.system("usdzip -r untitled.usdz 0 untitled.usdc")
print("Info: Saved USDZ 'untitled.usdz'")
