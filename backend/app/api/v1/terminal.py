"""
Terminal WebSocket endpoint for executing commands.
"""
import asyncio
import json
import subprocess
import os
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.core.config import settings

router = APIRouter()


@router.websocket("/terminal")
async def websocket_terminal(
    websocket: WebSocket,
    repository_id: Optional[int] = Query(None),
):
    """
    WebSocket endpoint for terminal access.
    Executes commands in the workspace or repository directory.
    """
    await websocket.accept()
    
    # Determine working directory
    if repository_id:
        workspace_path = Path(settings.WORKSPACE_STORAGE_PATH)
        work_dir = workspace_path / f"repo_{repository_id}"
        if not work_dir.exists():
            await websocket.send_json({
                "type": "error",
                "content": f"Repository {repository_id} not found in workspace.\r\n"
            })
            await websocket.close()
            return
    else:
        work_dir = Path(settings.WORKSPACE_STORAGE_PATH)
        work_dir.mkdir(parents=True, exist_ok=True)
    
    # Store current working directory
    current_dir = Path(work_dir).resolve()
    process: Optional[subprocess.Popen] = None
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "output",
            "content": f"Polonium Terminal\r\nWorking directory: {current_dir}\r\nType 'help' for available commands.\r\n\r\n"
        })
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "input":
                command = message.get("command", "").strip()
                
                if not command:
                    continue
                
                # Handle built-in commands
                if command == "help":
                    help_text = """
Available commands:
  help              - Show this help message
  pwd               - Print current working directory
  ls [dir]          - List directory contents
  cd [dir]          - Change directory
  cat [file]        - Display file contents
  clear             - Clear terminal
  exit              - Close terminal connection

Note: Other commands are executed in the workspace directory.
"""
                    await websocket.send_json({
                        "type": "output",
                        "content": help_text
                    })
                    continue
                
                elif command == "clear":
                    await websocket.send_json({
                        "type": "output",
                        "content": "\x1b[2J\x1b[H"  # ANSI clear screen
                    })
                    continue
                
                elif command == "exit":
                    await websocket.send_json({
                        "type": "output",
                        "content": "Closing terminal...\r\n"
                    })
                    break
                
                elif command.startswith("cd "):
                    # Handle cd command
                    target = command[3:].strip()
                    if not target:
                        target = str(work_dir)
                    
                    try:
                        new_dir = (current_dir / target).resolve()
                        # Ensure we stay within workspace
                        workspace_base = Path(settings.WORKSPACE_STORAGE_PATH).resolve()
                        if str(new_dir).startswith(str(workspace_base)):
                            current_dir = new_dir
                            if not current_dir.exists():
                                current_dir.mkdir(parents=True, exist_ok=True)
                            await websocket.send_json({
                                "type": "output",
                                "content": f"{current_dir}\r\n"
                            })
                        else:
                            await websocket.send_json({
                                "type": "error",
                                "content": "Access denied: Cannot navigate outside workspace.\r\n"
                            })
                    except Exception as e:
                        await websocket.send_json({
                            "type": "error",
                            "content": f"cd: {str(e)}\r\n"
                        })
                    continue
                
                elif command == "pwd":
                    await websocket.send_json({
                        "type": "output",
                        "content": f"{current_dir}\r\n"
                    })
                    continue
                
                elif command.startswith("ls"):
                    # Handle ls command
                    target = command[2:].strip() or "."
                    try:
                        target_path = (current_dir / target).resolve()
                        if target_path.is_dir():
                            items = list(target_path.iterdir())
                            output = "\n".join([item.name for item in items]) + "\r\n"
                        elif target_path.exists():
                            output = f"{target_path.name}\r\n"
                        else:
                            output = f"ls: {target}: No such file or directory\r\n"
                        await websocket.send_json({
                            "type": "output",
                            "content": output
                        })
                    except Exception as e:
                        await websocket.send_json({
                            "type": "error",
                            "content": f"ls: {str(e)}\r\n"
                        })
                    continue
                
                elif command.startswith("cat "):
                    # Handle cat command
                    file_path = command[4:].strip()
                    try:
                        target_file = (current_dir / file_path).resolve()
                        workspace_base = Path(settings.WORKSPACE_STORAGE_PATH).resolve()
                        if str(target_file).startswith(str(workspace_base)) and target_file.exists():
                            content = target_file.read_text(encoding="utf-8", errors="replace")
                            await websocket.send_json({
                                "type": "output",
                                "content": content + "\r\n"
                            })
                        else:
                            await websocket.send_json({
                                "type": "error",
                                "content": f"cat: {file_path}: No such file or directory\r\n"
                            })
                    except Exception as e:
                        await websocket.send_json({
                            "type": "error",
                            "content": f"cat: {str(e)}\r\n"
                        })
                    continue
                
                else:
                    # Execute shell command
                    try:
                        # Determine shell based on OS
                        if os.name == "nt":  # Windows
                            shell_cmd = ["cmd", "/c", command]
                        else:  # Unix-like
                            shell_cmd = ["/bin/sh", "-c", command]
                        
                        process = subprocess.Popen(
                            shell_cmd,
                            cwd=str(current_dir),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            stdin=subprocess.PIPE,
                            text=True,
                            bufsize=1,
                        )
                        
                        # Read output line by line
                        for line in process.stdout:
                            await websocket.send_json({
                                "type": "output",
                                "content": line
                            })
                        
                        process.wait()
                        if process.returncode != 0:
                            await websocket.send_json({
                                "type": "error",
                                "content": f"\r\nProcess exited with code {process.returncode}\r\n"
                            })
                        else:
                            await websocket.send_json({
                                "type": "exit",
                                "code": process.returncode
                            })
                        
                        process = None
                        
                    except Exception as e:
                        await websocket.send_json({
                            "type": "error",
                            "content": f"Error executing command: {str(e)}\r\n"
                        })
            
            elif message.get("type") == "interrupt":
                # Handle Ctrl+C
                if process:
                    try:
                        process.terminate()
                        process.wait(timeout=1)
                    except:
                        process.kill()
                    process = None
                    await websocket.send_json({
                        "type": "output",
                        "content": "\r\n^C\r\n"
                    })
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "content": f"Terminal error: {str(e)}\r\n"
        })
    finally:
        if process:
            try:
                process.terminate()
            except:
                pass
        await websocket.close()





