#!/usr/bin/env python3
"""
Simple camera test using Picamera2 for Raspberry Pi Camera Module 3
Tests basic camera functionality with Picamera2 library
"""

import time
import sys

try:
    from picamera2 import Picamera2
    import cv2
    import numpy as np
except ImportError as e:
    print(f"Error: Required library not found: {e}")
    print("Please install picamera2: sudo apt install python3-picamera2")
    sys.exit(1)

def test_camera():
    """Test camera with Picamera2"""
    print("Initializing Picamera2...")
    
    try:
        # Initialize Picamera2
        picam2 = Picamera2()
        
        # Configure camera
        config = picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        picam2.configure(config)
        
        print("Starting camera...")
        picam2.start()
        
        # Give camera time to warm up
        time.sleep(2)
        
        print("Capturing frames... Press Ctrl+C to stop")
        frame_count = 0
        
        while True:
            # Capture frame
            frame = picam2.capture_array()
            frame_count += 1
            
            if frame is not None:
                print(f"Frame {frame_count}: Shape={frame.shape}, dtype={frame.dtype}")
                
                # Display frame using OpenCV
                cv2.imshow("Camera Test", frame)
                
                # Exit on 'q' key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Exiting...")
                    break
            else:
                print(f"Warning: Failed to capture frame {frame_count}")
            
            # Limit frame rate for testing
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        print("Cleaning up...")
        try:
            picam2.stop()
            picam2.close()
        except:
            pass
        cv2.destroyAllWindows()
        print("Done")

if __name__ == "__main__":
    test_camera()