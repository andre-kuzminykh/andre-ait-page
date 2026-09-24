import os, sys, glob, socket
ROOT = '/home/user/andre-ait-page'
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import record_lecture as rl
import lecture_check as lc

def chromium():
    return lc.chromium_path() or sorted(glob.glob('/opt/pw-browsers/chromium-*/chrome-linux/chrome'))[-1]

def start():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); rl.PORT = s.getsockname()[1]; s.close()
    return rl.serve(), rl.PORT

def route_ctx(ctx, extra=None):
    vendor = lc.vendor_dir()
    vr = rl.vendor_route(vendor) if vendor else None
    def h(route):
        url = route.request.url
        if extra:
            for k, v in extra.items():
                if url.endswith(k):
                    return route.fulfill(status=200, body=open(v, 'rb').read(), content_type='text/html; charset=utf-8')
        if vr: return vr(route)
        return route.continue_()
    ctx.route('**/*', h)
