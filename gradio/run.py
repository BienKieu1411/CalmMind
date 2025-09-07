# run.py
import os
import subprocess

if __name__ == "__main__":
    port = os.environ.get("PORT", "7860")
    os.environ["PORT"] = str(port)

    print(f"Starting backend (Gradio app.py) at http://localhost:{port}")

    subprocess.run(["python", "app.py"])
