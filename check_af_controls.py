#!/usr/bin/env python3
"""
Camera Module 3 WideのAFコントロール利用可能性を詳細チェック
"""

from picamera2 import Picamera2
from libcamera import controls
import time

print("=" * 60)
print("Camera Module 3 Wide AF Controls Check")
print("=" * 60)

# Picamera2初期化
picam2 = Picamera2()

# カメラコントロールを詳細表示
print("\n1. ALL Available Controls:")
print("-" * 40)
all_controls = picam2.camera_controls
for name, value in sorted(all_controls.items()):
    print(f"  {name}: {value}")

print("\n2. AF-Related Controls Only:")
print("-" * 40)
af_keywords = ['Af', 'af', 'Lens', 'lens', 'Focus', 'focus']
af_controls_found = {}
for name, value in all_controls.items():
    if any(keyword in name for keyword in af_keywords):
        af_controls_found[name] = value
        print(f"  ✓ {name}: {value}")

if not af_controls_found:
    print("  ✗ No AF-related controls found!")

# カメラを起動してメタデータを確認
print("\n3. Starting Camera and Checking Metadata:")
print("-" * 40)
config = picam2.create_preview_configuration(
    main={"size": (1536, 864), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()
time.sleep(2)

# メタデータを取得
metadata = picam2.capture_metadata()
print("Available metadata keys:")
af_metadata = {}
for key in sorted(metadata.keys()):
    if any(keyword in key for keyword in af_keywords):
        af_metadata[key] = metadata[key]
        print(f"  ✓ {key}: {metadata[key]}")

print("\n4. Testing Control Enums:")
print("-" * 40)

# 各AFモードを試す
af_modes_to_test = [
    ("Auto", controls.AfModeEnum.Auto),
    ("Manual", controls.AfModeEnum.Manual),
    ("Continuous", controls.AfModeEnum.Continuous),
]

for mode_name, mode_enum in af_modes_to_test:
    try:
        print(f"\nTesting AfMode={mode_name}...")
        picam2.set_controls({"AfMode": mode_enum})
        time.sleep(0.5)
        metadata = picam2.capture_metadata()
        af_mode = metadata.get("AfMode", "Not in metadata")
        af_state = metadata.get("AfState", "Not in metadata")
        lens_pos = metadata.get("LensPosition", "Not in metadata")
        print(f"  Set successful")
        print(f"  AfMode in metadata: {af_mode}")
        print(f"  AfState: {af_state}")
        print(f"  LensPosition: {lens_pos}")
    except Exception as e:
        print(f"  Failed: {e}")

# AfRangeのテスト
print("\n5. Testing AfRange Control:")
print("-" * 40)
af_ranges = [
    ("Normal", controls.AfRangeEnum.Normal),
    ("Macro", controls.AfRangeEnum.Macro),
    ("Full", controls.AfRangeEnum.Full),
]

for range_name, range_enum in af_ranges:
    try:
        print(f"Testing AfRange={range_name}...")
        picam2.set_controls({"AfRange": range_enum})
        time.sleep(0.5)
        print(f"  Set successful")
    except Exception as e:
        print(f"  Failed: {e}")

# AFトリガーのテスト
print("\n6. Testing AF Trigger:")
print("-" * 40)
try:
    print("Setting Auto mode and triggering AF...")
    picam2.set_controls({"AfMode": controls.AfModeEnum.Auto})
    time.sleep(0.5)
    picam2.set_controls({"AfTrigger": controls.AfTriggerEnum.Start})
    print("  Trigger sent")
    
    # AF完了を待つ
    for i in range(50):  # 5秒待つ
        metadata = picam2.capture_metadata()
        af_state = metadata.get("AfState", None)
        lens_pos = metadata.get("LensPosition", None)
        
        if af_state == controls.AfStateEnum.Focused:
            print(f"  AF SUCCESS! LensPosition: {lens_pos}")
            break
        elif af_state == controls.AfStateEnum.Failed:
            print(f"  AF FAILED! LensPosition: {lens_pos}")
            break
        
        time.sleep(0.1)
    else:
        print(f"  AF TIMEOUT! Final state: {af_state}, Position: {lens_pos}")
        
except Exception as e:
    print(f"  Failed: {e}")

# マニュアルフォーカスのテスト
print("\n7. Testing Manual Focus Control:")
print("-" * 40)
try:
    print("Setting Manual mode...")
    picam2.set_controls({"AfMode": controls.AfModeEnum.Manual})
    time.sleep(0.5)
    
    test_positions = [0.0, 2.0, 5.0, 10.0]
    for pos in test_positions:
        print(f"Setting LensPosition={pos}...")
        picam2.set_controls({"LensPosition": pos})
        time.sleep(1.0)
        metadata = picam2.capture_metadata()
        actual_pos = metadata.get("LensPosition", None)
        print(f"  Requested: {pos}, Actual: {actual_pos}")
        
        if actual_pos is not None:
            if abs(actual_pos - pos) < 0.1:
                print(f"  ✓ Position change successful")
            else:
                print(f"  ⚠ Position didn't match request")
        else:
            print(f"  ✗ No LensPosition in metadata")
            
except Exception as e:
    print(f"  Failed: {e}")

# クリーンアップ
picam2.stop()
picam2.close()

print("\n" + "=" * 60)
print("DIAGNOSIS:")
print("=" * 60)

if af_controls_found:
    if "AfMode" in af_controls_found and "LensPosition" in af_controls_found:
        print("✓ Camera appears to support autofocus controls")
        if "AfRange" not in af_controls_found:
            print("⚠ AfRange control not available - may need different approach")
    else:
        print("✗ Critical AF controls missing")
else:
    print("✗ No AF controls found - camera may not support autofocus")
    print("  This could indicate:")
    print("  1. Fixed focus camera module")
    print("  2. Missing driver support")
    print("  3. Firmware issues")

print("\nRECOMMENDATIONS:")
if "LensPosition" in af_controls_found:
    print("• Manual focus control should work")
    print("• Try: --focus-mode manual --focus-distance 20")
else:
    print("• Camera may be fixed focus")
    print("• Physical distance adjustment may be only option")