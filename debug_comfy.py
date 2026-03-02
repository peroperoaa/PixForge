import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("Querying ComfyUI for available models...")

try:
    # 获取所有节点定义，其中包含了模型列表
    resp = requests.get(f"{BASE_URL}/object_info")
    if resp.status_code != 200:
        print(f"Failed to get object info: {resp.status_code}")
        exit(1)
    
    info = resp.json()
    
    # 打印 Checkpoints
    print("\n[Available Checkpoints]")
    checkpoints = info.get("CheckpointLoaderSimple", {}).get("input", {}).get("required", {}).get("ckpt_name", [])
    if isinstance(checkpoints, list) and len(checkpoints) > 0 and isinstance(checkpoints[0], list):
        # 兼容新版 ComfyUI 格式
        checkpoints = checkpoints[0]
        
    for ckpt in checkpoints:
        print(f"  - {ckpt}")

    # 打印 ControlNets
    print("\n[Available ControlNets]")
    controlnets = info.get("ControlNetLoader", {}).get("input", {}).get("required", {}).get("control_net_name", [])
    if isinstance(controlnets, list) and len(controlnets) > 0 and isinstance(controlnets[0], list):
         controlnets = controlnets[0]
         
    for cn in controlnets:
        print(f"  - {cn}")

    print("\n" + "="*40)
    print("请复制上面列表中的 EXACT 文件名填入 JSON 中")
    print("="*40)

except Exception as e:
    print(f"Error: {e}")
