import os
import shutil
import subprocess


def fetch_build():
    # Specify the directory where the vite project is located
    vite_path = "/Users/jaewoong/FrontEnd/WebCraftShare-Web"
    static_path = "/Users/jaewoong/PycharmProjects/WebCraftShare/static"

    # Change the working directory to the specified directory
    os.chdir(vite_path)

    # Execute the "npm run build" command
    process = subprocess.Popen(['npm', 'run', 'build'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in process.stdout:
        print(line.decode().strip())
    result = process.wait()

    if result == 0:
        print("Build succeeded!")
    else:
        print("Build failed!")
        exit(1)

    # ... [rest of the script remains the same]


    # Delete all files and folders in the static folder
    for root, dirs, files in os.walk(static_path, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            print(f"Deleting {file_path}")
            os.remove(file_path)
        for name in dirs:
            dir_path = os.path.join(root, name)
            print(f"Deleting {dir_path}")
            shutil.rmtree(dir_path)

    dist_path = os.path.join(vite_path, "dist")
    assets_path = os.path.join(dist_path, "assets")

    # Copy assets folder to static folder from dist folder
    try:
        shutil.copytree(assets_path, os.path.join(static_path, "assets"))
        print("Assets copied successfully!")
    except Exception as e:
        print(f"Failed to copy assets folder! {str(e)}")
        exit(1)

    # Copy index.html file
    try:
        shutil.copy2(os.path.join(dist_path, "index.html"), static_path)
        print("index.html copied successfully!")
    except Exception as e:
        print(f"Failed to copy index.html file! {str(e)}")
        exit(1)

    # Copy all .html files in dist_path/public folder to static_path
    public_path = os.path.join(dist_path, "public")
    for file_name in os.listdir(public_path):
        if file_name.endswith(".html"):
            src_path = os.path.join(public_path, file_name)
            print(f"Copying {src_path}")
            try:
                shutil.copy2(src_path, static_path)
                print(f"{src_path} copied successfully!")
            except Exception as e:
                print(f"Failed to copy {src_path}! {str(e)}")
                exit(1)

    print("Successfully copied all files!")


if __name__ == '__main__':
    fetch_build()
