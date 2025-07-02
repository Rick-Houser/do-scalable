from flask import Flask, jsonify, render_template_string
import os
import socket
import requests
import json
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Kubernetes Scalability Demo</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container { 
            background: rgba(255,255,255,0.1); 
            padding: 30px; 
            border-radius: 10px; 
            backdrop-filter: blur(10px);
        }
        .pod-info { 
            background: rgba(255,255,255,0.2); 
            padding: 20px; 
            margin: 20px 0; 
            border-radius: 8px; 
        }
        .node-info { 
            background: rgba(0,255,0,0.2); 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 5px; 
        }
        .refresh-btn {
            background: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        .refresh-btn:hover { background: #45a049; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Kubernetes Scalability Demo</h1>
        <p style="text-align: center; font-style: italic; margin-bottom: 30px;">Demo by Rick Houser | <a href="https://rickhouser.me" target="_blank" style="color: #FFD700; text-decoration: none;">rickhouser.me</a></p>
        <div class="pod-info">
            <h2>Pod Information</h2>
            <p><strong>Pod Name:</strong> {{ pod_name }}</p>
            <p><strong>Pod IP:</strong> {{ pod_ip }}</p>
            <p><strong>Namespace:</strong> {{ namespace }}</p>
            <p><strong>Request Time:</strong> {{ timestamp }}</p>
        </div>

        <div class="node-info">
            <h2>Node Information</h2>
            <p><strong>Node Name:</strong> {{ node_name }}</p>
            <p><strong>Node IP:</strong> {{ node_ip }}</p>
        </div>

        <div style="margin-top: 30px;">
            <h3>🎯 Scalability Demo</h3>
            <p>This pod is running on <strong>{{ node_name }}</strong></p>
            <p>Refresh this page multiple times to see requests hit different pods across your {{ total_nodes }} node cluster!</p>
            <p>As load increases, HPA will create more pods distributed across nodes.</p>
        </div>

        <button class="refresh-btn" onclick="window.location.reload()">🔄 Refresh to Hit Different Pod</button>
        
        <div style="margin-top: 20px;">
            <a href="/api/info" style="color: #fff;">View Raw JSON Data</a>
        </div>
    </div>
</body>
</html>
"""

def get_pod_info():
    """Get pod and node information from Kubernetes environment variables"""
    return {
        'demo_author': 'Rick Houser',
        'website': 'https://rickhouser.me',
        'pod_name': os.getenv('HOSTNAME', 'unknown-pod'),
        'pod_ip': os.getenv('POD_IP', socket.gethostbyname(socket.gethostname())),
        'node_name': os.getenv('NODE_NAME', 'unknown-node'),
        'node_ip': os.getenv('NODE_IP', 'unknown-node-ip'),
        'namespace': os.getenv('POD_NAMESPACE', 'default'),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    }

@app.route('/')
def home():
    """Main page showing pod and node information"""
    pod_info = get_pod_info()
    return render_template_string(HTML_TEMPLATE, **pod_info)

@app.route('/api/info')
def api_info():
    """API endpoint returning JSON with pod/node info"""
    return jsonify(get_pod_info())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)