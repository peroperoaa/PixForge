import json

with open("tasks.json", "r", encoding="utf-8") as f:
    data = json.load(f)

new_tasks = [
  {
    "task": "Define Pixelization Module Structure and Schemas",
    "description": "Create directories, interfaces, and Pydantic models for the Pixelization module.",
    "steps": [
      {
        "step": 1,
        "description": "Create src/modules/pixelization and tests/modules/pixelization directories with __init__.py"
      },
      {
        "step": 2,
        "description": "Define PixelizationInput and PixelizationOutput Pydantic schemas in schemas.py"
      },
      {
        "step": 3,
        "description": "Define BasePixelization interface class in interface.py"
      },
      {
        "step": 4,
        "description": "Create exceptions.py for custom ComfyUI errors like connection and timeout errors"
      }
    ],
    "acceptance-criteria": "Project structure exists for module 3. Schemas validate input image paths. Interface enforces the generate() method.",
    "test-plan": {
      "unit": [
        "PixelizationInput accepts valid local file paths and image byte streams",
        "BasePixelization abstraction prevents direct instantiation"
      ],
      "integration": [],
      "e2e-manual": []
    },
    "skills": [
      "tdd-workflow"
    ],
    "complete": False
  },
  {
    "task": "Update ConfigManager for ComfyUI Settings",
    "description": "Extend ConfigManager to support ComfyUI URL and workflow template path configurations.",
    "steps": [
      {
        "step": 1,
        "description": "Add COMFYUI_URL and COMFYUI_WORKFLOW_TEMPLATE to .env.example"
      },
      {
        "step": 2,
        "description": "Update ConfigManager to parse these values, prioritizing runtime args over environment variables"
      }
    ],
    "acceptance-criteria": "ConfigManager returns valid ComfyUI endpoint URLs and template file paths.",
    "test-plan": {
      "unit": [
        "get_comfyui_url defaults to http://127.0.0.1:8000 if none provided",
        "Runtime arguments override environment variables for comfyui_url"
      ],
      "integration": [],
      "e2e-manual": []
    },
    "skills": [
      "tdd-workflow"
    ],
    "complete": False
  },
  {
    "task": "Implement ComfyUI API Client",
    "description": "Develop a lower-level HTTP and WebSocket client to communicate with the ComfyUI API.",
    "steps": [
      {
        "step": 1,
        "description": "Create comfyui_client.py to handle HTTP POST /prompt and POST /upload/image"
      },
      {
        "step": 2,
        "description": "Implement HTTP GET /history and GET /view to retrieve results"
      },
      {
        "step": 3,
        "description": "Implement WebSocket listener to block and track generation progress by prompt_id"
      },
      {
        "step": 4,
        "description": "Add configurable timeout logic to prevent infinite hangs"
      }
    ],
    "acceptance-criteria": "Client can successfully upload images, queue workflows, track execution via WebSocket, and download resulting images with explicit timeout limits.",
    "test-plan": {
      "unit": [
        "Client HTTP methods successfully parse 200 OK responses with mock data",
        "WebSocket listener correctly identifies completion message for specific prompt_id",
        "Client throws specific ComfyUITimeoutException when generation exceeds timeout"
      ],
      "integration": [
        "Client gracefully handles ConnectionRefusedError when local ComfyUI is offline"
      ],
      "e2e-manual": []
    },
    "skills": [
      "tdd-workflow",
      "systematic-debugging"
    ],
    "complete": False
  },
  {
    "task": "Implement ComfyUI Adapter Control Logic",
    "description": "Build the ComfyUIAdapter class to translate inputs into a JSON workflow and orchestrate the API Client.",
    "steps": [
      {
        "step": 1,
        "description": "Create comfyui_adapter.py implementing BasePixelization interface"
      },
      {
        "step": 2,
        "description": "Implement logic to load workflow_api.json template from disk"
      },
      {
        "step": 3,
        "description": "Inject dynamic variables (uploaded image filename, specific prompts, seed) into fixed Node IDs"
      },
      {
        "step": 4,
        "description": "Wrap generation execution with logging and map exceptions correctly"
      }
    ],
    "acceptance-criteria": "Adapter successfully coordinates the payload generation, uses the client to execute the task, and returns a verified PixelizationOutput.",
    "test-plan": {
      "unit": [
        "Adapter generates correct workflow JSON with dynamic node values updated",
        "generate method catches internal client errors and raises adapter-specific exceptions"
      ],
      "integration": [
        "Adapter executes full lifecycle (upload -> prompt -> wait -> download) using a mocked client instance"
      ],
      "e2e-manual": []
    },
    "skills": [
      "tdd-workflow"
    ],
    "complete": False
  },
  {
    "task": "Verify Module 3 with Integration Script",
    "description": "Create a demonstrator script that processes a local image through the full ComfyUI pipeline.",
    "steps": [
      {
        "step": 1,
        "description": "Create workflow_api_template.json with a valid ComfyUI Graph containing ControlNet and Checkpoint"
      },
      {
        "step": 2,
        "description": "Create demo_module3.py to load an image and invoke ComfyUIAdapter"
      }
    ],
    "acceptance-criteria": "Script runs end-to-end against a running local ComfyUI instance and outputs a pixelated image to disk.",
    "test-plan": {
      "unit": [],
      "integration": [],
      "e2e-manual": [
        "Execute script while ComfyUI is running locally -> verify converted pixel art image is generated in output folder",
        "Execute script while ComfyUI is stopped -> verify graceful connection error message is printed"
      ]
    },
    "skills": [
      "verification-before-completion"
    ],
    "complete": False
  }
]

data["tasks"].extend(new_tasks)

with open("tasks.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("tasks.json updated successfully")
