import cv2
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

capture = None


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith(".mjpg"):
            self.send_response(200)
            self.send_header(
                "Content-type", "multipart/x-mixed-replace; boundary=--jpgboundary"
            )
            self.end_headers()
            while True:
                try:
                    rc, img = capture.read()
                    if not rc:
                        print("Failed to capture from webcam")
                        continue

                    img_str = cv2.imencode(".jpg", img)[1].tostring()

                    self.send_header("Content-type", "image/jpeg")
                    self.send_header("Content-length", len(img_str))
                    self.end_headers()

                    self.wfile.write(img_str)
                    self.wfile.write(b"\r\n--jpgboundary\r\n")

                except KeyboardInterrupt:
                    self.wfile.write(b"\r\n--jpgboundary--\r\n")
                    break
                except BrokenPipeError:
                    continue


def main():
    global capture
    capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # This makes the frame rate faster
    capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))

    try:
        server = ThreadedHTTPServer(("", 8081), CamHandler)
        print("server started at localhost:8081/cam.mjpg")
        server.serve_forever()
    except KeyboardInterrupt:
        capture.release()
        server.socket.close()


if __name__ == "__main__":
    main()
