#!/bin/bash

# 启动后端服务器
echo "启动后端服务器..."
cd server
python3 web_server.py &
SERVER_PID=$!

# 等待后端启动
sleep 2

# 启动前端开发服务器
echo "启动前端开发服务器..."
cd ../web
npm start &
WEB_PID=$!

echo "服务已启动:"
echo "  - 后端: http://localhost:5001 (PID: $SERVER_PID)"
echo "  - 前端: http://localhost:3000 (PID: $WEB_PID)"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 捕获退出信号
trap "kill $SERVER_PID $WEB_PID; exit" INT TERM

# 等待
wait
