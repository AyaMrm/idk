# screenshotTacker.py
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
    def __init__(self, quality: int = 65, max_width: int = 1600):
        self.quality = max(30, min(95, quality))
        self.max_width = max_width
        self.platform = sys.platform
        self.check_platform()
        self.displays = self._detect_displays()  # Ajouté

    def check_platform(self):
        if not (self.platform.startswith('win') or self.platform.startswith('linux')):
            raise RuntimeError(f"Unsupported platform: {self.platform}")

    def _detect_displays(self) -> List[dict]:
        if not _HAS_MSS:
            return []
        try:
            with mss.mss() as sct:
                return sct.monitors[1:]
        except:
            return []

    def capture_display(self, monitor: dict) -> Optional[Image.Image]:
        if not _HAS_MSS:
            return None
        try:
            with mss.mss() as sct:
                screenshot = sct.grab(monitor)
                return Image.frombytes('RGB', screenshot.size, screenshot.rgb)
        except:
            return None

    def capture_mss(self) -> Optional[List[Dict]]:
        try:
            if not _HAS_MSS:
                return None
            monitors = []
            for monitor_id, monitor in enumerate(self._detect_displays(), 1):
                try:
                    img = self.capture_display(monitor)
                    if img:
                        monitors.append({
                            'id': monitor_id,
                            'image': img,
                            'width': img.width,
                            'height': img.height
                        })
                except:
                    continue
            return monitors if monitors else None
        except:
            return None

    def capture_windows_native(self) -> Optional[List[Dict]]:
        try:
            import win32gui, win32ui, win32con, win32api
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
            img = Image.frombytes('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX')

            win32gui.DeleteObject(screenshot.GetHandle())
            mem_dc.DeleteDC()
            win32gui.ReleaseDC(hdesktop, desktop_dc)

            return [{'id': 1, 'image': img, 'width': img.width, 'height': img.height}]
        except:
            return None

    def capture_linux_fallback(self) -> Optional[List[Dict]]:
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab()
            return [{'id': 1, 'image': img, 'width': img.width, 'height': img.height}]
        except:
            try:
                import subprocess, tempfile, os
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    temp_path = tmp.name
                try:
                    subprocess.run(['scrot', temp_path], check=True, timeout=10,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    img = Image.open(temp_path)
                    result = [{'id': 1, 'image': img, 'width': img.width, 'height': img.height}]
                finally:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                return result
            except:
                return None

    def optimize_image(self, image: Image.Image, quality: int, max_width: int = None) -> Image.Image:
        img = image.copy()
        if max_width and img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        return Image.open(buffer)

    def image_to_base64(self, image: Image.Image) -> Dict[str, Any]:
        try:
            buffer = io.BytesIO()
            image.save(buffer, 'JPEG', quality=self.quality, optimize=True)
            image_data = base64.b64encode(buffer.getvalue()).decode('ascii')
            size_kb = (len(image_data) * 3) // 4 // 1024
            return {
                'success': True,
                'data': image_data,
                'width': image.width,
                'height': image.height,
                'size_kb': size_kb,
                'quality': self.quality
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def capture_single(self) -> Dict[str, Any]:
        try:
            screens = None
            if self.platform.startswith('win'):
                screens = self.capture_mss() or self.capture_windows_native()
            else:
                screens = self.capture_mss() or self.capture_linux_fallback()

            if screens and len(screens) > 0:
                screen = screens[0]
                optimized_img = self.optimize_image(screen['image'], self.quality, self.max_width)
                return self.image_to_base64(optimized_img)
            else:
                return {'success': False, 'error': 'All capture methods failed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def capture_multiple(self) -> Dict[str, Any]:
        try:
            raw_screens = None
            if self.platform.startswith('win'):
                raw_screens = self.capture_mss() or self.capture_windows_native()
            else:
                raw_screens = self.capture_mss() or self.capture_linux_fallback()

            if not raw_screens or len(raw_screens) == 0:
                single = self.capture_single()
                if single['success']:
                    return {'success': True, 'displays': 1, 'results': [single]}
                else:
                    return {'success': False, 'error': 'No display captured'}

            results = []
            for screen in raw_screens:
                opt_img = self.optimize_image(screen['image'], self.quality, self.max_width)
                b64_result = self.image_to_base64(opt_img)
                if b64_result['success']:
                    b64_result['display_id'] = screen['id']
                    results.append(b64_result)

            return {'success': True, 'displays': len(results), 'results': results}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_config(self, quality: int = None, max_width: int = None) -> Dict[str, Any]:
        if quality is not None:
            self.quality = max(30, min(95, quality))
        if max_width is not None:
            self.max_width = max_width
        return {'quality': self.quality, 'max_width': self.max_width}

_capture_instance = None

def get_capturer(quality: int = 65, max_width: int = 1600) -> 'screenshotTacker':
    global _capture_instance
    if _capture_instance is None:
        _capture_instance = screenshotTacker(quality=quality, max_width=max_width)
    else:
        if quality != _capture_instance.quality or max_width != _capture_instance.max_width:
            _capture_instance.update_config(quality=quality, max_width=max_width)
    return _capture_instance


def take_screenshot(quality: int = 65, multi_display: bool = False) -> Dict[str, Any]:
    capturer = get_capturer(quality=quality) 

    if multi_display:
        result = capturer.capture_multiple()
        if result['success']:
            for r in result['results']:
                r['quality'] = capturer.quality
        return result
    else:
        result = capturer.capture_single()
        if result['success']:
            result['quality'] = capturer.quality
        return result


def handle_command(command_data: str) -> str:
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
    result = take_screenshot(quality=70, multi_display=False)
    if result['success']:
        print(f"SUCCESS: {result['width']}x{result['height']} - {result['size_kb']}KB")
    else:
        print(f"FAILED: {result.get('error')}")