#!/usr/bin/env python3
"""
カメラのフォーカス機能を確認するスクリプト
"""

from picamera2 import Picamera2
from libcamera import controls
import time

print("Camera Focus Capability Check")
print("=" * 50)

# Picamera2初期化
picam2 = Picamera2()

# カメラ情報取得
camera_info = picam2.camera_properties
print("\nCamera Properties:")
for key, value in camera_info.items():
    print(f"  {key}: {value}")

# 利用可能なコントロール確認
print("\nAvailable Camera Controls:")
camera_controls = picam2.camera_controls
for control_name, control_info in camera_controls.items():
    print(f"\n  {control_name}:")
    if isinstance(control_info, tuple) and len(control_info) >= 3:
        print(f"    Min: {control_info[0]}")
        print(f"    Max: {control_info[1]}")
        print(f"    Default: {control_info[2]}")
    else:
        print(f"    {control_info}")

# フォーカス関連のコントロールを特別にチェック
print("\n" + "=" * 50)
print("Focus-related controls:")
focus_controls = ['AfMode', 'LensPosition', 'AfRange', 'AfSpeed', 'AfTrigger', 'AfState']
for control in focus_controls:
    if control in camera_controls:
        print(f"  ✓ {control}: {camera_controls[control]}")
    else:
        print(f"  ✗ {control}: Not available")

# カメラを設定して起動
print("\n" + "=" * 50)
print("Testing focus control...")
config = picam2.create_preview_configuration(
    main={"size": (1536, 864), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()

time.sleep(2)

# メタデータ取得
print("\nCapturing metadata...")
metadata = picam2.capture_metadata()
print("\nMetadata (focus-related):")
for key in metadata:
    if 'focus' in key.lower() or 'lens' in key.lower() or 'af' in key.lower():
        print(f"  {key}: {metadata[key]}")

# フォーカス制御を試す
print("\n" + "=" * 50)
print("Testing focus control...")

try:
    # オートフォーカスを試す
    print("\n1. Trying Auto focus mode...")
    picam2.set_controls({"AfMode": controls.AfModeEnum.Auto})
    time.sleep(1)
    metadata = picam2.capture_metadata()
    if 'AfState' in metadata:
        print(f"   AF State: {metadata['AfState']}")
    if 'LensPosition' in metadata:
        print(f"   Lens Position: {metadata['LensPosition']}")
    print("   Auto focus set successfully")
except Exception as e:
    print(f"   Error: {e}")

try:
    # マニュアルフォーカスを試す
    print("\n2. Trying Manual focus mode...")
    picam2.set_controls({"AfMode": controls.AfModeEnum.Manual})
    time.sleep(0.5)
    
    # 異なるレンズ位置を試す
    test_positions = [0.0, 2.0, 5.0, 8.0, 10.0]
    for pos in test_positions:
        print(f"\n   Setting LensPosition to {pos}...")
        picam2.set_controls({"LensPosition": pos})
        time.sleep(1)
        metadata = picam2.capture_metadata()
        if 'LensPosition' in metadata:
            actual_pos = metadata['LensPosition']
            print(f"   Requested: {pos}, Actual: {actual_pos}")
            if abs(actual_pos - pos) < 0.1:
                print(f"   ✓ Lens moved successfully")
            else:
                print(f"   ⚠ Lens position didn't change as expected")
        else:
            print(f"   No LensPosition in metadata")
            
except Exception as e:
    print(f"   Error: {e}")

# クリーンアップ
picam2.stop()
picam2.close()

print("\n" + "=" * 50)
print("Check complete.")
print("\nIMPORTANT NOTE:")
print("If LensPosition doesn't change or AfMode controls don't work,")
print("your camera module might be:")
print("1. A fixed-focus variant (no AF support)")
print("2. Missing AF firmware/driver support")
print("3. Camera Module 3 Wide NoIR might have different AF implementation")