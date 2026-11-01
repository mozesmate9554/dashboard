#!/usr/bin/env python3
"""Create the small Xcode project and original app icons (no Apple signing)."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/'mobile_flutter/ios'
objects=[]
def add(identifier,body): objects.append(f'\t\t{identifier} = {{ {body} }};')
files=[
 ('01','AppDelegate.swift','sourcecode.swift'),('02','GeneratedPluginRegistrant.m','sourcecode.c.objc'),
 ('03','GeneratedPluginRegistrant.h','sourcecode.c.h'),('04','Runner-Bridging-Header.h','sourcecode.c.h'),
 ('05','Info.plist','text.plist.xml'),('06','Base.lproj/Main.storyboard','file.storyboard'),
 ('07','Base.lproj/LaunchScreen.storyboard','file.storyboard'),('08','Assets.xcassets','folder.assetcatalog'),
 ('09','Runner.entitlements','text.plist.entitlements')]
def ident(suffix): return 'ABCDEF0000000000000000'+suffix
for suffix,path,kind in files:
 add(ident(suffix),f'isa = PBXFileReference; lastKnownFileType = {kind}; path = "{path}"; sourceTree = "<group>";')
for suffix in ['01','02','06','07','08']:
 add('BCDEF00000000000000000'+suffix,f'isa = PBXBuildFile; fileRef = {ident(suffix)};')
add(ident('10'),'isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = Runner.app; sourceTree = BUILT_PRODUCTS_DIR;')
add(ident('11'),'isa = PBXFileReference; lastKnownFileType = text.xcconfig; path = Debug.xcconfig; sourceTree = "<group>";')
add(ident('12'),'isa = PBXFileReference; lastKnownFileType = text.xcconfig; path = Release.xcconfig; sourceTree = "<group>";')
add(ident('13'),'isa = PBXFileReference; lastKnownFileType = text.xcconfig; path = Generated.xcconfig; sourceTree = "<group>";')
add(ident('20'),f'isa = PBXGroup; children = ({ident("21")},{ident("22")},{ident("23")}); sourceTree = "<group>";')
add(ident('21'),'isa = PBXGroup; children = ('+','.join(ident(f[0]) for f in files)+'); path = Runner; sourceTree = "<group>";')
add(ident('22'),f'isa = PBXGroup; children = ({ident("11")},{ident("12")},{ident("13")}); path = Flutter; sourceTree = "<group>";')
add(ident('23'),f'isa = PBXGroup; children = ({ident("10")}); name = Products; sourceTree = "<group>";')
add(ident('30'),'isa = PBXSourcesBuildPhase; buildActionMask = 2147483647; files = (BCDEF0000000000000000001,BCDEF0000000000000000002); runOnlyForDeploymentPostprocessing = 0;')
add(ident('31'),'isa = PBXResourcesBuildPhase; buildActionMask = 2147483647; files = (BCDEF0000000000000000006,BCDEF0000000000000000007,BCDEF0000000000000000008); runOnlyForDeploymentPostprocessing = 0;')
add(ident('32'),'isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = (); runOnlyForDeploymentPostprocessing = 0;')
for suffix,name,command in [('33','Flutter Build','build'),('34','Embed Flutter','embed_and_thin')]:
 script='"$FLUTTER_ROOT/packages/flutter_tools/bin/xcode_backend.sh" '+command
 add(ident(suffix),f'isa = PBXShellScriptBuildPhase; alwaysOutOfDate = 1; buildActionMask = 2147483647; files = (); inputPaths = (); name = "{name}"; outputPaths = (); runOnlyForDeploymentPostprocessing = 0; shellPath = /bin/sh; shellScript = '+json.dumps(script)+';')
target='97C146ED1CF9000F007C117D'
add(target,f'isa = PBXNativeTarget; buildConfigurationList = {ident("51")}; buildPhases = ({ident("33")},{ident("30")},{ident("32")},{ident("31")},{ident("34")}); buildRules = (); dependencies = (); name = Runner; productName = Runner; productReference = {ident("10")}; productType = "com.apple.product-type.application";')
project='97C146E61CF9000F007C117D'
add(project,f'isa = PBXProject; attributes = {{ LastUpgradeCheck = 1600; TargetAttributes = {{ {target} = {{ CreatedOnToolsVersion = 16.0; LastSwiftMigration = 1600; }}; }}; }}; buildConfigurationList = {ident("50")}; compatibilityVersion = "Xcode 14.0"; developmentRegion = en; hasScannedForEncodings = 0; knownRegions = (en,Base,hu); mainGroup = {ident("20")}; productRefGroup = {ident("23")}; projectDirPath = ""; projectRoot = ""; targets = ({target});')
for index,name in enumerate(['Debug','Release','Profile']):
 suffix=str(60+index)
 settings='ALWAYS_SEARCH_USER_PATHS = NO; CLANG_ENABLE_MODULES = YES; CLANG_ENABLE_OBJC_ARC = YES; ENABLE_BITCODE = NO; IPHONEOS_DEPLOYMENT_TARGET = 15.5; SDKROOT = iphoneos; TARGETED_DEVICE_FAMILY = "1,2"; ENABLE_USER_SCRIPT_SANDBOXING = NO;'
 settings+=' DEBUG_INFORMATION_FORMAT = "dwarf"; GCC_OPTIMIZATION_LEVEL = 0; ONLY_ACTIVE_ARCH = YES;' if name=='Debug' else ' DEBUG_INFORMATION_FORMAT = "dwarf-with-dsym"; SWIFT_COMPILATION_MODE = wholemodule;'
 add(ident(suffix),f'isa = XCBuildConfiguration; buildSettings = {{ {settings} }}; name = {name};')
 tsuffix=str(70+index);base=ident('11' if name=='Debug' else '12')
 settings='ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon; CLANG_ENABLE_MODULES = YES; CODE_SIGN_STYLE = Automatic; CODE_SIGN_ENTITLEMENTS = Runner/Runner.entitlements; CURRENT_PROJECT_VERSION = "$(FLUTTER_BUILD_NUMBER)"; ENABLE_BITCODE = NO; INFOPLIST_FILE = Runner/Info.plist; IPHONEOS_DEPLOYMENT_TARGET = 15.5; LD_RUNPATH_SEARCH_PATHS = ("$(inherited)","@executable_path/Frameworks"); PRODUCT_BUNDLE_IDENTIFIER = hu.simcontrol.studio; PRODUCT_NAME = "$(TARGET_NAME)"; SWIFT_OBJC_BRIDGING_HEADER = "Runner/Runner-Bridging-Header.h"; SWIFT_VERSION = 5.0; TARGETED_DEVICE_FAMILY = "1,2"; VERSIONING_SYSTEM = "apple-generic";'
 if name=='Debug':settings+=' SWIFT_OPTIMIZATION_LEVEL = "-Onone";'
 add(ident(tsuffix),f'isa = XCBuildConfiguration; baseConfigurationReference = {base}; buildSettings = {{ {settings} }}; name = {name};')
add(ident('50'),f'isa = XCConfigurationList; buildConfigurations = ({ident("60")},{ident("61")},{ident("62")}); defaultConfigurationIsVisible = 0; defaultConfigurationName = Release;')
add(ident('51'),f'isa = XCConfigurationList; buildConfigurations = ({ident("70")},{ident("71")},{ident("72")}); defaultConfigurationIsVisible = 0; defaultConfigurationName = Release;')
pbx='// !$*UTF8*$!\n{ archiveVersion = 1; classes = {}; objectVersion = 56; objects = {\n'+'\n'.join(objects)+'\n}; rootObject = '+project+'; }\n'
(ROOT/'Runner.xcodeproj/project.pbxproj').write_text(pbx)
try:
 from PIL import Image,ImageDraw
 dest=ROOT/'Runner/Assets.xcassets/AppIcon.appiconset';dest.mkdir(parents=True,exist_ok=True)
 images=[]
 for idiom,sizes,scales in [('iphone',[20,29,40,60],[2,3]),('ipad',[20,29,40,76],[1,2]),('ipad',[83.5],[2]),('ios-marketing',[1024],[1])]:
  for size in sizes:
   for scale in scales:
    px=int(size*scale);name=f'icon-{idiom}-{size}-{scale}.png'
    image=Image.new('RGB',(px,px),'#101216');draw=ImageDraw.Draw(image)
    for points in [[(35,24),(49,24),(37,84),(23,84)],[(58,24),(82,24),(70,84),(46,84)]]:
     draw.polygon([(int(x*px/108),int(y*px/108)) for x,y in points],fill='#ed3044')
    image.save(dest/name)
    images.append(dict(size=f'{size}x{size}',idiom=idiom,filename=name,scale=f'{scale}x'))
 (dest/'Contents.json').write_text(json.dumps({'images':images,'info':{'version':1,'author':'sim-control-studio'}},indent=2)+'\n')
 (dest.parent/'Contents.json').write_text('{"info":{"version":1,"author":"sim-control-studio"}}\n')
except ImportError:
 print('Pillow missing: app icons were not generated.')
print('Xcode project written; requires macOS/Xcode and actual signing/build verification.')
