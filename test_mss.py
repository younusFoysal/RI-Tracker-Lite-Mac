import mss
import mss.tools
from PIL import Image
import io

# Create an instance of the mss class
with mss.mss() as sct:
    # Get information about the monitors
    print(f"Number of monitors: {len(sct.monitors)}")
    print(f"All monitors: {sct.monitors}")
    
    # Monitor 0 is the "All in One" monitor (all monitors combined)
    print(f"Monitor 0 (all monitors): {sct.monitors[0]}")
    
    # Individual monitors start from index 1
    for i, monitor in enumerate(sct.monitors[1:], 1):
        print(f"Monitor {i}: {monitor}")
        
    # Take a screenshot of all monitors combined
    all_monitors = sct.monitors[0]
    print(f"\nTaking screenshot of all monitors combined...")
    screenshot = sct.grab(all_monitors)
    
    # Save the screenshot to a file
    mss.tools.to_png(screenshot.rgb, screenshot.size, output="all_monitors.png")
    print(f"Screenshot saved to all_monitors.png")
    
    # Take screenshots of individual monitors
    for i, monitor in enumerate(sct.monitors[1:], 1):
        print(f"\nTaking screenshot of monitor {i}...")
        screenshot = sct.grab(monitor)
        
        # Save the screenshot to a file
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=f"monitor_{i}.png")
        print(f"Screenshot saved to monitor_{i}.png")
        
    # Example of how to combine multiple monitor screenshots into one image
    if len(sct.monitors) > 2:  # If there are multiple monitors
        print("\nCombining screenshots of all monitors into one image...")
        
        # Get screenshots of each monitor
        screenshots = [sct.grab(monitor) for monitor in sct.monitors[1:]]
        
        # Calculate the total width and maximum height
        total_width = sum(screenshot.width for screenshot in screenshots)
        max_height = max(screenshot.height for screenshot in screenshots)
        
        # Create a new image with the combined size
        combined_image = Image.new('RGB', (total_width, max_height))
        
        # Paste each screenshot into the combined image
        x_offset = 0
        for screenshot in screenshots:
            # Convert the screenshot to a PIL Image
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
            combined_image.paste(img, (x_offset, 0))
            x_offset += screenshot.width
        
        # Save the combined image
        combined_image.save('combined_monitors.png')
        print(f"Combined screenshot saved to combined_monitors.png")