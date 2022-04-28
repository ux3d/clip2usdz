from pxr import Usd, UsdGeom, UsdShade

stage = Usd.Stage.CreateNew('untitled.usda')

#

untitled = UsdGeom.Xform.Define(stage, '/untitled')

scope = UsdGeom.Scope.Define(stage, '/untitled/Materials')

material = UsdShade.Material.Define(stage, '/untitled/Materials/material0')

# Stage settings

prim = stage.GetPrimAtPath('/untitled')
stage.SetDefaultPrim(prim)

stage.SetStartTimeCode(0.0)
stage.SetEndTimeCode(143.5)
stage.SetTimeCodesPerSecond(120.0)

stage.SetMetadata('upAxis', 'Y')

# Saving

print("Info: Saved glTF 'untitled.usda'")

stage.GetRootLayer().Save()
